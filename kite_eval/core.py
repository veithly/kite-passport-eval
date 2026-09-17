"""Standard-library evaluation primitives. Literal checks are not semantic proof."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import tempfile
import time
from typing import Any

UPSTREAM_COMMIT = "1ff773981566ac1755ccf23e98983cd76c81bf08"
SUITE_SHA256 = "ba8af9651ab014242790b39491dcf9137d6d3323cc8c0f94698099c7535b2f5b"
MAX_FILE = 32 * 1024 * 1024
MAX_RESPONSE = 1024 * 1024
GROUPS = {
    "activity": [1, 2, 3],
    "authenticate-user": [4, 5, 6, 24, 25, 26],
    "request-session": [7, 8, 14, 15, 16, 31, 32, 44, 45, 46, 51, 52],
    "kite-discovery": [9, 10, 11, 38, 39, 40, 49],
    "manage-agents": [12, 13, 29, 30],
    "shopping": [17, 18, 19, 33, 34, 35, 36, 37, 48, 50],
    "wallet-send": [20, 21, 27, 28, 56],
    "x402-execute": [22, 23, 41, 42, 43, 47],
    "attach-session": [53, 54, 55],
    "buyer-agent-setup": [57, 58, 59, 60],
    "buyer-find-seller": [67, 68, 69, 70, 71],
    "buyer-purchase": [78, 79, 80, 81, 82, 83],
    "seller-agent-setup": [61, 62, 63, 64, 66],
    "seller-fulfill": [65, 72, 73, 74, 75, 77],
    "upgrade-passport": [84, 85, 86, 87, 88],
    "kite-passport": [89, 90, 91, 92],
    "seller-serve": [76, 93, 94, 95, 96, 97],
    "kite-seller": [98, 99, 100, 101, 109, 110],
    "seller-onboarding": list(range(102, 109)) + list(range(111, 139)),
}
SKILL_BY_ID = {case_id: slug for slug, ids in GROUPS.items() for case_id in ids}


class InputError(ValueError):
    """A malformed or inconsistent artifact, never a silently skipped case."""


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(text: str) -> Any:
    def invalid(value: str) -> None:
        raise InputError("Non-finite JSON value: " + value)
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid)
    except (ValueError, RecursionError) as exc:
        raise InputError("Invalid JSON: " + str(exc)) from exc


def read_bytes(path: Path, limit: int = MAX_FILE) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise InputError("File exceeds size limit: " + str(path))
    return data


def load_suite(path: Path, pinned: bool = False) -> tuple:
    data = read_bytes(path, 2 * 1024 * 1024)
    if pinned and digest(data) != SUITE_SHA256:
        raise InputError("Official suite SHA-256 mismatch; refusing drift")
    cases = decode(data.decode("utf-8"))
    if not isinstance(cases, list) or not cases or len(cases) > 10000:
        raise InputError("Suite must be a non-empty array, at most 10000 cases")
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "prompt", "expected_output", "assertions"}:
            raise InputError("Each case must contain exactly id, prompt, expected_output, assertions")
        cid = case["id"]
        if type(cid) is not int or cid <= 0 or cid in seen:
            raise InputError("Case IDs must be unique positive integers")
        seen.add(cid)
        for field in ("prompt", "expected_output"):
            if not isinstance(case[field], str) or not case[field].strip() or len(case[field]) > 32000:
                raise InputError("Invalid " + field + " in case " + str(cid))
        checks = case["assertions"]
        if not isinstance(checks, list) or not checks or len(checks) > 100:
            raise InputError("Case assertions must be a non-empty array, at most 100")
        if any(not isinstance(a, str) or not a.strip() or len(a) > 4096 for a in checks):
            raise InputError("Assertions must be nonblank literal strings")
        if len(set(checks)) != len(checks):
            raise InputError("Duplicate assertion in case " + str(cid))
    return cases, digest(data)


def verify_upstream(root: Path) -> None:
    """Require the advertised commit and unmodified tracked source files."""
    for args, expected in [(["rev-parse", "HEAD"], UPSTREAM_COMMIT),
                           (["status", "--porcelain", "--untracked-files=no"], "")]:
        result = subprocess.run(["git", "-C", str(root)] + args, capture_output=True,
                                text=True, timeout=15, check=True)
        if result.stdout.strip() != expected:
            raise InputError("Upstream checkout is not the clean pinned revision")


def context_for(root: Path, slug: str) -> list:
    root = root.resolve()
    folder = root / slug
    paths = [folder / "SKILL.md"] + sorted((folder / "references").rglob("*.md"))
    common = root / "docs" / "reference.md"
    if common.is_file():
        paths.append(common)
    documents, total = [], 0
    for path in paths:
        if path.is_symlink() or root not in path.resolve().parents:
            raise InputError("Context file escapes upstream: " + str(path))
        data = read_bytes(path, 512 * 1024)
        total += len(data)
        if total > 1024 * 1024:
            raise InputError("Skill context exceeds 1 MiB; never silently truncate")
        documents.append({"path": path.relative_to(root).as_posix(),
                          "sha256": digest(data), "text": data.decode("utf-8")})
    return documents


def request_for(case: dict, documents: list) -> dict:
    # Intentionally whitelist: expected_output and assertions never reach the adapter.
    return {"schema_version": 1, "id": case["id"], "prompt": case["prompt"],
            "skill": SKILL_BY_ID.get(case["id"], "custom"), "documents": documents,
            "mode": "text-only-no-side-effects"}


def invoke(argv: list, payload: dict, timeout: float, max_output: int) -> dict:
    """POSIX process-group deadline and combined stdout/stderr limit; shell=False.

    This controls resource use, NOT filesystem/network permissions. Only run trusted
    adapters. The supplied Claude adapter disables tools independently.
    """
    if os.name != "posix":
        raise InputError("Live adapters require POSIX; replay works on all platforms")
    if not argv or any(not isinstance(x, str) or "\x00" in x for x in argv):
        raise InputError("Adapter argv must be a non-empty string array")
    if not 0 < timeout <= 600 or not 128 <= max_output <= 16 * 1024 * 1024:
        raise InputError("Invalid process limits")
    start = time.monotonic()
    out, err = bytearray(), bytearray()
    status, code, process = "ok", None, None
    with tempfile.TemporaryFile() as source, selectors.DefaultSelector() as selector:
        source.write(canonical(payload)); source.seek(0)
        try:
            process = subprocess.Popen(argv, stdin=source, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True)
            selector.register(process.stdout, selectors.EVENT_READ, out)
            selector.register(process.stderr, selectors.EVENT_READ, err)
            while selector.get_map():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:
                    status = "timeout"; break
                for key, _ in selector.select(min(remaining, 0.1)):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                    else:
                        available = max_output - len(out) - len(err)
                        key.data.extend(chunk[:max(0, available)])
                        if len(chunk) > available:
                            status = "output_limit"; break
                if status != "ok":
                    break
            if status == "ok":
                try:
                    code = process.wait(timeout=max(0.01, timeout - (time.monotonic() - start)))
                    if code != 0:
                        status = "adapter_error"
                except subprocess.TimeoutExpired:
                    status = "timeout"
        except OSError:
            status = "spawn_error"
        finally:
            if process is not None:
                # Kill our group even if a parent exited while a descendant kept pipes open.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                process.stdout.close(); process.stderr.close()
    return {"status": status, "stdout": bytes(out), "stderr_sha256": digest(bytes(err)),
            "exit_code": code, "duration_ms": round((time.monotonic() - start) * 1000)}


def capture(case: dict, documents: list, adapter: dict, timeout: float, max_output: int) -> dict:
    request = request_for(case, documents)
    result = invoke(adapter["argv"], request, timeout, max_output)
    raw = result.pop("stdout")
    response, metadata = "", {}
    if result["status"] == "ok":
        try:
            envelope = decode(raw.decode("utf-8"))
            if not isinstance(envelope, dict) or not isinstance(envelope.get("response"), str):
                raise InputError("Adapter must return a JSON object with string response")
            response = envelope["response"]
            if len(response.encode("utf-8")) > MAX_RESPONSE:
                raise InputError("Response too large")
            # Metadata is data only; limit it and never render it as HTML.
            metadata = envelope.get("metadata", {})
            if not isinstance(metadata, dict) or len(canonical(metadata)) > 16384:
                raise InputError("Invalid adapter metadata")
        except (ValueError, UnicodeError, TypeError):
            result["status"] = "protocol_error"
            response, metadata = "", {}
    return {"schema_version": 1, "id": case["id"], "kind": "agent",
            "prompt_sha256": digest(case["prompt"].encode("utf-8")),
            "request_sha256": digest(canonical(request)), "response": response,
            "response_sha256": digest(response.encode("utf-8")),
            "adapter": adapter["name"], "adapter_config_sha256": digest(canonical(adapter)),
            "documents": [{"path": d["path"], "sha256": d["sha256"]} for d in documents],
            "metadata": metadata, **result}


def load_transcripts(path: Path, cases: list) -> dict:
    allowed = {c["id"]: c for c in cases}
    records = {}
    for line in read_bytes(path).decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = decode(line)
        if not isinstance(row, dict) or type(row.get("id")) is not int:
            raise InputError("Transcript must contain an integer id")
        cid = row["id"]
        if cid not in allowed or cid in records:
            raise InputError("Unknown or duplicate transcript id: " + str(cid))
        if type(row.get("schema_version")) is not int or row["schema_version"] != 1 or row.get("kind") not in ("agent", "fixture"):
            raise InputError("Transcript schema_version=1 and explicit kind required")
        if row.get("prompt_sha256") != digest(allowed[cid]["prompt"].encode("utf-8")):
            raise InputError("Transcript prompt hash mismatch: " + str(cid))
        response = row.get("response")
        if not isinstance(response, str) or len(response.encode("utf-8")) > MAX_RESPONSE:
            raise InputError("Transcript response must be a bounded string")
        if row.get("response_sha256") != digest(response.encode("utf-8")):
            raise InputError("Transcript response hash mismatch: " + str(cid))
        if row.get("status") not in ("ok", "timeout", "adapter_error", "spawn_error", "output_limit", "protocol_error"):
            raise InputError("Unknown transcript status")
        duration = row.get("duration_ms", 0)
        if type(duration) not in (int, float) or not 0 <= duration <= 600000:
            raise InputError("Invalid transcript duration_ms")
        if "adapter" in row and (not isinstance(row["adapter"], str) or len(row["adapter"]) > 256):
            raise InputError("Invalid transcript adapter label")
        records[cid] = row
    return records


def load_reviews(path: Path, records: dict) -> dict:
    rows = decode(read_bytes(path).decode("utf-8"))
    if not isinstance(rows, list):
        raise InputError("Reviews must be an array")
    reviews = {}
    for row in rows:
        if not isinstance(row, dict) or type(row.get("id")) is not int:
            raise InputError("Invalid review id")
        cid = row["id"]
        if cid in reviews or cid not in records:
            raise InputError("Unknown or duplicate review")
        if row.get("verdict") not in ("pass", "fail"):
            raise InputError("Review verdict must be pass or fail")
        for field in ("reviewer", "rationale", "quote"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise InputError("Review requires reviewer, rationale and evidence quote")
        record = records[cid]
        if record["status"] != "ok" or row.get("response_sha256") != record["response_sha256"]:
            raise InputError("Review is not bound to a successful current transcript")
        if row["quote"] not in record["response"]:
            raise InputError("Review quote does not exist in the transcript")
        reviews[cid] = row
    return reviews


def grade(cases: list, records: dict, suite_hash: str, reviews: dict = None) -> dict:
    reviews = reviews or {}
    results = []
    for case in cases:
        cid = case["id"]
        record = records.get(cid)
        text = record["response"] if record else ""
        usable = bool(record and record["status"] == "ok")
        checks = []
        for assertion in case["assertions"]:
            offset = text.find(assertion) if usable else -1
            checks.append({"literal": assertion, "passed": offset >= 0,
                           "offset": offset if offset >= 0 else None,
                           "line": text.count("\n", 0, offset) + 1 if offset >= 0 else None})
        status = "missing" if record is None else "error" if not usable else (
            "pass" if all(c["passed"] for c in checks) else "fail")
        results.append({**case, "skill": SKILL_BY_ID.get(cid, "custom"), "status": status,
                        "checks": checks, "transcript": record, "review": reviews.get(cid)})
    counts = {key: sum(c["status"] == key for c in results) for key in ("pass", "fail", "error", "missing")}
    kinds = sorted({r["kind"] for r in records.values()})
    return {"schema_version": 1, "suite_sha256": suite_hash,
            "scope": "literal-transcript-checks", "onchain_verified": False,
            "provenance_kind": "+".join(kinds) if kinds else "none",
            "summary": {"total": len(cases), **counts,
                        "recorded": len(records), "complete": len(records) == len(cases),
                        "assertions": sum(len(c["checks"]) for c in results),
                        "assertions_passed": sum(a["passed"] for c in results for a in c["checks"]),
                        "reviewed": len(reviews),
                        "review_failed": sum(r["verdict"] == "fail" for r in reviews.values())},
            "cases": results}


def exit_status(report: dict, require_review: bool = False) -> int:
    s = report["summary"]
    return int(bool(s["fail"] or s["error"] or s["missing"] or s["review_failed"] or
                    (require_review and s["reviewed"] != s["total"])))
