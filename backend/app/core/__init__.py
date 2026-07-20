"""Cross-cutting infrastructure: typed config, DB session, logging, errors.

May import: app.domain only (and stdlib/infrastructure libraries).
May be imported by: every layer above domain.
Utilities live here only when three call-sites exist (Doc 08 SS3).
"""
