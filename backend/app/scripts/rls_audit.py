"""RLS audit (Doc 10, Epic 12's security pass) — run against any environment.

Asserts, from the live catalogue, that every Ring-1 table has row-level
security ENABLED and FORCED with select+insert policies present, and that no
table carrying a workspace_id column has been created outside the Ring-1
register (the drift that tenancy regressions are made of). Exit code 1 on
any violation, so the drill is scriptable.

Usage: python -m app.scripts.rls_audit
"""

import sys

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.repositories.orm import RING_1_TABLES

# Infrastructure tables that carry workspace_id for scoping but are not
# customer data surfaces (payloads are IDs only, Doc 05).
_WORKSPACE_COLUMN_ALLOWED_OUTSIDE_RING_1 = frozenset({"jobs"})


def main() -> None:
    violations: list[str] = []
    with Session(get_engine()) as session:
        for table in RING_1_TABLES:
            row = session.execute(
                text("SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname = :t"),
                {"t": table},
            ).one_or_none()
            if row is None:
                violations.append(f"{table}: table missing")
                continue
            enabled, forced = row
            if not enabled or not forced:
                violations.append(
                    f"{table}: RLS enabled={enabled} forced={forced} — must be true/true"
                )
            policies = {
                cmd
                for (cmd,) in session.execute(
                    text("SELECT cmd FROM pg_policies WHERE tablename = :t"), {"t": table}
                ).all()
            }
            if "SELECT" not in policies or "INSERT" not in policies:
                violations.append(f"{table}: missing select/insert policy (has {policies})")

        strays = session.execute(
            text(
                "SELECT table_name FROM information_schema.columns "
                "WHERE column_name = 'workspace_id' AND table_schema = 'public'"
            )
        ).all()
        for (table_name,) in strays:
            if (
                table_name not in RING_1_TABLES
                and table_name not in _WORKSPACE_COLUMN_ALLOWED_OUTSIDE_RING_1
            ):
                violations.append(
                    f"{table_name}: carries workspace_id but is not in the Ring-1 register"
                )

    if violations:
        print("RLS AUDIT FAILED:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    print(f"RLS audit clean: {len(RING_1_TABLES)} Ring-1 tables enabled+forced with policies.")


if __name__ == "__main__":
    main()
