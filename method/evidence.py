"""Evidence is selected by immutable IDs, never reconstructed from model-written quotations."""

import re


def catalog(target):
    units = []
    for field, text in target["fields"].items():
        if not (
            field
            in [
                "question",
                "student_response",
                "selected_option",
                "sentence",
                "entity1",
                "entity2",
            ]
            or field.startswith("reference[")
        ):
            continue
        # Segments only index the unchanged text. The entire source also remains visible.
        cuts = (
            [0]
            + [m.end() for m in re.finditer(r"[.!?;](?=\s)|\n+", text)]
            + [len(text)]
        )
        for left, right in zip(cuts, cuts[1:]):
            while left < right and text[left].isspace():
                left += 1
            while right > left and text[right - 1].isspace():
                right -= 1
            if left == right:
                continue
            units.append(
                {
                    "id": f"E{len(units):03d}",
                    "field": field,
                    "start": left,
                    "end": right,
                    "text": text[left:right],
                }
            )
    return units


def resolve(ids, target):
    table = {u["id"]: u for u in catalog(target)}
    if not isinstance(ids, list) or len(ids) > 3:
        raise ValueError("evidence_ids must contain at most three source IDs")
    result = []
    seen = set()
    for sid in ids:
        if not isinstance(sid, str) or sid not in table:
            raise ValueError("Evidence ID does not exist in this input")
        if sid in seen:
            continue
        seen.add(sid)
        u = table[sid]
        source = target["fields"][u["field"]]
        assert source[u["start"] : u["end"]] == u["text"]
        result.append(
            {
                "source_id": sid,
                "field": u["field"],
                "matches": [[u["start"], u["end"]]],
                "quote": u["text"],
                "origin": "program_extracted",
            }
        )
    return result
