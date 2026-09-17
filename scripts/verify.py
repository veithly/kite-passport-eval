"""Reproducible release checks: full synthetic suite, documented failures, live replay.

Synthetic positive strings and reconstructed failures are ONLY harness tests.
They are never labeled as live agent results or used as a model performance score.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kite_eval.core import canonical, digest, exit_status, grade, load_suite, load_transcripts


def fixture(case, response):
    return {"schema_version": 1, "id": case["id"], "kind": "fixture", "status": "ok",
            "prompt_sha256": digest(case["prompt"].encode()), "response": response,
            "response_sha256": digest(response.encode()), "adapter": "documented-regression-fixture"}


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")


def write_jsonl(path, records):
    with path.open("x", encoding="utf-8") as stream:
        for row in records:
            stream.write(canonical(row).decode() + "\n")


def replay(suite, transcripts, out, expected_exit, reviews=None):
    command = [sys.executable, "-m", "kite_eval", "replay", "--suite", str(suite),
               "--transcripts", str(transcripts), "--out", str(out)]
    if reviews:
        command += ["--reviews", str(reviews)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != expected_exit:
        raise AssertionError("Replay exit {} != {}: {} {}".format(result.returncode, expected_exit, result.stdout, result.stderr))
    return json.loads((out / "report.json").read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="New output directory")
    parser.add_argument("--live", type=Path, default=Path("evidence/recovered/transcripts.jsonl"))
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    if args.require_live and not args.live.is_file():
        parser.error("Release verification requires the live capture file")
    os.environ["KITE_UPSTREAM"] = str(args.upstream)
    args.out.mkdir(parents=True, exist_ok=False)
    tests = unittest.defaultTestLoader.discover("tests")
    with (args.out / "unittest.log").open("x", encoding="utf-8") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    if not result.wasSuccessful():
        print((args.out / "unittest.log").read_text())
        return 1
    suite_path = args.upstream / "evals/evals.json"
    cases, sha = load_suite(suite_path, True)
    positives = [fixture(c, "\n".join(c["assertions"])) for c in cases]
    positive_path = args.out / "synthetic-positive.jsonl"
    write_jsonl(positive_path, positives)
    positive_report = replay(suite_path, positive_path, args.out / "synthetic-positive", 0)
    assert positive_report["summary"]["pass"] == 138
    assert positive_report["provenance_kind"] == "fixture"
    # These examples reconstruct the obsolete syntax documented in upstream evals/README.md.
    # They are NOT falsely presented as historical captured agent conversations.
    responses = {
        4: "kpass login init --email <EMAIL> --output json --no-interactive",
        9: "ksearch services list --query weather --output json",
        31: "kpass session status --request-id <REQUEST_ID> --wait --output json",
        76: "kagent listen --forward ./handler.sh --output json",
    }
    negative_cases = [c for c in cases if c["id"] in responses]
    negatives = [fixture(c, responses[c["id"]]) for c in negative_cases]
    negative_suite = args.out / "known-failures-suite.json"
    negative_path = args.out / "known-failures.jsonl"
    write_json(negative_suite, negative_cases)
    write_jsonl(negative_path, negatives)
    row31 = next(r for r in negatives if r["id"] == 31)
    reviews = [{"id": 31, "response_sha256": row31["response_sha256"], "verdict": "fail",
                "reviewer": "documented fixture expectation (not a live audit)", "quote": "--wait",
                "rationale": "The upstream case requires one status check without --wait after explicit user approval. This deliberately reconstructed stale command passes positive literals but violates expected behavior."}]
    reviews_path = args.out / "known-failure-reviews.json"
    write_json(reviews_path, reviews)
    negative_report = replay(negative_suite, negative_path, args.out / "known-failures", 1, reviews_path)
    assert {c["id"] for c in negative_report["cases"] if c["status"] == "fail"} == {4, 9, 76}
    assert negative_report["summary"]["review_failed"] == 1
    assert next(c for c in negative_report["cases"] if c["id"] == 31)["status"] == "pass"
    summary = {"generated_at": datetime.now(timezone.utc).isoformat(), "suite_sha256": sha,
               "unit_tests": result.testsRun, "unit_failures": len(result.failures), "unit_errors": len(result.errors),
               "unit_skips": len(result.skipped), "official_cases": 138, "assertion_deletion_mutants": 424,
               "synthetic_positive_summary": positive_report["summary"],
               "known_failure_summary": negative_report["summary"],
               "known_literal_failure_ids": [4, 9, 76], "known_semantic_blind_spot_id": 31}
    if args.live.is_file():
        records = load_transcripts(args.live, cases)
        expected = grade(cases, records, sha)
        if len(records) != 138 or any(r["kind"] != "agent" or r["status"] != "ok" for r in records.values()):
            raise AssertionError("Release requires all 138 actual agent captures, with no infrastructure errors")
        live_report = replay(suite_path, args.live, args.out / "live-replay", exit_status(expected))
        assert live_report["summary"] == expected["summary"]
        # A broken grader cannot turn the real failures green unnoticed.
        baseline = args.live.parent / "report.json"
        if baseline.is_file():
            previous = json.loads(baseline.read_text())
            assert [(c["id"], c["checks"], c["status"]) for c in live_report["cases"]] == [
                    (c["id"], c["checks"], c["status"]) for c in previous["cases"]]
        summary["live_replay_summary"] = live_report["summary"]
        summary["live_capture_sha256"] = digest(args.live.read_bytes())
        summary["reported_model_cost_usd"] = round(sum(r.get("metadata", {}).get("cost_usd", 0) or 0 for r in records.values()), 6)
    write_json(args.out / "verification.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
