"""
BLP-2025 Task 1 — Data integrity audit (no manual annotation required).

Objective checks that produce publishable findings before any human annotation:
  1. Label distribution across splits
  2. Exact-duplicate texts carrying CONFLICTING labels  (direct label-noise evidence)
  3. Train/test leakage (identical texts in both)
  4. Degenerate items (too short to classify, empty, URL/emoji-only)
  5. Label-schema coherence in 1C (type vs severity vs target consistency)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import pathlib
import re, json, unicodedata

import os
_HERE = pathlib.Path(__file__).resolve().parent
_ROOT = _HERE.parent
# Dataset location: env var BLP25_DATA, else ../blp25_task1, else ./blp25_task1
_CANDIDATES = [os.environ.get("BLP25_DATA"), _ROOT / "blp25_task1",
               _ROOT.parent / "blp25_task1"]
_BASE = next((pathlib.Path(c) for c in _CANDIDATES if c and pathlib.Path(c).exists()), None)
if _BASE is None:
    raise SystemExit("Dataset not found. Clone https://github.com/AridHasan/blp25_task1 "
                     "next to this repo, or set BLP25_DATA=/path/to/blp25_task1")

DATA = _BASE / "data"
OUT = _ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

def load(sub, split):
    p = DATA / f"subtask_{sub}" / f"blp25_hatespeech_subtask_{sub}_{split}.tsv"
    if not p.exists():
        return None
    return pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False, na_values=[])

def norm(t):
    """Normalization for duplicate detection: NFC, collapse whitespace, strip punctuation/emoji."""
    if not isinstance(t, str):
        return ""
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

report = {}

# ---------- 1. Label distributions ----------
print("=" * 70)
print("1. LABEL DISTRIBUTIONS")
print("=" * 70)
dist = {}
for sub, col in [("1A", "label"), ("1B", "label")]:
    for split in ["train", "dev", "dev_test_with_labels", "test_with_labels"]:
        df = load(sub, split)
        if df is None or col not in df.columns:
            continue
        vc = df[col].value_counts()
        dist[f"{sub}/{split}"] = vc.to_dict()
        print(f"\n{sub} {split}  (n={len(df)})")
        for k, v in vc.items():
            print(f"    {k:<18} {v:>7}  {100*v/len(df):>5.1f}%")

df1c = load("1C", "test_with_labels")
for col in ["hate_type", "hate_severity", "to_whom"]:
    vc = df1c[col].value_counts()
    dist[f"1C/test/{col}"] = vc.to_dict()
    print(f"\n1C test — {col}  (n={len(df1c)})")
    for k, v in vc.items():
        print(f"    {k:<18} {v:>7}  {100*v/len(df1c):>5.1f}%")
report["distributions"] = dist

# ---------- 2. Duplicate texts with conflicting labels ----------
print("\n" + "=" * 70)
print("2. EXACT-DUPLICATE TEXTS WITH CONFLICTING LABELS")
print("=" * 70)
dup_report = {}
for sub in ["1A", "1B"]:
    frames = []
    for split in ["train", "dev", "dev_test_with_labels", "test_with_labels"]:
        d = load(sub, split)
        if d is None or "label" not in d.columns:
            continue
        d = d.assign(split=split)
        frames.append(d)
    allx = pd.concat(frames, ignore_index=True)
    allx["ntext"] = allx["text"].map(norm)
    allx = allx[allx["ntext"] != ""]

    g = allx.groupby("ntext")["label"].nunique()
    conflicted = g[g > 1].index
    dup_rows = allx[allx["ntext"].isin(conflicted)].sort_values("ntext")

    n_dup_texts = allx["ntext"].duplicated().sum()
    n_conf_texts = len(conflicted)
    n_conf_rows = len(dup_rows)
    print(f"\nSubtask {sub}:  total rows={len(allx)}")
    print(f"   duplicate rows (same text seen again): {n_dup_texts}")
    print(f"   distinct texts with >1 distinct label: {n_conf_texts}")
    print(f"   rows involved in a label conflict:     {n_conf_rows} "
          f"({100*n_conf_rows/len(allx):.2f}% of corpus)")
    dup_report[sub] = dict(rows=len(allx), dup_rows=int(n_dup_texts),
                           conflicting_texts=int(n_conf_texts),
                           conflicting_rows=int(n_conf_rows))
    if n_conf_rows:
        dup_rows[["id", "split", "label", "text"]].to_csv(
            OUT / f"conflicting_labels_{sub}.csv", index=False)
        print(f"   -> written to results/conflicting_labels_{sub}.csv")
        print("\n   Examples:")
        for t in list(conflicted)[:5]:
            sl = dup_rows[dup_rows["ntext"] == t]
            print(f"     TEXT: {t[:80]}")
            print(f"           labels = {sorted(sl['label'].unique())} "
                  f"across splits {sorted(sl['split'].unique())}")
report["duplicates"] = dup_report

# ---------- 3. Train/test leakage ----------
print("\n" + "=" * 70)
print("3. TRAIN / TEST LEAKAGE")
print("=" * 70)
leak_report = {}
for sub in ["1A", "1B"]:
    tr = load(sub, "train"); te = load(sub, "test_with_labels")
    if tr is None or te is None:
        continue
    trn = set(tr["text"].map(norm)) - {""}
    ten = te["text"].map(norm)
    leaked = ten.isin(trn)
    print(f"Subtask {sub}: {leaked.sum()} / {len(te)} test items "
          f"({100*leaked.mean():.2f}%) appear verbatim in train")
    leak_report[sub] = dict(n_leaked=int(leaked.sum()), n_test=len(te),
                            pct=round(100*float(leaked.mean()), 3))
    if leaked.sum():
        te[leaked][["id", "text", "label"]].to_csv(
            OUT / f"leaked_test_items_{sub}.csv", index=False)
report["leakage"] = leak_report

# ---------- 4. Degenerate items ----------
print("\n" + "=" * 70)
print("4. DEGENERATE / UNCLASSIFIABLE ITEMS (test set, 1A)")
print("=" * 70)
te = load("1A", "test_with_labels")
te["ntext"] = te["text"].map(norm)
te["nchar"] = te["ntext"].str.len()
te["nword"] = te["ntext"].str.split().str.len()
bangla = re.compile(r"[ঀ-৿]")
te["has_bangla"] = te["ntext"].str.contains(bangla)

very_short = te[te["nword"] <= 2]
no_bangla = te[~te["has_bangla"]]
empty = te[te["nchar"] == 0]

print(f"   empty after normalization:      {len(empty)}")
print(f"   <= 2 words:                     {len(very_short)} ({100*len(very_short)/len(te):.2f}%)")
print(f"   contains no Bangla characters:  {len(no_bangla)} ({100*len(no_bangla)/len(te):.2f}%)")
print(f"   median words: {te['nword'].median():.0f}   mean: {te['nword'].mean():.1f}")
print("\n   Label distribution among <=2-word items:")
print(very_short["label"].value_counts().to_string())
print("\n   Sample <=2-word items labelled as hate:")
sh = very_short[very_short["label"] != "None"].head(10)
for _, r in sh.iterrows():
    print(f"     [{r['label']:<14}] {r['text']}")
very_short.to_csv(OUT / "very_short_items_1A.csv", index=False)
report["degenerate"] = dict(empty=len(empty), le2_words=len(very_short),
                            no_bangla=len(no_bangla),
                            median_words=float(te["nword"].median()))

# ---------- 5. 1C schema coherence ----------
print("\n" + "=" * 70)
print("5. SUBTASK 1C SCHEMA COHERENCE (test set)")
print("=" * 70)
d = load("1C", "test_with_labels")
# A 'None' hate_type should co-occur with 'Little to None' severity and 'None' target.
inc1 = d[(d.hate_type == "None") & (d.hate_severity != "Little to None")]
inc2 = d[(d.hate_type == "None") & (d.to_whom != "None")]
inc3 = d[(d.hate_type != "None") & (d.to_whom == "None")]
inc4 = d[(d.hate_type != "None") & (d.hate_severity == "Little to None")]
print(f"   type=None  but severity!=Little to None : {len(inc1)}")
print(f"   type=None  but target!=None            : {len(inc2)}")
print(f"   type!=None but target==None            : {len(inc3)}")
print(f"   type!=None but severity==Little to None: {len(inc4)}")
tot_inc = len(pd.concat([inc1, inc2, inc3, inc4]).drop_duplicates(subset=["id"]))
print(f"   >>> rows with >=1 schema incoherence   : {tot_inc} "
      f"({100*tot_inc/len(d):.2f}% of test set)")
pd.concat([inc1, inc2, inc3, inc4]).drop_duplicates(subset=["id"]).to_csv(
    OUT / "schema_incoherent_1C.csv", index=False)
report["schema_coherence_1C"] = dict(
    type_none_sev_not_little=len(inc1), type_none_target_not_none=len(inc2),
    type_not_none_target_none=len(inc3), type_not_none_sev_little=len(inc4),
    total_incoherent=int(tot_inc), n_test=len(d),
    pct=round(100*tot_inc/len(d), 2))

with open(OUT / "integrity_report.json", "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("\n\nFull report -> audit/results/integrity_report.json")
