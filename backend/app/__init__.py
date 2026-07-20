"""Xenia backend — a modular monolith (Doc 08).

Package boundaries are law (AP2), enforced by import-linter:

    api -> services -> domain <- repositories
             ^ ai / integrations invoked by services through domain-defined interfaces
"""
