"""Figures for the BLP-2025 audit paper. Outputs vector PDFs for LaTeX."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path("/home/claude/paper"); OUT.mkdir(exist_ok=True)

BLUE, ORANGE = "#2a78d6", "#eb6834"       # validated CVD-safe pair
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d8d8d4"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.labelcolor": INK,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

N = 10200
BOARD = {
    "1A: Hate type": [("Code_Gen", .7362), ("SyntaxMind", .7345), ("zannatul_007", .7340),
                      ("TeamHateMate", .7331), ("Ecstasy", .7328)],
    "1B: Target": [("TeamHateMate", .7356), ("Code_Gen", .7335), ("Gradient Masters", .7328),
                   ("Ecstasy", .7317), ("SyntaxMind", .7317)],
    "1C: Joint": [("TeamHateMate", .7392), ("CUET-NLP_Zenith", .7378), ("Code_Gen", .7361),
                  ("Ecstasy", .7332), ("BElite", .7312)],
}

def wilson(p, n, z=1.96):
    d = 1 + z**2/n; c = p + z**2/(2*n)
    h = z*np.sqrt(p*(1-p)/n + z**2/(4*n**2))
    return (c-h)/d, (c+h)/d

# ---------------- Figure 1: leaderboard CIs ----------------
fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.15), sharex=False)
for ax, (title, teams) in zip(axes, BOARD.items()):
    names = [t for t, _ in teams]
    ps = np.array([p for _, p in teams])
    los, his = zip(*[wilson(p, N) for p in ps])
    y = np.arange(len(ps))[::-1]

    lead_lo, lead_hi = wilson(ps[0], N)
    ax.axvspan(100*lead_lo, 100*lead_hi, color=BLUE, alpha=0.10, lw=0,
               zorder=0)
    ax.errorbar(100*ps, y, xerr=[100*(ps-np.array(los)), 100*(np.array(his)-ps)],
                fmt="o", color=BLUE, ecolor=BLUE, elinewidth=1.1,
                capsize=2.4, capthick=0.9, ms=4.2, zorder=3,
                markeredgecolor="white", markeredgewidth=0.6)
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_title(title, pad=5)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(71.9, 75.1)
axes[1].set_xlabel("micro-F1 (%) with 95% Wilson CI, n = 10,200")
fig.tight_layout(w_pad=1.4)
fig.savefig(OUT / "fig1_leaderboard.pdf")
print("fig1 ->", OUT / "fig1_leaderboard.pdf")

# ---------------- Figure 2: metric sensitivity ----------------
CLASSES = [("None", 5751), ("Abusive", 2312), ("Political Hate", 1220),
           ("Profane", 709), ("Religious Hate", 179), ("Sexism", 29)]
se_pp = 100*np.sqrt(0.735*0.265/N)

fig, ax = plt.subplots(figsize=(3.45, 2.2))
names = [c for c, _ in CLASSES][::-1]
swings = np.array([100*n/N for _, n in CLASSES])[::-1]
ns = [n for _, n in CLASSES][::-1]
y = np.arange(len(names))
cols = [ORANGE if s_ < se_pp else BLUE for s_ in swings]

# Dot plot, not bars: on a log axis a bar's LENGTH does not encode magnitude
# proportionally, so bars would misrepresent the comparison.
ax.axvspan(0.15, se_pp, color=INK, alpha=0.055, lw=0, zorder=0)
ax.axvline(se_pp, color=INK, ls="--", lw=0.9, zorder=4)
for yi, (sw, c) in enumerate(zip(swings, cols)):
    ax.plot([0.15, sw], [yi, yi], color=c, lw=0.8, alpha=0.35, zorder=2)
ax.scatter(swings, y, s=42, color=cols, zorder=5,
           edgecolor="white", linewidth=0.7)
ax.set_xscale("log")
ax.set_yticks(y)
ax.set_yticklabels([f"{nm}  (n={n:,})" for nm, n in zip(names, ns)])
ax.set_xlabel("max. micro-F1 swing (pp)")
ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
ax.set_axisbelow(True)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.set_xlim(0.15, 200)
ax.set_ylim(-0.7, len(names)-0.3)

for yi, sw in enumerate(swings):
    if sw < se_pp:          # flagged point: label above, clear of rule and ticks
        ax.text(sw, yi + 0.34, f"{sw:.2f}", va="bottom", ha="center",
                fontsize=6.6, color=ORANGE)
    else:
        ax.text(sw*1.28, yi, f"{sw:.2f}", va="center", ha="left",
                fontsize=6.6, color=MUTED)
ax.text(se_pp*0.88, len(names)-0.55, "sampling noise floor 0.44 pp",
        fontsize=6.3, color=INK, ha="right", va="center")
fig.tight_layout()
fig.savefig(OUT / "fig2_metric_sensitivity.pdf")
print("fig2 ->", OUT / "fig2_metric_sensitivity.pdf")

# PNG previews
for src in ["fig1_leaderboard", "fig2_metric_sensitivity"]:
    pass
print("done")

# ---------------- Figure 3: win-rate vs gap ----------------
import pandas as pd
pw = pd.read_csv("/home/claude/audit/results/gap_vs_winrate.csv")
fig, ax = plt.subplots(figsize=(3.45, 2.35))

BLP_MAX = 0.21   # largest BLP top-2 gap
ax.axvspan(0.008, BLP_MAX, color=ORANGE, alpha=0.13, lw=0, zorder=0)
ax.axhline(50, color=MUTED, ls=":", lw=0.8, zorder=1)
ax.axhline(95, color=INK, ls="--", lw=0.8, zorder=1)

ax.scatter(pw.gap_pp, 100*pw.win_rate, s=26, color=BLUE, alpha=0.75,
           zorder=4, edgecolor="white", linewidth=0.5)
near = pw.nsmallest(1, "gap_pp").iloc[0]
ax.scatter([near.gap_pp], [100*near.win_rate], s=64, color=ORANGE,
           zorder=6, edgecolor="white", linewidth=0.8)
ax.annotate(f"{near.gap_pp:.2f} pp gap\n{100*near.win_rate:.0f}% - a coin flip",
            xy=(near.gap_pp, 100*near.win_rate), xytext=(0.35, 62),
            fontsize=6.4, color=ORANGE, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
ax.text(0.115, 101.5, "BLP-2025\ntop-2 gaps", fontsize=6.3, color=ORANGE,
        ha="center", va="bottom", linespacing=1.15)
ax.text(0.0095, 95.6, "95%", fontsize=6.2, color=INK, ha="left", va="bottom")

ax.set_xscale("log")
ax.set_xlim(0.008, 22)
ax.set_ylim(44, 108)
ax.set_yticks([50, 60, 70, 80, 90, 100])
ax.set_xlabel("observed micro-F1 gap between two systems (pp)")
ax.set_ylabel("bootstrap win rate (%)")
ax.grid(color=GRID, lw=0.5, zorder=0)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "fig3_gap_vs_winrate.pdf")
print("fig3 ->", OUT / "fig3_gap_vs_winrate.pdf")
