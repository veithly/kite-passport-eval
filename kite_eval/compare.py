"""Fail-closed comparison of Proofroom reports for CI regression gating."""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .core import InputError, decode, digest, read_bytes

STATUSES = ("pass", "fail", "error", "missing")
STATUS_RANK = {"missing": 0, "error": 1, "fail": 2, "pass": 3}
REVIEW_RANK = {"fail": 0, "pending": 1, "pass": 2}


def _report_cases(report: dict, label: str) -> dict:
    if not isinstance(report, dict) or type(report.get("schema_version")) is not int or report["schema_version"] != 1:
        raise InputError(label + " report requires schema_version=1")
    suite_sha = report.get("suite_sha256")
    if not isinstance(suite_sha, str) or re.fullmatch(r"[0-9a-f]{64}", suite_sha) is None:
        raise InputError(label + " report has invalid suite_sha256")
    capture_sha = report.get("capture_sha256")
    if capture_sha is not None and (not isinstance(capture_sha, str)
                                    or re.fullmatch(r"[0-9a-f]{64}", capture_sha) is None):
        raise InputError(label + " report has invalid capture_sha256")
    cases = report.get("cases")
    if not isinstance(cases, list) or not cases or len(cases) > 10000:
        raise InputError(label + " report must contain a non-empty bounded cases array")
    result = {}
    for case in cases:
        if not isinstance(case, dict) or type(case.get("id")) is not int or case["id"] <= 0:
            raise InputError(label + " report contains an invalid case id")
        cid = case["id"]
        if cid in result:
            raise InputError(label + " report contains duplicate case id " + str(cid))
        status = case.get("status")
        if status not in STATUSES:
            raise InputError(label + " report contains invalid status for case " + str(cid))
        checks = case.get("checks")
        if not isinstance(checks, list) or not checks:
            raise InputError(label + " report contains no checks for case " + str(cid))
        literals = []
        passed = []
        for check in checks:
            if (not isinstance(check, dict) or not isinstance(check.get("literal"), str)
                    or not check["literal"].strip() or type(check.get("passed")) is not bool):
                raise InputError(label + " report contains invalid checks for case " + str(cid))
            literals.append(check["literal"])
            passed.append(check["passed"])
        if len(literals) != len(set(literals)):
            raise InputError(label + " report contains duplicate literals for case " + str(cid))
        if status == "pass" and not all(passed):
            raise InputError(label + " report has pass status with failed checks for case " + str(cid))
        if status == "fail" and all(passed):
            raise InputError(label + " report has fail status with no failed checks for case " + str(cid))
        if status in ("error", "missing") and any(passed):
            raise InputError(label + " report has unusable status with passing checks for case " + str(cid))
        review = case.get("review")
        if review is not None and (not isinstance(review, dict) or review.get("verdict") not in ("pass", "fail")):
            raise InputError(label + " report contains an invalid semantic review for case " + str(cid))
        transcript = case.get("transcript")
        response_sha = None
        if transcript is not None:
            if not isinstance(transcript, dict):
                raise InputError(label + " report contains an invalid transcript for case " + str(cid))
            response_sha = transcript.get("response_sha256")
            if response_sha is not None and (not isinstance(response_sha, str)
                                             or re.fullmatch(r"[0-9a-f]{64}", response_sha) is None):
                raise InputError(label + " report contains an invalid response hash for case " + str(cid))
        result[cid] = {
            "status": status,
            "literals": literals,
            "passed": passed,
            "review": review["verdict"] if review else "pending",
            "response_sha256": response_sha,
        }
    return result


def load_report(path: Path) -> dict:
    try:
        report = decode(read_bytes(path).decode("utf-8"))
    except UnicodeError as exc:
        raise InputError("Report is not valid UTF-8: " + str(path)) from exc
    _report_cases(report, str(path))
    return report


