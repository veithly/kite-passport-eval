"""CLI entry point; complete evidence is written even when checks fail."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import subprocess
import sys

from . import __version__
from .core import (GROUPS, SKILL_BY_ID, UPSTREAM_COMMIT, InputError, canonical, capture,
                   context_for, decode, digest, exit_status, grade, load_reviews,
                   load_suite, load_transcripts, read_bytes, verify_upstream)
from .report import write_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Kite Passport Eval Runner — evidence, not guesses")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate unchanged upstream case format")
    validate.add_argument("--suite", type=Path, required=True)
    validate.add_argument("--pinned", action="store_true")
    replay = sub.add_parser("replay", help="Grade captured transcripts, never invoke an agent")
    replay.add_argument("--suite", type=Path, required=True)
    replay.add_argument("--transcripts", type=Path, required=True)
    replay.add_argument("--pinned", action="store_true")
    run = sub.add_parser("run", help="Run every selected prompt through a trusted JSON adapter")
    run.add_argument("--upstream", type=Path, required=True)
    run.add_argument("--adapter", type=Path, required=True)
    run.add_argument("--jobs", type=int, choices=range(1, 9), default=2)
    run.add_argument("--timeout", type=float, default=120)
    run.add_argument("--max-output", type=int, default=1048576)
    run.add_argument("--ids", help="Explicit comma-separated pilot subset; report will mark partial coverage")
    for command in (replay, run):
        command.add_argument("--out", type=Path, required=True, help="New directory; never overwrite a run")
        command.add_argument("--reviews", type=Path)
        command.add_argument("--require-review", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            cases, sha = load_suite(args.suite, args.pinned)
            print(json.dumps({"cases": len(cases), "assertions": sum(len(c["assertions"]) for c in cases),
                              "sha256": sha, "pinned": args.pinned}))
            return 0
        if args.command == "replay":
            cases, sha = load_suite(args.suite, args.pinned)
            records = load_transcripts(args.transcripts, cases)
            reviews = load_reviews(args.reviews, records) if args.reviews else {}
            report = grade(cases, records, sha, reviews)
            report["capture_sha256"] = digest(read_bytes(args.transcripts))
            args.out.mkdir(parents=True, exist_ok=False)
            (args.out / "transcripts.jsonl").write_bytes(read_bytes(args.transcripts))
        else:
            if not 0 < args.timeout <= 600 or not 128 <= args.max_output <= 16777216:
                raise InputError("Timeout must be (0,600]; output limit [128,16777216]")
            verify_upstream(args.upstream)
            cases, sha = load_suite(args.upstream / "evals/evals.json", True)
            selected = cases
            if args.ids:
                try:
                    ids = [int(i) for i in args.ids.split(",")]
                except ValueError as exc:
                    raise InputError("--ids must be comma-separated integers") from exc
                if len(ids) != len(set(ids)) or not set(ids) <= {c["id"] for c in cases}:
                    raise InputError("Unknown or duplicate --ids value")
                selected = [c for c in cases if c["id"] in ids]
            adapter = decode(read_bytes(args.adapter, 32768).decode("utf-8"))
            if not isinstance(adapter, dict) or set(adapter) != {"name", "argv"}:
                raise InputError("Adapter config requires exactly name and argv")
            if not isinstance(adapter["name"], str) or not adapter["name"].strip():
                raise InputError("Adapter name is required")
            if not isinstance(adapter["argv"], list) or not adapter["argv"] or any(
                    not isinstance(v, str) or "\x00" in v for v in adapter["argv"]):
                raise InputError("Adapter argv must be a nonempty string array, never a shell string")
            contexts = {slug: context_for(args.upstream, slug) for slug in
                        {SKILL_BY_ID[c["id"]] for c in selected}}
            args.out.mkdir(parents=True, exist_ok=False)
            records = {}
            # A journal preserves completed calls on interruption; replay it, never silently pay twice.
            with (args.out / "transcripts.jsonl").open("x", encoding="utf-8") as journal:
                with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                    futures = {pool.submit(capture, c, contexts[SKILL_BY_ID[c["id"]]], adapter,
                                           args.timeout, args.max_output): c["id"] for c in selected}
                    for future in as_completed(futures):
                        record = future.result()
                        record["captured_at"] = datetime.now(timezone.utc).isoformat()
                        records[record["id"]] = record
                        journal.write(canonical(record).decode("utf-8") + "\n"); journal.flush()
                        print("case {}: {} ({}/{})".format(record["id"], record["status"],
                              len(records), len(selected)), file=sys.stderr, flush=True)
            reviews = load_reviews(args.reviews, records) if args.reviews else {}
            # The denominator is ALWAYS the whole suite, including an explicit pilot subset.
            report = grade(cases, records, sha, reviews)
            report["upstream_commit"] = UPSTREAM_COMMIT
            report["selected_ids"] = [c["id"] for c in selected]
            report["capture_sha256"] = digest(read_bytes(args.out / "transcripts.jsonl"))
        report["require_review"] = args.require_review
        report["runner_version"] = __version__
        report["generated_at"] = datetime.now(timezone.utc).isoformat()
        report["environment"] = {"python": sys.version.split()[0], "platform": sys.platform}
        write_report(args.out, report)
        print(json.dumps(report["summary"], sort_keys=True))
        print("Report: " + str(args.out / "index.html"))
        return exit_status(report, args.require_review)
    except (InputError, OSError, UnicodeError, subprocess.SubprocessError) as exc:
        print("Input/infrastructure error: " + str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted. Preserve transcripts.jsonl and use replay to account for missing cases.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
