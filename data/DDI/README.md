# DDI

Given a sentence and two marked drug mentions, classify the interaction expressed for that pair.

Open [pilot inputs](pilot_inputs.jsonl) for the actual model inputs. The compressed [candidate pool](cleaned_candidate_pool.jsonl.gz) contains all cleaned records before pilot selection.

The [pilot manifest](pilot_manifest.csv) lists all 100 evaluated cases, their original source and group IDs, gold labels, and cleaned-input checksums. Original split: `BLURB_dev`. Candidate pool: 2,496 rows.

Labels: `no_relation`, `advice`, `effect`, `mechanism`, `int`. The [task card](../../method/task_cards/DDI.json) lists definitions and the mapping used in every route.
