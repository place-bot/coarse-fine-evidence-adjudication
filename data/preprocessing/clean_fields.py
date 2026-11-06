"""Normalize whitespace and preserve entity-to-text alignment."""

import re

OFFSET_FIELDS = {
    "entity1_char_spans_inclusive",
    "entity2_char_spans_inclusive",
    "entity1_char_span_exclusive",
    "entity2_char_span_exclusive",
}


def normalize(text):
    """Return normalized text and each output character's original [start,end) range."""
    out = []
    mapping = []
    for m in re.finditer(r"\r\n|[\r\n\u2028\u2029]|[^\S\r\n\u2028\u2029]+|[^\s]", text):
        token = m.group()
        if token in ["\r\n", "\r", "\n", "\u2028", "\u2029"]:
            if out and out[-1] == " ":
                out.pop()
                mapping.pop()
            out.append("\n")
            mapping.append([m.start(), m.end()])
        elif token.isspace():
            if out and out[-1] not in [" ", "\n"]:
                out.append(" ")
                mapping.append([m.start(), m.end()])
        else:
            out.append(token)
            mapping.append([m.start(), m.end()])
    while out and out[0].isspace():
        out.pop(0)
        mapping.pop(0)
    while out and out[-1].isspace():
        out.pop()
        mapping.pop()
    result = "".join(out)
    assert re.sub(r"\s", "", text) == re.sub(r"\s", "", result), (
        "Substantive content changed"
    )
    assert text.split() == result.split(), "Word/token boundary changed"
    return result, mapping


def remap_span(start, end, mapping):
    idx = [i for i, (a, b) in enumerate(mapping) if b > start and a < end]
    if not idx:
        raise ValueError("Entity range lost all content")
    return idx[0], idx[-1] + 1


def clean_fields(fields):
    clean = {}
    align = {}
    changes = []
    for name, text in fields.items():
        if name in OFFSET_FIELDS:
            continue
        value, mapping = normalize(text)
        clean[name] = value
        align[name] = mapping
        if value != text:
            changes.append(name)
    if "sentence" in fields:
        for key in OFFSET_FIELDS:
            if key not in fields:
                continue
            if key.endswith("_inclusive"):
                ranges = [
                    [int(v) for v in part.split("-")] for part in fields[key].split(";")
                ]
                new = [remap_span(a, b + 1, align["sentence"]) for a, b in ranges]
                clean[key] = ";".join(f"{a}-{b - 1}" for a, b in new)
            else:
                a, b = map(int, fields[key].split(":"))
                a, b = remap_span(a, b, align["sentence"])
                clean[key] = f"{a}:{b}"
            if clean[key] != fields[key]:
                changes.append(key)
    return clean, align, changes


def entity_check(fields):
    problems = []
    for j in [1, 2]:
        inc = f"entity{j}_char_spans_inclusive"
        exc = f"entity{j}_char_span_exclusive"
        if inc in fields:
            ranges = [
                (int(a), int(b) + 1)
                for a, b in (part.split("-") for part in fields[inc].split(";"))
            ]
        elif exc in fields:
            ranges = [tuple(map(int, fields[exc].split(":")))]
        else:
            continue
        text = fields["sentence"]
        if not all(0 <= a < b <= len(text) for a, b in ranges):
            problems.append({"entity": j, "reason": "out_of_bounds"})
            continue
        extracted = " ".join(text[a:b] for a, b in ranges)
        if extracted.split() != fields[f"entity{j}"].split():
            problems.append(
                {
                    "entity": j,
                    "reason": "source_entity_text_mismatch",
                    "from_span": extracted,
                    "entity_text": fields[f"entity{j}"],
                }
            )
    return problems
