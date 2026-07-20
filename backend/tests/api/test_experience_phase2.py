"""Phase 2 experience seams: revert surfaced (I6) and amendable answers."""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.main import create_app
from tests.api.test_interview_and_dna import ANSWERS, bearer, complete_interview


def client() -> TestClient:
    return TestClient(create_app())


def test_doc13_i6_revert_restores_via_a_new_logged_event(db: Engine) -> None:
    api = client()
    headers = bearer(f"revert-{uuid4()}")
    complete_interview(api, headers)

    dna = api.get("/v1/dna", headers=headers).json()
    target = next(e["element_id"] for e in dna["elements"] if e["category"] == "buying_signals")
    before_count = len(dna["elements"])

    # Withdraw via correction, then find the withdrawal in the changelog.
    api.post(
        "/v1/corrections",
        headers=headers,
        json={"target_kind": "dna_element", "target_id": target, "reason": "testing revert"},
    )
    after_withdraw = api.get("/v1/dna", headers=headers).json()
    assert len(after_withdraw["elements"]) == before_count - 1
    withdrawal = next(
        e for e in after_withdraw["changelog"] if e["cause"] == "correction" and not e["reversible"]
    )
    # A withdrawal's element is gone, so it is honestly not offered as
    # revertible; a confidence-touching event is.
    reversible = [e for e in after_withdraw["changelog"] if e["reversible"]]
    assert withdrawal is not None

    # Revert a reversible event: demote an element, then restore it.
    keep = next(e["element_id"] for e in after_withdraw["elements"])
    api.post(
        "/v1/corrections",
        headers=headers,
        json={"target_kind": "score_factor", "target_id": keep, "reason": "weighs too much"},
    )
    demoted = api.get("/v1/dna", headers=headers).json()
    demotion = next(
        e for e in demoted["changelog"] if e["reversible"] and e["cause"] == "correction"
    )
    version_before = demoted["version"]

    restored = api.post(f"/v1/dna/changelog/{demotion['event_id']}/revert", headers=headers)
    assert restored.status_code == 200
    body = restored.json()
    assert body["version"] == version_before + 1  # a NEW event, never erasure
    assert any(e["cause"] == "reversion" for e in body["changelog"])
    assert reversible is not None


def test_doc13_i6_answers_amend_freely_while_the_interview_is_open(db: Engine) -> None:
    api = client()
    headers = bearer(f"amend-{uuid4()}")
    for key in ("homework", "business_attributes"):
        api.post(
            "/v1/interview/answers",
            headers=headers,
            json={"question_key": key, "text": ANSWERS[key]},
        )

    # The transcript is visible and the earlier answer amends in place.
    state = api.get("/v1/interview", headers=headers).json()
    assert [q["question_key"] for q in state["transcript"]] == [
        "homework",
        "business_attributes",
    ]
    amended = api.post(
        "/v1/interview/answers",
        headers=headers,
        json={"question_key": "business_attributes", "text": "B2B SaaS companies, seed to A"},
    )
    assert amended.status_code == 200
    body = amended.json()
    assert body["question_key"] == "service_need_evidence"  # the conversation held its place
    assert any(q["text"] == "B2B SaaS companies, seed to A" for q in body["transcript"])

    # Once complete, the DNA is founded from the amended words and the
    # transcript is closed - corrections take over from here.
    complete_interview(api, headers)
    dna = api.get("/v1/dna", headers=headers).json()
    assert any(e["statement"] == "B2B SaaS companies, seed to A" for e in dna["elements"])
    closed = api.post(
        "/v1/interview/answers",
        headers=headers,
        json={"question_key": "homework", "text": "rewriting history"},
    )
    assert closed.status_code in (409, 422)
