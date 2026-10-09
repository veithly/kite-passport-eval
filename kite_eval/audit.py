"""Offline provenance audit for Kite Passport evaluation evidence.

This verifies internal consistency and immutable, code-reviewed release pins.
It does NOT certify that a provider honestly produced a given transcript.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import subprocess
from typing import Optional
import xml.etree.ElementTree as ET

from .core import (
    SKILL_BY_ID, UPSTREAM_COMMIT, InputError, canonical, context_for, decode,
    digest, grade, load_suite, load_transcripts, read_bytes, request_for,
    verify_upstream,
)

# Independently recorded in the original v1.0 release. Moving these pins
# requires an explicit code-reviewed change; bundle checksums are not a trust root.
RELEASE_PINS = {
    "original": "9c68df39da103b4bfa4968b2dc1f77433e9e9568e6478208441b67203af899e6",
    "retry": "ec0d8961c1bf6a5426c8b391ee080c2f1b8394a735ab89a5eef409bce58831da",
    "recovered": "fdb076c886d8f1025d48042016db0330dbd10822eceaa3d06a371ee314e06a13",
    "report": "3cf3ee8cbb7d76a20aba99bfce2fd577da8dead2330e6b0aca406971e6e4d76a",
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
BASE_FILES = ("transcripts.jsonl", "report.json", "report.md", "index.html", "junit.xml")


class Ledger:
    def __init__(self):
        self.checks = []

    def check(self, group: str, name: str, passed: bool, evidence: str) -> bool:
        self.checks.append({
            "group": group, "id": name, "passed": bool(passed),
            "evidence": str(evidence)[:1200],
        })
        return bool(passed)

    def result(self, suite_hash: str, capture_hash: str, pinned: bool, case_count: int,
               assertion_count: int) -> dict:
        passed = sum(row["passed"] for row in self.checks)
        return {
            "schema_version": 1,
            "kind": "kite-passport-offline-evidence-audit",
            "scope": "hashes, request reconstruction, scored report, recovery lineage; not provider authenticity",
            "onchain_verified": False,
            "release_pins_enabled": pinned,
            "upstream_commit": UPSTREAM_COMMIT,
            "suite_sha256": suite_hash,
            "capture_sha256": capture_hash,
            "summary": {
                "checks": len(self.checks), "passed": passed,
                "failed": len(self.checks) - passed,
                "official_cases": case_count, "literal_assertions": assertion_count,
            },
            "checks": self.checks,
        }


def _json_bytes(value: bytes, label: str, ledger: Ledger) -> Optional[object]:
    try:
        parsed = decode(value.decode("utf-8"))
    except (UnicodeError, InputError) as exc:
        ledger.check("Files", label + ".decoded-json", False, "JSON decoding failed: " + str(exc))
        return None
    ledger.check("Files", label + ".decoded-json", True, "Strict UTF-8 JSON decoded without duplicate keys")
    return parsed


def _safe_read(path: Path, ledger: Ledger, label: str) -> Optional[bytes]:
    if path.is_symlink() or not path.is_file():
        ledger.check("Files", label, False, "Missing, not regular, or symbolic-link file: " + str(path))
        return None
    try:
        data = read_bytes(path)
    except (OSError, InputError) as exc:
        ledger.check("Files", label, False, "Unusable file: " + str(exc))
        return None
    ledger.check("Files", label, True, "Readable, bounded regular file")
    return data


def _bundle(path: Path, role: str, ledger: Ledger, recovery: bool = False) -> dict:
    files = BASE_FILES + (("recovery.json",) if recovery else ())
    result = {}
    if path.is_symlink() or not path.is_dir():
        ledger.check("Files", role + ".directory", False, "Missing or symbolic-link bundle directory")
        return result
    ledger.check("Files", role + ".directory", True, "Regular evidence directory")
    for filename in files:
        result[filename] = _safe_read(path / filename, ledger, role + "." + filename)
    raw_manifest = _safe_read(path / "checksums.json", ledger, role + ".checksums.json")
    if raw_manifest is None:
        return result
    manifest = _json_bytes(raw_manifest, role + ".checksums", ledger)
    if not isinstance(manifest, dict):
        ledger.check("Files", role + ".checksum-schema", False, "Expected a JSON object of file SHA-256 hashes")
        return result
    ledger.check("Files", role + ".checksum-schema", set(manifest) == set(files)
                 and all(isinstance(sha, str) and SHA256.fullmatch(sha) for sha in manifest.values()),
                 "Exact expected filenames with 64-character lowercase hexadecimal digests")
    for filename in files:
        data = result.get(filename)
        actual = digest(data) if data is not None else "missing"
        ledger.check("Checksums", role + "." + filename, data is not None
                     and manifest.get(filename) == actual, "SHA-256 " + actual)
    return result


def _records(path: Path, cases: list, ledger: Ledger, role: str) -> Optional[dict]:
    try:
        values = load_transcripts(path, cases)
    except (InputError, OSError, UnicodeError) as exc:
        ledger.check("Transcripts", role + ".schema", False, str(exc))
        return None
    ledger.check("Transcripts", role + ".schema", True,
                 "{} distinct IDs with valid prompt/response hashes".format(len(values)))
    return values


def _validate_reviews(report: dict, records: dict, ledger: Ledger) -> dict:
    reviews = {}
    raw_cases = report.get("cases")
    if not isinstance(raw_cases, list):
        ledger.check("Report", "semantic-review-schema", False, "Report is missing case array")
        return reviews
    valid = True
    for case in raw_cases:
        if not isinstance(case, dict) or type(case.get("id")) is not int:
            valid = False
            continue
        item = case.get("review")
        if item is None:
            continue
        cid = case["id"]
        record = records.get(cid)
        if (cid in reviews or not isinstance(item, dict) or not record or
                record.get("status") != "ok" or item.get("verdict") not in ("pass", "fail") or
                any(not isinstance(item.get(key), str) or not item[key].strip()
                    for key in ("reviewer", "rationale", "quote")) or
                item.get("response_sha256") != record.get("response_sha256") or
                item["quote"] not in record["response"]):
            valid = False
        else:
            reviews[cid] = item
    ledger.check("Report", "semantic-review-schema", valid,
                 "{} hash- and quote-bound reviews; unchecked reviews are not endorsed".format(len(reviews)))
    return reviews


def audit_evidence(upstream: Path, adapter_path: Path, recovered: Path,
                   original: Path, retry: Path, release_pins: bool = False) -> dict:
    """Independently reconstruct requests and scores, and verify error-only lineage."""
    ledger = Ledger()
    try:
        verify_upstream(upstream)
        ledger.check("Inputs", "upstream-git", True, "Clean upstream Git commit " + UPSTREAM_COMMIT)
    except (InputError, OSError, subprocess.SubprocessError) as exc:
        # A pin mismatch is a failed audit, not permission to use unpinned docs.
        ledger.check("Inputs", "upstream-git", False, str(exc))

    cases, suite_hash = load_suite(upstream / "evals/evals.json", pinned=True)
    ledger.check("Inputs", "suite-pin", True, "Official SHA-256 " + suite_hash)
    ledger.check("Inputs", "suite-size", len(cases) == 138
                 and sum(len(c["assertions"]) for c in cases) == 424,
                 "{} cases / {} assertions".format(len(cases), sum(len(c["assertions"]) for c in cases)))

    config_data = _safe_read(adapter_path, ledger, "adapter-config")
    config = _json_bytes(config_data, "adapter-config", ledger) if config_data else None
    config_ok = (isinstance(config, dict) and set(config) == {"name", "argv"}
                 and isinstance(config.get("name"), str) and bool(config["name"].strip())
                 and isinstance(config.get("argv"), list) and bool(config["argv"])
                 and all(isinstance(x, str) and x and "\x00" not in x for x in config["argv"]))
    ledger.check("Inputs", "adapter-format", config_ok,
                 "Explicit non-shell argv config" if config_ok else "Adapter config is malformed")
    adapter_hash = digest(canonical(config)) if config_ok else ""

    source = _bundle(recovered, "recovered", ledger, recovery=True)
    first = _bundle(original, "original", ledger)
    second = _bundle(retry, "retry", ledger)
    if release_pins:
        for role, data, key in [
            ("original", first, "transcripts.jsonl"),
            ("retry", second, "transcripts.jsonl"),
            ("recovered", source, "transcripts.jsonl"),
            ("report", source, "report.json"),
        ]:
            content = data.get(key)
            ledger.check("Release pins", role, content is not None and digest(content) == RELEASE_PINS[role],
                         "Trusted v1.0 SHA-256 {}".format(RELEASE_PINS[role]))

    records = _records(recovered / "transcripts.jsonl", cases, ledger, "recovered") \
        if source.get("transcripts.jsonl") is not None else None
    originals = _records(original / "transcripts.jsonl", cases, ledger, "original") \
        if first.get("transcripts.jsonl") is not None else None
    retries = _records(retry / "transcripts.jsonl", cases, ledger, "retry") \
        if second.get("transcripts.jsonl") is not None else None

    contexts = {}
    for slug in sorted({SKILL_BY_ID[c["id"]] for c in cases}):
        try:
            contexts[slug] = context_for(upstream, slug)
            ledger.check("Inputs", "context." + slug, True,
                         "{} official documents".format(len(contexts[slug])))
        except (OSError, InputError, UnicodeError) as exc:
            ledger.check("Inputs", "context." + slug, False, str(exc))

    if records is not None:
        ledger.check("Transcripts", "complete-capture", set(records) == {c["id"] for c in cases},
                     "{} of {} cases are accounted for".format(len(records), len(cases)))
        for case in cases:
            cid = case["id"]
            item = records.get(cid)
            key = "case.{:03d}".format(cid)
            slug = SKILL_BY_ID[cid]
            documents = contexts.get(slug)
            if item is None:
                for suffix in ("request", "documents", "adapter", "capture"):
                    ledger.check("Cases", key + "." + suffix, False, "No transcript for this official case")
                continue
            if documents is None:
                for suffix in ("request", "documents"):
                    ledger.check("Cases", key + "." + suffix, False, "Cannot reconstruct missing upstream context")
            else:
                expected_request = digest(canonical(request_for(case, documents)))
                ledger.check("Cases", key + ".request", item.get("request_sha256") == expected_request,
                             "Independent request SHA-256 " + expected_request)
                manifest = [{"path": doc["path"], "sha256": doc["sha256"]} for doc in documents]
                ledger.check("Cases", key + ".documents", item.get("documents") == manifest,
                             "{} verified official context document hashes".format(len(manifest)))
            ledger.check("Cases", key + ".adapter", config_ok and item.get("adapter") == config["name"]
                         and item.get("adapter_config_sha256") == adapter_hash,
                         "Pinned adapter configuration SHA-256 " + adapter_hash)
            metadata = item.get("metadata")
            ledger.check("Cases", key + ".capture", item.get("kind") == "agent"
                         and item.get("status") == "ok"
                         and isinstance(metadata, dict)
                         and metadata.get("mode") == "text-only-no-side-effects"
                         and metadata.get("tools_enabled") is False,
                         "Real-agent record with recorded tools-disabled metadata; not proof of provider behavior")

    report = _json_bytes(source["report.json"], "recovered.report", ledger) \
        if source.get("report.json") is not None else None
    if records is not None and isinstance(report, dict):
        reviews = _validate_reviews(report, records, ledger)
        expected = grade(cases, records, suite_hash, reviews)
        ledger.check("Report", "schema-and-suite", report.get("schema_version") == 1
                     and report.get("suite_sha256") == suite_hash
                     and report.get("scope") == "literal-transcript-checks"
                     and report.get("onchain_verified") is False,
                     "Version 1, official suite, literal scope, no on-chain claim")
        ledger.check("Report", "summary", report.get("summary") == expected["summary"],
                     "Summary independently recomputed from all {} assertions".format(
                         expected["summary"]["assertions"]))
        ledger.check("Report", "every-case", report.get("cases") == expected["cases"],
                     "Every prompt, expected output, grade, offset, line and transcript independently reproduced")
        ledger.check("Report", "provenance", report.get("provenance_kind") == "agent",
                     "Entire capture is classified as agent responses, never test fixtures")
        journal = source.get("transcripts.jsonl")
        ledger.check("Report", "capture-hash", journal is not None
                     and report.get("capture_sha256") == digest(journal),
                     "Exact source JSONL journal hash")
    else:
        ledger.check("Report", "independent-score", False, "Cannot reconstruct score from missing inputs")

    manifest = _json_bytes(source["recovery.json"], "recovered.recovery", ledger) \
        if source.get("recovery.json") is not None else None
    if isinstance(manifest, dict) and records is not None and originals is not None and retries is not None:
        first_raw = first.get("transcripts.jsonl")
        retry_raw = second.get("transcripts.jsonl")
        source_raw = source.get("transcripts.jsonl")
        expected_ids = sorted(retries)
        ledger.check("Recovery", "source-hashes", first_raw is not None and retry_raw is not None
                     and manifest.get("original_sha256") == digest(first_raw)
                     and manifest.get("retry_sha256") == digest(retry_raw),
                     "Original and retry journals match recovery manifest")
        ledger.check("Recovery", "manifest-metadata",
                     manifest.get("original_path") == "evidence/live/transcripts.jsonl"
                     and manifest.get("retry_path") == "evidence/retry-135/transcripts.jsonl"
                     and manifest.get("replacement_ids") == expected_ids
                     and manifest.get("policy") == "infrastructure-errors-only; identical request and adapter",
                     "Explicit infrastructure-only replacement manifest")
        ledger.check("Recovery", "original-summary",
                     manifest.get("original_summary") == grade(cases, originals, suite_hash)["summary"],
                     "Original 138-case result recomputed without recovered data")
        candidate = dict(originals)
        provenance_ok = bool(retries) and set(originals) == set(records)
        for cid, replacement in retries.items():
            previous = originals.get(cid)
            if not previous or previous["status"] == "ok" or replacement["status"] != "ok" or (
                    replacement["kind"] != "agent" or previous["kind"] != "agent"):
                provenance_ok = False
                continue
            if any(not previous.get(name) or previous.get(name) != replacement.get(name)
                   for name in ("request_sha256", "prompt_sha256", "adapter_config_sha256")):
                provenance_ok = False
                continue
            candidate[cid] = replacement
        ledger.check("Recovery", "anti-cherry-pick", provenance_ok,
                     "Only prior infrastructure failures replaced; requests and adapter hashes unchanged")
        ledger.check("Recovery", "exact-records", provenance_ok and candidate == records,
                     "Recovered 138-record journal contains only original rows and explicit retry replacements")
        reconstructed = (b"".join(canonical(candidate[cid]) + b"\n" for cid in sorted(candidate))
                         if provenance_ok else None)
        ledger.check("Recovery", "canonical-journal", reconstructed is not None and source_raw == reconstructed,
                     "Recovered bytes exactly equal the error-only canonical merge")
        ledger.check("Recovery", "report-manifest", isinstance(report, dict)
                     and report.get("recovery") == manifest,
                     "Published report and standalone recovery manifest agree")
    else:
        ledger.check("Recovery", "lineage-complete", False,
                     "Cannot audit original → retry → recovered lineage")

    return ledger.result(
        suite_hash,
        digest(source["transcripts.jsonl"]) if source.get("transcripts.jsonl") is not None else "",
        release_pins, len(cases), sum(len(c["assertions"]) for c in cases),
    )


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def _xml_text(value) -> str:
    return re.sub(r"[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]", "�", str(value))


def _html_report(result: dict) -> str:
    s = result["summary"]
    categories = []
    for group in dict.fromkeys(row["group"] for row in result["checks"]):
        rows = [row for row in result["checks"] if row["group"] == group]
        failures = sum(not row["passed"] for row in rows)
        parts = []
        for row in rows:
            kind = "good" if row["passed"] else "bad"
            parts.append('<tr class="{}"><td><span aria-label="{}">{}</span></td><td><code>{}</code></td><td>{}</td></tr>'.format(
                kind, "Pass" if row["passed"] else "Fail", "✓" if row["passed"] else "×",
                _escape(row["id"]), _escape(row["evidence"])))
        categories.append(
            '<details {}><summary><span>{}</span><strong>{} checks · {} failures</strong></summary>'
            '<div class="table-wrap"><table><thead><tr><th>Result</th><th>Check</th><th>Evidence</th></tr></thead><tbody>{}</tbody>'
            '</table></div></details>'.format("open" if failures else "", _escape(group), len(rows),
                                              failures, "".join(parts)))
    template = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; script-src 'none'; base-uri 'none'; form-action 'none'">
<title>Kite Proofroom · Evidence Audit</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101514;color:#eee9df;font:15px/1.6 ui-sans-serif,system-ui,sans-serif}
header{border-bottom:1px solid #39453d;padding:18px max(24px,calc((100vw - 1160px)/2));display:flex;align-items:center;justify-content:space-between;gap:20px}
.mark{font-size:18px;font-weight:850;letter-spacing:.1em}.tag{font:11px/1.4 ui-monospace,SFMono-Regular,monospace;letter-spacing:.12em;color:#aac3ad}
main{max-width:1160px;margin:auto;padding:70px 24px 100px}.eyebrow{font:12px ui-monospace,monospace;letter-spacing:.15em;color:#9ebca3}
h1{font-weight:700;letter-spacing:-.055em;font-size:clamp(42px,7.5vw,92px);line-height:1.03;margin:16px 0 24px}
h1 em{color:#b8dfbf;font-style:normal}.intro{max-width:680px;color:#c0c5ba;font-size:17px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin:50px 0;background:#39453d;gap:1px;border:1px solid #39453d}
.stat{background:#17201a;padding:23px 20px}.stat small{display:block;color:#b8c3b4;font:11px ui-monospace,monospace;letter-spacing:.09em}
.stat strong{display:block;font-size:clamp(28px,4vw,45px);line-height:1.3;font-weight:650}.bad-number{color:#ffaaa0}.good-number{color:#b8dfbf}
.meta{background:#1a221d;border:1px solid #39453d;padding:22px 24px;margin:20px 0 56px}
.meta p{margin:8px 0;color:#c2c9be}.meta code{overflow-wrap:anywhere;color:#eee9df}
.heading{display:flex;justify-content:space-between;gap:16px;align-items:end;border-bottom:1px solid #39453d;padding-bottom:12px;margin-bottom:14px}
h2{font-size:24px;letter-spacing:-.03em;margin:0}.footnote{color:#acb8aa;font-size:13px}
details{border-bottom:1px solid #39453d}summary{padding:21px 10px;display:flex;cursor:pointer;gap:14px;justify-content:space-between;align-items:center}
summary strong{color:#b2bfac;font:12px ui-monospace,monospace;font-weight:400}.table-wrap{overflow:auto}
table{border-collapse:collapse;width:100%;min-width:680px}th,td{padding:11px 10px;text-align:left;border-bottom:1px solid #29342d;vertical-align:top}
th{color:#9aa99b;font:11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.07em}td code{font:12px ui-monospace,monospace}
td:last-child{word-break:break-word;color:#c3c9bf}td:first-child{font-size:18px;color:#a6d6ad}.bad td:first-child{color:#ffaa9b}.bad{background:#2a1919}
footer{max-width:1160px;margin:auto;padding:35px 24px;border-top:1px solid #39453d;color:#a4b4a8;font-size:13px}
@media(max-width:700px){main{padding:44px 16px 70px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.heading{display:block}header{padding:16px}summary{align-items:start;flex-direction:column}}
</style></head><body><header><span class="mark">KITE / PROOFROOM</span><span class="tag">PASSPORT SKILLS · 1.2</span></header>
<main><p class="eyebrow">04 / RELEASE EVIDENCE AUDIT</p><h1>Trust the chain.<br><em>Check every link.</em></h1>
<p class="intro">Independent, offline reconstruction of the Kite Passport evaluation requests, 138 responses, literal grading,
recovery lineage and artifact checksums. A green result is evidence consistency, not a claim that a model performed transactions.</p>
<section class="stats"><div class="stat"><small>AUDIT CHECKS</small><strong>{total}</strong></div>
<div class="stat"><small>VERIFIED</small><strong class="good-number">{passed}</strong></div>
<div class="stat"><small>INTEGRITY FAILURES</small><strong class="{failed_class}">{failed}</strong></div>
<div class="stat"><small>OFFICIAL CASES</small><strong>{cases}</strong></div></section>
<div class="meta"><p><b>Result:</b> {verdict} · Release pins: {pinned}</p>
<p><b>Official suite:</b> <code>{suite}</code></p><p><b>Capture SHA-256:</b> <code>{capture}</code></p>
<p>File hashes can detect accidental or isolated changes, not a coordinated attack that rewrites both files and trust anchors.
External provider authenticity, account access, semantic correctness and on-chain execution are <b>not verified</b>.</p></div>
<div class="heading"><h2>Inspection ledger</h2><span class="footnote">Select a group to inspect each invariant</span></div>
{details}</main><footer>Independent community tooling · Deterministic local checks · No network, wallet or model calls.</footer></body></html>"""
    values = {
        "total": s["checks"], "passed": s["passed"], "failed": s["failed"],
        "cases": s["official_cases"],
        "failed_class": "good-number" if s["failed"] == 0 else "bad-number",
        "verdict": "ALL CHECKS PASSED" if s["failed"] == 0 else "FAILED — EVIDENCE IS NOT TRUSTWORTHY",
        "pinned": "enforced" if result["release_pins_enabled"] else "not enforced",
        "suite": _escape(result["suite_sha256"]),
        "capture": _escape(result["capture_sha256"]),
        "details": "".join(categories),
    }
    return re.sub(r"\{(total|passed|failed|cases|failed_class|verdict|pinned|suite|capture|details)\}",
                  lambda match: str(values[match.group(1)]), template)


