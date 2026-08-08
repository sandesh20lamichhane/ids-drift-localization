# PREREG Addendum A5 — Trigger v3: Persistence Rule + Strengthened Null

Follows A3 (benign-only reference, v1) and A4 (Phase-I/II calibration, v2).
**Commit BEFORE running notebook 26 v3.**
Date: ____________ · Git commit: ____________

## A5.1 What v1 and v2 established (kept) and why v2 failed (diagnosed)

Kept from v1/v2: the benign-only monitor reference removed the initialization
composition artifact (control quiet score ≈ 0.47 vs treatment ≈ 0.013 against
τ ≈ 0.015 — a 30× offset, gone). The remaining failure is different in kind:

- **Multiplicity (predictable):** v2's τ_eff = max of 4 null scores. Under
  exchangeability, each of the 8 monitored quiet windows exceeds a max-of-4
  with probability 1/5 → expected 8/5 = 1.6 false fires; 2 were observed,
  identically across breadths (one shared benign stream). A point threshold
  from n nulls cannot gate m > n future looks to zero. Recorded as A4's
  deviation; v3's design is derived from this rank argument.
- **False fires are destructive, not just wasteful:** `run_instrumented`'s
  triggered policy retrains on the accumulated fired-window pool only, so a
  quiet-window fire replaces the detector with a benign-only model. This is
  retained as a finding (it is *why* selectivity matters in this loop), and
  it motivates gating on fires rather than exceedances.

## A5.2 The v3 mechanism (two changes, both standard SPC)

1. **Persistence (Western-Electric-style run rule):** the trigger FIRES only
   after K_PERSIST = 2 *consecutive* windows exceed τ_eff. Isolated
   noise-band exceedances become non-events; on a contiguous drift period the
   cost is at most +1 window of latency (L_MAX therefore 1 → 2).
2. **Strengthened null:** τ_eff = max( max of N_NULL = 6 genuinely disjoint
   null windows — 2 contiguous CAL windows + BURN_IN = 4 quiet stream
   windows — , the 0.999 empirical quantile of N_PERM = 200 seeded
   permutation null draws: 5,000-row windows sampled without replacement
   from the pooled CAL + burn-in benign rows ). Permutation draws are
   marginally valid null samples; overlap correlates them, which biases a
   *variance* estimate but not an empirical *quantile*, hence the quantile
   form (this is the corrected version of v1's failed bootstrap-σ design).

Everything else is unchanged: benign-only REF_T, nb21 construction (D039),
seed 42, breadths [1, 2, 4], window 5,000, identical streams and detectors
across arms, control arm = nb21-verbatim monitor (no persistence — it is the
historical reference), `run_instrumented` untouched for all existing
policies. The persistence-triggered policy is implemented notebook-locally
with retrain/pool semantics copied verbatim from `cost_eval.run_instrumented`
(promoted to src only if gates pass, per the nb17 promotion pattern).

## A5.3 Pre-registered false-fire arithmetic (what makes the gate satisfiable)

Phase-II quiet windows: 10 − BURN_IN = 6. Under exchangeability with 6
disjoint nulls, per-window exceedance ≤ 1/7; expected isolated exceedances
over quiet ≈ 6/7 ≈ 0.9 (exceedances are EXPECTED and reported, not gated).
Expected persistence FIRES ≈ 5 adjacent pairs × (1/7)² ≈ 0.10 per stream,
further reduced by the permutation-quantile term. The quiet stream is shared
across breadths, so the three breadths are one draw, not three.

## A5.4 Gates

- **G-FA (v3):** quiet-period false FIRES = 0 at every breadth
  (expected ≈ 0.1 under A5.3; exceedance counts reported alongside).
- **G-DET (v3):** first fire within L_MAX = 2 windows of drift onset at
  every breadth, AND treatment triggered_2500 drift recall ≥ control − 0.05
  at every breadth.
- **G-CTRL:** carried as established (A3 run + control arm re-run here for
  the same-table comparison).
- **G-DETERM:** fixed seed end-to-end.

**Verdict `ARTIFACT-FIXED-V3`** iff G-FA ∧ G-DET.
`FIX-COSTS-SENSITIVITY` if G-FA ∧ ¬G-DET.
`FIX-INSUFFICIENT-V3` otherwise — and then the honest terminus for paper #2
is: artifact removed, residual noise-band selectivity characterized with the
rank arithmetic above, persistence analysis reported. No v4 threshold-tuning
iterations; a fourth iteration would require a different monitor statistic
(e.g., EWMA/CUSUM of the KS score), pre-registered separately.

## A5.5 Predictions (falsifiable)

- P-A5-1: quiet exceedances ≈ 0–2 per stream (isolated), FIRES = 0.
- P-A5-2: onset latency = 1 at every breadth (persistence adds exactly one
  window on a contiguous drift period).
- P-A5-3: the in-notebook adjacency diagnostic shows v2's two quiet fires
  were isolated (if they were adjacent, P-A5-1 may fail — reported either
  way; this is the open question the v2 PDF could not answer).

## A5.6 Deviations

| Date | Deviation | Reason |
|------|-----------|--------|
|      |           |        |
