# Where to post the preprint

Short answer: **yes, you can post it — but probably not to arXiv, not yet.**

---

## First, a correction

I told you twice to be careful about an ARR anonymity period. **That was outdated.**
ARR removed the anonymity period as of the 15 February 2024 deadlines:

> "Beginning with the February 15, 2024 ARR deadlines, there is no anonymity period or
> limitation on posting or discussing non-anonymous preprints while the work is under
> peer review."

So there is **no timing constraint from ARR**. Post whenever you want. Your *submission*
must still be the anonymised `main.pdf`; the preprint can be `main_authored.pdf`. Those
are two files from the same source, which is why both exist.

---

## The real obstacle: arXiv endorsement

arXiv is where NLP people actually look, so it's the one worth wanting. But you can't
just upload.

**arXiv tightened its policy on 21 January 2026.** An institutional email address is no
longer sufficient on its own. A new submitter now needs *either*:

1. An institutional email **and** prior authorship on a paper already accepted to arXiv
   in that endorsement domain, **or**
2. A personal endorsement from an established arXiv author in the field.

You have neither yet. And arXiv staff explicitly cannot waive this or endorse you
themselves.

**What an endorsement actually involves:** you start a submission, arXiv issues you an
endorsement code, and you send that code to someone who already publishes in `cs.CL`.
They click a link. It takes them about a minute. The ask is small — the hard part is
having someone to ask.

Realistic people to ask, in order:
- Your Theory of Computation teacher, if he has arXiv papers (check Google Scholar first)
- Any faculty member at NSU or JU who publishes in NLP or ML
- A Bangladeshi NLP researcher whose work you cite — the BLP community is small and
  generally welcoming to students

Yes, this needs contacting someone. There is no path around it. But it's a one-minute
favour, not a request for supervision, and having a finished paper and a public repo
makes it a much easier ask than an abstract one.

---

## What you can post today, with no gatekeeping

### Zenodo — the best option ⭐

[zenodo.org](https://zenodo.org) — operated by CERN, free, permanent, and it issues a
real **DOI**. No endorsement, no screening, no affiliation check. A Zenodo DOI is a
legitimate citable record and you can put it straight on your CV.

It also handles versioning: post v1 now, post v2 after the citation fixes, and the DOI
resolves to the latest while each version keeps its own.

Bonus: Zenodo integrates with GitHub. Connect the repo and every release automatically
gets archived with its own DOI — which makes the *code* citable too, not just the paper.

### Others worth knowing

| Where | DOI | Gatekeeping | Notes |
|---|---|---|---|
| **Zenodo** | Yes | None | CERN-run. Best default. |
| **OSF Preprints** | Yes | None | Clean, academic, well regarded. |
| **TechRxiv** | Yes | Light screening | IEEE-run, engineering-focused. Reasonable fit. |
| **ResearchGate** | No | None | High visibility, but not a real archive. Fine as a mirror. |
| **Your GitHub repo** | No | None | Already done. Immediate, not citable. |

**Don't** use a venue that charges you. Every option above is free.

---

## ⚠️ Do the citations first

A preprint is close to permanent. arXiv never deletes; Zenodo DOIs are meant to persist.
You can post a corrected version, but v1 stays visible forever.

Right now the only [VERIFIED] entry in `refs.bib` is the BLP Task 1 overview. Everything
else was written from memory and is explicitly flagged. **Fix those before you post
anywhere with a DOI.** An hour of clicking BibTeX buttons on the ACL Anthology.

Posting a version with a fabricated author list is exactly the kind of thing someone
notices later, and it's entirely avoidable.

---

## Recommended sequence

1. **Verify the citations** — one hour, and it gates everything below
2. **Push the repo** to GitHub (public is fine now)
3. **Post `main_authored.pdf` to Zenodo** — get the DOI, add it to your CV
4. **Connect the repo to Zenodo** so the code gets its own DOI
5. **Ask someone for an arXiv endorsement** — and once you have it, post there too;
   Zenodo and arXiv are not mutually exclusive
6. **Submit the anonymised `main.pdf` to ARR** by 12 October

Step 3 gets you a citable line on your CV this week. Step 5 is worth doing eventually,
but it isn't blocking you.

---

## Sources

- [arXiv endorsement policy update, 21 Jan 2026](https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/)
- [arXiv endorsement help](https://info.arxiv.org/help/endorsement.html)
- [ARR author guidelines — preprints and anonymity](https://aclrollingreview.org/authors)
