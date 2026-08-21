# Auditing the BLP-2025 Bangla Hate Speech Shared Task

A statistical and annotation audit of [BLP-2025 Task 1](https://aclanthology.org/2025.banglalp-1.32/)
(Bangla Hate Speech Identification), following the methodology of Jin et al.,
*Text-to-SQL Benchmarks are Broken* (CIDR 2026).

**Headline result: the top five systems are statistically indistinguishable in all three
subtasks, and the evaluation metric cannot detect whether a system handles sexist content
at all.**

---

## Findings

| # | Finding |
|---|---|
| 1 | Top-5 spread is 0.34–0.80 pp against a 95% CI half-width of 0.85–0.86 pp. **All five teams fall inside the leader's own interval** in every subtask. |
| 2 | For the leader-vs-runner-up gap to be significant, two systems would have to disagree on **under 1.2%** of test items. Measured discordance across 45 real system pairs: **3.6–36.3%**. |
| 3 | **Label noise does not explain the 0.736 plateau.** Three-way majority voting over κ=0.71 annotations yields gold labels ≈97% reliable — a 24-point gap to the best system. |
| 4 | **Sexism is invisible to the metric.** 29 of 10,200 test items → max micro-F1 swing 0.28 pp, below the 0.44 pp sampling noise floor. 5 of our 10 systems detect none of its 29 instances; the best detects 3. |
| 5 | The system with the best macro-F1 *and* best Sexism-F1 ranks **4th of 10** on micro-F1. Optimising the reported metric demotes the system that handles rare classes best. |
| 6 | **342 test items** carry a hate type but no target — a direct contradiction of the annotation scheme. |
| 7 | Negative result, reported: the dataset is otherwise **clean** — zero duplicate-label conflicts, zero train/test leakage, zero degenerate items. |

Full write-up: [`docs/FINDINGS.md`](docs/FINDINGS.md) · Paper: [`paper/main.pdf`](paper/main.pdf)

---

## Reproduce

```bash
git clone https://github.com/AridHasan/blp25_task1.git   # the dataset (CC BY-NC-SA 4.0)
pip install -r requirements.txt

python src/01_data_integrity.py          # duplicates, leakage, schema coherence
python src/02_leaderboard_stats.py       # Wilson CIs, McNemar sensitivity
python src/03_ceiling_and_metric.py      # annotation ceiling, class sensitivity
python src/06_train_systems.py           # train 10 systems (~4 min, CPU)
python src/07_discordance_and_stability.py
python src/08_gap_vs_stability.py
python src/09_verify_paper_claims.py   # independent check of all 32 paper claims
```

Scripts expect the dataset at `blp25_task1/` alongside this repo; edit the `DATA` path at
the top of each script otherwise. All randomness is seeded (`SEED = 20260819`) — reruns are
byte-identical.

### The `None` trap ⚠️

`pandas.read_csv` coerces the literal string `"None"` to `NaN` by default, and `None` is the
**majority class** (56.4% of subtask 1A). A naive load silently deletes it. Always:

```python
pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_values=[])
```

Sanity check: the majority-class baseline must come out to **0.5638**, matching the
organisers' reported figure.

---

## Annotation study (Stage 2)

Three annotators re-label a stratified sample **blind** — gold labels never reach them.

```bash
python src/04_build_annotation_set.py --pilot     # 124 items
python src/04_build_annotation_set.py --n 500     # 495 items
python src/05_analyse_annotations.py --tag pilot --simulate   # self-test
python src/05_analyse_annotations.py --tag pilot              # real data
```

Workbooks are in [`annotation/`](annotation/); the protocol is
[`docs/ANNOTATION_GUIDELINE.md`](docs/ANNOTATION_GUIDELINE.md) (bilingual English/Bangla).
The sample key (`*_WITH_GOLD.csv`) is **deliberately not committed** — regenerate it locally
and do not distribute it to annotators.

Two rates are reported: **primary** (≥2 of 3 annotators agree on a label differing from
gold) and **conservative** (all 3 converge on the same alternative). Items where all three
differ carry no majority and are reported separately as evidence of ill-posed items.

---

## Repository layout

```
src/        analysis pipeline, scripts 01–09
paper/      LaTeX source, figures, compiled PDF
docs/       findings, annotation guideline, submission checklist
results/    JSON and CSV outputs
annotation/ blind annotator workbooks
```

## Data

This repository redistributes **no data**. The BLP-2025 Task 1 dataset is released by the
organisers under CC BY-NC-SA 4.0 at
[github.com/AridHasan/blp25_task1](https://github.com/AridHasan/blp25_task1).

## Note

This audit was only possible because the organisers released their data, gold test labels,
and scorer. That is a higher standard of openness than most shared tasks meet, and the
criticism here is of the evaluation design, not of the resource or the participating teams.

## License

Code: MIT (see [LICENSE](LICENSE)). Analysis outputs derived from the BLP-2025 dataset
remain subject to the dataset's CC BY-NC-SA 4.0 terms.
