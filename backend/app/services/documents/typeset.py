"""Shared typesetting for workbench documents (Doc 06 §8, applied).

Hierarchy through typography, not chrome: type scale and spacing carry the
structure; one quiet rule under headings; no boxes, no colour theatre.
Core PDF fonts only (self-contained, deterministic); text is coerced to
cp1252 — the concierge documents are English (Doc 09 §5's language ruling).
Compression is off so golden-file tests and diffs stay legible.
"""

from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

PAGE_MARGIN_MM = 22.0
_BODY_SIZE = 10.5
_LINE_HEIGHT = 5.2


def cp1252_safe(text: str) -> str:
    return text.encode("cp1252", errors="replace").decode("cp1252")


class XeniaDocument(FPDF):
    """A quietly typeset A4 document with a stable creation date."""

    def __init__(self, *, created_at: datetime) -> None:
        super().__init__(format="A4")
        self.core_fonts_encoding = "windows-1252"
        self.set_compression(False)
        self.set_creation_date(created_at)
        self.set_margins(PAGE_MARGIN_MM, PAGE_MARGIN_MM, PAGE_MARGIN_MM)
        self.set_auto_page_break(auto=True, margin=PAGE_MARGIN_MM)
        self.add_page()

    def add_title(self, text: str) -> None:
        self.set_font("Helvetica", style="B", size=19)
        self._paragraph(8.5, text)
        self.ln(1)

    def meta_line(self, text: str) -> None:
        self.set_font("Helvetica", size=9)
        self.set_text_color(90, 90, 90)
        self._paragraph(4.5, text)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def heading(self, text: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", style="B", size=12)
        self._paragraph(6.0, text)
        rule_y = self.get_y() + 0.6
        self.set_draw_color(200, 200, 200)
        self.line(PAGE_MARGIN_MM, rule_y, self.w - PAGE_MARGIN_MM, rule_y)
        self.ln(2.4)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", size=_BODY_SIZE)
        self._paragraph(_LINE_HEIGHT, text)

    def quiet(self, text: str) -> None:
        """Receipts and marginalia: present, findable, never cluttering."""
        self.set_font("Helvetica", style="I", size=8.5)
        self.set_text_color(110, 110, 110)
        self._paragraph(4.2, text)
        self.set_text_color(0, 0, 0)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", size=_BODY_SIZE)
        self._paragraph(_LINE_HEIGHT, f"-  {text}")

    def _paragraph(self, line_height: float, text: str) -> None:
        self.multi_cell(0, line_height, cp1252_safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def render(self) -> bytes:
        return bytes(self.output())
