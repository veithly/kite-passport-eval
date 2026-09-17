"""Offline, escaped reports. No scripts, fonts or analytics fetched from a CDN."""
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .core import digest


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def xml_text(value) -> str:
    return re.sub(r"[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]", "�", str(value))


def md(value) -> str:
    return esc(value).replace("|", "&#124;").replace("\n", "<br>")


def junit(report: dict) -> bytes:
    s = report["summary"]
    def failed(c):
        return c["status"] == "fail" or bool(c["review"] and c["review"]["verdict"] == "fail") or bool(
            report.get("require_review") and not c["review"])
    failures = sum(failed(c) for c in report["cases"] if c["status"] not in ("error", "missing"))
    root = ET.Element("testsuite", name="Kite Passport literal assertions", tests=str(s["total"]),
                      failures=str(failures), errors=str(s["error"] + s["missing"]), skipped="0")
    properties = ET.SubElement(root, "properties")
    for name, value in [("scope", report["scope"]), ("suite_sha256", report["suite_sha256"]),
                        ("onchain_verified", "false"), ("provenance_kind", report["provenance_kind"])]:
        ET.SubElement(properties, "property", name=name, value=xml_text(value))
    for case in report["cases"]:
        record = case["transcript"] or {}
        node = ET.SubElement(root, "testcase", name="case-" + str(case["id"]),
                             classname=case["skill"], time=str(record.get("duration_ms", 0) / 1000))
        if case["status"] in ("missing", "error"):
            ET.SubElement(node, "error", type=record.get("status", "missing"),
                          message="No usable transcript; assertions were not waived")
        elif failed(case):
            missing_literals = [a["literal"] for a in case["checks"] if not a["passed"]]
            ET.SubElement(node, "failure", message="Literal or semantic-review failure").text = xml_text(
                "Missing literal assertions: " + ", ".join(missing_literals) + "\n" +
                (case["review"]["rationale"] if case["review"] else "Semantic review: pending"))
        ET.SubElement(node, "system-out").text = xml_text("\n".join(
            ("PASS " if a["passed"] else "FAIL ") + a["literal"] for a in case["checks"]))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def render(report: dict) -> str:
    s = report["summary"]
    cells, rows = [], []
    for c in report["cases"]:
        cid, status = c["id"], c["status"]
        record = c["transcript"] or {}
        symbol = {"pass": "✓", "fail": "×", "error": "!", "missing": "—"}[status]
        cells.append(f'<a class="cell {status}" href="#case-{cid}" aria-label="Case {cid}: {status}" '
                     f'title="{esc(c["skill"])} · {cid} · {status}"><span aria-hidden="true">{symbol}</span>{cid}</a>')
        checks = "".join('<tr><td class="check ' + ("pass" if a["passed"] else "fail") + '">' +
                         ("✓ PASS" if a["passed"] else "× FAIL") + '</td><td><code>' + esc(a["literal"]) +
                         '</code></td><td>' + ("Line " + str(a["line"]) + " · offset " + str(a["offset"])
                         if a["passed"] else "Not found") + '</td></tr>' for a in c["checks"])
        review = c["review"]
        review_html = (f'<b>{esc(review["verdict"].upper())}</b> · {esc(review["reviewer"])}'
                       f'<p>{esc(review["rationale"])}</p><blockquote>{esc(review["quote"])}</blockquote>') if review else (
                       'Pending. Literal matches alone cannot prove safe behavior, command order or execution.')
        rows.append(f'''<details class="case" id="case-{cid}" data-status="{status}" data-skill="{esc(c["skill"])}">
<summary><span class="case-id">{cid:03}</span><span class="case-title"><small>{esc(c["skill"])}</small>{esc(c["prompt"])}</span>
<span class="badge {status}">{status.upper()}</span><span class="plus" aria-hidden="true">+</span></summary>
<div class="case-body"><h3>Expected behavior</h3><p>{esc(c["expected_output"])}</p>
<h3>Every assertion, accounted for</h3><div class="table-wrap"><table><caption class="sr">Literal assertion evidence for case {cid}</caption>
<thead><tr><th>Result</th><th>Exact substring</th><th>Evidence</th></tr></thead><tbody>{checks}</tbody></table></div>
<h3>Captured response <span class="muted">/ {esc(record.get("kind", "missing"))}</span></h3>
<pre>{esc(record.get("response", "No response was recorded. This case is not skipped."))}</pre>
<p class="hash">Response SHA-256: {esc(record.get("response_sha256", "unavailable"))}<br>
Adapter: {esc(record.get("adapter", "not specified"))} · Capture status: {esc(record.get("status", "missing"))}</p>
<h3>Semantic review</h3><div class="review">{review_html}</div></div></details>''')
    assets = Path(__file__).parent / "assets"
    css = (assets / "report.css").read_text(encoding="utf-8")
    js = (assets / "report.js").read_text(encoding="utf-8")
    skill_options = "".join(f'<option>{esc(slug)}</option>' for slug in sorted({c["skill"] for c in report["cases"]}))
    coverage = "Complete capture" if s["complete"] else "Incomplete capture"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>Kite Proofroom · Passport evaluation report</title><style>{css}</style></head><body>
