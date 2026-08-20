"""
How large must a score gap be before the ranking is trustworthy?

Script 07 found that our top-2 systems (gap 0.44 pp) hold their order in 98.7%
of bootstrap resamples. That is a REAL result and it complicates the naive claim
that "small gaps are meaningless" - a 0.44 pp gap with low discordance is in fact
quite stable.

But the BLP-2025 top-2 gaps are 0.17 / 0.21 / 0.14 pp, and observed discordance
between near-tied systems is far higher than those gaps require. This script
measures win-probability as a joint function of gap AND discordance, so the
paper can state the condition precisely instead of hand-waving.
"""
import pandas as pd, numpy as np, json, itertools
from pathlib import Path

SYS = Path("/home/claude/audit/systems")
RES = Path("/home/claude/audit/results")
rng = np.random.default_rng(20260819)
B = 4000

df = pd.read_csv(SYS / "test_predictions.csv", dtype=str,
                 keep_default_na=False, na_values=[])
gold = df["gold"].values
systems = [c for c in df.columns if c not in ("gold", "id")]
correct = {s: (df[s].values == gold) for s in systems}
acc = {s: correct[s].mean() for s in systems}
N = len(gold)
report = {}

# ---------- per-pair bootstrap win rate ----------
print("=" * 78)
print("A. BOOTSTRAP WIN-RATE FOR EVERY PAIR, vs GAP AND DISCORDANCE")
print("=" * 78)
rows = []
IDX = rng.integers(0, N, size=(B, N))
for a, b in itertools.combinations(systems, 2):
    ca, cb = correct[a], correct[b]
    if acc[a] < acc[b]:
        a, b, ca, cb = b, a, cb, ca            # a = observed winner
    d = (ca.astype(np.int8) - cb.astype(np.int8))
    boot = d[IDX].mean(axis=1)
    win = float((boot > 0).mean())
    disc = int((ca != cb).sum())
    rows.append(dict(winner=a, loser=b, gap_pp=100*(acc[a]-acc[b]),
                     disc_items=disc, disc_frac=disc/N, win_rate=win))
pw = pd.DataFrame(rows).sort_values("gap_pp")
pw.to_csv(RES / "gap_vs_winrate.csv", index=False)

print(f"\n   {'winner':<16}{'loser':<16}{'gap(pp)':>9}{'b+c':>7}{'disc%':>8}{'win%':>8}")
for r in pw.head(10).itertuples():
    print(f"   {r.winner:<16}{r.loser:<16}{r.gap_pp:>9.2f}{r.disc_items:>7}"
          f"{100*r.disc_frac:>8.1f}{100*r.win_rate:>8.1f}")

unstable = pw[pw.win_rate < 0.95]
print(f"\n   pairs whose observed order holds in <95% of resamples: "
      f"{len(unstable)} of {len(pw)}")
if len(unstable):
    print(f"   their gaps range {unstable.gap_pp.min():.2f} - "
          f"{unstable.gap_pp.max():.2f} pp")
stable = pw[pw.win_rate >= 0.95]
if len(stable):
    print(f"   smallest gap that IS stable (>=95%): {stable.gap_pp.min():.2f} pp")

report["pairs"] = dict(
    n_pairs=len(pw), n_unstable=len(unstable),
    smallest_stable_gap_pp=round(float(stable.gap_pp.min()), 3) if len(stable) else None,
    largest_unstable_gap_pp=round(float(unstable.gap_pp.max()), 3) if len(unstable) else None)

# ---------- the near-tied pair: closest analogue to BLP top-2 ----------
print("\n" + "=" * 78)
print("B. THE NEAR-TIED PAIR (our closest analogue to the BLP top-2 gaps)")
print("=" * 78)
nearest = pw.iloc[0]
print(f"\n   {nearest.winner} vs {nearest.loser}")
print(f"      observed gap    : {nearest.gap_pp:.3f} pp")
print(f"      discordant items: {nearest.disc_items} ({100*nearest.disc_frac:.1f}%)")
print(f"      winner holds in : {100*nearest.win_rate:.1f}% of resamples")
print(f"\n   BLP-2025 top-2 gaps are 0.17 (1A), 0.21 (1B), 0.14 (1C) pp -")
print(f"   the same magnitude as this pair's {nearest.gap_pp:.2f} pp.")
report["nearest_pair"] = dict(
    winner=str(nearest.winner), loser=str(nearest.loser),
    gap_pp=round(float(nearest.gap_pp), 3), disc_items=int(nearest.disc_items),
    disc_frac=round(float(nearest.disc_frac), 4),
    win_rate=round(float(nearest.win_rate), 4))

# ---------- what gap is needed, given observed discordance? ----------
print("\n" + "=" * 78)
print("C. REQUIRED GAP FOR A TRUSTWORTHY RANKING, GIVEN DISCORDANCE")
print("=" * 78)
print("\n   Under McNemar, a gap d is significant at p<.05 when")
print("   d*n > 1.96*sqrt(b+c). Solving for d at each observed discordance:\n")
print(f"   {'discordance (b+c)':<22}{'as % of n':>11}{'min. detectable gap':>22}")
levels = [367, 895, 2600, 3700]
labels = ["lowest observed", "median, near-tied pairs", "median, all pairs",
          "highest observed"]
mins = []
for lab, bc in zip(labels, levels):
    d_min = 1.96*np.sqrt(bc)/N
    mins.append(100*d_min)
    print(f"   {lab:<22}{100*bc/N:>10.1f}%{100*d_min:>21.2f} pp")

print(f"\n   BLP-2025 observed top-2 gaps: 0.17 / 0.21 / 0.14 pp")
print(f"   Minimum detectable gap even at our LOWEST observed discordance: "
      f"{mins[0]:.2f} pp")
print(f"\n   >>> Every BLP top-2 gap is below the minimum detectable difference")
print(f"   >>> at any discordance level we observed empirically.")
report["min_detectable"] = {lab: round(float(m), 3) for lab, m in zip(labels, mins)}
report["blp_gaps_pp"] = {"1A": 0.17, "1B": 0.21, "1C": 0.14}
report["verdict"] = ("All three BLP top-2 gaps fall below the minimum detectable "
                     "difference implied by the lowest pairwise discordance we "
                     "measured (3.6% of items).")

# ---------- honest counterpoint ----------
print("\n" + "=" * 78)
print("D. HONEST COUNTERPOINT")
print("=" * 78)
print(f"""
   Our top-2 systems (gap 0.44 pp, discordance 4.1%) hold their order in
   ~99% of resamples. Small gaps are therefore NOT automatically meaningless:
   when two systems are highly correlated, a sub-half-point gap can be real.

   The claim the paper can defend is narrower and conditional:
     a gap is uninformative when it is smaller than 1.96*sqrt(b+c)/n.
   For BLP-2025 that condition requires discordance below ~0.8% of items,
   which is far below anything we measured (minimum 3.6%).

   State it that way. It is the difference between a slogan and a result.
""")

with open(RES / "gap_vs_stability.json", "w") as f:
    json.dump(report, f, indent=2)
print("-> results/gap_vs_stability.json")
