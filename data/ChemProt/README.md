# ChemProt

Given a sentence and the marked chemical and gene/protein, classify their relation into the five evaluated positive types or no_relation.

Run `python data/preprocessing/rebuild.py` from the repository root after the one-time [setup](../README.md). It downloads the pinned archive and writes the full text, entity offsets, and cleaned candidate pool to `data/rebuilt/ChemProt/`. The manifest contains the stable PubMed and entity-pair identifiers.

The [pilot manifest](pilot_manifest.csv) lists all 100 evaluated cases, their original source and group IDs, gold labels, and cleaned-input checksums. Original split: `development`. Candidate pool: 11,264 rows.

Labels: `no_relation`, `CPR:3`, `CPR:4`, `CPR:5`, `CPR:6`, `CPR:9`. The [task card](../../method/task_cards/ChemProt.json) lists definitions and the mapping used in every route.
