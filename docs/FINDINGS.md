# BLP-2025 Task 1 — Audit Findings (Stage 1, computational)

**Gazi Shoaib · 19 August 2026**
All numbers below are computed from the released data and the ten systems trained in `06`.
Nothing here required manual annotation.
Reproduce with scripts `01`–`08`; `09_verify_paper_claims.py` independently re-checks all 32 numbers.

---

## Working title

> **Indistinguishable at the Top: A Statistical and Annotation Audit of the BLP-2025 Bangla Hate Speech Shared Task**

---

## The story that emerged

I started from the hypothesis that label noise caps performance at ~0.736 micro-F1. **The data refutes that.** What the audit found instead is a more interesting and more defensible claim:

> The BanglaMultiHate dataset is *well built*. The **evaluation** is what fails — the headline metric cannot separate the top five systems, and is formally blind to the rarest hate category.

That reframing is the paper. Reporting the refuted hypothesis honestly is a feature, not a retreat.

---

## Finding 1 — The top five systems are statistically indistinguishable

Reported micro-F1, n_test = 10,200:

| Subtask | Leader | 5th place | Top-5 spread | Wilson 95% CI half-width |
|---|---|---|---|---|
| 1A | .7362 | .7328 | **0.34 pp** | ±0.86 pp |
| 1B | .7356 | .7317 | **0.39 pp** | ±0.86 pp |
| 1C | .7392 | .7312 | **0.80 pp** | ±0.85 pp |

In all three subtasks, **5 of 5 teams have confidence intervals overlapping the leader's lower bound.**

**McNemar sensitivity.** For the leader-vs-runner-up gap to reach p < .05, the two systems would have to disagree on fewer than:

- 1A: **78 of 10,200 items (0.77%)**
- 1B: **119 items (1.17%)**
- 1C: **53 items (0.52%)**

**This was originally an assumption.** It is now measured (Finding 5): across 45 real system pairs, McNemar discordance ranges 3.6–36.3%. The lowest value observed anywhere is 3.6%, roughly five times the ~0.8% the gap would require. No top-2 gap can be significant.

**Monte-Carlo.** Simulating two systems of *identical* true skill, the probability of seeing a gap at least as large as the observed one by chance alone:

| Discordance assumption | 1A | 1B | 1C |
|---|---|---|---|
| 5% | .454 | .353 | .509 |
| 15% (typical) | **.664** | **.592** | **.702** |
| 25% | .738 | .678 | .767 |

A coin flip would produce these rankings about as often as skill does.

---

## Finding 2 — Label noise does NOT explain the 73.5% plateau

The organisers report Fleiss' κ = 0.71 (type), 0.79 (target), 0.84 (severity), with 3 annotators and majority-vote gold.

Backing out per-annotator accuracy from κ and the observed class marginals (P_e = 0.3887):

| Dimension | κ | Pairwise agreement | Per-annotator accuracy | **Majority-vote gold accuracy** |
|---|---|---|---|---|
| Type | 0.71 | 0.823 | 0.906 / 0.902 | **0.975 / 0.973** |
| Target | 0.79 | 0.872 | 0.933 / 0.931 | 0.987 / 0.986 |
| Severity | 0.84 | 0.902 | 0.950 / 0.948 | 0.993 / 0.992 |

(Two error models: errors scattered uniformly vs. maximally correlated onto a single confusable class. Both give ~97%.)

**Best system 0.7362 vs. ceiling ~0.973 → a 23.7 pp gap.** Three-way majority voting is remarkably effective at cleaning κ = 0.71 annotations. This is a genuine modelling gap, not an annotation artifact.

---

## Finding 3 — Micro-F1 is formally blind to the Sexism class

Sampling SE of a single micro-F1 score at n = 10,200: **0.44 pp.**

| Class | n | Max possible micro-F1 swing | In SE units |
|---|---|---|---|
| None | 5,751 | 56.38 pp | 129.0 |
| Abusive | 2,312 | 22.67 pp | 51.9 |
| Political Hate | 1,220 | 11.96 pp | 27.4 |
| Profane | 709 | 6.95 pp | 15.9 |
| Religious Hate | 179 | 1.75 pp | 4.0 |
| **Sexism** | **29** | **0.28 pp** | **0.65 — below the noise floor** |

> A system that detects **every** sexist comment and one that detects **none** differ by 0.28 pp of micro-F1 — less than one standard error, and smaller than the 0.34 pp spread separating the entire top five.

The headline metric is mathematically incapable of rewarding sexism detection. For a hate-speech benchmark, that is a substantive design failure, and it is the paper's sharpest single sentence.

Majority-class baseline: 0.5638 (**exactly matching the reported 0.5638** — validates the pipeline). Total headroom above baseline: **17.24 pp.**

---

## Finding 4 — 342 test items are logically incoherent

Subtask 1C carries type, severity, and target jointly. Cross-checking:

| Condition | Count | % of test |
|---|---|---|
| type = None but severity ≠ Little to None | 0 | 0.00% |
| type = None but target ≠ None | 0 | 0.00% |
| **type ≠ None but target = None** | **342** | **3.35%** |
| type ≠ None but severity = Little to None | 986 | 9.67% |
| Any incoherence | 1,185 | 11.62% |

By hate type:

| Type | n | severity = Little to None | target = None |
|---|---|---|---|
| Abusive | 2,312 | 646 (27.9%) | 209 (9.0%) |
| Political Hate | 1,220 | 263 (21.6%) | 61 (5.0%) |
| Profane | 709 | 41 (5.8%) | 50 (7.1%) |
| Religious Hate | 179 | 29 (16.2%) | 19 (10.6%) |
| Sexism | 29 | 7 (24.1%) | 3 (10.3%) |

