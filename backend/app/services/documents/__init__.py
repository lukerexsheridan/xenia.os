"""The workbench's document rendering (Doc 06 §7): brief and DNA PDFs.

"The brief is a document, not a dashboard" — typeset like a memo, verdict
first, receipts quiet, couldn't-see always visible. Rendering is
deterministic: the same stored artefact yields byte-identical PDF output
(golden-file tested), which is what lets format versions be compared
honestly (Doc 07's revision loop).
"""

from app.services.documents.render_brief_pdf import RenderBriefPdf
from app.services.documents.render_dna_document import RenderDnaDocument

__all__ = ["RenderBriefPdf", "RenderDnaDocument"]
