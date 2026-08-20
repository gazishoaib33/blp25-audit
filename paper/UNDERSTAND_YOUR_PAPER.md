# Understand Your Own Paper
### Everything in it, taught from the ground up

You need to be able to defend every number in this paper without me. A reviewer will
challenge you, your teacher will ask questions, and eventually you'll present it. This
document builds each idea from scratch and traces every figure to where it came from.

Work through it with a calculator. Redo the arithmetic yourself — that's how it becomes
yours.

---

# Part 0 — The paper in one paragraph

> A Bangla hate-speech competition published a ranking of the systems that entered.
> We show the ranking isn't real: the top five are statistically tied. We then test the
> obvious explanation for why everyone stalls at 73% — noisy labels — and find it's wrong;
> the labels are ~97% reliable. The actual problem is the scoring metric, which is
> mathematically incapable of noticing whether a system detects sexist content.

Four claims. Each needs one statistical tool. Let's take them one at a time.

---

# Part 1 — The five tools

## 1.1 Micro-F1, and why it equals accuracy here

F1 is normally the harmonic mean of precision and recall. But there's a special case you
must know, because your whole paper rests on it:

> **When every item gets exactly one gold label and exactly one predicted label,
> micro-F1 = micro-precision = micro-recall = accuracy.**

Why? Micro-averaging pools all classes into one big confusion count. Every prediction is
either right (a true positive for some class) or wrong (simultaneously a false positive for
the predicted class and a false negative for the true class). So:

- micro-precision = correct / total predictions = correct / n
- micro-recall = correct / total gold labels = correct / n

They're identical, so their harmonic mean is the same number. **Micro-F1 is just accuracy
wearing a fancier name.**

**Check it yourself.** The `None` class is 5,751 of 10,200 test items = 0.5638. A system
that predicts `None` for everything gets 5,638 of 10,200 right → accuracy 0.5638. The
organisers report a majority baseline of **0.5638**. Exact match. That's how I knew my data
pipeline was correct.

*This matters because it lets you treat the score as a simple proportion, which unlocks
every tool below.*

## 1.2 Macro-F1 — the other averaging

Macro-F1 computes F1 **separately for each class**, then takes the plain mean.

| | Weighting |
|---|---|
| **Micro** | Every *item* counts once. Big classes dominate. |
| **Macro** | Every *class* counts once. A class with 29 items counts as much as one with 5,751. |

This one difference is the paper's whole §7. With `None` at 56% and `Sexism` at 0.28%,
micro-F1 is essentially "how well do you do on `None` and `Abusive`."

## 1.3 Confidence intervals — and why Wilson, not the textbook formula

A test set is a **sample**. If you'd drawn 10,200 different comments, every system's score
would come out slightly different. A confidence interval says how much wobble to expect.

For a proportion $p$ from $n$ items, the standard error is:

$$SE = \sqrt{\frac{p(1-p)}{n}}$$

**Work it:** $p = 0.735$, $n = 10{,}200$

$$SE = \sqrt{\frac{0.735 \times 0.265}{10200}} = \sqrt{\frac{0.19478}{10200}} = \sqrt{0.0000191} = 0.00437$$

**= 0.44 percentage points.** That single number is the paper's noise floor. Memorise it.

The textbook interval is $p \pm 1.96 \times SE$. That's the **Wald** interval, and it
misbehaves when $p$ is near 0 or 1 (it can produce intervals extending past 100%). The
**Wilson** interval fixes this by inverting the test properly:

