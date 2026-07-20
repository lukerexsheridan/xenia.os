"""The workbench end to end: the concierge kit's whole flow (Doc 10, Sprint 6).

Editor authorisation, snapshot → business record → evidence → prospect →
DNA → brief → finalise (frozen receipt table + derivation) → PDFs → edit
log — the machinery a real concierge brief runs on, exercised against real
Postgres with only the outward fetch faked.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from app.api.internal import workbench
from app.domain.research_brief import BriefSectionCode
from app.integrations.sources.politeness import FetchedContent
from app.main import create_app
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.capture_snapshot import CaptureSnapshot
from tests.conftest import TEST_EDITOR_SUBJECT, mint_supabase_token
from tests.services.test_capture_snapshot import InMemoryObjectStore, ScriptedEngine

OBSERVED_AT = datetime(2026, 7, 13, 9, 0, tzinfo=UTC)


def editor_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_supabase_token(TEST_EDITOR_SUBJECT)}"}


def make_client() -> TestClient:
    app = create_app()
    internal_app = _mounted_internal_app(app)

    # Override the capture dependency so no network is touched: the scripted
    # engine returns one page per call.
    from fastapi import Depends

    from app.api.deps import get_db_session

    def get_fake_capture(
        session: Any = Depends(get_db_session),
    ) -> CaptureSnapshot:
        return CaptureSnapshot(
            ScriptedEngine(
                [
                    FetchedContent(
                        url="https://brightpath.example/about",
                        status=200,
                        content=b"<html>Brightpath sells DTC skincare</html>",
                        content_type="text/html",
                    )
                ]
            ),
            InMemoryObjectStore(),
            SqlSourceSnapshotRepo(session),
        )

    internal_app.dependency_overrides[workbench.get_capture_snapshot] = get_fake_capture
    return TestClient(app)


def _mounted_internal_app(app: FastAPI) -> FastAPI:
    for route in app.routes:
        if getattr(route, "path", None) == "/internal":
            mounted = route.app  # type: ignore[attr-defined]
            assert isinstance(mounted, FastAPI)
            return mounted
    raise AssertionError("internal app not mounted")


def provision_workspace(client: TestClient) -> str:
    response = client.get(
        "/v1/me",
        headers={"Authorization": f"Bearer {mint_supabase_token(f'concierge-{uuid4()}')}"},
    )
    assert response.status_code == 200
    return str(response.json()["workspace"]["id"])


def full_sections(cited: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "code": code.value,
            "content": f"Authored content for {code.value}.",
            "cited_evidence_ids": cited if code is BriefSectionCode.B4_MARKETING_GAP else [],
        }
        for code in BriefSectionCode
    ]


# ── Editor authorisation (Doc 08 §8) ─────────────────────────────────────────


def test_doc08_s8_internal_routes_require_a_token(db: Engine) -> None:
    response = make_client().get("/internal/status")
    assert response.status_code == 401


def test_doc08_s8_a_valid_session_without_editor_authorisation_is_refused(db: Engine) -> None:
    response = make_client().get(
        "/internal/status",
        headers={"Authorization": f"Bearer {mint_supabase_token('just-a-customer')}"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "not_authorised"


def test_doc08_s8_an_editor_reaches_the_console(db: Engine) -> None:
    response = make_client().get("/internal/status", headers=editor_headers())
    assert response.status_code == 200


def test_ap4_workbench_routes_never_appear_in_the_public_openapi(db: Engine) -> None:
    schema = create_app().openapi()
    assert not [path for path in schema["paths"] if "workbench" in path or "internal" in path]


# ── The concierge flow, end to end ───────────────────────────────────────────


def test_doc10_sprint6_the_concierge_flow_produces_a_replayable_brief(db: Engine) -> None:
    client = make_client()
    headers = editor_headers()
    workspace_id = provision_workspace(client)

    # 1. Snapshot the prospect's page (politeness-engined, content-addressed).
    snapshot = client.post(
        "/internal/workbench/snapshots",
        json={"url": "https://brightpath.example/about"},
        headers=headers,
    )
    assert snapshot.status_code == 200
    snapshot_id = snapshot.json()["id"]

    # 2. Register the business in the Ring-2 world model.
    business = client.post(
        "/internal/workbench/business-records",
        json={"canonical_name": "Brightpath Ltd", "website_domain": "brightpath.example"},
        headers=headers,
    )
    assert business.status_code == 200
    business_id = business.json()["id"]

    # 3. Capture evidence bound to the snapshot (the provenance contract).
    evidence = client.post(
        "/internal/workbench/evidence",
        json={
            "business_record_id": business_id,
            "claim": "They sell DTC skincare with active paid social",
            "evidence_type": "e1_measured_observation",
            "snapshot_id": snapshot_id,
            "observed_at": OBSERVED_AT.isoformat(),
            "extraction_confidence": 0.9,
            "freshness_class": "weeks",
        },
        headers=headers,
    )
    assert evidence.status_code == 200
    evidence_id = evidence.json()["id"]

    # 4. Bind the workspace to the business (identity claim with confidence).
    prospect = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/prospects",
        json={"business_record_id": business_id, "binding_confidence": 0.95},
        headers=headers,
    )
    assert prospect.status_code == 200
    prospect_id = prospect.json()["id"]

    # 5. The hand-built DNA, changelog written from birth.
    dna = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/dna",
        json={
            "elements": [
                {
                    "category": "business_attributes",
                    "statement": "DTC e-commerce brands, £1-20m revenue",
                    "confidence": 0.8,
                    "decay_class": "customer_law",
                    "origin": "interview",
                },
                {
                    "category": "disqualifiers",
                    "statement": "No franchise businesses",
                    "confidence": 1.0,
                    "decay_class": "customer_law",
                    "origin": "interview",
                },
            ]
        },
        headers=headers,
    )
    assert dna.status_code == 200
    assert dna.json()["element_count"] == 2

    # 6. Author the brief; a draft is not yet complete without all sections.
    brief = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/briefs",
        json={
            "prospect_id": prospect_id,
            "sections": full_sections(cited=[evidence_id])[:-1],
            "couldnt_see": ["Their ad spend levels — the library shows presence only"],
            "confidence_score": 0.72,
        },
        headers=headers,
    )
    assert brief.status_code == 200
    brief_id = brief.json()["id"]
    assert brief.json()["status"] == "draft"
    assert brief.json()["confidence_band"] == "likely"
    assert any("missing section" in p for p in brief.json()["completeness_problems"])

    # 7. Finalising an incomplete brief is refused (Doc 04 §3's floor).
    refused = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{brief_id}/finalise",
        headers=headers,
    )
    assert refused.status_code == 422
    assert "missing section" in refused.json()["message"]

    # 8. Complete the missing section, log a founder edit (the QA delta).
    missing_code = BriefSectionCode.B8_CONFIDENCE_FRESHNESS.value
    updated = client.put(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{brief_id}/sections",
        json={"code": missing_code, "content": "Confidence: likely.", "cited_evidence_ids": []},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["completeness_problems"] == []

    edit = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{brief_id}/edits",
        json={"rubric_dimension": "insight", "note": "sharpened the gap analysis"},
        headers=headers,
    )
    assert edit.status_code == 201

    # 9. Finalise: the receipt table freezes and the derivation is recorded.
    finalised = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{brief_id}/finalise",
        headers=headers,
    )
    assert finalised.status_code == 200
    assert finalised.json()["status"] == "final"
    assert finalised.json()["receipt_count"] == 1

    # 10. A final brief is never edited — regeneration is a new brief.
    frozen = client.put(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{brief_id}/sections",
        json={"code": missing_code, "content": "tampering", "cited_evidence_ids": []},
        headers=headers,
    )
    assert frozen.status_code == 409

    # 11. Both documents render as PDFs.
    brief_pdf = client.get(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{brief_id}/document.pdf",
        headers=headers,
    )
    assert brief_pdf.status_code == 200
    assert brief_pdf.headers["content-type"] == "application/pdf"
    assert brief_pdf.content.startswith(b"%PDF")

    dna_pdf = client.get(
        f"/internal/workbench/workspaces/{workspace_id}/dna/document.pdf",
        headers=headers,
    )
    assert dna_pdf.status_code == 200
    assert dna_pdf.content.startswith(b"%PDF")

    # 12. The derivation record is replayable and the acts were audited.
    with db.connect() as connection:
        derivation = connection.execute(
            text("SELECT derivation FROM research_briefs WHERE id = :id"),
            {"id": brief_id},
        ).scalar_one()
        assert derivation["receipt_table_evidence_ids"] == [evidence_id]
        assert derivation["finalised_by"] == TEST_EDITOR_SUBJECT
        assert derivation["edit_log_entries"] == 1
        assert derivation["produced_by"] == "workbench-concierge/1"

        audited = (
            connection.execute(
                text("SELECT action FROM audit_entries WHERE workspace_id = :id ORDER BY action"),
                {"id": workspace_id},
            )
            .scalars()
            .all()
        )
    assert "prospect.created" in audited
    assert "dna.created" in audited
    assert "research_brief.finalised" in audited


def test_doc03_s7_one_dna_per_workspace_at_v1(db: Engine) -> None:
    client = make_client()
    headers = editor_headers()
    workspace_id = provision_workspace(client)
    payload = {
        "elements": [
            {
                "category": "business_attributes",
                "statement": "DTC brands",
                "confidence": 0.6,
                "decay_class": "customer_law",
                "origin": "interview",
            }
        ]
    }
    first = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/dna", json=payload, headers=headers
    )
    assert first.status_code == 200
    second = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/dna", json=payload, headers=headers
    )
    assert second.status_code == 409


def test_a_nonexistent_workspace_is_a_404_not_a_surprise(db: Engine) -> None:
    response = make_client().get(
        f"/internal/workbench/workspaces/{uuid4()}/dna/document.pdf",
        headers=editor_headers(),
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


# ── Epic 4: binding floor queue + source health (internal API) ───────────────


def test_adr008_the_editor_resolves_the_binding_floor_queue(db: Engine) -> None:
    from sqlalchemy.orm import Session

    from app.repositories.acquisition import SqlEntityBindingReviewRepo
    from app.repositories.business_records import SqlBusinessRecordRepo
    from app.repositories.orm import CanonicalContentRow
    from app.repositories.snapshots import SqlSourceSnapshotRepo

    client = make_client()
    headers = editor_headers()

    with Session(db) as session:
        business_id = (
            SqlBusinessRecordRepo(session)
            .find_or_create(
                canonical_name="Brightpath Ltd",
                website_domain="brightpath.example",
                register_number=None,
            )
            .id
        )
        snapshot = SqlSourceSnapshotRepo(session).add(
            url="https://graph.example/ads",
            content_sha256="0" * 64,
            content_type="application/json",
            http_status=200,
            size_bytes=10,
            fetcher_version="test/1",
        )
        row = CanonicalContentRow(
            item_kind="ad_record",
            content_key="1" * 64,
            source_family="ad_library",
            payload={"external_id": "x"},
            snapshot_id=snapshot.id,
            business_record_id=None,
        )
        session.add(row)
        session.flush()
        review = SqlEntityBindingReviewRepo(session).enqueue(
            candidate_name="Brightpath",
            website_domain=None,
            register_number=None,
            confidence=0.7,
            canonical_item_ids=[row.id],
        )
        session.commit()
        review_id, canonical_id = review.id, row.id

    pending = client.get("/internal/workbench/binding-reviews", headers=headers)
    assert pending.status_code == 200
    assert [item["id"] for item in pending.json()] == [str(review_id)]

    resolved = client.post(
        f"/internal/workbench/binding-reviews/{review_id}/resolve",
        json={"business_record_id": str(business_id)},
        headers=headers,
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "bound"

    with db.connect() as connection:
        bound_to = connection.execute(
            text("SELECT business_record_id FROM canonical_content WHERE id = :id"),
            {"id": canonical_id},
        ).scalar_one()
    assert str(bound_to) == str(business_id)

    # A resolved review is never resolved twice.
    again = client.post(
        f"/internal/workbench/binding-reviews/{review_id}/resolve",
        json={"business_record_id": None},
        headers=headers,
    )
    assert again.status_code == 409


def test_doc09_s10_source_health_is_visible_to_the_editor(db: Engine) -> None:
    from sqlalchemy.orm import Session

    from app.repositories.acquisition import SqlSourceHealthRepo

    with Session(db) as session:
        SqlSourceHealthRepo(session).record(
            source_family="website", event="fetched", detail="https://brightpath.example/"
        )
        session.commit()

    response = make_client().get("/internal/workbench/source-health", headers=editor_headers())
    assert response.status_code == 200
    assert response.json()["website"]["fetched"] == 1
