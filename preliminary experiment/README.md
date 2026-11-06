# Preliminary experiment on 500 development cases

[Open the 500 predictions](pilot_predictions.csv) to see each case’s gold label, direct/coarse/fine judgments, four independent direct draws, ordinary vote, and final CFEA label. [The full decision traces](route_decisions.jsonl) explain what each route reported, what disagreement triggered adjudication, and what the adjudicator decided. Join either file to the [data](../data/) by `case_id`.

| Dataset (100 each) | Mean single accuracy | Four votes | CFEA | Fixed / harmed vs four votes |
| --- | ---: | ---: | ---: | ---: |
| MIME | 51.50% | 52% | 52% | 3 / 3 |
| SciEntsBank | 64.00% | 65% | 65% | 4 / 4 |
| BEETLE | 55.25% | 55% | 54% | 2 / 3 |
| DDI | 60.25% | 61% | 66% | 6 / 1 |
| ChemProt | 67.50% | 67% | 74% | 9 / 2 |
| **All** | **59.70%** | **60.00%** | **62.20%** | **24 / 13** |

The single baseline averages accuracy over four direct draws. The voting baseline takes their plurality, breaking ties uniformly with a fixed case-specific seed (2026102804). CFEA starts from the first direct draw. The coarse and fine judgments each run once. CFEA fixed 18 and harmed 11 relative to that first direct draw. It adjudicated 111 cases, for 3.222 logical calls per example. The table uses ordinary example accuracy. Sampling and prior development exposure matter when comparing these estimates with published benchmarks.

[Paired changes](paired_changes.csv) lists fixes, harms and net correct cases versus each baseline. The [per-dataset metrics](pilot_metrics.csv) include macro-F1. The [detailed results](pilot_details.json) include per-class performance, confusion matrices, paired changes, bootstrap intervals, and logical inference costs. From the repository root, reproduce the table of accuracy and changes with `python3 "preliminary experiment/reproduce_scores.py"`.
