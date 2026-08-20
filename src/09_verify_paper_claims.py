"""
INDEPENDENT VERIFICATION of every numerical claim in the paper.

This script deliberately does NOT import or reuse any function from scripts
01-08. Every quantity is recomputed from the raw TSV files with formulas
written out longhand, then asserted against the value printed in the paper.
If a claim in main.tex is wrong, this fails loudly.

Run:  python 09_verify_paper_claims.py
"""
import csv, math, random
from pathlib import Path

import os
_ROOT = Path(__file__).resolve().parent.parent
_C = [os.environ.get("BLP25_DATA"), _ROOT / "blp25_task1", _ROOT.parent / "blp25_task1"]
_BASE = next((Path(c) for c in _C if c and Path(c).exists()), None)
if _BASE is None:
    raise SystemExit("Dataset not found. Set BLP25_DATA or clone blp25_task1 alongside.")
DATA = _BASE / "data"
PRED = _ROOT / "results" / "test_predictions.csv"

PASS, FAIL = [], []

def check(name, got, want, tol, unit=""):
    ok = abs(got - want) <= tol
    (PASS if ok else FAIL).append(name)
    mark = "PASS" if ok else "**FAIL**"
    print(f"  [{mark}] {name:<52} got {got:.4f}{unit}  paper says {want}{unit}")
    return ok

# ---- read raw data with the standard library only (no pandas) ----
def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

te1a = read_tsv(DATA / "subtask_1A" / "blp25_hatespeech_subtask_1A_test_with_labels.tsv")
te1b = read_tsv(DATA / "subtask_1B" / "blp25_hatespeech_subtask_1B_test_with_labels.tsv")
te1c = read_tsv(DATA / "subtask_1C" / "blp25_hatespeech_subtask_1C_test_with_labels.tsv")
tr1a = read_tsv(DATA / "subtask_1A" / "blp25_hatespeech_subtask_1A_train.tsv")

N = len(te1a)
print("=" * 78)
print("INDEPENDENT VERIFICATION OF PAPER CLAIMS")
print("=" * 78)
print(f"\nSplit sizes read from disk: train={len(tr1a)}  test={N}")
check("test set size", N, 10200, 0)
check("train set size", len(tr1a), 35522, 0)

# ---- 1. class counts and the majority baseline ----
print("\n1. CLASS DISTRIBUTION AND MAJORITY BASELINE")
counts = {}
for r in te1a:
    counts[r["label"]] = counts.get(r["label"], 0) + 1
for k in sorted(counts, key=lambda x: -counts[x]):
    print(f"      {k:<16} {counts[k]:>6}   {counts[k]/N:.4f}")
check("None count", counts["None"], 5751, 0)
check("Sexism count", counts["Sexism"], 29, 0)
check("Religious Hate count", counts["Religious Hate"], 179, 0)
check("majority-class baseline", counts["None"]/N, 0.5638, 0.0001)

# ---- 2. sampling standard error ----
print("\n2. SAMPLING STANDARD ERROR   SE = sqrt(p(1-p)/n)")
p = 0.735
se = math.sqrt(p*(1-p)/N)
print(f"      sqrt({p} * {1-p:.3f} / {N}) = {se:.6f}")
check("SE in percentage points", 100*se, 0.44, 0.005, " pp")

# ---- 3. micro-F1 swing bounds per class ----
print("\n3. MAXIMUM MICRO-F1 SWING PER CLASS  = class share")
check("Sexism max swing", 100*counts["Sexism"]/N, 0.28, 0.005, " pp")
check("Religious Hate max swing", 100*counts["Religious Hate"]/N, 1.75, 0.005, " pp")
below = 100*counts["Sexism"]/N < 100*se
print(f"      Sexism swing below the noise floor? {below}")
assert below, "core claim of section 7 does not hold!"

# ---- 4. Wilson interval half-width ----
print("\n4. WILSON 95% INTERVAL (written out longhand)")
def wilson_lo_hi(p_, n, z=1.96):
    denom = 1 + z*z/n
    centre = (p_ + z*z/(2*n)) / denom
    half = (z*math.sqrt(p_*(1-p_)/n + z*z/(4*n*n))) / denom
    return centre - half, centre + half
