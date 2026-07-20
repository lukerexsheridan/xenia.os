"""The Editor console shell (Doc 10, Sprint 16; Doc 08 §2).

One static HTML page, no build step, no framework — the console is ops
tooling and gets none of the novelty budget (AP8). The shell itself holds no
data and needs no auth; every byte of data comes from the internal API,
which requires Editor authorisation per request. The token is pasted once
and kept in sessionStorage. Two screens and two pages, by decree: the
grading queue, the approval gate, the golden set, and source health.
Rendering is display only — every judgment (ship bar, L0, gate state)
arrives from the API as data (AP5).
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Xenia — Editor console</title>
<style>
  body { font-family: Georgia, serif; margin: 2rem auto; max-width: 60rem; color: #1a1a1a; }
  h1 { font-size: 1.4rem; } h2 { font-size: 1.1rem; margin-top: 2rem; }
  nav button { margin-right: .5rem; }
  table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
  th, td { border-bottom: 1px solid #ccc; padding: .4rem .6rem; text-align: left;
           font-size: .9rem; }
  input, button { font: inherit; padding: .2rem .5rem; }
  .muted { color: #666; font-size: .85rem; }
  .flag { color: #8b0000; }
</style>
</head>
<body>
<h1>Xenia — Editor console</h1>
<p class="muted">The gate before customers. Paste your Editor token and a workspace id;
every act here is authorised per request and audited.</p>
<p>
  <label>Token <input id="token" size="40" type="password"></label>
  <label>Workspace <input id="workspace" size="36"></label>
  <button onclick="saveCtx()">Set</button>
</p>
<nav>
  <button onclick="show('grading')">Grading queue</button>
  <button onclick="show('approval')">Approval gate</button>
  <button onclick="show('golden')">Golden set</button>
  <button onclick="show('health')">Source health</button>
</nav>
<div id="out"><p class="muted">Set context, then pick a screen.</p></div>
<script>
"use strict";
const out = document.getElementById("out");
function ctx() {
  return { token: sessionStorage.getItem("token"), ws: sessionStorage.getItem("ws") };
}
function saveCtx() {
  sessionStorage.setItem("token", document.getElementById("token").value);
  sessionStorage.setItem("ws", document.getElementById("workspace").value);
  out.innerHTML = "<p class='muted'>Context set.</p>";
}
async function call(path, options) {
  const { token } = ctx();
  const response = await fetch(path, Object.assign({
    headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json" },
  }, options));
  if (!response.ok) { throw new Error(await response.text()); }
  return response.status === 204 ? null : response.json();
}
function esc(value) {
  const div = document.createElement("div");
  div.textContent = String(value);
  return div.innerHTML;
}
function table(headers, rows) {
  return "<table><tr>" + headers.map(h => `<th>${esc(h)}</th>`).join("") + "</tr>"
    + rows.map(r => "<tr>" + r.map(c => `<td>${c}</td>`).join("") + "</tr>").join("")
    + "</table>";
}
async function show(screen) {
  const { ws } = ctx();
  try {
    if (screen === "grading") {
      const items = await call(`/internal/workbench/workspaces/${ws}/grading-queue`);
      const report = await call(`/internal/workbench/workspaces/${ws}/quality-report`);
      out.innerHTML = "<h2>Grading queue</h2>"
        + `<p class="muted">Scored ${report.briefs_scored} — ship-bar passed `
        + `${report.ship_bar_passed} — unedited pass rate `
        + `${(report.unedited_pass_rate * 100).toFixed(0)}%</p>`
        + table(["Brief", "Prospect", "Status", "L0", "Edits"],
            items.map(i => [esc(i.brief_id), esc(i.prospect_id), esc(i.status),
                            esc(i.l0 ?? "hand-authored"), esc(i.edits)]));
    } else if (screen === "approval") {
      const items = await call(`/internal/workbench/workspaces/${ws}/approval-queue`);
      out.innerHTML = "<h2>Approval gate</h2>"
        + "<p class='muted'>Nothing reaches a customer without finalisation here.</p>"
        + table(["Brief", "Prospect", "Graded", "Ship bar", ""],
            items.map(i => [esc(i.brief_id), esc(i.prospect_id),
              i.scored ? "yes" : "<span class='flag'>not yet</span>",
              i.meets_ship_bar === null ? "—" : (i.meets_ship_bar ? "meets" :
                "<span class='flag'>below</span>"),
              `<button onclick="approve('${esc(i.brief_id)}')">Approve</button>`]));
    } else if (screen === "golden") {
      const items = await call(`/internal/workbench/workspaces/${ws}/golden-set`);
      out.innerHTML = "<h2>Golden set</h2>"
        + "<p><label>Brief id <input id='gbrief' size='36'></label> "
        + "<label>Why exemplary <input id='gnote' size='40'></label> "
        + "<button onclick='addGolden()'>Add</button></p>"
        + table(["Brief", "Note", "Added by", ""],
            items.map(i => [esc(i.brief_id), esc(i.note), esc(i.added_by),
              `<button onclick="removeGolden('${esc(i.brief_id)}')">Remove</button>`]));
    } else if (screen === "health") {
      const health = await call("/internal/workbench/source-health");
      const rows = Object.entries(health).flatMap(([family, events]) =>
        Object.entries(events).map(([event, count]) => [esc(family), esc(event), esc(count)]));
      out.innerHTML = "<h2>Source health</h2>" + table(["Family", "Event", "Count"], rows);
    }
  } catch (error) { out.innerHTML = `<p class="flag">${esc(error.message)}</p>`; }
}
async function approve(briefId) {
  const { ws } = ctx();
  try {
    await call(`/internal/workbench/workspaces/${ws}/briefs/${briefId}/finalise`,
      { method: "POST", body: "{}" });
    await show("approval");
  } catch (error) { out.innerHTML = `<p class="flag">${esc(error.message)}</p>`; }
}
async function addGolden() {
  const { ws } = ctx();
  const briefId = document.getElementById("gbrief").value;
  const note = document.getElementById("gnote").value;
  try {
    await call(`/internal/workbench/workspaces/${ws}/briefs/${briefId}/golden`,
      { method: "POST", body: JSON.stringify({ note }) });
    await show("golden");
  } catch (error) { out.innerHTML = `<p class="flag">${esc(error.message)}</p>`; }
}
async function removeGolden(briefId) {
  const { ws } = ctx();
  try {
    await call(`/internal/workbench/workspaces/${ws}/briefs/${briefId}/golden`,
      { method: "DELETE" });
    await show("golden");
  } catch (error) { out.innerHTML = `<p class="flag">${esc(error.message)}</p>`; }
}
</script>
</body>
</html>"""


@router.get("/console", include_in_schema=False)
def console_shell() -> HTMLResponse:
    return HTMLResponse(_PAGE)
