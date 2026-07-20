"""Epic 11: billing state sync, drafts behind the gate, the five numbers."""

from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.ai.pipelines.compose_opener import ComposeOpener
from app.ai.providers.base import ProviderUsage
from app.api.v1.drafts import get_opener_pipeline
from app.main import create_app
from app.workers.handlers import JOB_HANDLERS
from app.workers.main import process_next_job
from tests.api.test_console import seed_draft_brief
from tests.api.test_stripe_webhook import signed_post
from tests.api.test_workbench import editor_headers, make_client
from tests.conftest import mint_supabase_token


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _override_pipeline(client: TestClient, provider: "ScriptedOpenerProvider") -> None:
    app = client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_opener_pipeline] = lambda: ComposeOpener(provider)


# ── Billing webhook E2E (Doc 10, Sprint 20) ─────────────────────────────────


def test_doc03_s9_checkout_and_cancellation_sync_the_workspace(db: Engine) -> None:
    client = TestClient(create_app())
    subject = f"billing-{uuid4()}"
    token = mint_supabase_token(subject)
    workspace_id = client.get("/v1/me", headers=bearer(token)).json()["workspace"]["id"]

    before = client.get("/v1/billing", headers=bearer(token)).json()
    assert before["subscription_status"] == "none"

    # Checkout completes: the webhook arrives, queues idempotently, and the
    # worker syncs the workspace.
    assert (
        signed_post(
            client,
            {
                "id": f"evt-{uuid4()}",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "client_reference_id": workspace_id,
                        "customer": "cus_founding_1",
                    }
                },
            },
        ).status_code
        == 200
    )
    while process_next_job(JOB_HANDLERS):
        pass
    active = client.get("/v1/billing", headers=bearer(token)).json()
    assert active["subscription_status"] == "active"

    # The subscription ends: the status follows, keyed by customer id.
    signed_post(
        client,
        {
            "id": f"evt-{uuid4()}",
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_founding_1"}},
        },
    )
    while process_next_job(JOB_HANDLERS):
        pass
    assert (
        client.get("/v1/billing", headers=bearer(token)).json()["subscription_status"] == "canceled"
    )


# ── Drafts (C6): behind the gate, always editable ───────────────────────────


class ScriptedOpenerProvider:
    def __init__(self, openers: list[str]) -> None:
        self._openers = openers
        self.calls = 0

    def structured(
        self, *, prompt: str, schema: dict[str, Any], schema_name: str
    ) -> tuple[dict[str, Any], ProviderUsage]:
        opener = self._openers[min(self.calls, len(self._openers) - 1)]
        self.calls += 1
        return {"opener": opener}, ProviderUsage(model="scripted", input_tokens=5, output_tokens=9)


GOOD_OPENER = (
    "Brightpath Ltd caught my eye this week: you are running paid social while "
    "hiring your first marketing manager, which usually means the workload has "
    "outgrown the team. We help DTC brands at exactly that point,"
)


def test_doc03_c6_drafts_exist_only_behind_the_editor_gate(db: Engine) -> None:
    client = make_client()
    _override_pipeline(client, ScriptedOpenerProvider([GOOD_OPENER]))
    world = seed_draft_brief(client, f"draft-{uuid4()}")
    owner = bearer(world["owner_token"])

    # No approved brief -> no draft, structurally.
    refused = client.post(f"/v1/prospects/{world['prospect_id']}/draft", headers=owner)
    assert refused.status_code == 404
    assert "reviewed evidence" in refused.json()["message"]

    # Approve, then compose: the draft names the business, in bounds.
    client.post(
        f"/internal/workbench/workspaces/{world['workspace_id']}/briefs/"
        f"{world['brief_id']}/finalise",
        headers=editor_headers(),
    )
    composed = client.post(f"/v1/prospects/{world['prospect_id']}/draft", headers=owner)
    assert composed.status_code == 200
    assert "Brightpath Ltd" in composed.json()["body"]

    # Always editable: the founder's edit is the final word.
    edited = client.put(
        f"/v1/prospects/{world['prospect_id']}/draft",
        headers=owner,
        json={"body": "My own words entirely."},
    )
    assert edited.status_code == 200
    fetched = client.get(f"/v1/prospects/{world['prospect_id']}/draft", headers=owner)
    assert fetched.json()["body"] == "My own words entirely."


def test_doc06_s2_a_banned_register_draft_dies_in_bounded_regeneration(db: Engine) -> None:
    banned = "Brightpath Ltd gets booked meetings on autopilot with us"
    client = make_client()
    provider = ScriptedOpenerProvider([banned, banned])
    _override_pipeline(client, provider)
    world = seed_draft_brief(client, f"draftbad-{uuid4()}")
    client.post(
        f"/internal/workbench/workspaces/{world['workspace_id']}/briefs/"
        f"{world['brief_id']}/finalise",
        headers=editor_headers(),
    )
    response = client.post(
        f"/v1/prospects/{world['prospect_id']}/draft", headers=bearer(world["owner_token"])
    )
    assert response.status_code == 200
    assert response.json()["body"] is None
    assert any("banned register" in p for p in response.json()["problems"])
    assert provider.calls == 2  # bounded, never a loop


# ── The five numbers (Doc 10, Sprint 20) ────────────────────────────────────


def test_the_five_numbers_are_computed_from_the_ledgers(db: Engine) -> None:
    client = make_client()
    world = seed_draft_brief(client, f"metrics-{uuid4()}")
    client.post(
        f"/internal/workbench/workspaces/{world['workspace_id']}/briefs/"
        f"{world['brief_id']}/rubric-score",
        headers=editor_headers(),
        json={"accuracy": 4, "evidence": 4, "insight": 3, "fit_reasoning": 3, "actionability": 3},
    )
    metrics = client.get("/internal/workbench/metrics", headers=editor_headers()).json()
    assert set(metrics) == {
        "acceptance_rate",
        "teaching_events",
        "unedited_pass_rate",
        "capture_rate",
        "tokens_per_brief",
    }
    assert metrics["unedited_pass_rate"] == 1.0  # scored at the bar, no edits
    assert metrics["acceptance_rate"] == 0.0  # no decisions yet, honestly zero
