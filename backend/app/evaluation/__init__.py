"""The evaluation harness (Doc 04): rubric, golden sets, regression runner,
L2 judge, calibration. Colocated with the code it tests because AI behaviour
and its evaluation are one artefact — a prompt change without its regression
run is an unfinished change (CI-enforced).

Golden fixtures live in tests/golden/, seeded from concierge artefacts
(Doc 09 SS12). May import: app.domain, app.ai, app.core.
"""