lo, hi = wilson_lo_hi(0.7362, N)
print(f"      p=0.7362 -> [{lo:.4f}, {hi:.4f}]")
check("Wilson half-width", 100*(hi-lo)/2, 0.86, 0.02, " pp")

# do all five 1A teams overlap the leader's lower bound?
teams_1a = [0.7362, 0.7345, 0.7340, 0.7331, 0.7328]
lead_lo, _ = wilson_lo_hi(teams_1a[0], N)
overlap = sum(1 for t in teams_1a if wilson_lo_hi(t, N)[1] >= lead_lo)
print(f"      teams whose CI reaches the leader's lower bound: {overlap}/5")
check("overlapping teams (1A)", overlap, 5, 0)
check("top-5 spread (1A)", 100*(teams_1a[0]-teams_1a[-1]), 0.34, 0.005, " pp")

# ---- 5. McNemar inversion ----
print("\n5. McNEMAR INVERSION   |b-c| > 1.96*sqrt(b+c)")
for sub, gap in [("1A", 0.7362-0.7345), ("1B", 0.7356-0.7335), ("1C", 0.7392-0.7378)]:
    diff = gap * N
    max_bc = (diff/1.96)**2
    print(f"      {sub}: gap {100*gap:.2f} pp = {diff:.1f} items -> b+c must be < {max_bc:.0f}")
check("1A max discordance", (0.0017*N/1.96)**2, 78, 1.0, " items")
check("1B max discordance", ((0.7356-0.7335)*N/1.96)**2, 119, 2.0, " items")
check("1C max discordance", ((0.7392-0.7378)*N/1.96)**2, 53, 2.0, " items")

# ---- 6. kappa -> annotation ceiling ----
print("\n6. ANNOTATION CEILING FROM FLEISS' KAPPA")
shares = [counts[k]/N for k in counts]
Pe = sum(s*s for s in shares)
Po = 0.71*(1-Pe) + Pe
print(f"      Pe = sum(p_i^2)              = {Pe:.4f}")
print(f"      Po = k(1-Pe)+Pe              = {Po:.4f}")
# solve alpha^2 + (1-alpha)^2/5 = Po  by bisection, written out
def f(a): return a*a + (1-a)**2/5 - Po
lo_a, hi_a = 1/6, 1.0
for _ in range(200):
    mid = (lo_a+hi_a)/2
    if f(lo_a)*f(mid) <= 0: hi_a = mid
    else: lo_a = mid
alpha = (lo_a+hi_a)/2
ceiling = alpha**3 + 3*alpha**2*(1-alpha)
print(f"      alpha (per-annotator acc.)   = {alpha:.4f}")
print(f"      majority-of-3 gold accuracy  = {ceiling:.4f}")
check("chance agreement Pe", Pe, 0.3887, 0.0005)
check("observed agreement Po", Po, 0.8227, 0.0005)
check("per-annotator accuracy", alpha, 0.906, 0.002)
check("annotation ceiling", ceiling, 0.975, 0.002)
check("gap to best system", 100*(ceiling-0.7362), 23.7, 0.3, " pp")

# ---- 7. schema coherence counts ----
print("\n7. SCHEMA COHERENCE (subtask 1C)")
no_target = sum(1 for r in te1c if r["hate_type"] != "None" and r["to_whom"] == "None")
sev_little = sum(1 for r in te1c if r["hate_type"] != "None"
                 and r["hate_severity"] == "Little to None")
none_bad = sum(1 for r in te1c if r["hate_type"] == "None"
               and (r["to_whom"] != "None" or r["hate_severity"] != "Little to None"))
print(f"      type!=None & target==None      : {no_target}")
print(f"      type!=None & severity==Little  : {sev_little}")
print(f"      type==None but other fields set: {none_bad}")
check("items with hate type but no target", no_target, 342, 0, " items")
check("items with hate type, Little severity", sev_little, 986, 0, " items")
check("percent of test with no target", 100*no_target/N, 3.35, 0.02, "%")

# ---- 8. integrity: duplicates and leakage ----
print("\n8. DATA INTEGRITY")
def norm(t): return " ".join(t.split())
train_texts = {norm(r["text"]) for r in tr1a}
leak = sum(1 for r in te1a if norm(r["text"]) in train_texts)
seen = {}
conflicts = 0
for r in te1a + tr1a:
    k = norm(r["text"])
    if k in seen and seen[k] != r["label"]:
        conflicts += 1
    seen[k] = r["label"]
