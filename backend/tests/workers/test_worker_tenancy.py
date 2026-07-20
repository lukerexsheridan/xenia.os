"""Worker jobs carry the tenancy context they act under (Doc 08 §8).

The braces bind per transaction: a worker writing Ring-1 rows without the
workspace GUC set would work under a superuser (local, CI) and silently
break — or leak — under a properly least-privileged application role. These
tests pin the contract: per-workspace jobs attach their workspace context,
and the Monday sweep fans out one job per workspace, never one job for all.
"""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from app.repositories.identity import SqlIdentityRepo
from app.repositories.jobs import JobQueue
from app.workers import handlers
from app.workers.handlers import (
    ASSEMBLE_WORKSPACE_QUEUE_JOB_TYPE,
    JOB_HANDLERS,
    handle_assemble_queues,
)
from app.workers.main import process_next_job


def provision(session: Session, tag: str) -> UUID:
    workspace, _ = SqlIdentityRepo(session).provision_workspace(
        name=f"Tenancy {tag}", auth_subject=f"tenancy-{tag}-{uuid4()}", email=None
    )
    return workspace.id


def test_the_monday_sweep_fans_out_one_job_per_workspace(db: Engine) -> None:
    """Blast radius: a poisoned workspace dead-letters its own Monday, not
    everyone's."""
    with Session(db) as session:
        first = provision(session, "a")
        second = provision(session, "b")
        JobQueue(session).enqueue("assemble_queues", idempotency_key=f"sweep-{uuid4()}")
        session.commit()

    assert process_next_job(JOB_HANDLERS)  # the sweep itself

    with Session(db) as session:
        rows = session.execute(
            text("SELECT job_type, workspace_id FROM jobs WHERE job_type = :t"),
            {"t": ASSEMBLE_WORKSPACE_QUEUE_JOB_TYPE},
        ).all()
    per_workspace = {row[1] for row in rows}
    assert first in per_workspace and second in per_workspace
    assert len(rows) >= 2  # one job per tenant, by construction


def test_per_workspace_jobs_attach_their_tenancy_context(
    db: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.core.db import set_app_context as real

    contexts: list[UUID] = []

    def spy(session: Session, **kwargs: object) -> None:
        workspace_id = kwargs.get("workspace_id")
        if isinstance(workspace_id, UUID):
            contexts.append(workspace_id)
        real(session, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(handlers, "set_app_context", spy)

    with Session(db) as session:
        workspace_id = provision(session, "ctx")
        queue = JobQueue(session)
        queue.enqueue(
            ASSEMBLE_WORKSPACE_QUEUE_JOB_TYPE,
            idempotency_key=f"assemble-{uuid4()}",
            payload={"workspace_id": str(workspace_id)},
            workspace_id=workspace_id,
        )
        queue.enqueue(
            "weekly_brief_send",
            idempotency_key=f"brief-{uuid4()}",
            payload={"workspace_id": str(workspace_id)},
            workspace_id=workspace_id,
        )
        session.commit()

    while process_next_job(JOB_HANDLERS):
        pass
    assert contexts.count(workspace_id) == 2  # assembly and the send, both


def test_the_sweep_is_idempotent_within_a_week(db: Engine) -> None:
    with Session(db) as session:
        provision(session, "idem")
        session.commit()
    with Session(db) as session:
        fake_job = None  # the handler ignores its job argument's payload
        handle_assemble_queues(session, fake_job)  # type: ignore[arg-type]
        handle_assemble_queues(session, fake_job)  # type: ignore[arg-type]
        session.commit()
        count = session.execute(
            text("SELECT count(*) FROM jobs WHERE job_type = :t"),
            {"t": ASSEMBLE_WORKSPACE_QUEUE_JOB_TYPE},
        ).scalar_one()
    assert count == 1  # the idempotency key holds for the week


def test_worker_handlers_touching_ring1_set_context() -> None:
    """The contract as a list: every per-workspace handler names its context
    call. A new handler that writes Ring-1 without appearing here should
    make its author read Doc 08 §8 first."""
    import inspect

    for handler_name in (
        "handle_assemble_workspace_queue",
        "handle_weekly_brief_send",
        "handle_outcome_prompt",
        "handle_stripe_webhook",
    ):
        source = inspect.getsource(getattr(handlers, handler_name))
        assert "set_app_context" in source, f"{handler_name} lacks tenancy context"
