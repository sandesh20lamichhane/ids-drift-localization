# Pre-Registration: CSE-CIC-IDS2018 Third-Dataset Replication

**Status:** committed BEFORE any localization benchmark is run on this dataset.
**Commit this file to the repo first. Do not edit after the first benchmark run;
append an addendum section instead (same discipline as D-log / F-log).**

Author: Sandesh Lamichhane · Date: ____________ · Git commit at registration: ____________

---

## 1. Purpose

Test whether the two central results of the thesis generalize to a third
dataset with ~10 capture days and a larger, more modern attack mix:

- **R1 (benchmark):** a label-free per-feature KS test is competitive with
  explanation-based drift localizers against a model-free drift truth, and the
  dual-model signal adds nothing over its single-model component.
- **R2 (geometry):** real IDS feature geometry does not admit a decorrelated,
  non-degenerate localization target (external-leakage floor above τ = 0.20).

This is a **test, not a confirmation**. Both replication and non-replication
outcomes are reportable; the decision rules below say what each outcome means.

## 2. Dataset and provenance (fixed in advance)

- Dataset: CSE-CIC-IDS2018, CICFlowMeter-V3 flow features, 10 capture days
  (2018-02-14 … 2018-03-02).
- Version: the **improved/corrected release** (Engelen-group format), already
  present at `data/raw/cicids2017_improved/CSECICIDS2018_improved/` (10 CSVs).
  [x] corrected/improved   [ ] original
- Sampling: if a day exceeds 1.5M flows after cleaning, per-day stratified
  subsample to 1.5M by `attack_category`, seed 42 (notebook 05, Stage 2).
  Recorded in `data_card_cse2018.md`.
- The first capture day used for frozen-detector training is
  **wed_14_02** (FTP/SSH brute force + benign), mirroring the CICIDS2017
  "early day" cold-start design.

## 3. Pre-registered quantities and predictions (falsifiable)

Computed exactly as thesis Defs. 1–3 (absolute Pearson correlation on the
standardised feature matrix; non-degeneracy = top value ≤ 0.90 of rows and
≥ 20 distinct values; decorrelation threshold τ = 0.20; leakage L(S) per Eq. 1).

| ID | Quantity | Prediction | Falsified if |
|----|----------|------------|--------------|
| P1 | median feature redundancy (non-degenerate features) | ≥ 0.85 | < 0.85 |
| P2 | external-leakage floor for best size-5 non-degenerate set | ≥ 0.20 | < 0.20 |
| P3 | dual − domain-SHAP margin (all 3 models, Wasserstein anchor) | ≤ 0 within noise (±0.05) | > +0.05 consistently |
| P4 | KS − domain-SHAP margin (RF, XGBoost) | ≥ −0.05 | < −0.05 consistently |
| P5 | circularity inflation score(dom-SHAP, GT_ex) − score(dom-SHAP, GT_in) | > +0.10 | ≤ +0.10 |
| P6 | MLP domain-SHAP vs KS | no prediction — this is the open question from §IV-G (drift-dependent boundary). Recorded either way. | n/a |

## 4. Experimental grid (fixed in advance)

Identical to the UNSW replication design (thesis §7.7):

- Drift construction: additive leave-one-family-out streams over the novel
  attack families; per-day chronological stream retained for the drift-premise
  check.
- Localizers: KS, domain-SHAP, dual-IDS, permutation, random.
- Models: RF (100 trees, depth 12), XGBoost, MLP (256–128–64) — same configs
  as Appendix B.
- Ground truths: GT_in = per-feature Wasserstein-1 anchor (primary);
  GT_ex = domain-oracle SHAP (for the circularity measurement only).
- Metric: precision@10; chance = 10/d for d harmonized features.
- Seeds: {42, 1, 7}. Significance: Wilcoxon signed-rank + bootstrap CI +
  d_z, pairs formed family×model×seed, pooled into Table IV's framework.

## 5. Acceptance gates (verdict scheme, fixed in advance)

Same tiering as thesis §5.12 (margin 0.05; sub-margin differences = noise).

- **G-DRIFT:** frozen cold-start recall on novel-family days drops by ≥ 0.30
  vs its training-day recall, and imbalance controls (balanced / downsampled)
  move recall by < 0.01. If G-DRIFT fails, the dataset is a *mild-regime*
  dataset; the benchmark still runs but is reported as such.
- **G-GEOM:** decision rule, not a pass/fail —
  - if **no** decorrelated (L(S) ≤ 0.20) non-degenerate size-5 target exists →
    R2 replicates; dataset joins CICIDS/UNSW as "unreachable regime" evidence.
  - if such a target **does** exist → run the leakage-to-recovery experiment
    (the C4-promotion test the thesis could not run) on it, gates to be
    pre-registered in an addendum BEFORE that run.
- **G-BENCH:** R1 replicates iff P3 and P4 both hold. If the MLP beats KS
  here (P6), report the drift-marginality diagnostic (per-feature KS_max on
  injected families) exactly as done for the UNSW/CICIDS contrast in §7.8.4.

## 6. What will be reported regardless of outcome

Geometry table (row for Table analog: n features, non-degenerate count,
median redundancy, leakage floor); full method×GT matrix; per-seed raw CSVs;
failed gates verbatim. No gate is revised after data contact; addenda only.

## 7. Deviations log

| Date | Deviation | Reason |
|------|-----------|--------|
|      |           |        |
