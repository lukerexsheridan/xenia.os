"""The departure rule, exercised (Doc 10, Epic 12 exit): a workspace leaves,
its data provably exported and provably gone — while the shared world model
stays, because facts belong to nobody."""

from uuid import uuid4

from sqlalchemy import Engine, text

from app.repositories.orm import RING_1_TABLES
from tests.api.test_console import seed_draft_brief
from tests.api.test_workbench import editor_headers, make_client


def ring1_row_count(db: Engine, workspace_id: str) -> int:
    total = 0
    with db.connect() as connection:
        for table in RING_1_TABLES:
            column = "id" if table == "workspaces" else "workspace_id"
            total += int(
                connection.execute(
                    text(f"SELECT count(*) FROM {table} WHERE {column} = :w"),
                    {"w": workspace_id},
                ).scalar_one()
            )
    return total


def test_doc10_epic12_exit_the_departure_rule(db: Engine) -> None:
    client = make_client()
    headers = editor_headers()
    world = seed_draft_brief(client, f"depart-{uuid4()}")
    workspace_id = world["workspace_id"]
    client.post(
        f"/internal/workbench/workspaces/{workspace_id}/briefs/{world['brief_id']}/finalise",
        headers=headers,
    )
    assert ring1_row_count(db, workspace_id) > 0

    # 1. The export: everything that is theirs, in one bundle.
    export = client.get(
        f"/internal/workbench/workspaces/{workspace_id}/offboarding-export", headers=headers
    )
    assert export.status_code == 200
    bundle = export.json()
    assert bundle["export_format_version"] == 1
    assert bundle["prospects"][0]["business_name"] == "Brightpath Ltd"
    assert bundle["prospects"][0]["approved_brief"]["receipts"]
    assert bundle["audit_trail"]  # their history leaves with them

    # 2. Deletion demands the exact name — irreversible acts get friction.
    wrong = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/offboard",
        headers=headers,
        json={"confirm_name": "not-the-name"},
    )
    assert wrong.status_code == 422
    assert ring1_row_count(db, workspace_id) > 0  # nothing happened

    name = bundle["workspace"]["name"]
    report = client.post(
        f"/internal/workbench/workspaces/{workspace_id}/offboard",
        headers=headers,
        json={"confirm_name": name},
    )
    assert report.status_code == 200
    assert report.json()["rows_deleted_by_table"]["workspaces"] == 1

    # 3. Provably gone: zero Ring-1 rows across every table in the register.
    assert ring1_row_count(db, workspace_id) == 0

    # 4. The shared world model stays: public facts belong to nobody.
    with db.connect() as connection:
        remaining = connection.execute(
            text("SELECT count(*) FROM business_records WHERE canonical_name = :n"),
            {"n": "Brightpath Ltd"},
        ).scalar_one()
    assert remaining >= 1
