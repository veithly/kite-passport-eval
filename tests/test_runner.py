"""No network, model credentials or wallet required. Run: python -m unittest discover -s tests -v"""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from kite_eval.core import (GROUPS, SKILL_BY_ID, SUITE_SHA256, InputError, canonical, capture,
                            context_for, decode, digest, exit_status, grade, invoke,
                            load_reviews, load_suite, load_transcripts, request_for)
from kite_eval.__main__ import main
from kite_eval.report import junit, render, write_report

CASE = {"id": 1, "prompt": "Show my activity", "expected_output": "Display a JSON card",
        "assertions": ["kpass activity", "--output json", "━━━"]}


def record(case=CASE, response="kpass activity --output json\n━━━", **kwargs):
    return {"schema_version": 1, "id": case["id"], "kind": "fixture", "status": "ok",
            "prompt_sha256": digest(case["prompt"].encode()), "response": response,
            "response_sha256": digest(response.encode()), **kwargs}


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.suite = self.root / "suite.json"
        self.suite.write_text(json.dumps([CASE]), encoding="utf-8")
        self.transcripts = self.root / "transcripts.jsonl"

    def write_records(self, rows):
        self.transcripts.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return load_transcripts(self.transcripts, [CASE])

    def test_suite_round_trip(self):
        cases, sha = load_suite(self.suite)
        self.assertEqual(cases, [CASE])
        self.assertEqual(sha, digest(self.suite.read_bytes()))

    def test_reject_pinned_drift(self):
        with self.assertRaises(InputError):
            load_suite(self.suite, pinned=True)

    def test_invalid_suite_shapes(self):
        variants = [[], {}, [None], [CASE, CASE], [{**CASE, "id": True}], [{**CASE, "id": 0}],
                    [{**CASE, "prompt": " "}], [{**CASE, "expected_output": 1}],
                    [{**CASE, "assertions": []}], [{**CASE, "assertions": [" "]}],
                    [{**CASE, "assertions": [1]}], [{**CASE, "assertions": ["x", "x"]}],
                    [{**CASE, "surprise": "unrecognized"}]]
        for value in variants:
            with self.subTest(value=value):
                self.suite.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(InputError):
                    load_suite(self.suite)

    def test_nonfinite_duplicate_and_malformed_json(self):
        for value in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{broken']:
            with self.subTest(value=value), self.assertRaises(InputError):
                decode(value)

    def test_input_size_is_bounded(self):
        self.suite.write_bytes(b" " * (2 * 1024 * 1024 + 1))
        with self.assertRaises(InputError):
            load_suite(self.suite)

    def test_no_answer_key_in_request(self):
        case = {**CASE, "expected_output": "SECRET_ORACLE", "assertions": ["NEVER_LEAK"]}
        request = request_for(case, [{"path": "x", "sha256": "a", "text": "public docs"}])
        text = canonical(request).decode()
        for secret in ("SECRET_ORACLE", "NEVER_LEAK", "expected_output", "assertions"):
            self.assertNotIn(secret, text)
        self.assertEqual(request["mode"], "text-only-no-side-effects")

    def test_assertion_offsets_and_unicode(self):
        text = "猫\n━━━\nkpass activity --output json"
        result = grade([CASE], {1: record(response=text)}, "hash")
        checks = result["cases"][0]["checks"]
        self.assertEqual(checks[0]["line"], 3)
        self.assertEqual(checks[2]["offset"], 2)
        self.assertEqual(result["summary"]["pass"], 1)
        self.assertFalse(result["onchain_verified"])

    def test_case_sensitive_and_not_regex(self):
        case = {**CASE, "assertions": ["abc.*", "ABC", "é"]}
        r = record(case, "abcXXX abc e\u0301")
        result = grade([case], {1: r}, "hash")
        self.assertEqual(result["summary"]["assertions_passed"], 0)
        self.assertEqual(exit_status(result), 1)

    def test_missing_cases_not_skipped(self):
        result = grade([CASE], {}, "hash")
        self.assertEqual(result["summary"]["missing"], 1)
        self.assertFalse(result["summary"]["complete"])
        self.assertEqual(result["summary"]["assertions"], 3)
        self.assertEqual(exit_status(result), 1)
        xml = ET.fromstring(junit(result))
        self.assertEqual(xml.attrib["skipped"], "0")
        self.assertEqual(xml.attrib["errors"], "1")

    def test_error_never_scores_partial_stdout(self):
        result = grade([CASE], {1: record(status="timeout")}, "hash")
        self.assertEqual(result["summary"]["error"], 1)
        self.assertEqual(result["summary"]["assertions_passed"], 0)

    def test_replay_roundtrip(self):
        self.assertEqual(self.write_records([record()])[1]["response"], record()["response"])

    def test_replay_unknown_duplicate_and_mismatched_records(self):
        variants = [[record(), record()], [record(id=2)], [record(id=True)],
                    [record(schema_version=True)], [record(kind="live-proven-onchain")],
                    [record(prompt_sha256="f" * 64)], [record(response_sha256="f" * 64)],
                    [{**record(), "response": None}], [record(status="skipped")],
                    [record(duration_ms="invalid")], [record(duration_ms=-1)],
                    [record(adapter={})]]
        for rows in variants:
            with self.subTest(rows=rows), self.assertRaises(InputError):
                self.write_records(rows)

    def test_reviews_bound_to_current_response(self):
        row = {"id": 1, "verdict": "pass", "reviewer": "test fixture", "rationale": "Fixture assertion",
               "quote": "kpass activity", "response_sha256": record()["response_sha256"]}
        path = self.root / "reviews.json"
        path.write_text(json.dumps([row]), encoding="utf-8")
        reviews = load_reviews(path, {1: record()})
        report = grade([CASE], {1: record()}, "hash", reviews)
        self.assertEqual(exit_status(report, require_review=True), 0)
        for changes in [{"response_sha256": "wrong"}, {"quote": "not present"}, {"verdict": "skip"},
                        {"reviewer": ""}, {"rationale": None}, {"id": 99}]:
            path.write_text(json.dumps([{**row, **changes}]), encoding="utf-8")
            with self.subTest(changes=changes), self.assertRaises(InputError):
                load_reviews(path, {1: record()})

    def test_review_failure_overrides_literal_pass(self):
        review = {"verdict": "fail", "rationale": "wrong ordering", "reviewer": "fixture", "quote": "kpass"}
        result = grade([CASE], {1: record()}, "hash", {1: review})
        self.assertEqual(result["summary"]["pass"], 1)
        self.assertEqual(exit_status(result), 1)
        self.assertEqual(ET.fromstring(junit(result)).attrib["failures"], "1")

    def test_required_review_fails_closed(self):
        result = grade([CASE], {1: record()}, "hash")
        self.assertEqual(exit_status(result), 0)
        self.assertEqual(exit_status(result, require_review=True), 1)

    def test_html_injection_and_xml_controls(self):
        hostile = '</pre><script>alert("x")</script><img src=x onerror=alert(1)>\x01'
        case = {**CASE, "prompt": hostile, "expected_output": hostile, "assertions": [hostile]}
        result = grade([case], {1: record(case, hostile)}, "hash")
        page = render(result)
        self.assertNotIn('<script>alert("x")', page)
        self.assertNotIn('<img src=x', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertEqual(page.count("<script>"), 1)
        ET.fromstring(junit(result))

    def test_export_integrity_and_no_overwrite(self):
        out = self.root / "report"; out.mkdir()
        result = grade([CASE], {1: record()}, "hash")
        write_report(out, result)
        hashes = json.loads((out / "checksums.json").read_text())
        for name, sha in hashes.items():
            self.assertEqual(digest((out / name).read_bytes()), sha)
        with self.assertRaises(FileExistsError):
            write_report(out, result)

    def test_cli_good_replay_and_overwrite_refusal(self):
        self.write_records([record()])
        args = ["replay", "--suite", str(self.suite), "--transcripts", str(self.transcripts),
                "--out", str(self.root / "cli")]
        self.assertEqual(main(args), 0)
        self.assertEqual(main(args), 2)

    def test_required_review_is_visible_in_junit(self):
        self.write_records([record()])
        out = self.root / "required-review"
        code = main(["replay", "--suite", str(self.suite), "--transcripts", str(self.transcripts),
                     "--out", str(out), "--require-review"])
        self.assertEqual(code, 1)
        self.assertEqual(ET.parse(out / "junit.xml").getroot().attrib["failures"], "1")

    def test_cli_validation_error_code(self):
        self.suite.write_text("[]", encoding="utf-8")
        self.assertEqual(main(["validate", "--suite", str(self.suite)]), 2)

    def test_symlink_context_rejected(self):
        folder = self.root / "skill"; folder.mkdir()
        (folder / "SKILL.md").symlink_to(self.suite)
        with self.assertRaises(InputError):
            context_for(self.root, "skill")

    @unittest.skipUnless(os.name == "posix", "Live process adapter is POSIX-only")
    def test_process_protocol_and_unicode(self):
        script = "import json,sys; r=json.load(sys.stdin); print(json.dumps({'response':r['prompt']+' 猫'}))"
        result = capture(CASE, [], {"name": "fixture-echo", "argv": [sys.executable, "-c", script]}, 5, 2048)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["response"], CASE["prompt"] + " 猫")

    @unittest.skipUnless(os.name == "posix", "Live process adapter is POSIX-only")
    def test_timeout_kills_process_group(self):
        script = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']); time.sleep(30)"
        result = invoke([sys.executable, "-c", script], {}, 0.15, 2048)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(result["duration_ms"], 3000)

    @unittest.skipUnless(os.name == "posix", "Live process adapter is POSIX-only")
    def test_orphan_keeps_pipe_open_is_bounded(self):
        script = "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])"
        self.assertEqual(invoke([sys.executable, "-c", script], {}, 0.15, 2048)["status"], "timeout")

    @unittest.skipUnless(os.name == "posix", "Live process adapter is POSIX-only")
    def test_output_limit_combines_stdout_and_stderr(self):
        script = "import os; os.write(1,b'x'*1000); os.write(2,b'y'*1000)"
        result = invoke([sys.executable, "-c", script], {}, 5, 1024)
        self.assertEqual(result["status"], "output_limit")
        self.assertLessEqual(len(result["stdout"]), 1024)

    @unittest.skipUnless(os.name == "posix", "Live process adapter is POSIX-only")
    def test_spawn_nonzero_invalid_protocol_and_shell_literal(self):
        self.assertEqual(invoke(["/nonexistent-kite-adapter"], {}, 1, 2048)["status"], "spawn_error")
        self.assertEqual(invoke([sys.executable, "-c", "raise SystemExit(7)"], {}, 5, 2048)["exit_code"], 7)
        for body in ["print('not json')", "print('{}')", "print('{\"response\":2}')"]:
            result = capture(CASE, [], {"name": "fixture", "argv": [sys.executable, "-c", body]}, 5, 2048)
            self.assertEqual(result["status"], "protocol_error")
        result = invoke([sys.executable, "-c", "import sys;print(sys.argv[1])", "$(echo dangerous); echo nope"], {}, 5, 2048)
        self.assertIn(b"$(echo dangerous)", result["stdout"])

    def test_invalid_limits_rejected(self):
        for timeout, limit in [(0, 2048), (601, 2048), (1, 0), (1, 999999999)]:
            with self.subTest(timeout=timeout, limit=limit), self.assertRaises(InputError):
                invoke([sys.executable], {}, timeout, limit)


class OfficialSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ.get("KITE_UPSTREAM", "../upstream/passport-skills"))
        cls.cases, cls.sha = load_suite(cls.root / "evals/evals.json", pinned=True)

    def test_every_official_id_mapped_once(self):
        all_ids = [cid for ids in GROUPS.values() for cid in ids]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(set(all_ids), {c["id"] for c in self.cases})
        self.assertEqual((len(self.cases), sum(len(c["assertions"]) for c in self.cases)), (138, 424))
        self.assertEqual(self.sha, SUITE_SHA256)

    def test_all_official_assertions_and_424_deletion_mutants(self):
        for case in self.cases:
            text = "\n".join(case["assertions"])
            with self.subTest(id=case["id"], kind="synthetic-positive"):
                self.assertEqual(exit_status(grade([case], {case["id"]: record(case, text)}, self.sha)), 0)
            for literal in case["assertions"]:
                with self.subTest(id=case["id"], deleted=literal):
                    mutated = text.replace(literal, "")
                    report = grade([case], {case["id"]: record(case, mutated)}, self.sha)
                    self.assertEqual(exit_status(report), 1)
                    self.assertTrue(any(not a["passed"] and a["literal"] == literal for a in report["cases"][0]["checks"]))

    def test_all_skill_contexts_have_no_eval_artifacts(self):
        for slug in GROUPS:
            docs = context_for(self.root, slug)
            self.assertTrue(docs)
            self.assertTrue(any(d["path"] == slug + "/SKILL.md" for d in docs))
            for doc in docs:
                self.assertNotIn("evals/", doc["path"])
                self.assertEqual(digest(doc["text"].encode()), doc["sha256"])


if __name__ == "__main__":
    unittest.main()
