# Pushing this to GitHub

The repository is fully initialised — seven commits, clean history, nothing sensitive
tracked. I could not push it myself because that needs your GitHub credentials, which I
don't have and shouldn't. Three commands finish it.

## 1. Create the empty repo

Go to [github.com/new](https://github.com/new). Name it `blp25-audit`. **Do not** tick
"Add a README", "Add .gitignore", or "Choose a license" — they already exist here and an
initial commit on GitHub's side will cause a conflict.

## 2. Push

```bash
cd blp25-audit
git remote add origin https://github.com/gazishoaib33/blp25-audit.git
git branch -M main
git push -u origin main
```

If prompted for a password, GitHub wants a **personal access token**, not your account
password: Settings → Developer settings → Personal access tokens → Fine-grained tokens →
generate one with `Contents: Read and write` on this repository.

## 3. Update the two placeholder URLs

- `CITATION.cff` → replace `USERNAME` with your GitHub username
- `README.md` → the clone URL near the top

```bash
sed -i 's/USERNAME/YOUR_USERNAME/' CITATION.cff
git commit -am "Update repository URL" && git push
```

---

## Before you make it public

**Keep it private until you've submitted.** ARR enforces an anonymity period, and a public
repo with your name on it, linked from a submission, breaks double-blind review. Two options:

- **Keep the repo private** through review, and submit the paper with an
  [anonymous.4open.science](https://anonymous.4open.science) mirror instead.
- **Make it public only after** the anonymity window closes.

Check the current ARR policy before deciding — the rules change between cycles.

## What is deliberately not committed

| Excluded | Why |
|---|---|
| `annotation/*_WITH_GOLD.csv` | The annotation key. If an annotator sees it, the blind study is void. Regenerate locally with `src/04_build_annotation_set.py`. |
| `blp25_task1/` | The dataset is the organisers' to distribute, under CC BY-NC-SA 4.0. We link to it rather than mirror it. |
| LaTeX build artifacts | Noise. |

`results/test_predictions.csv` **is** committed (836 KB) so the discordance analysis
reproduces without retraining. It contains model predictions and item IDs, not comment
text, so it redistributes no dataset content.

## Verify before pushing

```bash
git ls-files | grep -iE "WITH_GOLD|hatespeech.*tsv"   # must return nothing
```

## Commit history

```
Make dataset and output paths portable
Add README
Add ARR short paper draft with figures and submission checklist
Measure real system discordance instead of assuming it
Add blind annotation protocol and stratified sampling
Add computational audit: integrity checks, leaderboard CIs, annotation ceiling
Add project scaffolding, MIT license, and dependencies
```

The history is structured deliberately — each commit is one coherent step with a message
explaining *why*, not just *what*. Reviewers and admissions committees do read these.
