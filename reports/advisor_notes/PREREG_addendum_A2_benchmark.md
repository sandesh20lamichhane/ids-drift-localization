# PREREG Addendum A2 — CSE-CIC-IDS2018 Benchmark Arms & Gate

Append to: `reports/advisor_notes/PREREG_cse2018.md`
**Commit BEFORE running notebook 25.**
Date: ____________ · Git commit: ____________

## A2.1 Arms (decided from the frozen census, before any benchmark contact)

Leave-one-family-out arms: **{DoS, DDoS, Infiltration, Bot}**.

- **Web is EXCLUDED — underpowered.** The census (`24_family_power.csv`)
  found 75 Web flows corpus-wide (31 + 8 + 19 eval-split flows across two
  days, ≈75 total). The construction injects WINDOW × INJECT_P = 2,000
  family flows per post window; 75 flows cannot produce a measurable
  marginal shift, so every ground truth — Wasserstein anchor included —
  would be noise. Alternatives rejected: keep-at-natural-prevalence (GT
  meaningless), upsample-by-duplication (manufactures a synthetic drift
  signature from repeated rows).
- **Infiltration is RETAINED.** Its A1.3 exclusion from G-DRIFT decisive
  days was about attack-label noise in recall gates; the LOFO construction
  injects flows and measures distributional shift, where attack labels play
  no role in GT_in. ≈20k flows comfortably exceeds MIN_FAMILY = 3,000.
- **BruteForce** is the known-at-training family (A1.3) and remains part of
  the baseline mixture in every arm, never an arm itself — identical to the
  treatment of non-held-out families in the UNSW benchmark.

Significance pairs contributed: 4 families × 3 models × 3 seeds = 36.

## A2.2 Working pool (memory adaptation, construction-neutral)

The benchmark pool is a stratified subsample of 200,000 rows/day (seed 42,
by attack_category), ≈2M rows total, standardised once. Rationale: the
construction draws only 4,000-row windows; the full 15M-row matrix would
exhaust Colab RAM with zero effect on any drawn window. The pool is 10–100×
larger than every draw (WINDOW, ANCHOR_N, ORACLE_N = 4,000).

## A2.3 Construction, methods, GTs — inherited unchanged

Identical to notebook 13 (D030), which holds the 10b (D027) construction
fixed: additive post = baseline + H at prevalence 0.5; localizers {KS,
domain-SHAP, dual-IDS, perm-domain, random}; GTs {per-feature Wasserstein-1
anchor (model-free), domain-oracle-SHAP (circularity reference)};
precision@10; seeds {42, 1, 7}; models {RF (phase1_06 params), XGB, MLP
(256–128–64, F016 agnostic SHAP path)}; margin 0.05; top-k self-stability.

## A2.4 Gate (fixed in advance)

On the Wasserstein anchor, margin 0.05:

- **C2-REPLICATES-2018** iff `dual − domain-SHAP ≤ +0.05` for ALL three
  models (P3) AND `KS − domain-SHAP ≥ −0.05` for RF and XGB (P4).
- **P5 (circularity):** predict domain-SHAP inflation vs its own oracle
  > +0.10 for the tree models; MLP inflation recorded (was ≈+0.09 on UNSW).
- **P6 (open, recorded either way):** MLP `KS − domain-SHAP`. UNSW: MLP beat
  KS (weak marginal shift); CICIDS: it did not (strong shift). 2018 is the
  tiebreaker regime point for the drift-dependent boundary (§IV-G). If the
  MLP beats KS here, the explainer control (clone of 13b) runs before any
  interpretation.
- **DUAL-HELPS-2018** (dual − domain-SHAP > +0.05 for any model) would
  contradict both prior datasets: treated first as a suspected construction
  bug, investigated before being believed.

## A2.5 Deviations

| Date | Deviation | Reason |
|------|-----------|--------|
|      |           |        |
