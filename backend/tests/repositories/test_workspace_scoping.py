"""The belt (Doc 08 §8): repository-level scoping, independent of RLS."""

from uuid import uuid4

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.repositories.identity import SqlIdentityRepo
from app.repositories.users import SqlUserRepo


def test_user_repo_returns_only_its_workspace(db: Engine) -> None:
    with Session(db) as session:
        identity_repo = SqlIdentityRepo(session)
        workspace_a, user_a = identity_repo.provision_workspace(
            name="Agency A", auth_subject=f"belt-a-{uuid4()}", email=None
        )
        workspace_b, user_b = identity_repo.provision_workspace(
            name="Agency B", auth_subject=f"belt-b-{uuid4()}", email=None
        )
        session.commit()

        users_a = SqlUserRepo(session, workspace_a.id).list()
        users_b = SqlUserRepo(session, workspace_b.id).list()

    assert [user.id for user in users_a] == [user_a.id]
    assert [user.id for user in users_b] == [user_b.id]


def test_get_refuses_a_foreign_user(db: Engine) -> None:
    with Session(db) as session:
        identity_repo = SqlIdentityRepo(session)
        workspace_a, user_a = identity_repo.provision_workspace(
            name="Agency A", auth_subject=f"belt-c-{uuid4()}", email=None
        )
        workspace_b, _ = identity_repo.provision_workspace(
            name="Agency B", auth_subject=f"belt-d-{uuid4()}", email=None
        )
        session.commit()

        assert SqlUserRepo(session, workspace_b.id).get(user_a.id) is None
        found = SqlUserRepo(session, workspace_a.id).get(user_a.id)
    assert found is not None and found.id == user_a.id
