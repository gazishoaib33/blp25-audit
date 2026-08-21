# Using this work — no email required

Everything here you can do alone, today or over the next month.

---

## 1. Your academic CV (done — `cv.pdf`)

What changed from your old one:

| Old | New |
|---|---|
| "Seeking roles in Data Analytics & BI" | **Research Interests** — evaluation methodology, low-resource NLP, interpretable ML |
| "Actively seeking Data Analyst roles in Bangladesh" | Deleted. It signalled "not a researcher." |
| Projects listed as deliverables | Reframed around method and finding |
| No publications section | **Research** section leading with your manuscript |
| Skills as tool lists | Statistics section naming the actual methods you used |

Edit `cv.tex` and recompile with `pdflatex cv.tex` (twice). Update the manuscript
line as its status changes: *Manuscript* → *Under review, ARR* → *Preprint,
arXiv:XXXX.XXXXX* → the real citation.

**Keep your old CV too.** It's the right one for industry jobs. These are two
documents for two audiences, not a replacement.

---

## 2. Statement-of-purpose paragraph

Every application will ask about research experience. Adapt this — don't paste it
verbatim, since your own voice matters more than my phrasing:

> My interest in evaluation methodology began with a question I could not answer
> from a published leaderboard. Reviewing the BLP-2025 Bangla hate-speech shared
> task, I noticed the top five systems were separated by roughly a third of a
> percentage point on a 10,200-item test set, and that no confidence intervals
> were reported. I computed them, and found every top-five team fell within the
> leader's own interval. Pursuing this further, I estimated the annotation
> ceiling implied by the organisers' reported inter-annotator agreement and
> found — contrary to my own hypothesis — that label noise could not explain the
> performance plateau. The binding constraint was the metric itself: with the
> rarest hate category comprising 29 of 10,200 items, micro-F1 cannot register
> whether a system detects it at all. I trained ten systems to obtain real
> predictions and measured the pairwise disagreement my argument had until then
> assumed. Working through this taught me something I did not expect to learn
> from a critique: that the most useful result was the one that refuted my
> starting hypothesis, and that stating the limits of a claim precisely is more
> persuasive than stating the claim strongly.

The last sentence is doing the real work. Committees see hundreds of applicants
claiming results; very few describe changing their mind.

---

## 3. Push the repository

Makes the work linkable, and a public repo with real commits is evidence in a way
a PDF isn't. **Keep it private until you've submitted to ARR** — a public repo
under your name, linked from a double-blind submission, breaks anonymity.

See `PUSH_INSTRUCTIONS.md`. One command once the repo exists.

---

## 4. Run the pilot annotation yourself

You are annotator A1. Open `annotation_pilot_A1.xlsx`, label all 124 items, and
**do not** look at the gold labels. Roughly two hours.

Doing it yourself first tells you whether the guideline is clear before you ask
anyone else to spend their time on it — and you'll find the ambiguous cases
personally, which makes §5 of the paper much easier to write.

---

## 5. Read the three papers

From the study guide:

1. Card et al. (2020), *With Little Power Comes Great Responsibility* — EMNLP
2. Dror et al. (2018), *The Hitchhiker's Guide to Testing Statistical
   Significance in NLP* — ACL
3. Jin et al. (2026), *Text-to-SQL Benchmarks are Broken* — CIDR

All free. You should know the third better than anyone, since you transplanted
its method.

---

## 6. Verify the citations

An hour of tedious work you can do alone. Open each ACL Anthology page listed at
the top of `refs.bib`, click BibTeX, paste the entry over mine. This is the last
real defect in the paper.

---

## 7. Rehearse the three-minute pitch

Part 4 of the study guide. Say it out loud until it's fluent. You'll use it in
your first conversation with a supervisor, and being fluent in your own work is
what separates "did a project" from "is a researcher."

---

## 8. LinkedIn / profile text

Short version, for a bio or profile:

> MSc in Applied Statistics and Data Science. Currently working on evaluation
> methodology for low-resource NLP — most recently a statistical audit of a
> Bangla hate-speech benchmark, showing its published system ranking is not
> statistically separable and its metric cannot resolve its rarest class.

---

## Priority order

1. **Push the repo** (private) — 5 minutes, makes everything else linkable
2. **Verify the citations** — 1 hour, removes the paper's last real defect
3. **Do the pilot annotation** — 2 hours, and only you can do it
4. **Rehearse the pitch** — 20 minutes, highest return per minute spent
5. **Read the three papers** — a week, and it compounds

Note what's *not* on this list: more analysis. The paper is done. The remaining
work is verification, communication, and Stage 2.
