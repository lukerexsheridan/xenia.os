"""Regenerate the golden PDF files — deliberately, never automatically.

A golden change is a format-version decision (Doc 07's revision loop):
review the rendered output, then run this from backend/:

    uv run python -m tests.golden.regenerate
"""

from pathlib import Path


def main() -> None:
    from app.services.documents.render_brief_pdf import _render as render_brief
    from app.services.documents.render_dna_document import _render as render_dna
    from tests.services.test_render_documents import (
        fixture_dna,
        fixture_receipt_table,
        fixture_stored_brief,
    )

    golden_dir = Path(__file__).parent
    (golden_dir / "brief_v1.pdf").write_bytes(
        render_brief(fixture_stored_brief(), fixture_receipt_table())
    )
    (golden_dir / "dna_document_v1.pdf").write_bytes(
        render_dna(fixture_dna(), "Brightpath Digital")
    )

    from app.ai.prompts.compose_brief import render_prompt

    (golden_dir / "compose_brief_prompt_v1.txt").write_text(
        render_prompt(
            business_name="Brightpath Ltd",
            dna_summary="- [LAW] No franchise businesses",
            receipt_table="[1] (e1) Running ads",
        )
        + "\n"  # POSIX trailing newline, matching the pre-commit hook
    )
    print("golden files regenerated — review the diff before committing")


if __name__ == "__main__":
    main()
