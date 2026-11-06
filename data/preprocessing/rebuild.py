"""Rebuild the frozen inputs and cleaned pools from checksum-verified sources."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request

from clean_fields import clean_fields, entity_check
from read_sources import read_sources

DATA = Path(__file__).resolve().parents[1]


def fingerprint(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def ensure_archive(folder, info):
    path = folder / info["file"]
    if not path.exists():
        print("Downloading", path.name, flush=True)
        request = urllib.request.Request(
            info["url"], headers={"User-Agent": "CFEA-course-project"}
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != info["sha256"]:
            raise ValueError(f"Unexpected upstream version: {path.name}")
        path.write_bytes(content)
    if hashlib.sha256(path.read_bytes()).hexdigest() != info["sha256"]:
        raise ValueError(f"Checksum mismatch: {path}")


def encode_lines(records):
    return "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in records
    ).encode()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument(
        "--all",
        action="store_true",
        help="rebuild all five datasets; default is ChemProt",
    )
    cli.add_argument("--raw", type=Path, default=DATA / "downloads")
    args = cli.parse_args()
    args.raw.mkdir(parents=True, exist_ok=True)
    sources = json.loads((DATA / "sources/download_manifest.json").read_text())
    for info in sources:
        if args.all or info["file"] == "ChemProt_Corpus.zip":
            ensure_archive(args.raw, info)

    expected = json.loads((DATA / "preprocessing/cleaning_audit.json").read_text())[
        "canonical_pool_sha256"
    ]
    for dataset, rows in read_sources(args.raw, chemprot_only=not args.all).items():
        with (DATA / dataset / "pilot_manifest.csv").open() as f:
            manifest = list(csv.DictReader(f))
        wanted = {row["source_id"]: row for row in manifest}
        pilot = {}
        for row in rows:
            fields, _, _ = clean_fields(row["fields"])
            row["fields"] = fields
            ref = wanted.get(row["source_id"])
            if ref and fingerprint(fields) == ref["fields_sha256"]:
                if row["label"] != ref["label"] or entity_check(fields):
                    raise ValueError(
                        f"Label or entity alignment differs for {ref['case_id']}"
                    )
                pilot[ref["case_id"]] = dict(
                    case_id=ref["case_id"], corpus=dataset, fields=fields
                )
        checksum = hashlib.sha256(
            "".join(fingerprint(row) + "\n" for row in rows).encode()
        ).hexdigest()
        if checksum != expected[dataset] or len(pilot) != len(manifest):
            raise ValueError(
                f"{dataset} does not match the frozen candidate pool or sample"
            )
        folder = DATA / "rebuilt" / dataset
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "pilot_inputs.jsonl").write_bytes(
            encode_lines(pilot[r["case_id"]] for r in manifest)
        )
        (folder / "cleaned_candidate_pool.jsonl.gz").write_bytes(
            gzip.compress(encode_lines(rows), mtime=0)
        )
        print(
            f"{dataset}: verified {len(rows):,} candidate records and {len(pilot)} pilot inputs → {folder}"
        )


if __name__ == "__main__":
    main()
