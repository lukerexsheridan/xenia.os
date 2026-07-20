from datetime import date

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.repositories.flags import SqlFeatureFlagRepo


def test_absent_flag_is_off(db: Engine) -> None:
    with Session(db) as session:
        assert SqlFeatureFlagRepo(session).is_enabled("never-declared") is False


def test_declared_flag_reads_back(db: Engine) -> None:
    with Session(db) as session:
        flags = SqlFeatureFlagRepo(session)
        flags.declare(
            key="pipeline-v2",
            description="staged pipeline rollout example",
            removal_date=date(2026, 12, 31),
            enabled=True,
        )
        session.commit()
        assert flags.is_enabled("pipeline-v2") is True


def test_declare_never_clobbers_existing_state(db: Engine) -> None:
    with Session(db) as session:
        flags = SqlFeatureFlagRepo(session)
        flags.declare(
            key="format-experiment",
            description="first declaration",
            removal_date=date(2026, 12, 31),
            enabled=True,
        )
        session.commit()
        flags.declare(
            key="format-experiment",
            description="redeclaration must not flip state",
            removal_date=date(2027, 1, 31),
            enabled=False,
        )
        session.commit()
        assert flags.is_enabled("format-experiment") is True
