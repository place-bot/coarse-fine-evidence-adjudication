# Data

Open one of the five datasets to explore its task, model inputs, and pilot labels.

| Dataset | Task | Source partition |
| --- | --- | --- |
| [MIME](MIME/) | Classify the reasoning in a student’s math explanation | Real responses in the training split |
| [SciEntsBank](SciEntsBank/) | Classify a short science answer against reference answers | Five-way training Core |
| [BEETLE](BEETLE/) | Classify an answer about electric circuits | Five-way training Core |
| [DDI](DDI/) | Classify a relation between two drug mentions | BLURB development document index |
| [ChemProt](ChemProt/) | Classify a chemical–protein relation | Official development partition |

Each folder has a `pilot_manifest.csv` with exactly 100 cases. Match its `case_id` to a row in the [experiment predictions](../preliminary%20experiment/pilot_predictions.csv). Model inputs contain only the task fields, case ID and dataset name. Gold labels are in the separate manifest.

Four folders include their pilot text and full cleaned candidate pool. For ChemProt we keep the record IDs and annotations here, and reconstruct the source sentences and offsets directly from the original release. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r data/preprocessing/requirements.txt
python -m nltk.downloader punkt_tab
python data/preprocessing/rebuild.py
```

The output is `data/rebuilt/ChemProt/pilot_inputs.jsonl` and `cleaned_candidate_pool.jsonl.gz`. Add `--all` to rebuild all five corpora. The script verifies the source archives, every pilot input, and the entire cleaned pool against the original run. No model access is required.

## How the pilot was prepared

We normalized whitespace and remapped biomedical entity offsets to the resulting text. We preserved spelling, punctuation, negations and mathematical symbols. The [cleaning audit](preprocessing/cleaning_audit.json) records counts before panel selection. Candidate pools contain records before the eligibility and deduplication steps.

Each panel retains 45 earlier cases and adds 55 examples. The expansion excluded blank responses, ambiguous duplicate inputs and invalid entity spans, favored underrepresented groups, and used label quotas subject to availability. For ChemProt it excluded documents in the earlier tuned 45 and kept one case per selected document. The [sampling record](pilot_sampling.json) preserves the seed, case order, label counts and source-group counts. Use the frozen manifests to recover the same cases.

[Dataset credits, source links and terms](sources/) apply to the data in each folder.
