"""Render a pilot request offline, with the same instructions and inputs as the run."""

import argparse
import json
from pathlib import Path

from disagreement import plan
from evidence import catalog

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
STAGES = (
    "direct_classification",
    "coarse_judgment",
    "fine_label_comparison",
    "conflict_adjudication",
)


def task_card(dataset):
    return json.loads((HERE / "task_cards" / f"{dataset}.json").read_text())


def build_request(target, stage, judgments=None, repair=None):
    dataset = target["corpus"]
    settings = json.loads((HERE / "request_settings.json").read_text())
    options = settings.pop("routes")[stage]
    settings["max_output_tokens"] = options["max_output_tokens"]
    settings["metadata"] = options["metadata"]
    settings["metadata"]["case_id"] = target["case_id"]
    settings["metadata"]["repair"] = str(bool(repair))
    units = [
        {key: unit[key] for key in ("id", "field", "text")} for unit in catalog(target)
    ]
    card = task_card(dataset)
    data = {"task_card": card, "source_fields": target["fields"], "source_units": units}
    if stage == "conflict_adjudication":
        if not judgments:
            raise ValueError(
                "Supply the direct, coarse and fine judgments for adjudication"
            )
        decision = plan(
            card, judgments["direct"], judgments["coarse"], judgments["fine"]
        )
        if decision["action"] != "review_conflict":
            raise ValueError("All routes agree; keep the direct label")
        data.update(
            starting_label=decision["starting_label"],
            independent_judgments=decision["judgments"],
            disagreements=decision["disagreements"],
        )
    elif judgments is not None:
        raise ValueError("Upstream routes receive only the input and task card")
    if repair:
        data["format_validation_error"] = repair
    labels = list(
        card["coarse_mapping"]
        if stage == "coarse_judgment"
        else card["native_label_definitions"]
    )
    properties = {
        "label": {"type": "string", "enum": labels},
        "justification": {"type": "string"},
    }
    if stage == "conflict_adjudication":
        properties["decisive_proposition"] = {"type": "string"}
    properties["evidence_ids"] = {
        "type": "array",
        "maxItems": 3,
        "items": {"type": "string", "enum": [unit["id"] for unit in units]},
    }
    schema = {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
    settings["text"] = {
        "format": {
            "type": "json_schema",
            "name": options["format_name"],
            "strict": True,
            "schema": schema,
        }
    }
    instruction = (HERE / "prompts" / f"{stage}.txt").read_text().rstrip("\n")
    settings["input"] = [
        {"role": "system", "content": instruction},
        {
            "role": "user",
            "content": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        },
    ]
    return settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="SciEntsBank")
    parser.add_argument(
        "--case", help="case_id from a pilot manifest; default is the first example"
    )
    parser.add_argument("--stage", choices=STAGES, default=STAGES[0])
    parser.add_argument(
        "--judgments",
        type=Path,
        help="JSON object containing direct, coarse and fine outputs",
    )
    args = parser.parse_args()
    path = DATA / args.dataset / "pilot_inputs.jsonl"
    if not path.exists():
        path = DATA / "rebuilt" / args.dataset / "pilot_inputs.jsonl"
    if not path.exists():
        parser.error("Generate the inputs with data/preprocessing/rebuild.py first.")
    with path.open() as f:
        target = next(
            (
                r
                for r in map(json.loads, f)
                if args.case is None or r["case_id"] == args.case
            ),
            None,
        )
    if target is None:
        parser.error("case_id not found in the selected dataset.")
    judgments = json.loads(args.judgments.read_text()) if args.judgments else None
    print(
        json.dumps(
            build_request(target, args.stage, judgments), indent=2, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
