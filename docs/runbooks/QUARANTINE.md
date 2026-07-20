# Runbook — Source quarantine

*A source family is misbehaving: parse failures spiking, suspicious content,
or a target site signalling distress (Doc 05 §9-11; Doc 09 §10).*

1. **See it.** The console's source-health page shows per-family
   fetched/refused/parse-failed counts. A parse-failure spike is our bug; a
   refusal spike is the world telling us something.
2. **Stop fetching the family.** Unset the family's credential/config (ad
   library token) or, for crawl families, rely on the politeness engine's
   circuit breaker — it already stops per-domain on repeated failure and
   never evades (N2). For a hard stop, disable the research schedule.
3. **Quarantine the knowledge.** Do not delete evidence. Stale signals
   demote toward unknown by the decay sweep on their own; if the family
   produced *wrong* evidence (not just stale), treat as Sev1 candidates and
   follow that runbook for any affected delivered brief.
4. **Re-admit deliberately.** Fix the adapter against its recorded fixtures,
   run the live canary against the stable known entity, then re-enable and
   watch one full research run in staging before production.
5. Log the episode in `docs/runbooks/incidents/`.
