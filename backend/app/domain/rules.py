"""The domain's own error type.

The domain package imports nothing but itself and the standard library (AP2),
so it cannot use app.core.errors. Services translate DomainRuleViolation into
the core taxonomy at the use-case boundary when they orchestrate these rules.
"""


class DomainRuleViolation(Exception):
    """A constitutional domain rule was violated. The message names the rule."""
