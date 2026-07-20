"""The ring boundary at the database (Doc 05 §7; Doc 08 §8).

The Ring-1 RLS canary in test_rls.py already sweeps every table named in
RING_1_TABLES — including Epic 3's. This suite adds the Ring-2 structural
canary (no workspace column may ever appear on a shared-world table) and the
append-only guarantees for the DNA changelog and the edit log.
"""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.orm import RING_2_TABLES
from app.services.create_dna import CreateDna, DnaElementInput
from tests.domain.conftest import make_element
from tests.repositories.test_rls import probe_transaction


def test_doc05_s7_ring_2_tables_carry_no_workspace_column(db: Engine) -> None:
    """Structurally incapable of leaking tenancy (Doc 08 §8)."""
    with db.connect() as connection:
        for table in RING_2_TABLES:
            columns = (
                connection.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = :table"
                    ),
                    {"table": table},
                )
                .scalars()
                .all()
            )
            assert columns, f"Ring-2 table {table!r} does not exist"
            assert not any("workspace" in column for column in columns), (
                f"Ring-2 table {table!r} must never carry a workspace column"
            )


@pytest.fixture
def workspace_with_dna(db: Engine) -> UUID:
    with Session(db) as session:
        workspace, _ = SqlIdentityRepo(session).provision_workspace(
            name="Ring Test Agency", auth_subject=f"ring-{uuid4()}", email=None
        )
        element = make_element()
        CreateDna(
            SqlDnaRepo(session, workspace.id), SqlAuditEntryRepo(session, workspace.id)
        ).execute(
            workspace_id=workspace.id,
            elements=[
                DnaElementInput(
                    category=element.category,
                    statement=element.statement,
                    confidence=element.confidence,
                    decay_class=element.decay_class,
                    origin=element.origin,
                )
            ],
        )
        session.commit()
        return workspace.id


def test_doc04_s4_the_dna_changelog_is_append_only_under_rls(
    db: Engine, rls_probe: str, workspace_with_dna: UUID
) -> None:
    with probe_transaction(db, rls_probe, workspace_id=workspace_with_dna) as connection:
        visible = connection.execute(text("SELECT count(*) FROM dna_change_events")).scalar_one()
        assert visible >= 1
        updated = connection.execute(
            text("UPDATE dna_change_events SET cause = 'tampered'")
        ).rowcount
        deleted = connection.execute(text("DELETE FROM dna_change_events")).rowcount
    assert updated == 0
    assert deleted == 0


def test_doc07_s3_the_edit_log_is_append_only_under_rls(
    db: Engine, rls_probe: str, workspace_with_dna: UUID
) -> None:
    with probe_transaction(db, rls_probe, workspace_id=workspace_with_dna) as connection:
        updated = connection.execute(text("UPDATE edit_log_entries SET note = 'tampered'")).rowcount
        deleted = connection.execute(text("DELETE FROM edit_log_entries")).rowcount
    assert updated == 0
    assert deleted == 0
