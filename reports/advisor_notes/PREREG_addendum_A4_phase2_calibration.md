# PREREG Addendum A4 — Trigger Fix v2: Phase-I/Phase-II Calibration

Append after A3. **Commit BEFORE running notebook 26 v2 (Sections 4+).**
Date: ____________ · Git commit: ____________

## A4.0 What A3's run established (recorded, not revised)

- The composition artifact is CONFIRMED and REMOVED: control quiet scores
  ~0.47 vs tau 0.015 (30x elevation); treatment (benign-only reference)
  quiet trace flat at ~0.01. Fig. 26_benign_reference_trace.
- Verdict was FIX-INSUFFICIENT for two reasons, both diagnosed:
  (1) bootstrap calibration windows resampled from one 12.5k pool
  under-disperse the null (shared rows, shared pool quirks), so tau sits
  inside the noise band of fresh benign windows -> 2-3/10 marginal fires;
  (2) **gate-design error (A3.7 deviation):** the pre-registered Wilson
  upper <= 0.20 is unsatisfiable at n=10 (0/10 gives upper 0.277); nb21's
  original flag rule shares this property. Disclosed, not silently changed.
- Also recorded: the three breadths' treatment FA counts are near-replicates
  (same quiet rows, same benign pool at every breadth), not independent.

## A4.1 v2 change (one mechanism): Phase-I/Phase-II calibration

Control-chart standard, deployment-realistic. Null windows for tau are
genuinely disjoint 5,000-row windows:
- the 2 contiguous windows of the benign calibration pool (12.5k), plus
- the first BURN_IN = 2 quiet windows of the live stream (Phase I).
tau = mu + 3*sigma over these 4 disjoint nulls; additionally
tau_floor = max(null scores), with the effective threshold
tau_eff = max(tau, tau_floor). Monitoring (Phase II) starts at window
BURN_IN; burn-in windows are excluded from FA accounting. The reference
stays benign-only (A3.2, proven). No src changes.

## A4.2 Gates (fixed in advance; satisfiable by construction)

Quiet Phase-II windows: n = QUIET_WINDOWS - BURN_IN = 8 at size 5,000.

- **G-CTRL** (carried from A3, already established True).
- **G-FA-1 (primary):** treatment Phase-II quiet FA point rate <= 0.10 at
  every breadth (=> 0/8); Wilson CI reported, not gated (n=8 cannot certify
  0.20 at 95% — stated openly as a power limit of this stream length).
- **G-FA-2 (fine-grained, CI-gated):** at sub-window size 2,500 (16 Phase-II
  quiet sub-windows; tau recalibrated at that size from the same nulls split
  in half), FA count 0/16 required — Wilson upper 0.194 <= 0.20, the CI
  criterion attainable exactly at zero fires.
- **G-DET:** onset latency <= 1 (Phase-II indexing) and treatment
  triggered_2500 drift recall >= control - 0.05, every breadth.
- **G-DETERM:** fixed seed.

**Verdict `ARTIFACT-FIXED-V2`** iff G-FA-1 ∧ G-FA-2 ∧ G-DET (G-CTRL held).

## A4.3 Predictions

P-A4-1: tau_eff separates cleanly: max Phase-II quiet score < tau_eff <
min drift-window score, every breadth.
P-A4-2: FA 0/8 and 0/16 at every breadth.
P-A4-3: latency unchanged (0) and t2500 recall within noise of control.

## A4.4 Deviations

| Date | Deviation | Reason |
|------|-----------|--------|
|      |           |        |