def _junit(result: dict) -> bytes:
    s = result["summary"]
    root = ET.Element("testsuite", name="Kite Passport evidence provenance audit",
                      tests=str(s["checks"]), failures=str(s["failed"]), errors="0", skipped="0")
    props = ET.SubElement(root, "properties")
    ET.SubElement(props, "property", name="onchain_verified", value="false")
    ET.SubElement(props, "property", name="suite_sha256", value=result["suite_sha256"])
    ET.SubElement(props, "property", name="release_pins", value=str(result["release_pins_enabled"]).lower())
    for row in result["checks"]:
        node = ET.SubElement(root, "testcase", name=row["id"], classname="audit." + row["group"].replace(" ", "-"))
        if not row["passed"]:
            ET.SubElement(node, "failure", message="Evidence invariant failed").text = _xml_text(row["evidence"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_audit(out: Path, result: dict) -> None:
    s = result["summary"]
    md = ["# Kite Passport evidence audit", "",
          "**{}** · {} checks, {} passed, {} failed.".format(
              "PASS" if s["failed"] == 0 else "FAIL", s["checks"], s["passed"], s["failed"]),
          "", "Suite SHA-256: \`{}\`".format(result["suite_sha256"]),
          "", "Capture SHA-256: \`{}\`".format(result["capture_sha256"]),
          "", "External authenticity, on-chain activity and semantic correctness: **not verified**.",
          "", "| Category | Check | Result | Evidence |", "|---|---|---|---|"]
    for row in result["checks"]:
        def escape_cell(value: str) -> str:
            return html.escape(str(value), quote=True).replace("|", "&#124;").replace("\n", "<br>")
        md.append("| {} | {} | {} | {} |".format(
            escape_cell(row["group"]), escape_cell(row["id"]),
            "PASS" if row["passed"] else "FAIL", escape_cell(row["evidence"])))
    artifacts = {
        "audit.json": (json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode(),
        "audit.md": ("\n".join(md) + "\n").encode(),
        "junit.xml": _junit(result),
        "index.html": _html_report(result).encode(),
    }
    for name, data in artifacts.items():
        with (out / name).open("xb") as stream:
            stream.write(data)
    with (out / "checksums.json").open("x", encoding="utf-8") as stream:
        json.dump({name: digest(data) for name, data in artifacts.items()}, stream,
                  sort_keys=True, indent=2)
        stream.write("\n")
