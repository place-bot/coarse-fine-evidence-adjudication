"""Determine when the three route judgments require adjudication."""

import copy


def project(card, label):
    return "TERMINAL" if label in card["coarse_mapping"]["TERMINAL"] else "EXPANDED"


def plan(card, direct, g, f):
    records = {"direct": direct, "coarse": g, "fine": f}

    packet = {k: copy.deepcopy(r) for k, r in records.items()}
    d, gm, fm = [packet[k]["label"] for k in ["direct", "coarse", "fine"]]
    if (
        d not in card["native_label_definitions"]
        or fm not in card["native_label_definitions"]
        or gm not in ["TERMINAL", "EXPANDED"]
    ):
        raise ValueError("Invalid route label")
    conflicts = []
    if project(card, d) != gm:
        conflicts.append(
            {
                "comparison": "direct_vs_coarse",
                "direct_native_label": d,
                "direct_coarse_projection": project(card, d),
                "coarse_label": gm,
            }
        )
    if d != fm:
        conflicts.append(
            {
                "comparison": "direct_vs_fine",
                "direct_native_label": d,
                "fine_native_label": fm,
            }
        )
    if project(card, fm) != gm:
        conflicts.append(
            {
                "comparison": "fine_vs_coarse",
                "fine_native_label": fm,
                "fine_coarse_projection": project(card, fm),
                "coarse_label": gm,
            }
        )
    return {
        "starting_label": d,
        "route_labels": {"direct": d, "coarse": gm, "fine": fm},
        "action": "review_conflict" if conflicts else "keep_consensus",
        "judgments": packet,
        "disagreements": conflicts,
    }
