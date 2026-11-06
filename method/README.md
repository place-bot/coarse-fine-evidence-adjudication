# Coarse–Fine Evidence Adjudication

Each case goes through three independent judgments. All three see the original input, the same dataset task card and the same numbered evidence units.

| Route | Decision |
| --- | --- |
| [Direct classification](prompts/direct_classification.txt) | Choose one native label and give a short reason. |
| [Coarse judgment](prompts/coarse_judgment.txt) | Choose the terminal group or its complement. |
| [Fine label comparison](prompts/fine_label_comparison.txt) | Choose one native label and explain the distinction from its closest alternative. |
| [Conflict adjudication](prompts/conflict_adjudication.txt) | When the routes disagree, inspect the source, all three reasons and the competing interpretations. Keep the direct label when the dispute remains unresolved. |

In education, the terminal label is the fully correct response. In biomedicine, it is `no_relation`. Each [task card](task_cards/) defines its other labels. The shared prompts are the actual system messages from the selected run, including the evidence instructions.

The [trigger](disagreement.py) keeps the direct prediction when the direct and fine labels agree and that label’s group matches the coarse judgment. Otherwise the adjudicator may return any native label. It ran on 111 of 500 cases.

## Inspect a real decision

The following commands print the inference request locally. Viewing a request uses no API credits.

```sh
python3 method/build_request.py --dataset SciEntsBank --case 7b0a970120da236e
python3 method/build_request.py --dataset SciEntsBank --case 7b0a970120da236e --stage conflict_adjudication --judgments method/example_judgments.json
```

[The three saved judgments](example_judgments.json) belong to this specific case. The final decision is in [the experiment traces](../preliminary%20experiment/route_decisions.jsonl), keyed by the same case ID. A trace contains the original route labels, brief justifications, evidence IDs, and actual adjudication when triggered. Evidence IDs resolve to source spans via [evidence.py](evidence.py).

The pilot used `gpt-5.4-nano-2026-03-17`, temperature 0.7, reasoning effort `none`, and output limits of 400 tokens per initial judgment and 600 for adjudication. [Request settings](request_settings.json) specify the model and decoding options. The request builder inserts the allowed labels and evidence IDs into each route’s output schema. This version used fixed prompts.
