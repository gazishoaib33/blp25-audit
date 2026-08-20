# Annotation Guideline — BLP-2025 Task 1 Audit
### বাংলা হেট-স্পিচ ডেটাসেট নিরীক্ষা — অ্যানোটেশন নির্দেশিকা

**Version 1.0 · 19 August 2026**
Adapted from the E1–E4 error taxonomy of Jin et al., *Text-to-SQL Benchmarks are Broken* (CIDR 2026), re-derived for multi-class text classification.

---

## 1. What this is / এটি কী

You are re-labelling a sample of Bangla YouTube comments drawn from the BLP-2025 Task 1 test set. Each comment already has a published "gold" label. **You will not see it.** After all three annotators finish independently, we compare your labels to the published ones and estimate how often the published label is wrong.

আপনি BLP-2025 টাস্ক ১-এর টেস্ট সেট থেকে নেওয়া কিছু বাংলা ইউটিউব মন্তব্য নতুন করে লেবেল করবেন। প্রতিটি মন্তব্যের একটি প্রকাশিত "গোল্ড" লেবেল আছে, **কিন্তু আপনি সেটি দেখতে পাবেন না।** তিনজন অ্যানোটেটর স্বাধীনভাবে কাজ শেষ করার পর আমরা তুলনা করব।

### Three rules that cannot be broken / তিনটি বাধ্যতামূলক নিয়ম

1. **Do not look up the original labels.** They are public on GitHub. Looking destroys the study.
2. **Do not discuss individual items with the other annotators** until all three of you have submitted.
3. **Do not skip items.** If you cannot decide, pick your best guess, set confidence to `Low`, and flag the reason. A guess with an honest confidence rating is data; a blank cell is not.

---

## 2. Label schema / লেবেল স্কিমা

### 2.1 Hate type / বিদ্বেষের ধরন

| Label | Definition | বাংলা |
|---|---|---|
| `None` | No hate, abuse, or profanity. | কোনো বিদ্বেষ, গালি বা অশ্লীলতা নেই। |
| `Abusive` | Insulting, demeaning, or degrading a person or group. | কাউকে অপমান বা হেয় করা। |
| `Sexism` | Hostility based on gender or sexuality. | লিঙ্গ বা যৌনতাভিত্তিক বিদ্বেষ। |
| `Religious Hate` | Hostility toward a religion or its followers. | ধর্ম বা ধর্মাবলম্বীদের প্রতি বিদ্বেষ। |
| `Political Hate` | Hostility toward a party, leader, or ideology. | রাজনৈতিক দল, নেতা বা মতাদর্শের প্রতি বিদ্বেষ। |
| `Profane` | Obscene or vulgar language, not necessarily targeted. | অশ্লীল বা কুরুচিপূর্ণ ভাষা। |

### 2.2 Target / লক্ষ্য

`None` · `Individual` (a specific person) · `Organization` (party, company, institution, media) · `Community` (religious, ethnic, gender, regional group) · `Society` (society or the country at large)

### 2.3 Severity / তীব্রতা

| Label | Definition |
|---|---|
| `Little to None` | Minimal or no hateful intent. / সামান্য বা কোনো বিদ্বেষপূর্ণ উদ্দেশ্য নেই। |
| `Mild` | Moderately offensive, or implicitly hateful. / মাঝারি আপত্তিকর। |
| `Severe` | Strongly derogatory, or inciting harm. / তীব্র অবমাননাকর বা উস্কানিমূলক। |

---

## 3. Decision procedure / সিদ্ধান্তের ধাপ

Work through these **in order**. Stop at the first one that applies.

1. **Is there any hostility, insult, or obscenity at all?**
   No → `None` / `None` / `Little to None`. Done.
2. **Is the language obscene but aimed at no one?**
   → `Profane`, target `None`.
3. **What is the hostility *based on*?**
   Gender → `Sexism`. Religion → `Religious Hate`. Politics → `Political Hate`. None of these, just insult → `Abusive`.
4. **Who receives it?** Pick the most specific target that fits.
5. **How intense?** Set severity.
6. **Flag the difficulty** using C0–C4 (§4).

### The five hardest judgement calls