**Be careful here.** "Hate type with Little-to-None severity" is a *tension*, not automatically an error — casual profanity can plausibly be Profane with little hateful intent. But **"hate with no target"** contradicts the annotation guideline directly. Those 342 items are the priority audit stratum, not a headline error count.

---

## Finding 5 — Measured discordance, and the claim narrowed

Scripts `06`–`08` train ten systems on the official split to obtain real predictions,
replacing the assumption above with measurement.

| Quantity | Value |
|---|---|
| Pairwise prediction disagreement (45 pairs) | median 32.0%, range 4.4–48.5% |
| McNemar discordance $b+c$ | median 25.5%, range **3.6–36.3%** |
| Near-tied pairs (within 1 pp) | median discordance 8.8% (895 items) |
| Minimum detectable gap at lowest observed discordance | **0.37 pp** |
| BLP top-2 gaps | 0.17 / 0.21 / 0.14 pp — all below it |

**A result that forced the claim to narrow.** Our own top two systems differ by 0.44 pp
with only 4.1% discordance and hold their order in 98.7% of 4,000 bootstrap resamples.
So "small gaps are meaningless" is *false* as a slogan. The defensible claim is
conditional: a gap is uninformative when smaller than $1.96\sqrt{b+c}/n$. The pair
separated by 0.02 pp wins **51.5%** of resamples — a coin flip.

## Finding 6 — Micro-F1 demotes the system that handles rare classes best

Of ten systems, five detect **none** of the 29 sexist comments; the best detects **3**.
The system with the best macro-F1 (0.5019) *and* the best Sexism F1 (0.115) ranks only
**fourth of ten** on micro-F1. Micro and macro rankings agree weakly (Kendall
$\tau = 0.467$, $p = .073$).

*(Correction: an earlier draft said five systems "never predict Sexism at all." F1 = 0
means zero true positives, not zero predictions — only one system never emits the label.
The verification suite in `09` caught this.)*

---

## Finding 7 (negative, and worth reporting) — the dataset is clean

| Check | Result |
|---|---|
| Duplicate texts with conflicting labels | **0** of 50,746 |
| Verbatim train/test leakage | **0** of 10,200 |
| Empty or ≤2-word items | **0** |
| Items with no Bangla characters | **0** |
| Median comment length | 9 words (mean 13.8) |

Compare Jin et al. (CIDR 2026): 52.8% error in BIRD Mini-Dev, 66.1% in Spider 2.0-Snow. **BanglaMultiHate is markedly better constructed than the English text-to-SQL benchmarks that motivated this audit.** Say so plainly — it makes the critique of the *metric* far more credible, because you're clearly not out to trash the resource.

---

## Finding 8 — A reproducibility hazard worth a footnote

`pandas.read_csv` treats the literal string `"None"` as `NaN` by default. Since `None` is the **majority class** (56.4% of 1A, 59.7% of 1B), a naive load silently deletes it. I hit this in my own first run: it turned a real 11.6% coherence rate into a spurious 66%.

Correct load: `pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_values=[])`

Any participant who loaded the TSVs naively trained on a corrupted label set. Worth one footnote and one line in the artifact README.

---

## Proposed paper structure (4 pages + refs, ARR short)

1. **Introduction** — shared tasks report leaderboards to 4 decimal places; almost none report confidence intervals.
2. **Related work** — Jin et al. (CIDR 2026); reproducibility in NLP; hate-speech benchmark critiques.
3. **Statistical audit** (Findings 1) — Wilson CIs, McNemar sensitivity, Monte-Carlo. *No new annotation needed.*
4. **Metric audit** (Findings 2, 3) — the ceiling estimate and the class-sensitivity result.
5. **Annotation audit** (Stage 2) — 495-item stratified re-annotation, 3 blind annotators, C0–C4 taxonomy.
6. **Recommendations** — report CIs; report macro-F1 alongside micro-F1; enforce schema coherence at release; publish per-system predictions so McNemar is computable.
7. **Limitations** — no access to system predictions; ceiling estimate assumes annotator independence.

**Contribution over Jin et al.:** they report no annotator count, no agreement metric, and no adjudication protocol. Running this audit *with* three blind annotators and a reported Fleiss' κ is a methodological improvement over the paper being replicated — say that explicitly in §2.

---

## What Stage 2 needs from you

Findings 1–8 are **done and defensible today**, and are what the submitted paper rests on. Stage 2 (manual re-annotation) upgrades it from a statistics note to a full audit:

- 3 blind annotators (you + 2 native-speaker classmates)
- 124-item pilot first → check κ, refine the guideline → then the 495-item full set
- Roughly 1.5–3 hours per annotator for the pilot

Everything is built: `04_build_annotation_set.py` produced the workbooks, `05_analyse_annotations.py` processes them and has been verified end-to-end on synthetic input.

---

## Honest risk assessment

- **The statistical findings are safe.** They follow from published numbers and arithmetic.
- **The ceiling estimate is the softest claim.** It assumes annotator independence and a simple error model. Present it as a bound with both error models shown, and flag the assumption in Limitations. A reviewer will push here.
- **This paper criticises a workshop's shared task.** Frame it as constructive — the organisers released everything needed to run this audit, which is exactly why it was possible. Thank them in the acknowledgements and cite the overview paper prominently.
- **Novelty is real but modest.** This is a solid workshop short paper, not an ACL main-track paper. That is the correct target.
