# Payment reconciliation fix

Source repository: https://github.com/quadri40/koya-payment-reconciliation

This directory contains a corrected Python implementation and regression tests.
It is a local working copy, not a GitHub fork. The original payments.jsonl file
was extracted from the repository ZIP supplied by the user and is included.

The implementation ignores unreadable JSON and entries without a transaction ID,
selects the latest event by its timestamp for each transaction, and sums amounts
only for transactions whose latest status is success. Decimal arithmetic avoids
binary floating-point errors. Amount strings with thousands separators are supported. No currency filter is applied because the source
README requires all valid events to count. Equal timestamps use the last event
in file order; the source README does not specify a tie-breaking rule.

To finish:

1. Fork the source repository on GitHub and clone your fork.
2. Copy reconcile.py and test_reconcile.py from this directory into your fork.
3. Run `python3 -m unittest -v` and `python3 reconcile.py` in your fork.
4. Commit and push the fix.
5. Submit the actual printed code, your fork URL, and a screenshot of the terminal
   after the successful reconciliation run.

The expected success count is 22733, as published in the source expected.txt.
Verified against the original dataset: 22733 successful payments; exact total
NGN 1964687345.74; submission code KOYA-1964687346. An independent sort-based
calculation confirmed the count and total. All five regression tests pass.

A terminal screenshot could not be captured because this environment cannot
connect to the desktop display. Run the command locally and capture its output.
The GitHub fork and remote commit remain outstanding; the fix is committed locally.
