import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from kite_eval.__main__ import main
from kite_eval.compare import (compare_reports, comparison_exit, comparison_junit,
                               load_report, write_comparison)
from kite_eval.core import InputError, digest


def report(*, status=None, checks=None, review=None, response_hash="a" * 64,
           suite="c" * 64, case_id=1):
    checks = checks if checks is not None else [("alpha", True), ("beta", True)]
    status = status or ("pass" if all(passed for _, passed in checks) else "fail")
    return {
        "schema_version": 1,
        "suite_sha256": suite,
        "capture_sha256": "d" * 64,
        "summary": {"untrusted": "comparison derives its own summary"},
        "cases": [{
            "id": case_id,
            "status": status,
            "checks": [{"literal": literal, "passed": passed} for literal, passed in checks],
            "review": None if review is None else {"verdict": review},
            "transcript": {"response_sha256": response_hash},
        }],
    }


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_identical_reports_pass_strict_gate(self):
        result = compare_reports(report(), report())
        self.assertEqual(result["summary"]["regressions"], 0)
        self.assertEqual(result["summary"]["unchanged"], 1)
        self.assertEqual(comparison_exit(result), 0)
        self.assertEqual(ET.fromstring(comparison_junit(result)).attrib["failures"], "0")

    def test_any_lost_assertion_is_regression_even_with_a_gain(self):
        before = report(checks=[("alpha", True), ("beta", False)])
        after = report(checks=[("alpha", False), ("beta", True)])
        result = compare_reports(before, after)
        row = result["cases"][0]
        self.assertEqual(row["classification"], "regressed")
        self.assertEqual(row["lost_assertions"], ["alpha"])
        self.assertEqual(row["gained_assertions"], ["beta"])
        self.assertEqual(result["summary"]["assertion_regressions"], 1)
        self.assertEqual(comparison_exit(result), 1)

    def test_status_and_semantic_review_downgrades_fail(self):
        before = report(status="fail", checks=[("alpha", False), ("beta", True)], review="pass")
        after = report(status="error", checks=[("alpha", False), ("beta", False)], review=None)
        result = compare_reports(before, after)
        row = result["cases"][0]
        self.assertTrue(row["status_regression"])
        self.assertTrue(row["semantic_review_regression"])
        self.assertEqual(result["summary"]["regressions"], 1)

    def test_improvements_do_not_hide_or_invent_regressions(self):
        before = report(status="fail", checks=[("alpha", False), ("beta", True)], review=None)
        after = report(status="pass", checks=[("alpha", True), ("beta", True)], review="pass")
        result = compare_reports(before, after)
        self.assertEqual(result["cases"][0]["classification"], "improved")
        self.assertEqual(result["summary"]["assertion_improvements"], 1)
        self.assertEqual(result["summary"]["regressions"], 0)

    def test_response_change_is_visible_but_not_itself_a_regression(self):
        before = report(response_hash="a" * 64)
        after = report(response_hash="b" * 64)
        result = compare_reports(before, after)
        self.assertTrue(result["cases"][0]["response_changed"])
        self.assertEqual(result["summary"]["response_changed"], 1)
        self.assertEqual(result["summary"]["regressions"], 0)

    def test_refuses_incomparable_reports(self):
        variants = [
            (report(), report(suite="e" * 64)),
            (report(), report(case_id=2)),
            (report(), report(checks=[("alpha", True), ("gamma", True)])),
        ]
        for before, after in variants:
            with self.subTest(after=after), self.assertRaises(InputError):
                compare_reports(before, after)
        with self.assertRaises(InputError):
            compare_reports(report(), report(status="pass", checks=[("alpha", False), ("beta", True)]))

    def test_load_write_hashes_and_no_overwrite(self):
        source = self.root / "report.json"
        source.write_text(json.dumps(report()), encoding="utf-8")
        loaded = load_report(source)
        result = compare_reports(loaded, loaded)
        out = self.root / "out"
        out.mkdir()
        write_comparison(out, result)
        hashes = json.loads((out / "checksums.json").read_text())
        for name, sha in hashes.items():
            self.assertEqual(digest((out / name).read_bytes()), sha)
        ET.parse(out / "junit.xml")
        with self.assertRaises(FileExistsError):
            write_comparison(out, result)

    def test_comparison_html_escapes_assertion_text(self):
        hostile = "</td><script>alert(1)</script>"
        before = report(checks=[(hostile, True), ("beta", True)])
        after = report(checks=[(hostile, False), ("beta", True)])
        result = compare_reports(before, after)
        out = self.root / "escaped"
        out.mkdir()
        write_comparison(out, result)
        page = (out / "index.html").read_text()
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;/td&gt;&lt;script&gt;", page)

    def test_cli_compare_exit_codes(self):
        baseline = self.root / "baseline.json"
        candidate = self.root / "candidate.json"
        baseline.write_text(json.dumps(report()), encoding="utf-8")
        candidate.write_text(json.dumps(report()), encoding="utf-8")
        self.assertEqual(main(["compare", "--baseline", str(baseline), "--candidate", str(candidate),
                               "--out", str(self.root / "clean")]), 0)
        candidate.write_text(json.dumps(report(checks=[("alpha", False), ("beta", True)])), encoding="utf-8")
        self.assertEqual(main(["compare", "--baseline", str(baseline), "--candidate", str(candidate),
                               "--out", str(self.root / "regressed")]), 1)
        candidate.write_text("{}", encoding="utf-8")
        self.assertEqual(main(["compare", "--baseline", str(baseline), "--candidate", str(candidate),
                               "--out", str(self.root / "invalid")]), 2)


if __name__ == "__main__":
    unittest.main()
