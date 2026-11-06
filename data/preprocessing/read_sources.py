"""Read candidate records from the source releases used in the pilot."""

import csv, io, tarfile, zipfile
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
from nltk.tokenize import sent_tokenize


def item(c, sid, group, fields, label, split, stratum=None):
    return dict(
        corpus=c,
        source_id=str(sid),
        group=str(group),
        fields=fields,
        label=label,
        split=split,
        stratum=stratum or label,
    )


def read_sources(raw, chemprot_only=False):
    out = defaultdict(list)
    if not chemprot_only:
        with (raw / "dataset_minus_700_for_github.csv").open() as f:
            for r in csv.DictReader(f):
                if r["Source"] == "real" and r["split"] == "train":
                    fields = {
                        "question": r["Question.Text"],
                        "selected_option": r["MC_Answer"],
                        "student_response": r["StudentExplanation"],
                    }
                    out["MIME"].append(
                        item(
                            "MIME",
                            r["ExplanationId"],
                            r["QuestionId"],
                            fields,
                            r["Category"].split("_", 1)[1],
                            "train",
                            r["Category"],
                        )
                    )
        with zipfile.ZipFile(raw / "semeval-5way.zip") as z:
            for c, folder in [("SciEntsBank", "sciEntsBank"), ("BEETLE", "beetle")]:
                for n in sorted(z.namelist()):
                    if not (
                        n.startswith(folder + "/train/Core/") and n.endswith(".xml")
                    ):
                        continue
                    q = ET.fromstring(z.read(n))
                    fields = {"question": q.findtext("questionText") or ""}
                    for j, a in enumerate(
                        q.findall("./referenceAnswers/referenceAnswer")
                    ):
                        fields[f"reference[{j}]"] = "".join(a.itertext())
                    for a in q.findall("./studentAnswers/studentAnswer"):
                        out[c].append(
                            item(
                                c,
                                a.attrib["id"],
                                Path(n).stem,
                                {**fields, "student_response": "".join(a.itertext())},
                                a.attrib["accuracy"],
                                "train",
                            )
                        )
        ads = raw
        with (
            tarfile.open(ads / "blurb_data_generation.tar.gz") as idx,
            tarfile.open(ads / "DDIextraction_2013.tar.gz") as z,
        ):
            names = (
                idx.extractfile("data_generation/indexing/DDI/dev_files.tsv")
                .read()
                .decode()
                .splitlines()
            )
            for name in names:
                for s in ET.fromstring(
                    z.extractfile("DDIextraction_2013/" + name).read()
                ).findall("sentence"):
                    es = {e.attrib["id"]: e.attrib for e in s.findall("entity")}
                    for pair in s.findall("pair"):
                        p = pair.attrib
                        fields = {"sentence": s.attrib["text"]}
                        for j, k in enumerate(["e1", "e2"], 1):
                            e = es[p[k]]
                            fields[f"entity{j}"] = e["text"]
                            fields[f"entity{j}_type"] = e["type"]
                            fields[f"entity{j}_char_spans_inclusive"] = e["charOffset"]
                        lab = p.get("type") if p["ddi"] == "true" else "no_relation"
                        lab = "advice" if lab == "advise" else lab
                        out["DDI"].append(
                            item("DDI", p["id"], name, fields, lab, "BLURB_dev")
                        )
    with zipfile.ZipFile(raw / "ChemProt_Corpus.zip") as outer:
        with zipfile.ZipFile(
            io.BytesIO(outer.read("ChemProt_Corpus/chemprot_development.zip"))
        ) as z:
            prefix = "chemprot_development/chemprot_development_"
            entities = defaultdict(list)
            relations = defaultdict(set)
            for l in z.read(prefix + "entities.tsv").decode().splitlines():
                doc, eid, typ, a, b, text = l.split("\t")
                entities[doc].append((eid, typ, int(a), int(b), text))
            for l in z.read(prefix + "gold_standard.tsv").decode().splitlines():
                doc, lab, a, b = l.split("\t")
                relations[(doc, a.split(":")[1], b.split(":")[1])].add(lab)
            for l in z.read(prefix + "abstracts.tsv").decode().splitlines():
                doc, title, abstract = l.split("\t")
                text = title + "\t" + abstract
                # BLURB uses NLTK sentences followed by title/abstract tab separation.
                sentences = [
                    s for whole in sent_tokenize(text) for s in whole.split("\t")
                ]
                offset = 0
                for sentence in sentences:
                    start = text.index(sentence, offset)
                    end = start + len(sentence)
                    offset = end
                    es = [e for e in entities[doc] if start <= e[2] and e[3] <= end]
                    for chem in [e for e in es if e[1] == "CHEMICAL"]:
                        for gene in [e for e in es if e[1].startswith("GENE")]:
                            labs = relations.get((doc, chem[0], gene[0]), set())
                            if len(labs) > 1:
                                continue  # prespecified single-label study
                            fields = {"sentence": sentence}
                            for j, e in enumerate([chem, gene], 1):
                                assert sentence[e[2] - start : e[3] - start] == e[4]
                                fields[f"entity{j}"] = e[4]
                                fields[f"entity{j}_type"] = e[1].split("-")[0]
                                fields[f"entity{j}_char_span_exclusive"] = (
                                    f"{e[2] - start}:{e[3] - start}"
                                )
                            lab = next(iter(labs)) if labs else "no_relation"
                            out["ChemProt"].append(
                                item(
                                    "ChemProt",
                                    f"{doc}.{chem[0]}.{gene[0]}",
                                    doc,
                                    fields,
                                    lab,
                                    "development",
                                )
                            )
    return out