def compare_reports(baseline: dict, candidate: dict) -> dict:
    before = _report_cases(baseline, "baseline")
    after = _report_cases(candidate, "candidate")
    if baseline["suite_sha256"] != candidate["suite_sha256"]:
        raise InputError("Suite SHA-256 differs; refusing an incomparable regression gate")
    if set(before) != set(after):
        missing = sorted(set(before) - set(after))
        added = sorted(set(after) - set(before))
        raise InputError("Case IDs differ; missing={} added={}".format(missing, added))

    rows = []
    for cid in sorted(before):
        old, new = before[cid], after[cid]
        if old["literals"] != new["literals"]:
            raise InputError("Assertion literals differ for case " + str(cid))
        lost = [literal for literal, was, now in zip(old["literals"], old["passed"], new["passed"])
                if was and not now]
        gained = [literal for literal, was, now in zip(old["literals"], old["passed"], new["passed"])
                  if not was and now]
        status_regression = STATUS_RANK[new["status"]] < STATUS_RANK[old["status"]]
        status_improvement = STATUS_RANK[new["status"]] > STATUS_RANK[old["status"]]
        review_regression = REVIEW_RANK[new["review"]] < REVIEW_RANK[old["review"]]
        review_improvement = REVIEW_RANK[new["review"]] > REVIEW_RANK[old["review"]]
        regressed = bool(lost or status_regression or review_regression)
        improved = bool(not regressed and (gained or status_improvement or review_improvement))
        classification = "regressed" if regressed else "improved" if improved else "unchanged"
        old_hash, new_hash = old["response_sha256"], new["response_sha256"]
        response_changed = (old_hash is not None or new_hash is not None) and old_hash != new_hash
        rows.append({
            "id": cid,
            "classification": classification,
            "baseline_status": old["status"],
            "candidate_status": new["status"],
            "baseline_review": old["review"],
            "candidate_review": new["review"],
            "lost_assertions": lost,
            "gained_assertions": gained,
            "status_regression": status_regression,
            "semantic_review_regression": review_regression,
            "response_changed": response_changed,
            "baseline_response_sha256": old_hash,
            "candidate_response_sha256": new_hash,
        })
    summary = {
        "total": len(rows),
        "regressions": sum(r["classification"] == "regressed" for r in rows),
        "improvements": sum(r["classification"] == "improved" for r in rows),
        "unchanged": sum(r["classification"] == "unchanged" for r in rows),
        "response_changed": sum(r["response_changed"] for r in rows),
        "assertion_regressions": sum(len(r["lost_assertions"]) for r in rows),
        "assertion_improvements": sum(len(r["gained_assertions"]) for r in rows),
        "status_regressions": sum(r["status_regression"] for r in rows),
        "semantic_review_regressions": sum(r["semantic_review_regression"] for r in rows),
    }
    return {
        "schema_version": 1,
        "kind": "proofroom-regression-comparison",
        "suite_sha256": baseline["suite_sha256"],
        "baseline_capture_sha256": baseline.get("capture_sha256"),
        "candidate_capture_sha256": candidate.get("capture_sha256"),
        "summary": summary,
        "cases": rows,
    }


def comparison_exit(comparison: dict) -> int:
    return int(bool(comparison["summary"]["regressions"]))


def _xml_text(value) -> str:
    return re.sub(r"[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]", "�", str(value))


def comparison_junit(comparison: dict) -> bytes:
    summary = comparison["summary"]
    root = ET.Element(
        "testsuite",
        name="Kite Proofroom regression gate",
        tests=str(summary["total"]),
        failures=str(summary["regressions"]),
        errors="0",
        skipped="0",
    )
    properties = ET.SubElement(root, "properties")
    ET.SubElement(properties, "property", name="suite_sha256", value=_xml_text(comparison["suite_sha256"]))
    ET.SubElement(properties, "property", name="assertion_regressions",
                  value=str(summary["assertion_regressions"]))
    for row in comparison["cases"]:
        node = ET.SubElement(root, "testcase", name="case-" + str(row["id"]), classname="proofroom.compare")
        if row["classification"] == "regressed":
            details = []
            if row["status_regression"]:
                details.append("status {} -> {}".format(row["baseline_status"], row["candidate_status"]))
            if row["lost_assertions"]:
                details.append("lost assertions: " + " | ".join(row["lost_assertions"]))
            if row["semantic_review_regression"]:
                details.append("semantic review {} -> {}".format(
                    row["baseline_review"], row["candidate_review"]))
            ET.SubElement(node, "failure", message="Regression detected").text = _xml_text("; ".join(details))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _markdown(comparison: dict) -> str:
    s = comparison["summary"]
    lines = [
        "# Kite Proofroom regression comparison",
        "",
        "Suite SHA-256: `{}`".format(comparison["suite_sha256"]),
        "",
        "- Regressions: **{}**".format(s["regressions"]),
        "- Improvements: **{}**".format(s["improvements"]),
        "- Unchanged: **{}**".format(s["unchanged"]),
        "- Lost assertions: **{}**".format(s["assertion_regressions"]),
        "- Gained assertions: **{}**".format(s["assertion_improvements"]),
        "- Response hashes changed: **{}**".format(s["response_changed"]),
        "",
        "| Case | Result | Status | Review | Lost assertions | Gained assertions |",
        "|---:|---|---|---|---|---|",
    ]
    for row in comparison["cases"]:
        def cell(values):
            return "<br>".join(
                html.escape(str(v), quote=True).replace("|", "&#124;").replace("\n", "<br>")
                for v in values
            ) if values else "—"
        lines.append("| {} | {} | {} → {} | {} → {} | {} | {} |".format(
            row["id"], row["classification"].upper(), row["baseline_status"], row["candidate_status"],
            row["baseline_review"], row["candidate_review"], cell(row["lost_assertions"]),
            cell(row["gained_assertions"])))
    return "\n".join(lines) + "\n"


