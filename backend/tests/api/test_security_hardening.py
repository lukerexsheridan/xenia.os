"""Hardening-sprint regression tests: each pins a verified defect closed."""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.main import create_app
from tests.api.test_console import seed_draft_brief
from tests.api.test_workbench import make_client
from tests.conftest import mint_supabase_token


def bearer(subject_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {subject_token}"}


def test_a_draft_cannot_reference_another_tenants_prospect(db: Engine) -> None:
    """The cross-tenant write/DoS: an attacker PUTting a draft against a
    foreign prospect UUID would squat the global unique constraint and 500
    the victim's own draft save. Now: their prospect, their workspace, or
    404 — indistinguishable from absence."""
    client = make_client()
    victim = seed_draft_brief(client, f"victim-{uuid4()}")

    attacker_token = mint_supabase_token(f"attacker-{uuid4()}")
    attack = client.put(
        f"/v1/prospects/{victim['prospect_id']}/draft",
        headers=bearer(attacker_token),
        json={"body": "squatting your draft slot"},
    )
    assert attack.status_code == 404

    # The victim's own edit path is unharmed.
    victims_edit = client.put(
        f"/v1/prospects/{victim['prospect_id']}/draft",
        headers=bearer(victim["owner_token"]),
        json={"body": "my own words"},
    )
    assert victims_edit.status_code == 200
    # And the attacker never sees the victim's draft either way.
    assert (
        client.get(
            f"/v1/prospects/{victim['prospect_id']}/draft", headers=bearer(attacker_token)
        ).status_code
        == 404
    )


def test_csv_export_neutralises_formula_names(db: Engine) -> None:
    """Business names come from the crawled world; '=HYPERLINK(...)' must
    not execute when the founder opens the export in a spreadsheet."""
    from sqlalchemy.orm import Session

    from app.repositories.audit import SqlAuditEntryRepo
    from app.repositories.business_records import SqlBusinessRecordRepo
    from app.repositories.prospects import SqlProspectRepo
    from app.services.create_prospect import CreateProspect

    api = TestClient(create_app())
    token = mint_supabase_token(f"csv-{uuid4()}")
    workspace_id = api.get("/v1/me", headers=bearer(token)).json()["workspace"]["id"]
    with Session(db) as session:
        from uuid import UUID

        record = SqlBusinessRecordRepo(session).find_or_create(
            canonical_name='=HYPERLINK("http://evil.example")',
            website_domain="evil.example",
            register_number=None,
        )
        CreateProspect(
            SqlProspectRepo(session, UUID(workspace_id)),
            SqlBusinessRecordRepo(session),
            SqlAuditEntryRepo(session, UUID(workspace_id)),
        ).execute(
            workspace_id=UUID(workspace_id),
            business_record_id=record.id,
            binding_confidence=0.9,
        )
        session.commit()

    export = api.get("/v1/prospects/export.csv", headers=bearer(token))
    assert export.status_code == 200
    data_line = export.text.splitlines()[1]
    assert data_line.startswith("\"'=") or data_line.startswith("'=")


def test_a_paste_accident_cannot_flood_the_dna_with_laws(db: Engine) -> None:
    api = TestClient(create_app())
    headers = bearer(mint_supabase_token(f"flood-{uuid4()}"))
    for key, answer in (
        ("homework", "We run paid social."),
        ("business_attributes", "DTC brands"),
        ("service_need_evidence", "Weak creative"),
        ("buying_signals", "Hiring marketers"),
    ):
        assert (
            api.post(
                "/v1/interview/answers",
                headers=headers,
                json={"question_key": key, "text": answer},
            ).status_code
            == 200
        )
    flood = api.post(
        "/v1/interview/answers",
        headers=headers,
        json={"question_key": "disqualifiers", "text": "\n".join(f"No {i}" for i in range(50))},
    )
    assert flood.status_code == 422
    assert "hard lines" in flood.json()["message"]