$$\frac{p + \frac{z^2}{2n} \pm z\sqrt{\frac{p(1-p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

At $n = 10{,}200$ Wald and Wilson barely differ. **Use Wilson anyway** — it's strictly
better, costs nothing, and a statistically literate reviewer will notice which one you
chose. Half-width comes out to 0.85–0.86 pp.

> **The finding:** the entire top-five spread is 0.34 pp (subtask 1A). The interval
> half-width is 0.86 pp. The spread is smaller than the wobble on any *single* score.

## 1.4 McNemar's test — the right tool for paired systems

Here's a subtlety you must understand, because it's the first thing a good reviewer probes.

Wilson intervals treat two systems as **independent samples**. But they aren't — both were
scored on *the same 10,200 items*. If item #4,231 is a genuinely confusing comment, it's
hard for *both* systems. That shared difficulty is common noise that cancels out when you
compare them directly. Treating them as independent throws away that cancellation and makes
you **too conservative** — you'd miss real differences.

McNemar's test handles paired data. Build a 2×2 table over the items:

| | B correct | B wrong |
|---|---|---|
| **A correct** | $a$ | $b$ |
| **A wrong** | $c$ | $d$ |

Cells $a$ and $d$ are items where the systems agree — they carry **zero information** about
which is better. Only the **discordant** cells $b$ and $c$ matter.

The score gap is:

$$d_{\text{gap}} = \frac{b - c}{n}$$

and under the null hypothesis (systems equally good), each discordant item is a coin flip,
so $b \sim \text{Binomial}(b+c,\ 0.5)$. Significance at $p < .05$ needs:

$$|b - c| > 1.96\sqrt{b + c}$$

### The clever inversion — this is the paper's key move

We don't have the shared task's predictions, so we can't compute $b$ and $c$. **But we can
ask what they would have to be.**

Subtask 1A: leader 0.7362, runner-up 0.7345. Gap = 0.0017.

$$b - c = 0.0017 \times 10200 = 17.34 \text{ items}$$

Substituting into the significance condition:

$$17.34 > 1.96\sqrt{b+c} \;\Rightarrow\; \sqrt{b+c} < 8.85 \;\Rightarrow\; b + c < 78$$

> **So: for that 0.17 pp gap to be significant, the two systems would have to disagree on
> fewer than 78 of 10,200 items — under 0.8%.**

You've turned "I can't run the test" into "here's what the test would require." That's a
genuinely elegant argument, and it's yours to explain.

## 1.5 The bootstrap — simulating test sets you don't have

You have one test set. You want to know what would happen with a different one.

The bootstrap says: **resample your own data with replacement.** Draw 10,200 items from your
10,200, allowing repeats. Some items appear twice, some not at all. That's a plausible
"alternative test set." Rescore both systems. Repeat 4,000 times. Count how often each wins.

If a system wins 99% of resamples, its lead is solid. If it wins 51%, the ranking is a coin
flip.

**We measured:** a pair separated by 0.02 pp wins **51.5%** — a coin flip, exactly as
predicted. A pair separated by 0.44 pp wins 98.7% — genuinely better.

## 1.6 Fleiss' κ, and backing out the annotation ceiling

This is the hardest part of the paper and the softest claim. Understand it well enough to
concede its limits gracefully.

**Fleiss' κ** measures agreement among 3+ raters, corrected for chance:

$$\kappa = \frac{P_o - P_e}{1 - P_e}$$

$P_o$ = observed agreement; $P_e$ = agreement expected by chance. The correction matters:
if 90% of items are `None`, two random annotators agree most of the time by luck alone.
κ = 0 means "no better than chance," κ = 1 means perfect.

### Step 1 — chance agreement

$P_e = \sum p_i^2$, summing squared class proportions:

$$0.564^2 + 0.227^2 + 0.120^2 + 0.070^2 + 0.018^2 + 0.003^2 = 0.3887$$

### Step 2 — recover observed agreement

Rearranging the κ formula: $P_o = \kappa(1 - P_e) + P_e$

$$P_o = 0.71 \times 0.6113 + 0.3887 = 0.4340 + 0.3887 = \mathbf{0.8227}$$

Two annotators agreed 82.3% of the time.

### Step 3 — recover per-annotator accuracy

Model each annotator as correct with probability $\alpha$, else mistaken. Two annotators
agree when both are right, **or** both are wrong in the same way. If wrong answers scatter
uniformly over the other $K-1 = 5$ classes:

$$\alpha^2 + \frac{(1-\alpha)^2}{5} = 0.8227$$

Solve the quadratic → $\alpha = 0.906$.

### Step 4 — how good is a majority vote of 3?

Gold is right if all three are right, or exactly two are:

$$\alpha^3 + 3\alpha^2(1-\alpha) = 0.744 + 0.231 = \mathbf{0.975}$$

> **The ceiling is ~97.5%.** The best system scores 73.6%. So there's a 24-point gap that
> label noise does **not** explain. My starting hypothesis was wrong.

**Why majority voting works so well:** three annotators at 90.6% each produce a 97.5% gold
label. Errors have to *coincide* to survive the vote, and independent errors rarely do.

**Where this is vulnerable — know this cold.** The whole derivation assumes annotators err
**independently**. Real annotators share training, culture, and guidelines, so their
mistakes correlate. Correlated errors survive majority voting, which would push the ceiling
down. The paper reports a second model where errors are maximally correlated — it gives
0.973, barely different — but both are *models*, not measurements. **If a reviewer presses
here, concede it.** That's exactly what the Limitations section is for.

---

# Part 2 — Every number, traced

| Number | Where it comes from | Recompute with |
|---|---|---|
| 0.5638 | 5,751 `None` ÷ 10,200 | `01_data_integrity.py` |
| 0.44 pp | $\sqrt{0.735 \times 0.265 / 10200}$ | `02_leaderboard_stats.py` |
| 0.85–0.86 pp | Wilson half-width at n=10,200 | `02` |
| 78 items | $(0.0017 \times 10200 / 1.96)^2$ | `02` |
| $P_e$ = 0.3887 | $\sum p_i^2$ over 1A class shares | `03_ceiling_and_metric.py` |
| $P_o$ = 0.8227 | $0.71(1-0.3887)+0.3887$ | `03` |
| ~0.975 | $\alpha^3 + 3\alpha^2(1-\alpha)$, α=0.906 | `03` |
| 0.28 pp | 29 `Sexism` ÷ 10,200 | `03` |
| 342 | type≠None AND target=None in 1C | `01` |
| 3.6–36.3% | discordance over 45 real system pairs | `07_discordance_and_stability.py` |
| 0.37 pp | $1.96\sqrt{367}/10200$ | `08_gap_vs_stability.py` |
| 51.5% | bootstrap win rate, 0.02 pp pair | `08` |

**Drill:** cover the middle column and derive three of these from scratch. If you can't,
reread the relevant section above.

---

# Part 3 — Defending it

### "You never actually ran McNemar. You don't have the predictions."

*Correct, and §4 says so. I inverted the test instead: for the 0.17 pp gap to be
significant, the systems would need to disagree on under 0.8% of items. I then measured
real discordance across 45 pairs of systems I built myself and found a minimum of 3.6% —
more than four times what would be required. It's a bound, not a test, but the bound is
comfortable. I've asked the organisers for the prediction files.*

### "Your models only reach 0.68. The real systems are transformers at 0.736."

*Also correct, and it's my main limitation. Two transformers fine-tuned from the same
pretrained checkpoint share an initialisation my systems don't, so their discordance could
be lower than anything I measured. I call 3.6% an empirically grounded floor, not a proven
one. Note the direction of the risk though: they'd need to be twenty times more similar than
my most-similar pair.*

### "The ceiling estimate is a toy model."

*Yes. It assumes conditional independence and a two-parameter error model. I report both a
uniform-error and a maximally-correlated-error variant, and they agree at ~0.97. But they're
models, and I say so in Limitations. What I'd defend is the direction: majority voting over
three annotators is a powerful denoiser, so κ=0.71 does not imply 73% gold labels.*

### "Isn't this just attacking other people's work?"

*The opposite. This audit was only possible because these organisers released their data,
gold labels, and scorer — a higher standard than most shared tasks meet. My §7 reports that
the dataset is clean: no duplicate conflicts, no leakage, no degenerate items. The
criticism is of the metric, and the participating teams may well differ in quality — my
point is precisely that the evaluation can't tell us.*

### "Isn't a 0.3-point gap obviously meaningless? Why is this a paper?"

*It isn't obvious, and that's the interesting part. My own top two systems differ by
0.44 pp and hold their order in 98.7% of resamples — a real difference. Small gaps aren't
automatically noise. The condition is whether the gap exceeds $1.96\sqrt{b+c}/n$, and what
condemns these particular gaps is their size relative to plausible discordance, not their
size alone.*

### "So what should the organisers actually do?"

*Four things, all cheap: report confidence intervals, release per-system predictions,
report macro-F1 alongside micro-F1, and declare ties where systems are indistinguishable.*

---

# Part 4 — The three-minute version

Practice this out loud until it's fluent.

> "There was a Bangla hate-speech shared task last year — 160 participants, a published
> leaderboard. I checked whether the ranking was statistically meaningful.
>
> It isn't. The top five teams are separated by about a third of a percentage point, but the
> confidence interval on any single score is nearly a full point. Every team falls inside
> the leader's interval, in all three subtasks.
>
> I then asked why everyone plateaus around 73%. The obvious answer is noisy labels, so I
> estimated the ceiling from the reported inter-annotator agreement — and it came out around
> 97%. Label noise doesn't explain it. My hypothesis was wrong.
>
> So I looked at the metric. They score with micro-F1, and the Sexism class is 29 of 10,200
> test items. A system that catches every sexist comment and one that catches none differ by
> 0.28 points — below the sampling noise floor. The metric literally cannot see sexism.
>
> To check my reasoning I trained ten systems to get real predictions. Five of them never
> predict Sexism at all. And the system with the *best* macro-F1 and the best Sexism score
> ranks only fourth on micro-F1 — the reported metric actively demotes the fairest system.
>
> The dataset itself is well built; I say so in the paper. The problem is how it's scored."

---

# Part 5 — What to study next

Read these three in order. They're the intellectual foundation of your paper, and knowing
them makes you sound like you belong in the conversation.

1. **Card et al. (2020), "With Little Power Comes Great Responsibility"** (EMNLP) — the
   statistical-power argument. Closest in spirit to your work.
2. **Dror et al. (2018), "The Hitchhiker's Guide to Testing Statistical Significance in
   NLP"** (ACL) — a practical guide to which test when.
3. **Jin et al. (2026), "Text-to-SQL Benchmarks are Broken"** (CIDR) — the paper whose
   method you transplanted. You should know it better than anyone.

And one skill to build: **be able to rerun `02`, `03`, `07`, `08` and explain every line of
output.** When someone asks a question you didn't anticipate, being able to go compute the
answer is worth more than having memorised this document.
