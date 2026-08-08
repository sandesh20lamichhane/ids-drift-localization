# Open Questions

Things noticed but deliberately parked, so we do not forget them.
Each entry carries a Status line: OPEN or RESOLVED. Resolve via
`resolve_open_question(...)`, or by editing the Status line by hand.

Seeded and appended via `src/utils/documentation.py`.

## Q001 — Why is the Thursday-Friday cross-day duplicate rate anomalously high (74 vs ~30)?
*Raised 2026-06-04 | context: `05_data_characterization`*

**Status:** OPEN

**Why parked.** Overall duplicate rate is 0.402%, below the 1% acceptability bar (D010).

**Revisit when.** If day-split leakage is suspected, or if Thursday/Friday results look anomalous in Phase 1.


## Q002 — Should the remaining int64 feature columns be downcast (they exceed int32 range)?
*Raised 2026-06-04 | context: `03_csv_to_parquet / 06 dtype check`*

**Status:** OPEN

**Why parked.** Functionally fine for RF and TreeSHAP; only ~30 MB overhead.

**Revisit when.** If memory-bound during streaming experiments, or before any public data release.


## Q003 — Do the near-constant flag features (urg/cwr/ece, ICMP code/type) carry rare-attack signal?
*Raised 2026-06-04 | context: `05_data_characterization, D009`*

**Status:** OPEN

**Why parked.** Kept them; the cost of keeping is low.

**Revisit when.** During feature ablation, or if SHAP flags them as important under drift.


## Q004 — Will CSE-CIC-IDS-2018 be needed as a Phase 2 dataset?
*Raised 2026-06-04 | context: `D005 (34 GB downloaded but not converted to Parquet)`*

**Status:** OPEN

**Why parked.** UNSW-NB15 is the primary second dataset; converting 34 GB now is premature.

**Revisit when.** Phase 2 multi-dataset generalization design.


## Q005 — Should Engelen *-Attempted rows be dropped for a robustness ablation?
*Raised 2026-06-04 | context: `D002 (currently *-Attempted counts as attack)`*

**Status:** OPEN

**Why parked.** Tangential to the drift / localization contribution.

**Revisit when.** Robustness ablation when writing the paper.


## Q006 — How should Heartbleed (only 11 flows) be handled in per-attack analysis?
*Raised 2026-06-04 | context: `D006`*

**Status:** OPEN

**Why parked.** Effectively absent for binary classification.

**Revisit when.** If per-attack-category results need it; otherwise note as a dataset limitation.


## Q007 — Does dual-model SHAP divergence localize better than the auxiliary-model SHAP importance ALONE?
*Raised 2026-06-04 | context: `Raised reviewing notebook 06: cold_start collapses to all-benign on Wed-Fri`*

**Status:** RESOLVED (2026-06-04) — Measured (post-drift, GT1, p@10): dual_gain=0.667 vs aux_only=0.711, margin=-0.044. Dual does NOT beat aux-only; reframe as auxiliary-model explanation localization (see F005).

**Why parked.** Requires the Phase 1 main experiment (notebook 07) to test.

**Revisit when.** Notebook 07 MUST include an aux_only_shap localization baseline. The risk: on Wed-Fri the frozen model predicts all-benign, so its SHAP may be near-zero/noisy and the divergence could reduce trivially to the auxiliary-model importance. If dual-model does NOT beat aux_only, reframe the contribution as "auxiliary-model explanation localization" rather than "dual-model divergence".


## Q008 — Does KS-D (input-distribution drift) align with SHAP-importance drift for the ground-truth drifted set?
*Raised 2026-06-04 | context: `Raised reviewing D008 / D012`*

**Status:** RESOLVED (2026-06-04) — GT1 (KS input-drift) vs GT2 (oracle importance) Jaccard = 0.676 (post-drift mean). Input-drift and importance-drift largely agree.

**Why parked.** Requires notebook 07 to measure both.

**Revisit when.** Notebook 07 should define a SECOND, model-relative ground truth (features the oracle relies on that cold_start does not) and report precision@K against BOTH the KS-based and the model-relative sets. If they disagree, that disagreement is itself a finding worth reporting.

