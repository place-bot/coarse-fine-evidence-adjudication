"""Compute performance and paired changes from the 500 saved decisions (no API)."""

import csv
from pathlib import Path

folder = Path(__file__).resolve().parent
with (folder / "pilot_predictions.csv").open() as f:
    rows = list(csv.DictReader(f))
if len(rows) != len({r["case_id"] for r in rows}) or len(rows) != 500:
    raise ValueError("Expected exactly 500 unique pilot cases")
print(
    "Dataset         n   single mean   4-vote   CFEA    fixed/harmed vs 4-vote   vs direct #1"
)
for name in dict.fromkeys([r["dataset"] for r in rows] + ["All"]):
    part = [r for r in rows if name == "All" or r["dataset"] == name]
    correct = lambda key: sum(r[key] == r["gold"] for r in part)

    def changes(base):
        fixed = sum(r[base] != r["gold"] == r["cfea"] for r in part)
        harmed = sum(r[base] == r["gold"] != r["cfea"] for r in part)
        return f"{fixed}/{harmed}"

    n = len(part)
    single = sum(correct(f"single_{i}") for i in range(1, 5)) / (4 * n)
    print(
        f"{name:<13} {n:>3} {single:>12.2%} {correct('four_vote') / n:>8.1%} {correct('cfea') / n:>6.1%} {changes('four_vote'):>17} {changes('direct'):>16}"
    )
