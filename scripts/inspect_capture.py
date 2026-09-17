"""Emit a compact public evidence inventory and conservative secret-pattern check."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kite_eval.core import digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    models, patterns = Counter(), []
    warnings = []
    signatures = {"private-key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                  "github-token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
                  "provider-key": r"\bsk-(?:ant-)?[A-Za-z0-9_-]{40,}\b",
                  "local-user-path": r"/Users/[^/\s]+/"}
    for case in report["cases"]:
        record = case["transcript"] or {}
        models.update(record.get("metadata", {}).get("model_usage", {}).keys())
        for label, pattern in signatures.items():
            if re.search(pattern, record.get("response", "")):
                warnings.append({"id": case["id"], "pattern": label})
        missing = [a["literal"] for a in case["checks"] if not a["passed"]]
        if missing:
            patterns.append({"id": case["id"], "skill": case["skill"], "status": case["status"], "missing_literals": missing})
    summary = {"summary": report["summary"], "models": dict(models),
               "reported_cost_usd": round(sum((c["transcript"] or {}).get("metadata", {}).get("cost_usd", 0) or 0 for c in report["cases"]), 6),
               "secret_pattern_warnings": warnings,
               "privacy_note": "Pattern scan only; not a guarantee of absence of sensitive information.",
               "adapter_sha256": digest(Path("adapters/claude_safe.py").read_bytes()),
               "source_report_sha256": digest(args.report.read_bytes()),
               "failures": patterns}
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2); stream.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
