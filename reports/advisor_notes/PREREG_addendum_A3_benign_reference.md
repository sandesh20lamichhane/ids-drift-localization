# PREREG Addendum A3 — Benign-Only Monitor Reference (Notebook 26)

Append to the Phase-5 pre-registration trail (decisions D035/D039/D040).
**Commit BEFORE running notebook 26.**
Date: ____________ · Git commit: ____________

## A3.1 The artifact being fixed (diagnosis, stated in advance)

Notebooks 20–22 report trigger false alarms on quiet windows (nb21 gate G3
flags Wilson upper > 0.20; thesis §8 reports 15–25%). Mechanism as diagnosed:
the UNSW streams' quiet stretch is **benign-only by construction**, while the
monitor's initial reference and its calibration windows are the **warm-up
mixture** (benign + SEEN attack families). The mean-KS score on early quiet
windows therefore measures a *composition* difference (mixture vs benign),
not drift; because the triggered policy's reference updates to the last fired
window, the monitor fires on the first quiet window(s), resets onto benign
data, then goes silent — an initialization artifact, not noise.

## A3.2 The fix (call-site only; no src changes)

Decouple the **monitor's** data from the **detector's** warm-up:
- Detector warm-up: unchanged (benign + SEEN; a supervised RF needs both
  classes — nb21's rejection of benign-only *warm-up* stands).
- Monitor initial reference `REF_MON`: the first half (12.5k rows, seeded
  permutation) of the warm-up's 25k benign rows — benign-only.
- Monitor calibration: the other 12.5k benign rows. Because that pool yields
  only 2 contiguous 5k windows, the null distribution is estimated from
  **N_CAL = 10 seeded bootstrap windows** (5,000 rows sampled without
  replacement per window from the calibration pool); tau = mu + 3·sigma as
  everywhere in Phase 5. **Sensitivity check (reported, not gated):** tau
  recomputed from the 2 contiguous windows; the FA/detection conclusions
  must be stated under both if they differ.
- `KSMonitor`, `run_instrumented`, all policies: byte-identical. Only
  `reference0` (and the calibration data behind `tau`) change.

## A3.3 Design

Exact nb21 construction (D039): UNSW full data, WINDOW 5,000, ≥10 quiet
benign windows then novel-family drift, breadths B = [1, 2, 4], seed 42,
policies never / always_sliding / triggered_250 / triggered_2500.
Two monitor arms on **identical streams and identical detectors**:
- **control** — mixed reference + contiguous mixed calibration (nb21
  verbatim; must reconcile with the stored nb21 summary).
- **treatment** — benign-only reference + bootstrap benign calibration
  (A3.2).

False-alarm accounting: trigger set of `triggered_250` over quiet windows,
k/n with Wilson 95% CI (nb21 convention). Onset latency: first fired window
minus first drift window.

## A3.4 Gates (fixed in advance; failures reported, not tuned)

- **G-CTRL (artifact reproduces):** control arm quiet-FA point rate > 0.10
  at ≥ 1 breadth on these streams. If it does not, the artifact premise
  fails and the notebook reports an honest null (the fix would be moot).
- **G-FA (fix works):** treatment arm quiet-FA at **every** breadth:
  point ≤ 0.10 AND Wilson upper ≤ 0.20.
- **G-DET (no sensitivity cost):** treatment trigger fires within
  L_MAX = 1 window of drift onset at every breadth, AND treatment
  triggered_2500 drift-window recall ≥ control triggered_2500 recall − 0.05
  at every breadth.
- **G-DETERM:** fixed seed end-to-end.

**Verdict `ARTIFACT-FIXED`** iff G-CTRL ∧ G-FA ∧ G-DET.
`FIX-COSTS-SENSITIVITY` if G-FA holds but G-DET fails.
`ARTIFACT-NOT-REPRODUCED` if G-CTRL fails.

## A3.5 Predictions (falsifiable)

P-A3-1: control quiet FA ≈ nb21's flagged rates (point 0.1–0.3 band).
P-A3-2: treatment quiet FA = 0/n at every breadth.
P-A3-3: treatment onset latency ≤ control's (a benign-only reference should
be *more* sensitive to a 50%-novel drift window, not less).

## A3.6 What this feeds

Paper #2's trigger section: the nb21/22 selectivity limitation becomes
"diagnosed (initialization composition artifact) → fixed (benign-only
reference, call-site change) → re-validated on identical streams". Notebook
27 then re-confirms the regime gates (nb22) under the fixed trigger with a
fresh pre-registration.

## A3.7 Deviations

| Date | Deviation | Reason |
|------|-----------|--------|
|      |           |        |
