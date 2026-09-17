"""Merge explicitly retried infrastructure errors; never cherry-pick scored responses."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kite_eval.core import InputError, canonical, digest, exit_status, grade, load_suite, load_transcripts
from kite_eval.report import write_report


def merge_records(original, retries):
    if not retries:
        raise InputError("Recovery requires at least one explicit retry")
    merged = dict(original)
    for cid, retry in retries.items():
        if cid not in original or original[cid]["status"] == "ok":
            raise InputError("Recovery may replace infrastructure errors only, never scored responses")
        if retry["status"] != "ok" or retry["kind"] != "agent" or original[cid]["kind"] != "agent":
            raise InputError("Recovery requires a successful real agent capture")
        for key in ("request_sha256", "adapter_config_sha256", "prompt_sha256"):
            if not original[cid].get(key) or original[cid][key] != retry.get(key):
                raise InputError("Recovery input or adapter changed: " + key)
        merged[cid] = retry
    return merged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--retry", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        cases, sha = load_suite(args.suite, True)
        original = load_transcripts(args.original, cases)
        retries = load_transcripts(args.retry, cases)
        records = merge_records(original, retries)
        args.out.mkdir(parents=True, exist_ok=False)
        with (args.out / "transcripts.jsonl").open("x", encoding="utf-8") as stream:
            for cid in sorted(records):
                stream.write(canonical(records[cid]).decode() + "\n")
        recovery = {"original_path": args.original.as_posix(), "original_sha256": digest(args.original.read_bytes()),
                    "retry_path": args.retry.as_posix(), "retry_sha256": digest(args.retry.read_bytes()),
                    "replacement_ids": sorted(retries), "policy": "infrastructure-errors-only; identical request and adapter",
                    "original_summary": grade(cases, original, sha)["summary"]}
        report = grade(cases, records, sha)
        report["generated_at"] = datetime.now(timezone.utc).isoformat()
        report["capture_sha256"] = digest((args.out / "transcripts.jsonl").read_bytes())
        report["recovery"] = recovery
        report["capture_note"] = "Error-recovered capture: explicit retries replaced infrastructure errors for case(s) " + ", ".join(map(str, sorted(retries))) + ". Original evidence is retained; no scored response was retried."
        with (args.out / "recovery.json").open("x", encoding="utf-8") as stream:
            json.dump(recovery, stream, indent=2); stream.write("\n")
        write_report(args.out, report)
        print(json.dumps(report["summary"], indent=2))
        return exit_status(report)
    except (InputError, OSError, UnicodeError) as exc:
        print("Recovery error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
