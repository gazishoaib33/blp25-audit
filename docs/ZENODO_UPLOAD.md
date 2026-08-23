# Posting to Zenodo — step by step

Total time: about 15 minutes. Everything you need to paste is below.

---

## Step 0 — Get an ORCID first (2 minutes)

Do this before Zenodo. [orcid.org/register](https://orcid.org/register)

ORCID is a permanent researcher ID — a number like `0000-0002-1825-0097` that stays
yours for life and disambiguates you from every other Gazi Shoaib. Free, instant, no
approval. Every journal, grant, and application will eventually ask for it, and having
one already signals you know how the system works.

Attach it to your Zenodo upload so the paper is permanently linked to you.

---

## Step 1 — Sign in to Zenodo

[zenodo.org](https://zenodo.org) → **Sign up**. Use **"Sign up with GitHub"** — it takes
one click and it also sets up the code-archiving integration in Step 5.

---

## Step 2 — New upload

Click **New upload** (top right, or under the Upload menu).

Drag in **`main_authored.pdf`**.

> Upload the **authored** version, not `main.pdf`. The anonymous one is for ARR only.

---

## Step 3 — Fill the metadata

Paste each of these into the matching field.

**Resource type**
```
Publication  →  Preprint
```

**Title**
```
Indistinguishable at the Top: A Statistical Audit of the BLP-2025 Bangla Hate Speech Shared Task
```

**Creators**
```
Family name: Shoaib
Given names: Gazi
Affiliation: Jahangirnagar University
ORCID: (paste the one you just made)
```

**Description** — paste this whole block:

```
Shared-task leaderboards routinely report scores to four decimal places and rank
systems accordingly, but rarely report whether those ranks are distinguishable from
noise. We audit the BLP-2025 Bangla Hate Speech Identification shared task, whose
data, gold test labels, and evaluation scripts are fully public.

We find that in all three subtasks the top five systems are statistically
indistinguishable: the top-five spread is 0.34-0.80 percentage points against a 95%
confidence interval half-width of 0.85-0.86 points, and for the leader-versus-runner-up
gap to reach p < .05 under McNemar's test the two systems would have to disagree on
under 1.2% of test items.

We then test, and reject, the hypothesis that annotation noise caps performance:
three-way majority voting over annotations with kappa = 0.71 yields gold labels we
estimate to be approximately 97% reliable, leaving a 24-point gap to the best system.

The binding problem is instead the metric. Because Sexism comprises 29 of 10,200 test
items, a system that detects every sexist comment and one that detects none differ by
0.28 points of micro-F1 - below the 0.44-point sampling noise floor. Training ten
systems to obtain real predictions, we measure pairwise discordance of 3.6-36.3% and
show that the minimum detectable gap is 0.37 pp even in the best case, above every
reported top-two gap, while a pair separated by 0.02 pp wins only 51.5% of bootstrap
resamples. No system in our pool detects more than 3 of the 29 sexist comments, and
five detect none.

All analysis code is released at https://github.com/gazishoaib33/blp25-audit
```

**License**
```
Creative Commons Attribution 4.0 International (CC BY 4.0)
```
This is the standard open licence for preprints. It lets people read, share, and cite
your work as long as they credit you.

**Keywords** — add these one at a time:
```
natural language processing
Bangla
hate speech detection
evaluation methodology
benchmark reliability
statistical significance
shared task
low-resource languages
```

**Related works** (optional but worth doing)
```
Relation: "is supplemented by this upload"  →  https://github.com/gazishoaib33/blp25-audit
```

**Publication date** — today's date.

---

## Step 4 — Publish

Click **Publish**. You immediately get a DOI like:

```
10.5281/zenodo.XXXXXXX
```

**That is now a permanent, citable record of your work.** It will not disappear, and it
resolves forever.

---

## Step 5 — Archive the code too (optional, 3 minutes)

In Zenodo: **Profile → GitHub**. Find `blp25-audit` in the list and flip the switch on.

Then in GitHub: **Releases → Create a new release**, tag it `v1.0.0`, publish.

Zenodo automatically archives that release and issues it a *separate* DOI. Now your code
is citable independently of the paper — which reviewers and hiring committees both
notice.

The repo must be **public** for this to work. That's fine — ARR has no anonymity period.

---

## Step 6 — Update your CV

In `cv.tex`, change the manuscript line from:

```latex
\textit{Manuscript, 2026.}
```

to:

```latex
\textit{Preprint}, Zenodo, 2026. \texttt{doi:10.5281/zenodo.XXXXXXX}
```

Recompile with `pdflatex cv.tex` (twice). You now have a real, verifiable publication
line on your CV.

---

## A note on versions

Zenodo handles versioning properly. If you later revise the paper — after ARR reviews,
say — upload a **New version** from the same record. The old DOI keeps pointing at v1,
a new DOI points at v2, and a third "concept DOI" always resolves to the latest.

So publishing now costs you nothing. You are not locking anything in.

---

## What this does and doesn't get you

**Does:** a permanent citable DOI, a real line on your CV, a link you can send anyone,
and proof of the date you did this work.

**Doesn't:** peer review. A Zenodo preprint is not a reviewed publication, and you must
never describe it as one. On your CV it sits under "Preprints and Manuscripts", never
under "Publications". Mislabelling it is the kind of thing that ends applications.

The peer review comes from ARR in October.