<a class="skip" href="#results">Skip to results</a><header><a href="#" class="wordmark"><span class="mark" aria-hidden="true">↗</span> KITE <span>/ PROOFROOM</span></a>
<span class="edition">PASSPORT SKILLS · EVAL RUNNER</span><a href="report.json" download class="export">Export JSON ↗</a></header>
<main><section class="hero"><div><p class="eyebrow">BEHAVIORAL EVALUATION / 01</p><h1>Evidence,<br><em>not guesses.</em></h1>
<p class="intro">Every Passport scenario. Every literal assertion.<br>A traceable record of what the agent actually said.</p>
<div class="tags"><span>{esc(report["provenance_kind"].upper())} TRANSCRIPTS</span><span>{coverage.upper()}</span></div></div>
<aside class="provenance"><div class="section-number">RUN RECORD <span>↙</span></div><dl><dt>Suite</dt><dd>Kite Passport Skills</dd>
<dt>Recorded cases</dt><dd>{s["recorded"]} / {s["total"]}</dd><dt>Generated</dt><dd>{esc(report.get("generated_at", "not specified"))}</dd>
<dt>Scope</dt><dd>Text-only literal checks</dd></dl><p class="hash"><b>SUITE SHA-256</b><br>{esc(report["suite_sha256"])}</p>
<p class="scope-note">{esc(report.get("capture_note", "No on-chain transaction is certified by this report."))}</p></aside></section>
<section class="stats" aria-label="Run summary"><div><span class="stat-label">LITERAL PASS</span><strong>{s["pass"]}<small> / {s["total"]}</small></strong></div>
<div><span class="stat-label">ASSERTIONS MATCHED</span><strong>{s["assertions_passed"]}<small> / {s["assertions"]}</small></strong></div>
<div><span class="stat-label">FAIL / ERROR / MISSING</span><strong>{s["fail"]}<small> / {s["error"]} / {s["missing"]}</small></strong></div>
<div><span class="stat-label">SEMANTICALLY REVIEWED</span><strong>{s["reviewed"]}<small> / {s["total"]}</small></strong></div></section>
<section class="overview"><div class="section-heading"><h2>01 / Suite at a glance</h2><span>SELECT A CASE TO INSPECT</span></div>
<div class="matrix" aria-label="Case status matrix">{''.join(cells)}</div><div class="legend"><span>✓ Pass</span><span>× Fail</span><span>! Error</span><span>— Missing</span>
<p>Symbols and case numbers remain visible: status is never communicated by color alone.</p></div></section>
<section id="results"><div class="section-heading"><h2>02 / The evidence ledger</h2><span id="visible-count" aria-live="polite">{s["total"]} cases</span></div>
<div class="filters"><label class="search-label">Search cases<input id="search" type="search" placeholder="Search prompt, skill, assertion or response…"></label>
<label>Status<select id="status"><option value="all">All results</option><option value="pass">Pass</option><option value="fail">Fail</option><option value="error">Error</option><option value="missing">Missing</option></select></label>
<label>Skill<select id="skill"><option value="all">All skills</option>{skill_options}</select></label><button id="reset" type="button">Reset</button></div>
<p id="empty" hidden>No matching cases. Try another filter or reset the search.</p>{''.join(rows)}</section>
<section class="method"><h2>03 / Read the result correctly</h2><div><p><b>Literal means literal.</b> Case-sensitive substring matching, with zero-based Unicode character offsets and one-based line numbers. No regex, fuzzy matching or automatic waivers.</p>
<p><b>A pass is not a safety certificate.</b> An agent can quote a command without executing it, mention a forbidden action, or put steps in the wrong order and still match strings. Check expected behavior and attach a transcript-bound semantic review.</p>
<p><b>Replay is not a fresh model run.</b> Captures retain their provenance. Fixture runs test the harness; agent transcripts test responses. Neither proves skill triggering, account access or a settled payment.</p></div></section></main>
<footer><span>KITE PROOFROOM <span class="muted">/ Independent community tooling.</span></span><nav aria-label="Evidence downloads"><a href="report.md" download>Markdown</a><a href="junit.xml" download>JUnit XML</a><a href="transcripts.jsonl" download>Transcripts</a><a href="checksums.json" download>Checksums</a></nav></footer>
<script>{js}</script></body></html>'''


def write_report(out: Path, report: dict) -> None:
    s = report["summary"]
    text = ["# Kite Passport evaluation report", "", "Scope: literal transcript assertions; on-chain verification: **not performed**.",
            "", "Provenance: **" + md(report["provenance_kind"]) + "**. Semantic reviews: " + str(s["reviewed"]) + "/" + str(s["total"]) + ".",
            "", "Suite SHA-256: `" + report["suite_sha256"] + "`", "", "```json", json.dumps(s, indent=2), "```", ""]
    for c in report["cases"]:
        text += ["## Case " + str(c["id"]) + " — " + c["status"].upper(), "", md(c["prompt"]), "",
                 "Expected: " + md(c["expected_output"]), "", "| Assertion | Result | Line / offset |", "|---|---|---|"]
        for a in c["checks"]:
            text.append("| " + md(a["literal"]) + " | " + ("PASS" if a["passed"] else "FAIL") + " | " +
                        (str(a["line"]) + " / " + str(a["offset"]) if a["passed"] else "not found") + " |")
        text += ["", "Semantic review: " + (md(c["review"]["verdict"] + ": " + c["review"]["rationale"]) if c["review"] else "pending"), ""]
    artifacts = {"report.json": (json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode(),
                 "junit.xml": junit(report), "report.md": ("\n".join(text) + "\n").encode(),
                 "index.html": render(report).encode()}
    for name, data in artifacts.items():
        with (out / name).open("xb") as stream:
            stream.write(data)
    hashes = {name: digest(data) for name, data in artifacts.items()}
    for name in ("transcripts.jsonl", "recovery.json"):
        if (out / name).is_file():
            hashes[name] = digest((out / name).read_bytes())
    with (out / "checksums.json").open("x", encoding="utf-8") as stream:
        json.dump(hashes, stream, indent=2, sort_keys=True); stream.write("\n")
