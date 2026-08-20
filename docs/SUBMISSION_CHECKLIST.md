# Submission checklist — ARR October cycle (deadline 12 Oct 2026)

## What's in this package

| File | What it is |
|---|---|
| `main.pdf` | The compiled paper — 4 pages content + refs, ACL format, anonymised |
| `main.tex` | LaTeX source |
| `refs.bib` | Bibliography |
| `figures.py` | Regenerates both figures from the numbers |
| `acl.sty`, `acl_natbib.bst` | ACL style files |

Build: `pdflatex main && bibtex main && pdflatex main && pdflatex main`

---

## Before you submit — do these in order

### 1. Verify every citation yourself ⚠️

I wrote the `.bib` from memory of the literature. **Every entry needs checking against
the ACL Anthology or the publisher** — correct authors, year, venue, page numbers. Two
entries are deliberately incomplete because I could not confirm the full author lists:

- `hasan2025blptask1` — "Hasan, Md Arid and others". Get the full list from
  [aclanthology.org/2025.banglalp-1.32](https://aclanthology.org/2025.banglalp-1.32/)
- `jin2026broken` — "{Jin} and others". Get the full list from the CIDR 2026 PDF.

The ACL Anthology gives you a correct BibTeX entry for any of its papers — use those
verbatim rather than mine. A wrong citation is the cheapest possible way to lose a
reviewer's trust.

### 2. Re-run the analysis and confirm the numbers

```bash
python 01_data_integrity.py
python 02_leaderboard_stats.py
python 03_ceiling_and_metric.py
```

Every number in the paper traces to these three scripts. If any output differs from
what's written, the paper is wrong, not the script. Check especially:
majority baseline **0.5638**, sampling SE **0.44 pp**, Sexism swing **0.28 pp**,
target-None count **342**, ceiling **~0.97**.

### 3. Decide the author list

If your Theory of Computation teacher advises on this, he's a co-author. If a
classmate does the Stage-2 annotation, they're a co-author. Settle this *before*
submission, not after acceptance.

### 4. Anonymisation

The file is set to `\usepackage[review]{acl}`, which is correct for ARR. Before
submitting, check that:

- no author names appear anywhere
- the code URL is anonymised (use anonymous.4open.science, not your GitHub)
- `\author{Anonymous ARR submission}` stays as is

Switch to `[final]` only for camera-ready.

### 5. Post the preprint — but check the ARR policy first

ARR has an anonymity period. Posting to arXiv **before** it opens can disqualify a
submission. Read the current ARR policy page and time the preprint accordingly.
Once permitted, arXiv gives you something citable on your application immediately.

---

## Where to send it

| Venue | When | Notes |
|---|---|---|
| **ARR October cycle** | **12 Oct 2026** | → NAACL 2027 / COLING 2027, commit by 20 Dec 2026. Primary target. |
| **BLP 3rd edition** | TBA | The natural home — but it critiques BLP's own shared task, so expect engaged reviewers either way. Watch `blp-workshop.github.io`. |
| **ARR January cycle** | Jan 2027 | Fallback, → ACL 2027. |

---

## What a reviewer will attack

Prepare answers for these three:

1. **"You don't have system predictions, so you never actually ran McNemar."**
   True, and §4 and Limitations both say so. Your defence is that the *bound* is
   informative: no plausible discordance rate makes the gap significant. Consider
   emailing the organisers to request the predictions — if they share them, you can
   run the real test and the paper gets substantially stronger.

2. **"The ceiling estimate rests on a toy error model."**
   Also true. You report two models bracketing the plausible range, and both give
   ~0.97. Don't over-claim beyond that.

3. **"Isn't this just criticising other people's work?"**
   Your §7 answer ("the dataset is otherwise clean") and the acknowledgement of the
   organisers are what make this constructive rather than a hatchet job. Keep both.
   Do not cut them for space.

---

## Adding Stage 2

If the annotation study finishes before 12 October, fold it in as a new §8 and move
the paper from a statistics note to a full audit. If it doesn't, submit as is — the
paper stands on Findings 1–4 alone, and Stage 2 becomes the follow-up.
