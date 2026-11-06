# SciEntsBank

Given a science question, its reference answers and a student answer, assign the original five-way label.

Open [pilot inputs](pilot_inputs.jsonl) for the actual model inputs. The compressed [candidate pool](cleaned_candidate_pool.jsonl.gz) contains all cleaned records before pilot selection.

The [pilot manifest](pilot_manifest.csv) lists all 100 evaluated cases, their original source and group IDs, gold labels, and cleaned-input checksums. Original split: `train`. Candidate pool: 4,969 rows.

Labels: `correct`, `partially_correct_incomplete`, `contradictory`, `irrelevant`, `non_domain`. The [task card](../../method/task_cards/SciEntsBank.json) lists definitions and the mapping used in every route.
