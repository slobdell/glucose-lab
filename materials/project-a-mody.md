# Project A: MODY variant detective

**Question:** Can AI mutation predictors tell broken diabetes-gene variants from
overactive ones? And which unexplained variants found in patients are most likely to matter?

## Background

MODY (maturity-onset diabetes of the young) is diabetes caused by a change in a single
gene. It's roughly 1–5% of diabetes cases, and it's often misdiagnosed as type 1 or type 2.
The right diagnosis changes treatment. People with GCK-MODY usually need no treatment;
many with HNF1A-MODY do well on inexpensive pills instead of insulin.

When a patient's DNA is tested, the lab often finds a variant nobody has seen before. It
gets reported as a **variant of uncertain significance (VUS)**, which leaves the family
without an answer.

Two key genes:

- **GCK (glucokinase)** is the pancreas's glucose sensor. Broken GCK raises blood sugar
  (MODY). *Overactive* GCK does the opposite: it causes dangerous low blood sugar.
- **HNF1A** is a transcription factor, a protein that switches other genes on. Broken
  HNF1A causes MODY. Some variants make it *more* active.

## The answer keys

Labs have used multiplexed assays to measure nearly every possible single-letter change
in these proteins:

- **GCK activity:** about 97% of possible variants (Gersing et al. 2023).
- **GCK abundance:** whether each variant makes the protein fall apart (Gersing et al. 2024).
- **HNF1A activity:** 11,970 variants. About 1 in 5 rare variants found in people are
  gain-of-function (DeForest et al. 2023).

Links are in [sources.md](sources.md).

## The gap

Most AI predictors (AlphaMissense, ESM, REVEL and others) answer "is this variant
damaging?" They aren't designed to recognize *overactive* variants, and both genes have
plenty. We haven't yet found a paper that grades current predictors on telling the
two apart in these genes. **Checking the literature properly is step one.**

## Rough plan (about 14 weeks)

1. **Learn the proteins.** Look at GCK (PDB `1V4S`) in 3D: the glucose pocket, the ATP
   pocket, and the site where activator drugs bind.
2. **Build the answer key.** Download the lab maps, plus ClinVar (clinical labels) and
   gnomAD (variants in healthy people).
3. **Run predictors on the GPU.** ESM-1v and ESM-2 (protein language models), a
   stability predictor, and precomputed AlphaMissense scores.
4. **Grade them.** How well does each one rank lab-measured damage? Where does it fail:
   overactive variants, particular regions, unstable-versus-stable variants?
5. **Apply it.** Use the best approach on **HNF4A**, a MODY gene with many VUS and no
   published lab map. Rank its VUS, and look closely at the top few in 3D.
6. **Write it up.** Make your claim match your evidence: "best candidates for lab
   testing", not "these cause disease".

## Decisions that are yours

- Which predictors to compare, and which measure of "good" to use, *before* looking at results
- Whether to focus on gain-of-function detection, stability, or region-by-region failures
- What threshold makes a VUS "worth testing"

## What you'd learn

Protein structure, enzyme regulation, human genetics and variant classification (the
ClinGen rules clinical labs use), and how to evaluate a model fairly.