short = sum(1 for r in te1a if len(norm(r["text"]).split()) <= 2)
print(f"      verbatim train/test leakage    : {leak}")
print(f"      duplicate texts, conflicting   : {conflicts}")
print(f"      test items of <=2 words        : {short}")
check("train/test leakage", leak, 0, 0, " items")
check("conflicting duplicate labels", conflicts, 0, 0, " items")
check("degenerate short items", short, 0, 0, " items")

# ---- 9. discordance, from the prediction file ----
print("\n9. MEASURED DISCORDANCE (from saved predictions)")
rows = read_tsv_pred = list(csv.DictReader(open(PRED, encoding="utf-8")))
sys_names = [c for c in rows[0] if c not in ("gold", "id")]
gold = [r["gold"] for r in rows]
preds = {s: [r[s] for r in rows] for s in sys_names}
disc_fracs, mcn_fracs = [], []
for i in range(len(sys_names)):
    for j in range(i+1, len(sys_names)):
        a, b_ = sys_names[i], sys_names[j]
        pa, pb = preds[a], preds[b_]
        disagree = sum(1 for x, y in zip(pa, pb) if x != y)
        bb = sum(1 for x, y, g in zip(pa, pb, gold) if x == g and y != g)
        cc = sum(1 for x, y, g in zip(pa, pb, gold) if x != g and y == g)
        disc_fracs.append(disagree/len(gold))
        mcn_fracs.append((bb+cc)/len(gold))
disc_fracs.sort(); mcn_fracs.sort()
print(f"      pairs compared                 : {len(disc_fracs)}")
print(f"      prediction disagreement range  : {min(disc_fracs):.3f} - {max(disc_fracs):.3f}")
print(f"      McNemar b+c range              : {min(mcn_fracs):.3f} - {max(mcn_fracs):.3f}")
check("min McNemar discordance", 100*min(mcn_fracs), 3.6, 0.15, "%")
check("max McNemar discordance", 100*max(mcn_fracs), 36.3, 0.15, "%")
check("n pairs", len(disc_fracs), 45, 0)

# minimum detectable difference at the lowest observed discordance
min_bc = min(mcn_fracs)*len(gold)
mdd = 1.96*math.sqrt(min_bc)/len(gold)
print(f"      min detectable gap at b+c={min_bc:.0f}: {100*mdd:.3f} pp")
check("minimum detectable gap", 100*mdd, 0.37, 0.02, " pp")
blp_gaps = [0.17, 0.21, 0.14]
print(f"      BLP top-2 gaps {blp_gaps} all below {100*mdd:.2f} pp? "
      f"{all(g < 100*mdd for g in blp_gaps)}")
assert all(g < 100*mdd for g in blp_gaps), "core claim of section 5 does not hold!"

# ---- 10. sexism blindness in the system pool ----
print("\n10. SEXISM DETECTION ACROSS THE SYSTEM POOL")
n_sex = sum(1 for g in gold if g == "Sexism")
zero_tp, best_tp = [], 0
for s in sys_names:
    tp = sum(1 for x, g in zip(preds[s], gold) if x == "Sexism" and g == "Sexism")
    best_tp = max(best_tp, tp)
    if tp == 0:
        zero_tp.append(s)
never = [s for s in sys_names if "Sexism" not in preds[s]]
print(f"      gold Sexism items              : {n_sex}")
print(f"      systems detecting ZERO of them : {len(zero_tp)} -> {', '.join(zero_tp)}")
print(f"      best system detects            : {best_tp} of {n_sex}")
print(f"      systems never emitting the label: {len(never)} ({', '.join(never)})")
check("systems detecting zero Sexism items", len(zero_tp), 5, 0)
check("best system's Sexism detections", best_tp, 3, 0, " items")

# ---- verdict ----
print("\n" + "=" * 78)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
print("=" * 78)
if FAIL:
    print("\nFAILED CHECKS:")
    for f_ in FAIL:
        print("   -", f_)
    raise SystemExit(1)
print("\nEvery numerical claim in the paper is independently reproduced.")
