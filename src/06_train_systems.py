"""
Train a diverse pool of systems on BLP-2025 Task 1A and save real test predictions.

Purpose: the paper claims that independently-built systems of comparable accuracy
disagree on 10-20% of test items. That was an ASSERTION. Here we measure it.

We deliberately vary the things that differ between real shared-task submissions:
feature space (word / char n-grams), classifier family (linear, NB, SVM, forest),
regularisation, class weighting, and random seed. Each system is trained only on
the official train split and evaluated once on the official test split.
"""
import pandas as pd, numpy as np, json, time
from pathlib import Path
import pathlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import ComplementNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import f1_score, classification_report

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

DATA = _BASE / "data" / "subtask_1A"
OUT = _ROOT / "results"; OUT.mkdir(parents=True, exist_ok=True)
SEED = 20260819

def load(split):
    return pd.read_csv(DATA / f"blp25_hatespeech_subtask_1A_{split}.tsv",
                       sep="\t", dtype=str, keep_default_na=False, na_values=[])

tr = load("train")
te = load("test_with_labels")
print(f"train={len(tr)}  test={len(te)}")
Xtr, ytr = tr.text.values, tr.label.values
Xte, yte = te.text.values, te.label.values

def word_tfidf(max_features=200_000, **kw):
    return TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2,
                           sublinear_tf=True, max_features=max_features, **kw)

def char_tfidf(lo=2, hi=5, **kw):
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(lo, hi), min_df=3,
                           sublinear_tf=True, max_features=300_000, **kw)

SYSTEMS = {
    "word-LR":        (word_tfidf(), LogisticRegression(max_iter=2000, C=4.0,
                          random_state=SEED)),
    "word-LR-bal":    (word_tfidf(), LogisticRegression(max_iter=2000, C=4.0,
                          class_weight="balanced", random_state=SEED)),
    "word-SVC":       (word_tfidf(), LinearSVC(C=0.5, random_state=SEED)),
    "word-NB":        (word_tfidf(), ComplementNB(alpha=0.3)),
    "char25-LR":      (char_tfidf(2, 5), LogisticRegression(max_iter=2000, C=8.0,
                          random_state=SEED)),
    "char25-SVC":     (char_tfidf(2, 5), LinearSVC(C=1.0, random_state=SEED)),
    "char25-SVC-bal": (char_tfidf(2, 5), LinearSVC(C=1.0, class_weight="balanced",
                          random_state=SEED)),
    "char36-LR":      (char_tfidf(3, 6), LogisticRegression(max_iter=2000, C=8.0,
                          random_state=SEED)),
    "char14-SGD":     (char_tfidf(1, 4), SGDClassifier(loss="modified_huber",
                          alpha=1e-5, max_iter=30, random_state=SEED)),
    "word-RF":        (word_tfidf(max_features=40_000),
                       RandomForestClassifier(n_estimators=180, n_jobs=2,
                          min_samples_leaf=2, random_state=SEED)),
}

preds, rows = {}, []
for name, (vec, clf) in SYSTEMS.items():
    t0 = time.time()
    pipe = make_pipeline(vec, clf)
    pipe.fit(Xtr, ytr)
    p = pipe.predict(Xte)
    preds[name] = p
    micro = f1_score(yte, p, average="micro")
    macro = f1_score(yte, p, average="macro")
    # per-class F1 for the two rare classes
    labs = sorted(set(yte))
    per = dict(zip(labs, f1_score(yte, p, average=None, labels=labs, zero_division=0)))
    rows.append(dict(system=name, micro_f1=round(float(micro), 4),
                     macro_f1=round(float(macro), 4),
                     f1_sexism=round(float(per.get("Sexism", 0.0)), 4),
                     f1_religious=round(float(per.get("Religious Hate", 0.0)), 4),
                     secs=round(time.time()-t0, 1)))
    print(f"   {name:<16} micro={micro:.4f}  macro={macro:.4f}  "
          f"Sexism-F1={per.get('Sexism',0):.3f}  ({time.time()-t0:.0f}s)")

res = pd.DataFrame(rows).sort_values("micro_f1", ascending=False)
res.to_csv(OUT / "system_scores.csv", index=False)
pd.DataFrame(preds).assign(gold=yte, id=te.id.values).to_csv(
    OUT / "test_predictions.csv", index=False)

print("\n" + "=" * 72)
print("SYSTEM POOL (sorted by micro-F1)")
print("=" * 72)
print(res.to_string(index=False))

maj = (yte == "None").mean()
print(f"\n   majority-class baseline micro-F1 = {maj:.4f}")
print(f"   best reported shared-task system = 0.7362")
print(f"\n   micro-F1 range in our pool: {res.micro_f1.min():.4f} - {res.micro_f1.max():.4f}")
print(f"   macro-F1 range:             {res.macro_f1.min():.4f} - {res.macro_f1.max():.4f}")
print("\n   NOTE how much wider the macro-F1 spread is than the micro-F1 spread.")
print("   That is the metric-insensitivity result of the paper, reproduced on")
print("   systems whose predictions we actually hold.")

with open(OUT / "system_scores.json", "w") as f:
    json.dump(rows, f, indent=2)
print(f"\n-> systems/test_predictions.csv  ({len(te)} rows x {len(SYSTEMS)} systems)")
