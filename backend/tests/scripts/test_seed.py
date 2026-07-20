"""The synthetic-workspace seed (ADR-006): deterministic and idempotent."""

from sqlalchemy import Engine, text

from app.scripts.seed import SYNTHETIC_WORKSPACES, seed


def workspace_names(db: Engine) -> list[str]:
    with db.connect() as connection:
        return list(connection.execute(text("SELECT name FROM workspaces ORDER BY name")).scalars())


def test_seed_creates_two_isolated_synthetic_workspaces(db: Engine) -> None:
    seed()
    assert workspace_names(db) == sorted(name for name, _, _ in SYNTHETIC_WORKSPACES)


def test_seed_is_idempotent(db: Engine) -> None:
    seed()
    seed()
    assert len(workspace_names(db)) == len(SYNTHETIC_WORKSPACES)
