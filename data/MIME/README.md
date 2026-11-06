# MIME

Given the math question, the selected option and the student’s explanation, classify the reasoning the student expressed.

Open [pilot inputs](pilot_inputs.jsonl) for the actual model inputs. The compressed [candidate pool](cleaned_candidate_pool.jsonl.gz) contains all cleaned records before pilot selection.

The [pilot manifest](pilot_manifest.csv) lists all 100 evaluated cases, their original source and group IDs, gold labels, and cleaned-input checksums. Original split: `train`. Candidate pool: 26,657 rows.

Labels: `Correct`, `Misconception`, `Neither`. The [task card](../../method/task_cards/MIME.json) lists definitions and the mapping used in every route.
