# PREREG Addendum A6 — Notebook 27: Regime Confirmation Under the v3 Trigger

Follows D040 (nb22 corrected gates) and A5 (v3 trigger, ARTIFACT-FIXED-V3).
**Commit BEFORE running notebook 27.**
Date: ____________ · Git commit: ____________

## A6.1 Purpose

nb22 confirmed the corrected regime gates (D040) over 4 seeds using the
legacy trigger, and reported its quiet-window false alarms as an honest
limitation. Notebook 26 v3 then fixed that trigger (A5). Notebook 27 closes
the arc: re-run nb22's exact multi-seed sweep with the **v3 trigger as the
cheap policy** and show (i) the regime conclusions are trigger-version-
invariant, (ii) the selectivity limitation is gone at 12-stream scale,
(iii) what the cleaner label pool buys the cheap policy.

## A6.2 Design (only the trigger changes vs nb22 / D040)

UNSW breadth sweep [1, 2, 4]; SEEDS = [42, 7, 123, 2024]; window 5,000;
≥10 quiet windows; full data; policies never / always_sliding /
triggered_persist_2500 / triggered_persist_250 (from
`src.adaptation.trigger_v3`, promoted after A5 passed). Monitor per stream:
benign-only reference (half the warm-up benign), tau_v3 with BURN_IN = 4
quiet windows + 2 CAL windows and the 200-draw Q0.999 permutation term,
K_PERSIST = 2. Phase-II monitoring/accounting from window 4. Control-trigger
values are NOT re-run; nb22's stored per-seed results are the reference
(loaded, or transcribed if the JSON is named differently).

## A6.3 Gates

**Regime gates — unchanged from D040, applied to this run's frozen/ceiling
values, all 4 seeds:** G1 (hardest frozen < 0.70), G2a (ceiling ≥ frozen +
0.15 at hardest), G2b (benefit ≤ −0.05 at mildest and ≥ +0.05 at hardest).
Verdict `REGIME-CONFIRMED-UNDER-V3` iff G1 ∧ G2a ∧ G2b in all seeds. These
do not involve the trigger; failure here would indicate a seed/stream
sensitivity problem, not a trigger problem, and is reported as such.

**Trigger gates (new):**
- **G-FA-27:** pooled quiet false FIRES across all 12 seed×breadth streams
  ≤ 1 (per-stream counts and exceedances reported). Rationale: A5.3's loose
  bound gives ≈0.10 expected fires/stream → ≈1.2 over 12 streams; a 0-of-12
  gate would fail ≈30% of the time by design; ≤1 pooled is satisfiable and
  still bounds the pooled rate at 1/72. Empirically (A5 run: 0 exceedances,
  perm-quantile-dominated tau) we predict 0.
- **G-DET-27:** first fire within L_MAX = 2 windows of onset in every
  stream.
- **G-CHEAP-27:** at the hardest breadth, triggered_persist_2500 recall ≥
  frozen + 0.05 in every seed (the cheap policy recovers recall in the hard
  regime). The nb22 original-G2 question (cheap within 0.05 of ceiling) is
  REPORTED per seed, not gated — with the prediction below.

## A6.4 Predictions (falsifiable)

- P-A6-1: pooled quiet fires = 0 across all 12 streams.
- P-A6-2: latency = 1 in every stream.
- P-A6-3: v3 cheap recall exceeds nb22's stored cheap recall at the same
  seed×breadth in ≥ 9 of 12 cells (the clean-pool effect from A5's +0.10 to
  +0.145 at seed 42 generalizes), and closes ≥ half of nb22's
  ceiling−cheap gap at the hardest breadth in ≥ 3 of 4 seeds.

## A6.5 Terminus

This is the last Phase-5/7 experiment before writing. Whatever the verdict,
no further trigger iterations: `REGIME-CONFIRMED-UNDER-V3` + trigger gates →
paper #2's trigger section is complete; any failed gate → reported verbatim
in the same section. Notebook 28 (2018 stream) remains optional future work.

## A6.6 Deviations

| Date | Deviation | Reason |
|------|-----------|--------|
|      |           |        |
