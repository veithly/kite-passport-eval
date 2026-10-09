"""Adversarial and real-release verification for Proofroom's offline auditor."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from kite_eval.__main__ import main
from kite_eval.audit import RELEASE_PINS, audit_evidence, write_audit
from kite_eval.core import canonical, digest


PROJECT = Path(__file__).resolve().parents[1]
UPSTREAM = Path(os.environ.get("KITE_UPSTREAM", str(PROJECT.parent / "upstream/passport-skills")))
ADAPTER = PROJECT / "adapters/claude-safe.json"


def update_manifest(folder: Path, filename: str) -> None:
    manifest = folder / "checksums.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data[filename] = digest((folder / filename).read_bytes())
    manifest.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("live", "retry-135", "recovered"):
            shutil.copytree(PROJECT / "evidence" / name, self.root / name)

    def audit(self, pinned=False):
        return audit_evidence(
            UPSTREAM, ADAPTER, self.root / "recovered",
            self.root / "live", self.root / "retry-135", pinned,
        )

    def fail_ids(self, result):
        return {row["id"] for row in result["checks"] if not row["passed"]}

    def test_real_138_case_release_all_pins_and_644_invariants(self):
        result = self.audit(True)
        self.assertEqual(result["summary"], {
            "checks": 644, "passed": 644, "failed": 0,
            "official_cases": 138, "literal_assertions": 424,
        })
        self.assertEqual(result["capture_sha256"], RELEASE_PINS["recovered"])
        self.assertFalse(result["onchain_verified"])
        self.assertEqual(len({(row["group"], row["id"]) for row in result["checks"]}), 644)

    def test_replay_identical_audit_is_deterministic(self):
        first = self.audit(True)
        second = self.audit(True)
        self.assertEqual(first, second)
        for index, result in enumerate((first, second)):
            out = self.root / "audit-{}".format(index)
            out.mkdir()
            write_audit(out, result)
        for name in ("audit.json", "audit.md", "junit.xml", "index.html", "checksums.json"):
            self.assertEqual((self.root / "audit-0" / name).read_bytes(),
                             (self.root / "audit-1" / name).read_bytes())

    def test_mutated_response_hash_detected_even_with_rewritten_checksums(self):
        bundle = self.root / "recovered"
        path = bundle / "transcripts.jsonl"
        lines = [json.loads(x) for x in path.read_text().splitlines()]
        lines[0]["response"] += "\nforged response"
        lines[0]["response_sha256"] = digest(lines[0]["response"].encode())
        path.write_bytes(b"".join(canonical(x) + b"\n" for x in lines))
        update_manifest(bundle, "transcripts.jsonl")
        result = self.audit(True)
        failed = self.fail_ids(result)
        self.assertIn("recovered", failed)  # immutable release pin
        self.assertIn("every-case", failed)  # published report still contains original transcript
        self.assertIn("canonical-journal", failed)  # error-only original/retry cannot create the forgery

    def test_forged_request_hash_rejected_by_independent_skill_reconstruction(self):
        bundle = self.root / "recovered"
        journal = bundle / "transcripts.jsonl"
        rows = [json.loads(x) for x in journal.read_text().splitlines()]
        rows[0]["request_sha256"] = "f" * 64
        journal.write_bytes(b"".join(canonical(row) + b"\n" for row in rows))
        update_manifest(bundle, "transcripts.jsonl")
        result = self.audit()
        self.assertIn("case.001.request", self.fail_ids(result))
        self.assertIn("exact-records", self.fail_ids(result))

    def test_changed_source_context_hash_rejected(self):
        bundle = self.root / "recovered"
        journal = bundle / "transcripts.jsonl"
        rows = [json.loads(x) for x in journal.read_text().splitlines()]
        rows[0]["documents"][0]["sha256"] = "0" * 64
        journal.write_bytes(b"".join(canonical(row) + b"\n" for row in rows))
        update_manifest(bundle, "transcripts.jsonl")
        self.assertIn("case.001.documents", self.fail_ids(self.audit()))

    def test_report_summary_cannot_be_resigned_using_checksum_manifest(self):
        bundle = self.root / "recovered"
        path = bundle / "report.json"
        report = json.loads(path.read_text())
        report["summary"]["pass"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        update_manifest(bundle, "report.json")
        result = self.audit(True)
        self.assertIn("summary", self.fail_ids(result))
        self.assertIn("report", self.fail_ids(result))  # release hash still pinned

    def test_missing_and_symlink_artifacts_fail_closed(self):
        bundle = self.root / "retry-135"
        report = bundle / "report.md"
        report.unlink()
        report.symlink_to(self.root / "live" / "report.md")
        result = self.audit()
        self.assertIn("retry.report.md", self.fail_ids(result))
        self.assertGreater(result["summary"]["failed"], 0)

    def test_malformed_checksum_json_and_traversal_keys(self):
        manifest = self.root / "recovered" / "checksums.json"
        manifest.write_text('{"report.json":"a","report.json":"b"}', encoding="utf-8")
        result = self.audit()
        self.assertIn("recovered.checksums.decoded-json", self.fail_ids(result))
        manifest.write_text(json.dumps({"../outside.json": "a" * 64}), encoding="utf-8")
        result = self.audit()
        self.assertIn("recovered.checksum-schema", self.fail_ids(result))

    def test_old_successful_response_is_never_eligible_for_replacement(self):
        bundle = self.root / "retry-135"
        journal = bundle / "transcripts.jsonl"
        live_rows = [json.loads(x) for x in (self.root / "live" / "transcripts.jsonl").read_text().splitlines()]
        first_success = next(row for row in live_rows if row["status"] == "ok")
        journal.write_bytes(canonical(first_success) + b"\n")
        update_manifest(bundle, "transcripts.jsonl")
        result = self.audit()
        self.assertIn("anti-cherry-pick", self.fail_ids(result))

    def test_disabled_tools_claim_cannot_be_silently_changed(self):
        bundle = self.root / "recovered"
        journal = bundle / "transcripts.jsonl"
        rows = [json.loads(x) for x in journal.read_text().splitlines()]
        rows[0]["metadata"]["tools_enabled"] = True
        journal.write_bytes(b"".join(canonical(row) + b"\n" for row in rows))
        update_manifest(bundle, "transcripts.jsonl")
        self.assertIn("case.001.capture", self.fail_ids(self.audit()))

    def test_export_reports_xml_checksums_and_refuses_overwrite(self):
        result = self.audit(True)
        out = self.root / "report-out"
        out.mkdir()
        write_audit(out, result)
        hashes = json.loads((out / "checksums.json").read_text())
        for name, sha in hashes.items():
            self.assertEqual(digest((out / name).read_bytes()), sha)
        xml = ET.parse(out / "junit.xml").getroot()
        self.assertEqual((xml.attrib["tests"], xml.attrib["failures"]), ("644", "0"))
        page = (out / "index.html").read_text()
        self.assertIn("Trust the chain.", page)
        self.assertNotIn('<script src=', page)
        self.assertIn("script-src 'none'", page)
        with self.assertRaises(FileExistsError):
            write_audit(out, result)

    def test_tampering_produces_machine_readable_failed_junit(self):
        result = self.audit(True)
        tampered = copy.deepcopy(result)
        tampered["checks"][0]["passed"] = False
        tampered["checks"][0]["evidence"] = '<script>alert(1)</script>\x01'
        tampered["summary"]["failed"] = 1
        tampered["summary"]["passed"] -= 1
        out = self.root / "bad-output"
        out.mkdir()
        write_audit(out, tampered)
        self.assertEqual(ET.parse(out / "junit.xml").getroot().attrib["failures"], "1")
        page = (out / "index.html").read_text()
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_cli_audit_success_and_failure_status(self):
        base = ["audit", "--upstream", str(UPSTREAM), "--adapter", str(ADAPTER),
                "--recovered", str(self.root / "recovered"),
                "--original", str(self.root / "live"),
                "--retry", str(self.root / "retry-135"), "--release-pins"]
        self.assertEqual(main(base + ["--out", str(self.root / "cli-good")]), 0)
        with (self.root / "recovered" / "report.md").open("ab") as stream:
            stream.write(b"\ntamper")
        self.assertEqual(main(base + ["--out", str(self.root / "cli-bad")]), 1)
        self.assertGreater(json.loads((self.root / "cli-bad" / "audit.json").read_text())["summary"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
