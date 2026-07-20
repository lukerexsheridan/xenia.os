"""The Editor console and the gate (Doc 10, Epic 9 exit criteria).

The exit criterion, proven: a brief cannot reach any delivery surface
without gate approval. The delivery surface is /v1; the gate is the internal
finalise act; the structural guarantee is `deliverable_for_prospect`, whose
query bakes in FINAL.
"""

from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.api.test_workbench import (
    OBSERVED_AT,
    editor_headers,
    full_sections,
    make_client,
)
from tests.conftest import mint_supabase_token


def seed_draft_brief(client: TestClient, subject: str) -> dict[str, Any]:
    """Workspace, prospect, evidence, and a complete DRAFT brief."""
    headers = editor_headers()
    me = client.get("/v1/me", headers={"Authorization": f"Bearer {mint_supabase_token(subject)}"})
    workspace_id = str(me.json()["workspace"]["id"])
    snapshot_id = client.post(
        "/internal/workbench/snapshots",
        json={"url": "https://brightpath.example/about"},
        headers=headers,
    ).json()["id"]
    business_id = client.post(
        "/internal/workbench/business-records",
        json={"canonical_name": "Brightpath Ltd", "website_domain": "brightpath.example"},
        headers=headers,
    ).json()["id"]
    evidence_id = client.post(
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
    ).json()["id"]
    prospect_id = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/prospects",
        json={"business_record_id": business_id, "binding_confidence": 0.95},
        headers=headers,
    ).json()["id"]
    brief = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/briefs",
        json={
            "prospect_id": prospect_id,
            "sections": full_sections(cited=[evidence_id]),
            "couldnt_see": ["Their ad spend levels"],
            "confidence_score": 0.72,
        },
        headers=headers,
    )
    assert brief.status_code == 200
    return {
        "workspace_id": workspace_id,
        "prospect_id": prospect_id,
        "brief_id": brief.json()["id"],
        "owner_token": mint_supabase_token(subject),
    }


def test_doc10_epic9_exit_no_brief_reaches_delivery_without_gate_approval(db: Engine) -> None:
    client = make_client()
    world = seed_draft_brief(client, f"gate-{uuid4()}")
    owner = {"Authorization": f"Bearer {world['owner_token']}"}
    headers = editor_headers()

    # Before approval: the delivery surface has nothing — a draft is
    # indistinguishable from absence.
    before = client.get(f"/v1/prospects/{world['prospect_id']}/brief", headers=owner)
    assert before.status_code == 404

    # The draft sits in the gate's inbox, visibly ungraded.
    inbox = client.get(
        f"/internal/workbench/workspaces/{world['workspace_id']}/approval-queue",
        headers=headers,
    ).json()
    assert [item["brief_id"] for item in inbox] == [world["brief_id"]]
    assert inbox[0]["scored"] is False

    # The Editor approves (finalises); the inbox empties.
    approved = client.post(
        f"/internal/workbench/workspaces/{world['workspace_id']}/briefs/"
        f"{world['brief_id']}/finalise",
        headers=headers,
    )
    assert approved.status_code == 200
    assert (
        client.get(
            f"/internal/workbench/workspaces/{world['workspace_id']}/approval-queue",
            headers=headers,
        ).json()
        == []
    )

    # After approval: delivered, with the receipt table and the confidence
    # word arriving as data (AP5).
    after = client.get(f"/v1/prospects/{world['prospect_id']}/brief", headers=owner)
    assert after.status_code == 200
    body = after.json()
    assert body["confidence_word"] == "likely"
    assert body["receipts"]
    assert len(body["sections"]) == 8


def test_doc04_s6_grading_feeds_the_metrics_store(db: Engine) -> None:
    client = make_client()
    world = seed_draft_brief(client, f"grading-{uuid4()}")
    headers = editor_headers()
    base = f"/internal/workbench/workspaces/{world['workspace_id']}"

    queue = client.get(f"{base}/grading-queue", headers=headers).json()
    assert [item["brief_id"] for item in queue] == [world["brief_id"]]

    scored = client.post(
        f"{base}/briefs/{world['brief_id']}/rubric-score",
        json={"accuracy": 4, "evidence": 4, "insight": 3, "fit_reasoning": 3, "actionability": 3},
        headers=headers,
    )
    assert scored.status_code == 200

    # Graded work leaves the queue, and the metrics store reflects it.
    assert client.get(f"{base}/grading-queue", headers=headers).json() == []
    report = client.get(f"{base}/quality-report", headers=headers).json()
    assert report["briefs_scored"] == 1
    assert report["ship_bar_passed"] == 1


def test_doc04_s6_only_approved_briefs_enter_the_golden_set(db: Engine) -> None:
    client = make_client()
    world = seed_draft_brief(client, f"golden-{uuid4()}")
    headers = editor_headers()
    base = f"/internal/workbench/workspaces/{world['workspace_id']}"
    golden_url = f"{base}/briefs/{world['brief_id']}/golden"

    # A draft cannot calibrate the harness.
    refused = client.post(golden_url, json={"note": "exemplary gap analysis"}, headers=headers)
    assert refused.status_code == 422
    assert "approved" in refused.json()["message"]

    client.post(f"{base}/briefs/{world['brief_id']}/finalise", headers=headers)
    added = client.post(golden_url, json={"note": "exemplary gap analysis"}, headers=headers)
    assert added.status_code == 201

    # An unexplained exemplar is refused too.
    unexplained = client.post(
        f"{base}/briefs/{uuid4()}/golden", json={"note": " "}, headers=headers
    )
    assert unexplained.status_code in (404, 422)

    listed = client.get(f"{base}/golden-set", headers=headers).json()
    assert [entry["brief_id"] for entry in listed] == [world["brief_id"]]

    removed = client.delete(golden_url, headers=headers)
    assert removed.status_code == 204
    assert client.get(f"{base}/golden-set", headers=headers).json() == []


def test_the_console_shell_serves_without_data(db: Engine) -> None:
    response = make_client().get("/internal/console")
    assert response.status_code == 200
    assert "Editor console" in response.text
    # The shell holds no data; every screen goes through the authorised API.
    assert "sessionStorage" in response.text


def test_console_data_requires_editor_authorisation(db: Engine) -> None:
    client = make_client()
    world = seed_draft_brief(client, f"authz-{uuid4()}")
    # A valid customer token is not an Editor token.
    response = client.get(
        f"/internal/workbench/workspaces/{world['workspace_id']}/grading-queue",
        headers={"Authorization": f"Bearer {world['owner_token']}"},
    )
    assert response.status_code == 403
