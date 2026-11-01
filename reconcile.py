#!/usr/bin/env python3
"""Reconcile the latest payment attempts. Run: python3 reconcile.py."""

import json
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path


def timestamp(value):
    """Compare actual UTC instants, including fractional seconds and offsets."""
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def reconcile(lines):
    latest = {}
    for line in lines:
        try:
            event = json.loads(line, parse_float=Decimal)
        except (ValueError, TypeError):
            continue
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue
        txn_id = event["txn_id"]
        occurred_at = timestamp(event["ts"])
        if txn_id not in latest or occurred_at >= latest[txn_id][0]:
            latest[txn_id] = (occurred_at, event)

    successful = [event for _, event in latest.values() if event["status"] == "success"]
    # Preserve the input's decimal precision throughout accumulation.
    amounts = [Decimal(str(event["amount"])) for event in successful]
    with localcontext() as context:
        context.prec = max(
            [28] + [len(amount.as_tuple().digits) + abs(amount.as_tuple().exponent)
                    + len(str(len(amounts))) + 2 for amount in amounts]
        )
        return len(successful), sum(amounts, Decimal(0))


def main():
    directory = Path(__file__).resolve().parent
    with (directory / "payments.jsonl").open(encoding="utf-8-sig") as source:
        count, total = reconcile(source)
    expected = int((directory / "expected.txt").read_text().strip())
    if count != expected:
        print(f"Check failed: counted {count} successful payments, expected {expected}.")
        print("Something in the data isn't being handled the way the README describes.")
        return 1
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
