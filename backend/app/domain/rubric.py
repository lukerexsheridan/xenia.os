"""The brief-quality rubric's dimensions (Doc 04 §3).

Five dimensions, 0-4 each; the harness's nouns are first-class domain
vocabulary (Doc 08 §5). Epic 3 uses the dimensions to categorise the edit
log — every founder edit to machine-assisted output tagged by the dimension
it repaired, which is the QA-delta measurement operating from the first
brief (Doc 07 §3). Scoring machinery arrives with the harness epics.
"""

from enum import StrEnum


class RubricDimension(StrEnum):
    ACCURACY = "accuracy"
    EVIDENCE = "evidence"
    INSIGHT = "insight"
    FIT_REASONING = "fit_reasoning"
    ACTIONABILITY = "actionability"
