# Coarse–Fine Evidence Adjudication

Team project on classifying student answers and biomedical relations. We make three judgments about the same input and ask for adjudication when the judgments disagree.

| Start here | What you can do |
| --- | --- |
| [Data](data/) | Open a dataset, inspect the texts and gold labels used in the pilot, or reproduce the cleaned data. |
| [Method](method/) | Read the four prompts, inspect the five task cards, and follow an actual decision. |
| [Preliminary experiment](preliminary%20experiment/) | Inspect all 500 predictions, compare against direct classification and voting, and reproduce the scores offline. |

The selected version classified **311 of 500** development cases correctly (62.2%). Four ordinary votes classified 300 correctly (60.0%). Averaging the four single runs gave 59.7%. The sample contains 100 examples per dataset and was stratified by label. The largest gains were on DDI and ChemProt.

To check the paired results after cloning:

```sh
python3 "preliminary experiment/reproduce_scores.py"
```
