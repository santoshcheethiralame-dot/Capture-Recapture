"""E09-R003: offline Neuronpedia label file for the T3 Gemma Scope tool (Q-D15).

    python analysis/e09/neuronpedia_labels.py --out results/E09/E09-R003/labels
    python analysis/e09/neuronpedia_labels.py --src <dir of batch-*.jsonl.gz> --out ...

Neuronpedia publishes its explanations as a public dataset on S3
(``neuronpedia-datasets/v1/<model>/<source>/explanations/batch-*.jsonl.gz``),
so the tool never calls Neuronpedia at run time. The source for
``gemma-scope-2b-pt-res-canonical`` / ``layer_12/width_16k/canonical`` is
``gemma-2-2b/12-gemmascope-res-16k`` (SAELens ``pretrained_saes.yaml``).

Writes ``<source>.json`` ({feature index: label}, the format
``gemma_scope.from_hf(labels_path=...)`` reads) and ``SOURCE.json`` (URLs,
sha256 of every batch file, counts, the de-duplication rule). A feature with
several explanations keeps the one from the default auto-interp method
(``oai_token-act-pair`` by gpt-4o-mini), so every label comes from the same
method; ties go to the first in file order.
"""

import argparse
import gzip
import hashlib
import json
import re
import urllib.request
from pathlib import Path

BUCKET = "https://neuronpedia-datasets.s3.amazonaws.com"
DEFAULT = "gemma-2-2b/12-gemmascope-res-16k"
PREFERRED = ("oai_token-act-pair", "gpt-4o-mini")


def list_batches(source):
    prefix = f"v1/{source}/explanations/"
    xml = urllib.request.urlopen(f"{BUCKET}/?list-type=2&prefix={prefix}").read().decode()
    return sorted(re.findall(r"<Key>([^<]+\.jsonl\.gz)</Key>", xml))


def download(source, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for key in list_batches(source):
        p = dest / Path(key).name
        if not p.exists():
            urllib.request.urlretrieve(f"{BUCKET}/{key}", p)
    return dest


def build(src, d_sae=None):
    files = sorted(Path(src).glob("batch-*.jsonl.gz"), key=lambda p: int(p.stem.split("-")[1].split(".")[0]))
    best, n_rows = {}, 0
    for f in files:
        with gzip.open(f, "rt") as fh:
            for line in fh:
                d = json.loads(line)
                n_rows += 1
                i = int(d["index"])
                pref = (d.get("typeName"), d.get("explanationModelName")) == PREFERRED
                if i not in best or (pref and not best[i][0]):
                    best[i] = (pref, d["description"].strip())
    labels = {i: best[i][1] for i in sorted(best)}
    info = dict(
        files=[dict(name=f.name, sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files],
        n_rows=n_rows, n_features_labelled=len(labels),
        n_non_preferred=sum(1 for v in best.values() if not v[0]),
        missing=[i for i in range(d_sae) if i not in labels] if d_sae else None,
        dedup_rule=f"prefer typeName/explanationModelName == {PREFERRED}, else first in file order",
    )
    return labels, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", default=DEFAULT, help="Neuronpedia <model>/<source> id")
    ap.add_argument("--src", default=None, help="local dir of batch-*.jsonl.gz (default: download)")
    ap.add_argument("--d-sae", type=int, default=16384)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    src = Path(a.src) if a.src else download(a.source, out / "raw")
    labels, info = build(src, a.d_sae)
    name = a.source.replace("/", "__") + ".json"
    (out / name).write_text(json.dumps(labels, indent=0, ensure_ascii=False) + "\n")
    info.update(source=a.source, url=f"{BUCKET}/index.html#v1/{a.source}/explanations/", labels_file=name,
                labels_sha256=hashlib.sha256((out / name).read_bytes()).hexdigest())
    (out / "SOURCE.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps({k: v for k, v in info.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
