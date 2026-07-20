"""The error taxonomy (Doc 08 SS3).

Services raise these; the API layer maps them to HTTP responses; the frontend
maps codes to the Doc 06 failure voice. Codes are stable contract, messages are
not.
"""

from enum import StrEnum


class ErrorCode(StrEnum):
    NOT_FOUND = "not_found"
    NOT_AUTHENTICATED = "not_authenticated"
    NOT_AUTHORISED = "not_authorised"
    VALIDATION_FAILED = "validation_failed"
    CONFLICT = "conflict"
    DELEGATION_REQUIRED = "delegation_required"  # the never-automatic floor (N3)
    BUDGET_EXHAUSTED = "budget_exhausted"  # AI-cost governors (Doc 08 SS8)


class XeniaError(Exception):
    """Base for all application errors."""

    code: ErrorCode = ErrorCode.VALIDATION_FAILED

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(XeniaError):
    code = ErrorCode.NOT_FOUND


class NotAuthenticatedError(XeniaError):
    code = ErrorCode.NOT_AUTHENTICATED


class NotAuthorisedError(XeniaError):
    code = ErrorCode.NOT_AUTHORISED


class ConflictError(XeniaError):
    code = ErrorCode.CONFLICT


class DelegationRequiredError(XeniaError):
    """Raised when an action-shaped operation lacks its DelegationGrant (N3)."""

    code = ErrorCode.DELEGATION_REQUIRED


class BudgetExhaustedError(XeniaError):
    """Raised by AI-cost governors; surfaces as an honest wait, never a failure."""

    code = ErrorCode.BUDGET_EXHAUSTED
