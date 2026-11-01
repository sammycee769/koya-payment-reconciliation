import json
import unittest
from decimal import Decimal

from reconcile import reconcile


def event(txn_id, status, amount, ts):
    return json.dumps(dict(txn_id=txn_id, status=status, amount=amount,
                           currency="NGN", ts=ts))


class ReconciliationTests(unittest.TestCase):
    def test_latest_attempt_wins_even_when_export_is_out_of_order(self):
        lines = [
            event("a", "failed", "10", "2026-01-02T00:00:00Z"),
            event("a", "success", "10", "2026-01-01T00:00:00Z"),
            event("b", "pending", "20", "2026-01-01T00:00:00Z"),
            event("b", "success", "20", "2026-01-02T00:00:00Z"),
        ]
        self.assertEqual(reconcile(lines), (1, Decimal("20")))

    def test_dirty_lines_and_missing_ids_are_ignored(self):
        lines = ["bad json", "", "null", "[]", "{}",
                 event(None, "success", "999", "2026-01-01T00:00:00Z"),
                 event("a", "success", "0.1", "2026-01-01T00:00:00Z"),
                 event("b", "success", "0.2", "2026-01-01T00:00:00Z")]
        self.assertEqual(reconcile(lines), (2, Decimal("0.3")))

    def test_timestamps_are_compared_as_instants(self):
        lines = [event("a", "success", "10", "2026-01-01T01:00:00+02:00"),
                 event("a", "pending", "10", "2026-01-01T00:00:00Z")]
        self.assertEqual(reconcile(lines), (0, Decimal(0)))

    def test_numeric_amounts_keep_decimal_precision(self):
        lines = ['{"txn_id":"a","status":"success","amount":12345678901234567890.12,"ts":"2026-01-01T00:00:00Z"}']
        self.assertEqual(reconcile(lines), (1, Decimal("12345678901234567890.12")))

    def test_amount_strings_with_thousands_separators(self):
        lines = [event("a", "success", "55,707.77", "2026-01-01T00:00:00Z")]
        self.assertEqual(reconcile(lines), (1, Decimal("55707.77")))


if __name__ == "__main__":
    unittest.main()
