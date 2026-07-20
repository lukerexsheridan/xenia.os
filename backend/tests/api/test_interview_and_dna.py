"""The interview founds the DNA; the customer endorses it (Doc 10, Sprint 18)."""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.main import create_app
from tests.conftest import mint_supabase_token


def client() -> TestClient:
    return TestClient(create_app())


def bearer(subject: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_supabase_token(subject)}"}


ANSWERS = {
    "homework": "We run paid social for DTC brands.",
    "business_attributes": "DTC e-commerce brands, one to twenty million revenue",
    "service_need_evidence": "Running ads with weak creative and no landing-page testing",
    "buying_signals": "Hiring their first marketing manager",
    "disqualifiers": "No franchise businesses\nNo dropshippers",
}


def complete_interview(api: TestClient, headers: dict[str, str]) -> None:
    state = api.get("/v1/interview", headers=headers).json()
    while not state["completed"]:
        response = api.post(
            "/v1/interview/answers",
            headers=headers,
            json={"question_key": state["question_key"], "text": ANSWERS[state["question_key"]]},
        )
        assert response.status_code == 200, response.text
        state = response.json()


def test_doc03_c1_the_interview_is_conversational_resumable_and_founds_the_dna(
    db: Engine,
) -> None:
    api = client()
    headers = bearer(f"interview-{uuid4()}")

    opening = api.get("/v1/interview", headers=headers).json()
    assert opening["question_key"] == "homework"  # homework-first (Doc 06 §4)
    assert opening["total"] == 5 and opening["answered"] == 0

    # Out-of-order answers are refused: the transcript is one conversation.
    wrong = api.post(
        "/v1/interview/answers",
        headers=headers,
        json={"question_key": "disqualifiers", "text": "No franchises"},
    )
    assert wrong.status_code == 422

    # Answer the first, then "close the tab": resuming lands mid-way.
    api.post(
        "/v1/interview/answers",
        headers=headers,
        json={"question_key": "homework", "text": ANSWERS["homework"]},
    )
    resumed = api.get("/v1/interview", headers=headers).json()
    assert resumed["answered"] == 1
    assert resumed["question_key"] == "business_attributes"

    complete_interview(api, headers)
    done = api.get("/v1/interview", headers=headers).json()
    assert done["completed"] is True and done["dna_created"] is True

    dna = api.get("/v1/dna", headers=headers).json()
    statements = [element["statement"] for element in dna["elements"]]
    # The customer's words, verbatim; disqualifier lines became laws.
    assert ANSWERS["business_attributes"] in statements
    assert "No franchise businesses" in statements and "No dropshippers" in statements
    laws = [e for e in dna["elements"] if e["category"] == "disqualifiers"]
    assert len(laws) == 2 and all(e["decay_class"] == "customer_law" for e in laws)
    # Founded unendorsed, changelog written from birth.
    assert dna["endorsed"] is False
    assert len(dna["changelog"]) == len(dna["elements"])


def test_doc03_s3_endorsement_is_its_own_moment(db: Engine) -> None:
    api = client()
    headers = bearer(f"endorse-{uuid4()}")
    complete_interview(api, headers)

    endorsed = api.post("/v1/dna/endorse", headers=headers)
    assert endorsed.status_code == 200
    body = endorsed.json()
    assert body["endorsed"] is True
    assert any(entry["cause"] == "endorsement" for entry in body["changelog"])

    # Exports: the DNA document and the N1-safe prospect CSV.
    pdf = api.get("/v1/dna/document.pdf", headers=headers)
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf"
    csv_export = api.get("/v1/prospects/export.csv", headers=headers)
    assert csv_export.status_code == 200
    assert csv_export.text.splitlines()[0] == "business_name,status,surfaced_at"