**a. Criticism is not hate.** Saying a policy is bad, a minister failed, or a company cheated customers is *criticism*. It becomes `Political Hate` when it attacks people for their affiliation rather than attacking the conduct.
*সমালোচনা আর বিদ্বেষ এক নয়। কাজের সমালোচনা ≠ বিদ্বেষ।*

**b. Judge the comment, not the topic.** A comment about religion is not automatically `Religious Hate`. A comment about a politician is not automatically `Political Hate`. The hostility must be in the text.

**c. Reported speech and quotation.** If the commenter quotes a slur to condemn it, the comment is not itself hateful. Flag `C4`.

**d. Religious + political overlap.** In Bangladeshi comment threads these fuse constantly. Pick the one the hostility is *grounded in*, and flag `C3`. If you genuinely cannot separate them, that item is evidence for the paper.

**e. Profanity as emphasis.** Bangla comments often use vulgar intensifiers with no target and no malice. That is `Profane` + target `None` + severity `Little to None` — a legitimate combination.

---

## 4. Error categories / ত্রুটির শ্রেণি

After labelling, record *why the item was hard*. This is the audit's diagnostic layer, adapted from Jin et al.'s E1–E4.

| Code | Jin et al. analogue | When to use |
|---|---|---|
| `C0-agree` | — | Straightforward. One reading, and you are confident. |
| `C1-label mismatch` | E1 (semantic mismatch) | The comment is **clear**, but you expect the published label got it wrong. Example: political criticism labelled as hate. *মন্তব্য স্পষ্ট, কিন্তু লেবেল ভুল মনে হচ্ছে।* |
| `C2-needs context` | E3 (domain knowledge) | Unjudgeable without the parent video, the thread, or the news event. These are YouTube comments stripped of context. *প্রসঙ্গ ছাড়া বিচার করা যাচ্ছে না।* |
| `C3-schema gap` | E2 (schema mismatch) | Genuinely hateful but no category fits, **or** two fit equally well. *স্কিমার সাথে মিলছে না।* |
| `C4-ambiguous/ironic` | E4 (ambiguity) | Sarcasm, irony, reclaimed slurs, reported speech — literal and intended readings differ. *ব্যঙ্গ বা দ্ব্যর্থবোধক।* |

**Use `C1` sparingly and only when you are confident.** `C1` is the category that drives the headline error rate, so it carries the most weight and the most scrutiny. When in doubt between `C1` and `C4`, choose `C4`.

---

## 5. Confidence / আত্মবিশ্বাস

`High` — you would defend this label in review.
`Medium` — you settled between two plausible readings.
`Low` — you guessed.

Be honest. `Low` is genuinely useful signal: items where all three annotators report `Low` are evidence the item is ill-posed, which is itself a finding. Under-reporting `Low` to look decisive weakens the paper.

---

## 6. Notes / মন্তব্য

One line whenever you pick `C1`–`C4`. English or Bangla, whichever is faster. Say *what* made it hard.

Good: `Criticises PM's flood response, not the person — reads as criticism, not political hate.`
Good: `ধর্মীয় ও রাজনৈতিক দুটোই মিলে আছে, আলাদা করা যাচ্ছে না।`
Useless: `hard` / `confusing`

---

## 7. Workflow

1. Open `annotation_pilot_<your ID>.xlsx`. Read the **Instructions** sheet.
2. Go to the `annotate_*` sheet. **Row 2 is a worked example — do not overwrite it.** Real items start at row 3.
3. Fill only the **yellow** columns. Dropdowns are provided; do not type free text into label columns.
4. Save with your ID in the filename and send it back. Do not rename the sheets.

**Pilot:** 124 items, roughly 1.5–3 hours. After the pilot we compute Fleiss' κ among the three of you, revise this guideline where you disagreed most, then run the full 495-item set.

---

## 8. Why the pilot exists

If our three annotators reach κ ≈ 0.71, we have replicated the organisers' reported reliability, and disagreements with gold become credible evidence about the labels. If we come in far below 0.71, the honest conclusion is that **the task is harder to annotate than reported** — which is a finding in its own right, but a different paper. Either outcome is publishable. Neither is a failure.

Do not tune the guideline to force agreement upward. Revise it only where annotators disagreed because the *guideline* was unclear, never to paper over genuine ambiguity in the data.
