"""
BLP-2025 Task 1 — Statistical audit of the leaderboard.

Question: are the reported rankings statistically distinguishable?

Reported micro-F1 (Hasan et al., BLP-2025 Task 1 overview), n_test = 10,200:

  1A: Code_Gen .7362 | SyntaxMind .7345 | zannatul_007 .7340 | TeamHateMate .7331 | Ecstasy .7328
  1B: TeamHateMate .7356 | Code_Gen .7335 | Gradient Masters .7328 | Ecstasy .7317 | SyntaxMind .7317
  1C: TeamHateMate .7392 | CUET-NLP_Zenith .7378 | Code_Gen .7361 | Ecstasy .7332 | BElite .7312

We do not have per-system predictions, so we bound the question two ways:
  (A) Wilson CI on a single system's score.
  (B) McNemar sensitivity: how similar would two systems have to be for the
      observed gap to reach p < .05?  Then check whether that is plausible.
  (C) Monte-Carlo: simulate two equal-skill systems and measure how often the
      observed top-5 spread arises by chance alone.
"""
import numpy as np
from scipy import stats
import json
from pathlib import Path
import pathlib
_ROOT = pathlib.Path(__file__).resolve().parent.parent

OUT = _ROOT / "results"; OUT.mkdir(parents=True, exist_ok=True)
N = 10200
rng = np.random.default_rng(20260819)

BOARD = {
    "1A": [("Code_Gen", .7362), ("SyntaxMind", .7345), ("zannatul_007", .7340),
           ("TeamHateMate", .7331), ("Ecstasy", .7328)],
    "1B": [("TeamHateMate", .7356), ("Code_Gen", .7335), ("Gradient Masters", .7328),
           ("Ecstasy", .7317), ("SyntaxMind", .7317)],
    "1C": [("TeamHateMate", .7392), ("CUET-NLP_Zenith", .7378), ("Code_Gen", .7361),
           ("Ecstasy", .7332), ("BElite", .7312)],
}

def wilson(p, n, z=1.96):
    d = 1 + z**2/n
    c = p + z**2/(2*n)
    h = z*np.sqrt(p*(1-p)/n + z**2/(4*n**2))
    return ((c-h)/d, (c+h)/d)

report = {}
print("=" * 74)
print("A.  WILSON 95% CONFIDENCE INTERVALS  (n = 10,200)")
print("=" * 74)
for sub, teams in BOARD.items():
    print(f"\nSubtask {sub}")
    lo_hi = []
    for name, p in teams:
        lo, hi = wilson(p, N)
        lo_hi.append((lo, hi))
        print(f"   {name:<20} {p:.4f}   95% CI [{lo:.4f}, {hi:.4f}]   +/-{100*(hi-lo)/2:.2f} pp")
    top_lo = lo_hi[0][0]
    overlap = sum(1 for lo, hi in lo_hi if hi >= top_lo)
    spread = teams[0][1] - teams[-1][1]
    print(f"   -> top-5 spread = {100*spread:.2f} pp; "
          f"CI half-width = {100*(lo_hi[0][1]-lo_hi[0][0])/2:.2f} pp")
    print(f"   -> {overlap}/5 teams have CIs overlapping the leader's lower bound")
    report[f"{sub}_wilson"] = dict(spread_pp=round(100*spread, 3),
                                   ci_halfwidth_pp=round(100*(lo_hi[0][1]-lo_hi[0][0])/2, 3),
                                   n_overlapping=overlap)

print("\n" + "=" * 74)
print("B.  McNEMAR SENSITIVITY  — how similar must two systems be for the")
print("    observed gap to be significant at p < .05?")
print("=" * 74)
print("\n  McNemar on paired predictions: with b, c the discordant counts,")
print("  the gap is d = (b - c)/n.  Significance needs |b - c| > 1.96*sqrt(b + c).")
print("  Solving for the maximum tolerable discordance b + c:\n")
for sub, teams in BOARD.items():
    d = teams[0][1] - teams[1][1]          # leader vs runner-up
    diff_count = d * N
    max_disc = (diff_count / 1.96) ** 2
    print(f"   {sub}: leader-vs-2nd gap = {100*d:.2f} pp = {diff_count:.0f} items")
    print(f"        -> the two systems must disagree on FEWER than {max_disc:.0f} "
          f"of {N} items ({100*max_disc/N:.2f}%)")
    report[f"{sub}_mcnemar_max_discordance"] = dict(
        gap_pp=round(100*d, 3), gap_items=round(float(diff_count), 1),
        max_discordant_items=round(float(max_disc), 1),
        max_discordant_pct=round(100*float(max_disc)/N, 3))
print("\n  Two independently-built systems at ~73.5% accuracy on a 6-way task")
print("  typically disagree on 10-20% of items (1,000-2,000 here). Required")
print("  discordance is one to two ORDERS OF MAGNITUDE below that.")
print("  => None of the top-2 gaps can be statistically significant.")

print("\n" + "=" * 74)
print("C.  MONTE-CARLO — two systems of IDENTICAL true skill (p = .735)")
print("=" * 74)
TRUE_P = 0.735
for rho_label, disc in [("high agreement (5% discordant)", 0.05),
                        ("typical (15% discordant)", 0.15),
                        ("low agreement (25% discordant)", 0.25)]:
    # Simulate: n*disc items where the two systems differ, split ~50/50 under H0.
    n_disc = int(N * disc)
    sims = rng.binomial(n_disc, 0.5, size=200_000)
    gaps = np.abs(2 * sims - n_disc) / N
    print(f"\n   {rho_label}")
    print(f"      median |gap| by chance : {100*np.median(gaps):.3f} pp")
    print(f"      95th percentile        : {100*np.percentile(gaps, 95):.3f} pp")
    for sub, teams in BOARD.items():
        obs = teams[0][1] - teams[1][1]
        pval = float((gaps >= obs).mean())
        print(f"      P(chance gap >= {sub} observed {100*obs:.2f} pp) = {pval:.3f}")
        report.setdefault(f"{sub}_montecarlo", {})[rho_label] = round(pval, 4)

print("\n" + "=" * 74)
print("D.  TOP-5 SPREAD vs. SAMPLING NOISE")
print("=" * 74)
for sub, teams in BOARD.items():
    spread = teams[0][1] - teams[-1][1]
    se_single = np.sqrt(TRUE_P*(1-TRUE_P)/N)
    print(f"   {sub}: observed top-5 spread {100*spread:.2f} pp  vs  "
          f"1 SE of a single score = {100*se_single:.2f} pp  "
          f"-> {spread/se_single:.2f} SE")
report["se_single_score_pp"] = round(100*float(np.sqrt(TRUE_P*(1-TRUE_P)/N)), 4)

with open(OUT / "leaderboard_stats.json", "w") as f:
    json.dump(report, f, indent=2)
print("\n\n-> audit/results/leaderboard_stats.json")
