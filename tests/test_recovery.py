import unittest
from scripts.recover import merge_records
from kite_eval.core import InputError


class RecoveryTests(unittest.TestCase):
    def row(self, status):
        return {"id": 135, "kind": "agent", "status": status, "request_sha256": "a",
                "adapter_config_sha256": "b", "prompt_sha256": "c"}

    def test_error_only_recovery_preserves_others(self):
        original = {135: self.row("adapter_error"), 1: {"status": "ok"}}
        recovered = merge_records(original, {135: self.row("ok")})
        self.assertEqual(recovered[135]["status"], "ok")
        self.assertEqual(original[135]["status"], "adapter_error")
        self.assertIs(recovered[1], original[1])

    def test_no_cherry_picking_or_changed_requests(self):
        for original, retry in [({135: self.row("ok")}, {135: self.row("ok")}),
                                ({135: self.row("timeout")}, {}),
                                ({}, {135: self.row("ok")}),
                                ({135: self.row("timeout")}, {135: self.row("timeout")}),
                                ({135: self.row("timeout")}, {135: {**self.row("ok"), "kind": "fixture"}}),
                                ({135: self.row("timeout")}, {135: {**self.row("ok"), "request_sha256": "different"}})]:
            with self.subTest(original=original, retry=retry), self.assertRaises(InputError):
                merge_records(original, retry)