def _html(comparison: dict) -> str:
    s = comparison["summary"]
    rows = []
    for row in comparison["cases"]:
        lost = "<br>".join(html.escape(v) for v in row["lost_assertions"]) or "—"
        gained = "<br>".join(html.escape(v) for v in row["gained_assertions"]) or "—"
        rows.append(
            "<tr class=\"{}\"><td>{}</td><td><b>{}</b></td><td>{} → {}</td>"
            "<td>{} → {}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                row["classification"], row["id"], row["classification"].upper(),
                html.escape(row["baseline_status"]), html.escape(row["candidate_status"]),
                html.escape(row["baseline_review"]), html.escape(row["candidate_review"]),
                lost, gained, "yes" if row["response_changed"] else "no"))
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Kite Proofroom · Regression gate</title><style>
body{{font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;margin:0;background:#0d0f10;color:#f4f5f6}}
main{{max-width:1180px;margin:auto;padding:40px 20px 80px}}h1{{font-size:clamp(34px,6vw,72px);line-height:1;margin:.2em 0}}
.meta{{color:#aeb4b8;word-break:break-all}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:#34383b;border:1px solid #34383b;margin:30px 0}}
.stats div{{background:#15181a;padding:18px}}.stats strong{{display:block;font-size:30px}}.ok{{color:#8fd6a8}}.bad{{color:#ff9c91}}
.wrap{{overflow:auto;border:1px solid #34383b}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #34383b}}
th{{position:sticky;top:0;background:#202427}}.regressed{{background:#2b1717}}.improved{{background:#15271d}}
a{{color:inherit}}code{{word-break:break-all}}@media(max-width:600px){{main{{padding:24px 12px}}}}
</style></head><body><main><p>KITE / PROOFROOM / WEEKLY REGRESSION GATE</p><h1>{headline}</h1>
<p class="meta">Suite SHA-256: <code>{suite}</code></p>
<section class="stats"><div><span>REGRESSIONS</span><strong class="{reg_class}">{reg}</strong></div>
<div><span>IMPROVEMENTS</span><strong>{imp}</strong></div><div><span>LOST ASSERTIONS</span><strong>{lost}</strong></div>
<div><span>CHANGED RESPONSES</span><strong>{changed}</strong></div></section>
<p>A regression is fail-closed: any previously passing literal that disappears, a worse case status, or a semantic-review downgrade fails the gate. Mixed gains never erase a loss.</p>
<div class="wrap"><table><thead><tr><th>Case</th><th>Classification</th><th>Status</th><th>Review</th><th>Lost assertions</th><th>Gained assertions</th><th>Response changed</th></tr></thead>
<tbody>{rows}</tbody></table></div></main></body></html>""".format(
        headline="No regressions detected." if not s["regressions"] else "Regression detected.",
        suite=html.escape(comparison["suite_sha256"]), reg_class="ok" if not s["regressions"] else "bad",
        reg=s["regressions"], imp=s["improvements"], lost=s["assertion_regressions"],
        changed=s["response_changed"], rows="".join(rows))


def write_comparison(out: Path, comparison: dict) -> None:
    artifacts = {
        "comparison.json": (json.dumps(comparison, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode(),
        "comparison.md": _markdown(comparison).encode(),
        "junit.xml": comparison_junit(comparison),
        "index.html": _html(comparison).encode(),
    }
    for name, data in artifacts.items():
        with (out / name).open("xb") as stream:
            stream.write(data)
    hashes = {name: digest(data) for name, data in artifacts.items()}
    with (out / "checksums.json").open("x", encoding="utf-8") as stream:
        json.dump(hashes, stream, indent=2, sort_keys=True)
        stream.write("\n")
