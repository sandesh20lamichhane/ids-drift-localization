# Findings Log

Chronological record of empirical discoveries. Append-only. Each
entry records what we did, what we found (with numbers), why it
matters, and what (if anything) surprised us.

Seeded and appended via `src/utils/documentation.py::log_finding`.

## F001 — Synthetic pilot (v1-v4b): the contribution is localization, not detection timing
*Logged 2026-06-04 | context: `pilot experiments, prior to real data`*

**What we did.** Built controlled synthetic drift (relevance-swap and distribution-shift) and tested several explanation-space signals -- single-model SHAP rank stability, dual-model SHAP divergence (Spearman, Jaccard, KL, Wasserstein, PSI), and a prediction-disagreement baseline -- for both drift DETECTION and feature-level LOCALIZATION.

**What we found.** (1) Single-model SHAP fails as a leading drift indicator. (2) Dual-model SHAP detection only matches the prediction-disagreement baseline; the apparent "lead time" was a noise-scaling artifact. (3) Dual-model SHAP LOCALIZATION wins decisively: precision@K = 1.0 vs 0.46-0.75 for the permutation baseline, across both drift types. (4) Localization holds even when the two models still agree on predictions.

**Why it matters.** Narrows the surviving novelty from "SHAP detects drift early" (falsified) to "dual-model SHAP localizes which features drifted" (supported in synthetic). This is the claim the real-data experiments must now test.

**What surprised us.** The leading-indicator intuition -- the original thesis hook -- was wrong. The value lives in WHICH features changed, not WHEN.


## F002 — CICIDS2017 drift is real but moderate (notebook 05)
*Logged 2026-06-04 | context: `01_phase0_foundation/05_data_characterization`*

**What we did.** Quantified per-feature distribution shift (KS-D per feature, each day vs Monday), per-day class composition, constant/near-constant features, cross-day duplicates, and per-batch SHAP compute cost.

**What we found.** KS-D peaks around 0.45 (Friday) -- moderate, not categorical. The most-drifted features are packet-length statistics (fwd_packet_length_max, packet_length_std, and similar). Zero truly-constant features (Engelen cleaning is thorough); 8 near-constant flag features kept. Cross-day duplicates 0.402% overall, with Thursday-Friday anomalously high (74 vs ~30 elsewhere). TreeSHAP ~6.5s per 1000 samples, so a full streaming matrix is ~54 min per drift type -- tractable on CPU.

**Why it matters.** Real drift is far gentler than the synthetic regime (KS approx 1.0). The synthetic precision@K = 1.0 will NOT transfer; expect substantial degradation on real data. The KS-top-K features become the first ground-truth drifted set (D008).


## F003 — Cold-start RF collapses on post-drift attack days (notebook 06)
*Logged 2026-06-04 | context: `01_phase0_foundation/06_baseline_rf_per_day`*

**What we did.** Trained five baselines (cold_start, cold_start_balanced, cold_start_downsampled, realistic, oracle) and evaluated per-day recall, a multi-threshold sweep, and a per-attack-category breakdown.

**What we found.** Cold-start gets 0.981 recall on Tuesday (the brute-force attacks it trained on) and EXACTLY 0.000 on Wednesday, Thursday, and Friday. Oracle gets 0.99+ every day. Max attack probability for cold-start on Wednesday is ~0.16, so no decision threshold recovers it (recall ~0.01 even at threshold 0.01). Headroom (oracle - cold_start) on attack days is +0.749.

**Why it matters.** Empirically validates the drift premise on real data, with large headroom for any drift-handling method to demonstrate value. The honest headline is "0.000 on Wed/Thu/Fri", not the Tuesday-inflated 0.245 mean.


## F004 — Drift, not class imbalance, is the dominant failure mode (notebook 06, D015)
*Logged 2026-06-04 | context: `01_phase0_foundation/06_baseline_rf_per_day`*

**What we did.** Compared the imbalance-control baselines (class_weight="balanced", benign downsampling to ~100:1) and the larger-data baseline (realistic) against raw cold-start.

**What we found.** Imbalance handling recovers +0.001 mean recall; doubling the Tuesday training data recovers ~+0.004. Both are measurement noise. Only the oracle -- trained on the post-drift distribution -- recovers recall (0.994).

**Why it matters.** Rules out class imbalance, training-set size, and threshold calibration as the cause. The model must LEARN post-drift attack signatures; it cannot be coaxed there by reweighting. This is classical concept drift (P(y|X) shifts across days) and it fixes cold_start as the Phase 1 reference baseline.


## F005 — Dual-model SHAP localization on CICIDS2017 (notebook 07)
*Logged 2026-06-04 | context: `02_phase1_main/07_localization_dual_shap`*

**What we did.** Froze the cold-start model, trained a per-day auxiliary RF, and scored each feature by dual-model SHAP divergence (directional dual_gain), with aux_only, main_only, permutation-disagreement and random baselines. Measured precision@K against an input-drift ground truth (GT1, KS) and an oracle-importance ground truth (GT2), across a Tuesday control and three post-drift days, over 3 seeds.

**What we found.** Post-drift mean precision@10 vs GT1: dual_gain=0.667, aux_only=0.711, perm_disagree=0.378 (random 0.183). Margin over strongest baseline = -0.044; dual_gain - aux_only = -0.044. Tuesday control dual_gain=0.000. GT1/GT2 Jaccard (post-drift) = 0.676. D012 tier: WEAK.

**Why it matters.** This is the gate for the whole approach. The D012 tier determines whether notebook 08 (adaptation/efficiency) proceeds as planned, narrows, or pivots; the Q007 margin determines whether the dual-model framing survives or is reframed as auxiliary-model explanation localization.


## F006 — Label-efficiency of dual-model vs aux-only SHAP localization (notebook 07b)
*Logged 2026-06-04 | context: `03_phase1_cicids/07b_label_efficiency`*

**What we did.** Swept the auxiliary-model label budget (250 -> 100000 rows) with all else fixed from nb07, and compared post-drift precision@10 of dual_gain vs aux_only across budgets, gating interpretability on aux-model recall >= 0.7. Pre-registered rescue/reframe rule (D018).

**What we found.** Verdict: REFRAME. Post-drift precision@10 by budget -- dual_gain: 250:0.72, 1000:0.68, 5000:0.64, 25000:0.67, 100000:0.67; aux_only: 250:0.77, 1000:0.76, 5000:0.70, 25000:0.71, 100000:0.71. Margin (dual-aux) by budget: 250:-0.04, 1000:-0.08, 5000:-0.06, 25000:-0.04, 100000:-0.04. Interpretable budgets (aux_recall>=0.7): [250, 1000, 5000, 25000, 100000].

**Why it matters.** Tests the dual framing on the axis that matters operationally (label scarcity), removing nb07 main compromise. The verdict determines whether the original dual-model hypothesis survives, survives weakly, or is formally reframed to auxiliary-model explanation localization before building the adaptation experiment (nb08).


## F007 — Label-free KS vs SHAP localization on CICIDS2017 (notebook 07c)
*Logged 2026-06-04 | context: `03_phase1_cicids/07c_ks_vs_shap_localization`*

**What we did.** Added KS-drift as a label-free, model-free localization method and compared it to auxiliary SHAP importance (aux at 100k labels, its strongest form) against three ground truths: GT1 (KS, circular), GT2 (oracle SHAP), and GT3 (oracle permutation importance w.r.t. recall, the SHAP-independent neutral arbiter). Pre-registered rule (D019).

**What we found.** Verdict: SHAP-ADDS-VALUE. Post-drift precision@10 vs GT3 (neutral): aux_only=0.389 vs ks=0.267 (margin +0.122, SE 0.079). vs GT2 (SHAP-modality): aux_only=0.767 vs ks=0.833 (margin -0.067). Mutual Jaccard(KS, aux) post-drift = 0.501.

**Why it matters.** Decides whether the explanation pipeline earns its place at all. If a free KS test localizes as well as SHAP against a behaviour-based ground truth, the localization contribution is redundant on CICIDS and the thesis must move its centre of gravity (adaptation-efficiency, a pure-concept-drift testbed, or a negative-empirical-study).


## F008 — Stability and cross-model generality of importance disagreement (notebook 07d)
*Logged 2026-06-04 | context: `03_phase1_cicids/07d_disagreement_stability`*

**What we did.** Tested whether the F007 importance-method disagreement is genuine (vs permutation noise) and general (vs RandomForest-specific), using three independent estimators (TreeSHAP, permutation with 20 repeats, built-in gain) over 5 seeds on the RF oracle and a fresh XGBoost oracle. Measured self-stability and cross-method top-15 Jaccard. Pre-registered gate (D020): the perm-free SHAP-vs-gain pair decides genuineness; XGBoost decides generality.

**What we found.** Verdict: PERMUTATION-DRIVEN. RandomForest post-drift: SHAP self-stability=0.921, perm self-stability=0.584; cross-method SHAP-perm=0.158, SHAP-gain=0.543, perm-gain=0.147 (chance ~0.10). XGBoost: SHAP-perm=0.350, SHAP-gain=0.247, perm-gain=0.195.

**Why it matters.** Decides whether the importance-disagreement mechanism is a headline thesis contribution or a footnote. SURVIVES -> build the framework on it; PERMUTATION-DRIVEN or RF-SPECIFIC -> demote and lean on the redundancy findings (F005-F007), which stand independently.


## F009 — Drift-regime conditions test on real features with known ground truth (notebook 07e / ARM B)
*Logged 2026-06-04 | context: `03_phase1_cicids/07e_drift_regime_testbed`*

**What we did.** Built a semi-synthetic 2x2 crossover on real CICIDS feature vectors with a synthetic label rule, so the drifted features are known in both arms. Distributional arm shifts input marginals (P(X) moves, rule fixed); concept arm swaps relevant features (P(X) stable, P(y|X) moves). Measured precision@10 of KS (label-free) and aux-SHAP at recovering the known drifted set, with construction-validity checks. Pre-registered H1 + falsifiers (D021).

**What we found.** Verdict: H1-REFUTED-CONCEPT. Precision@10 -- distributional: KS=1.000, aux_SHAP=0.200; concept: KS=0.267, aux_SHAP=0.267 (chance 0.18). Construction valid (concept P(X) stable): True.

**Why it matters.** This is the confound-controlled test of the conditions thesis. With ground truth held known in both arms, a KS-collapse-under-concept-drift / SHAP-works crossover attributes the difference to drift TYPE, not ground-truth availability -- which is what licenses the "conditions of validity" framing for the thesis.


## F010 — Feature-correlation ablation of explanation localization (notebook 07f)
*Logged 2026-06-04 | context: `03_phase1_cicids/07f_correlation_ablation`*

**What we did.** Swept the correlation of the known relevant set in the 07e concept-drift arm (P(X) stable, recover S2), selecting S2 from real CICIDS features at redundancy quantiles from weak to strong external leakage, and measured aux-SHAP precision@10 at recovering S2 (KS carried as the concept-blind baseline). Pre-registered H2 + gate (D022).

**What we found.** Verdict: H2-REFUTED-FLAT. Precision@10 vs known S2 -- weak correlation (leak 0.37): aux_SHAP=0.267, KS=0.100; strong correlation (leak 1.00): aux_SHAP=0.200, KS=0.233 (chance 0.12). SHAP trend (weak-strong) = +0.067.

**Why it matters.** 07e refuted drift TYPE as the governing variable. This isolates feature correlation as the candidate. If SHAP localization recovers when the relevant features are decorrelated, the conditions-of-validity result rests on a measurable variable (correlation) with a deployment diagnostic; if not, the negative is unconditional. Either way it fixes the thesis spine.


## F011 — Decorrelated-limit + synthetic mechanism control for explanation localization
*Logged 2026-06-04 | context: `03_phase1_cicids/07g_decorrelated_limit`*

**What we did.** Closed 07f's construction gap (its lowest leakage was 0.37, never decorrelated). Quantified the feature-redundancy distribution; ran a real-data arm selecting the lowest-redundancy features to minimise external leakage; and a synthetic control arm sweeping a clean external-correlation knob rho from 0 upward to isolate the identifiability mechanism. Pre-registered H2b + gate (D023).

**What we found.** Verdict: MECHANISM-HOLDS-SYNTH-ONLY. Synthetic: aux-SHAP precision@5 at rho=0 = 1.000, at rho=0.99 = 0.533 (trend +0.467), chance 0.061. Real lowest-redundancy set: leakage 0.024 (reached decorrelated: True), aux-SHAP 0.067. Redundancy: median 0.95, 6 of 82 features below 0.20.

**Why it matters.** 07f could not distinguish "correlation does not matter" from "could not escape correlation". The synthetic arm reaches leakage 0 and answers the mechanism directly; the real arm answers reachability. Together they settle whether the localization failure is non-identifiability under feature redundancy (a precise, measurable structural cause with a deployment diagnostic) or an unconditional unreliability of explanation localization.


## F012 — Degeneracy diagnostic + non-degeneracy-controlled real localization arm
*Logged 2026-06-04 | context: `03_phase1_cicids/07h_degeneracy_diagnostic`*

**What we did.** Resolved 07g's invalid real-low arm (NaN recall). Computed per-feature degeneracy (modal fraction, distinct values), reproduced 07g's lowest-redundancy set to show its degenerate label, then re-ran the real concept arm selecting lowest- vs highest-redundancy sets from NON-DEGENERATE features only (vary correlation, hold non-degeneracy fixed), gating each on aux-recall and label balance. D024.

**What we found.** Verdict: COMPOUND-STRUCTURAL-BLOCK. Of 82 features, 63 are non-degenerate (modal<=0.90, distinct>=20). 07g's lowest-redundancy set had modal fractions up to 1.000 and a label balance of 0.0000 (the NaN-recall cause). Lowest-redundancy non-degenerate set: external leakage 0.248 (decorrelated reachable: False); aux-SHAP 0.267 (recall 0.99, balance 0.50, chance 0.061). Correlated non-degenerate set: leakage 0.974, aux-SHAP 0.600. 07g synthetic mechanism confirmed (rho=0 SHAP=1.0).

**Why it matters.** Determines whether explanation localization fails on CICIDS for a compound, measurable structural reason (informative features collinear; decorrelated features degenerate) or whether a real decorrelated regime exists. Closes the positive-shaped search and supplies the two-dimensional pre-deployment diagnostic (redundancy AND distributional health) for the evaluation-framework contribution.


## F007 — CORRECTION (post-07d)  (2026-06-05)
**Applies to:** F007 (07c, KS vs SHAP localization). Annotation, not overwrite.

The cell's auto-verdict "SHAP-ADDS-VALUE" was artifact-sensitive and is corrected to
**REDUNDANT / KS-competitive**. It rested on GT3 (oracle *permutation* importance), which
07d showed to be the unstable estimator (permutation self-stability 0.584 vs SHAP 0.921;
SHAP and gain agree at 0.543 while permutation agrees with neither, ~0.15). GT3 was
therefore modality-matched to the permutation baseline, not the neutral arbiter it was
treated as. On GT2 (oracle SHAP) a label-free **KS test (0.833) beat aux-SHAP (0.766)**,
and GT2 vs GT3 overlapped at Jaccard 0.11-0.20 (~chance). Corrected reading: SHAP
localization does **not** robustly beat a free KS test on CICIDS.

## F011 — CORRECTION (post-07h)  (2026-06-05)
**Applies to:** F011 (07g, decorrelated-limit + synthetic mechanism). Annotation, not overwrite.

The auto-verdict "MECHANISM-HOLDS-SYNTH-ONLY" over-read a broken construction. The real
low-redundancy arm returned **aux_recall = NaN**: its features (fwd_urg_flags,
bwd_urg_flags, urg_flag_count, subflow_bwd_packets) are **constant in the Monday sample**
(distinct = 1, modal fraction 1.000), so the median-split label collapsed to a single class
(balance 0.0000) and the model never trained. Its 0.067 precision is noise, not evidence of
a "second factor."
**Bankable from 07g:** the *synthetic* identifiability mechanism is confirmed -- with a
proxy-free target aux-SHAP recovers perfectly (rho=0 precision 1.000), degrading
monotonically as proxies strengthen (rho=0.99 -> 0.533, trend +0.467), KS at chance
throughout. Real reachability is resolved in F012 (07h), not here.

## F012 — CAVEAT (corrected-arm confound)  (2026-06-05)
**Applies to:** F012 (07h, degeneracy diagnostic + corrected real arm). Annotation.

The verdict **COMPOUND-STRUCTURAL-BLOCK holds** on its logic: of 82 features, 63 are
non-degenerate, and the lowest-redundancy non-degenerate set of size 5 has external leakage
0.248 (> 0.20), so no decorrelated-and-informative set exists; the decorrelated features are
constant/near-constant. Two caveats for honest reporting:
(1) The corrected arm **remained confounded** -- the lowest-redundancy non-degenerate
features are still the most near-constant within the band (modal 0.900, 0.875), and the
**correlated set localized better than the decorrelated set** (aux-SHAP 0.600 vs 0.267),
the opposite of the identifiability prediction. So external leakage does **not** predict
recovery on real CICIDS features, and the real arm does not validate "decorrelate ->
recover."
(2) Consequently the identifiability account **explains** the synthetic regime and the
real-data failure, but does **not** yield a validated scalar deployment diagnostic on
CICIDS. Claim the redundancy/degeneracy diagnostic as *mechanism-motivated*, not
*validated-predictive*. The clean leakage->recovery test belongs in breadth (UNSW, less
collinear), which can construct the un-confounded regime CICIDS cannot.

## F013 — UNSW-NB15 geometry + controlled localization across RF and XGBoost (cross-dataset)
*Logged 2026-06-05 | context: `04_phase2_multidataset/09_unsw_geometry_localization`*

**What we did.** Applied the Phase-1 protocol to UNSW-NB15 and across RF + XGBoost: characterized feature redundancy and degeneracy (vs CICIDS), tested whether a decorrelated-and-non-degenerate set is reachable, and ran the controlled known-GT leakage->recovery sweep on real UNSW features (concept arm, recover S2), gating on recall + balance. D025.

**What we found.** Verdict: CROSS-DATASET-BLOCK. UNSW median redundancy 0.903 vs CICIDS 0.95; non-degenerate 29/42 vs 63/82. Min non-degenerate external leakage 0.444 (reached <= 0.20: False; CICIDS floor 0.248). At the lowest-leakage level: RF aux-SHAP 0.467 (recall 0.99), XGB aux-SHAP 0.600 (recall 0.99), KS 0.267, chance 0.119. RF vs XGB agree on recovery: False.

**Why it matters.** First breadth result. Determines whether the CICIDS structural block (no identifiable localization target) is dataset-specific or general, whether the identifiability mechanism holds on real data when the geometry permits the test, and whether the picture is model-class-dependent (RF vs XGBoost). This is the generalization the Q1 cross-dataset claim rests on.


## F014 — UNSW real distributional-drift benchmark: KS vs SHAP vs dual across RF and XGBoost
*Logged 2026-06-05 | context: `04_phase2_multidataset/10_unsw_distributional_benchmark`*

**What we did.** Benchmarked drift-localization under REAL distributional drift on UNSW (leave-one-attack-family-out), across RF + XGBoost, against a label-aware model-free AUC anchor (plus oracle-SHAP / oracle-gain to expose modality-circularity). Compared aux-SHAP, dual-SHAP, KS, permutation-disagreement, random by precision@K and Spearman, with a permutation self-stability check. D026.

**What we found.** Verdict: SHAP-ADDS-VALUE-ON-UNSW. On the AUC anchor (chance 0.238): aux-SHAP 0.422, dual-SHAP 0.322 (dual-aux -0.100), KS 0.133 (KS-aux -0.289), perm-dual 0.328. aux-SHAP inflates +0.439 against its own oracle-SHAP GT (modality-circularity). Self-stability: aux-SHAP 0.729 vs perm-dual 0.514. Families ['Generic', 'Exploits', 'Fuzzers']; RF + XGBoost; CICIDS reference KS-vs-aux +0.067 (KS 0.833 > aux 0.766).

**Why it matters.** Makes the redundancy/benchmark claim (C2: KS competitive with SHAP, dual adds nothing) a cross-dataset, cross-model, real-drift result rather than CICIDS-only, and re-confirms the modality-circularity and permutation-instability lessons on UNSW -- the core of the evaluation-framework contribution.


## F015 — UNSW corrected drift-localization benchmark: KS vs domain-SHAP vs dual (RF + XGBoost)
*Logged 2026-06-05 | context: `04_phase2_multidataset/10b_drift_localization_benchmark`*

**What we did.** Corrected the notebook-10 construction artifact (F014). Tested C2 under REAL additive drift on UNSW (inject family H at prevalence 0.50, baseline held constant), comparing drift-localizers only -- KS, domain-classifier SHAP, the original dual-IDS disagreement, perm-domain, random -- against a model-free Wasserstein drift anchor (domain-oracle GTs for modality-circularity), RF + XGBoost, with a self-stability check. D027; supersedes D026.

**What we found.** Verdict: C2-REPLICATES-CROSS-DATASET. On the Wasserstein anchor (chance 0.238): KS 0.411, domain-SHAP 0.367 (KS-domainSHAP +0.044), dual-IDS 0.372 (dual-domainSHAP +0.006), perm-domain 0.322. domain-SHAP inflates +0.422 against its own oracle GT. Self-stability: domain-SHAP 0.619 vs perm-domain 0.323. Families ['Generic', 'Exploits', 'Fuzzers']; RF + XGBoost.

**Why it matters.** This is the valid cross-dataset test of C2 (KS competitive with explanation-based localization; original dual disagreement adds nothing) under real drift, replacing the construction-limited notebook 10. It also re-confirms modality-circularity and permutation-instability on UNSW -- the core of the C1 evaluation-framework contribution.


## F014 — CORRECTION (construction-limited; superseded by F015)  (2026-06-05)
**Applies to:** F014 (notebook 10, UNSW distributional benchmark). Annotation, not overwrite.

The auto-verdict **SHAP-ADDS-VALUE-ON-UNSW is a construction artifact** and does **not**
overturn C2. Two coupled flaws: (1) the AUC anchor (H-vs-benign separability) is the *same
task* as aux-SHAP (a benign-vs-H model's attribution), so the anchor was aligned with SHAP,
not neutral; (2) the leave-one-family-out construction put the other attacks in the pre-window,
so KS (which targets the pre->post input shift) was scored on the wrong contrast and fell
**below chance** (0.133 < 0.238 random). That measured attack-attribution, not
drift-localization -- and C2 is a drift-localization claim.

**What survives (robust to the flaw):** dual adds nothing (dual-aux = -0.100, GT-robust
internal-SHAP comparison); **modality-circularity** confirmed on UNSW (aux-SHAP inflates
+0.439 vs its own oracle-SHAP GT); **permutation-instability** confirmed (perm-dual 0.514 vs
aux-SHAP 0.729 self-stability).

**Correction:** notebook **10b (F015, D027)** re-tests C2 with an additive-drift construction
(post = baseline + injected H, baseline held constant), drift-localizers only (KS vs a
pre-vs-post domain-classifier SHAP vs the original dual-IDS disagreement), and a model-free
Wasserstein drift anchor. F015 supersedes the KS-vs-SHAP reading of F014; the dual /
modality / stability results above stand.

## F001 — ANCHOR-INTEGRITY CONFIRMED (P(X) stable)  (2026-06-05)
**Applies to:** F001 (synthetic relevance-swap concept pilot). Caveat RESOLVED.

The relevance swap holds the input marginals stable. Per-feature KS between X_pre and X_post in the concept arm (ks_max 0.0168) is indistinguishable from the sampling-noise null (ks_max 0.0168) and far below the covariate-shift control (ks_max 0.9998); 07e independently reported 0.017. X_post is never modified in the concept construction, so P(X) is stable by construction and confirmed empirically. F001 is a clean concept-drift anchor and KS could NOT have localized it via input shift -- the pending caveat is resolved.

## F016 — MLP-SHAP infrastructure validated (model-agnostic explainer for the neural breadth phase)
*Logged 2026-06-09 | context: `05_phase3_generalization/11_mlp_shap_infrastructure`*

**What we did.** Added a model-agnostic SHAP path (PermutationExplainer default, KernelExplainer fallback) for an sklearn MLPClassifier (256,128,64), returning a (d,) global importance drop-in for the tree path. Validated on a known-GT synthetic construction: recovery of a decorrelated planted target with a recall gate, agreement with the trusted TreeSHAP path on an RF, and a 2-point redundancy sensitivity smoke test. D028.

**What we found.** Verdict: MLP-SHAP-INFRA-VALID. Recovery MLP-SHAP precision@5 = 1.000 (recall 0.968, random 0.067, chance 0.119); agnostic-vs-tree Spearman = 0.892; sensitivity drop rho 0->0.99 = +0.400.

**Why it matters.** A neural negative result is only credible if the explainer is known-good. This establishes and validates the MLP-SHAP estimator used by notebooks 12 and 13, so the cross-model claim (the failure is not tree-specific) rests on a sound attribution method rather than an unchecked one.


## F017 — Identifiability under redundancy is not tree-specific: the MLP degrades like RF/XGBoost
*Logged 2026-06-09 | context: `05_phase3_generalization/12_mlp_identifiability_sweep`*

**What we did.** Extended the synthetic identifiability sweep (C3/Fig.5) from RF + XGBoost to an MLP on one shared known-GT construction (P(X) fixed, planted set S, median-split labels). Swept partner-correlation rho in {0,0.2,0.4,0.6,0.8,0.9,0.99}; recovered S by precision@K from SHAP (TreeSHAP for trees, the validated agnostic path for the MLP via shap_importance_any), with a recall gate and KS as the concept-blind baseline. D029.

**What we found.** Verdict: NEURAL-IDENTIFIABILITY-CONFIRMED. MLP-SHAP precision@5 falls from 0.933 at rho=0 to 0.667 at rho=0.99 (drop +0.267), with min recall 0.961; tree reference drops RF +0.333, XGB +0.133; KS mean 0.076 ~ chance 0.119.

**Why it matters.** Answers the reviewer question on model breadth: if the MLP degrades with redundancy like the trees, the C3 identifiability limit is model-class-independent rather than an artifact of tree explainers. This is the synthetic half of the neural generalization; notebook 13 tests it on real UNSW geometry.


## F018 — Neural UNSW drift-localization benchmark: KS still competitive, dual still adds nothing, circularity persists (MLP)
*Logged 2026-06-09 | context: `05_phase3_generalization/13_mlp_unsw_benchmark`*

**What we did.** Re-ran the corrected UNSW drift-localization benchmark (10b / D027) with an MLP added as a third model class on identical additive leave-one-family-out arms. Compared drift-localizers (KS, domain-SHAP, dual-IDS, perm-domain, random) against a model-free Wasserstein anchor and a domain-oracle-SHAP circularity reference, SHAP via shap_importance_any (TreeSHAP for RF/XGB, the validated agnostic path for the MLP), with self-stability. D030.

**What we found.** Verdict (MLP): EXPLANATION-ADDS-VALUE-NEURAL. On the Wasserstein anchor (chance 0.238): MLP KS 0.411, domain-SHAP 0.589 (KS-domainSHAP -0.178), dual-IDS 0.511 (dual-domainSHAP -0.078). MLP domain-SHAP inflates +0.089 vs its own oracle; self-stability domain-SHAP 0.542 vs perm-domain 0.391. Families ['Generic', 'Exploits', 'Fuzzers']; same-run RF/XGB reproduce 10b.

**Why it matters.** This is the real-geometry half of the neural generalization. With notebook 12 (synthetic identifiability) it shows C1 (modality circularity) and C2 (a label-free KS test is competitive; the dual signal adds nothing) hold across RF, XGBoost, and a neural model -- so the paper can state the findings are not tree-specific. Last planned experiment; next is paper polish, not more models.


## F019 — Explainer control for the MLP domain-SHAP advantage (TreeSHAP vs PermutationExplainer on the same model)
*Logged 2026-06-09 | context: `05_phase3_generalization/13b_explainer_control`*

**What we did.** Controlled the F018 confound: for the same pre-vs-post domain classifier of each model class, computed domain-SHAP via TreeSHAP (RF/XGB) and the agnostic PermutationExplainer (RF/XGB/MLP) and scored precision@K vs the same Wasserstein anchor, on the notebook-13 arms. D031.

**What we found.** Verdict: MODEL-DRIVEN. KS (model-free) 0.411. KS - domainSHAP under PermutationExplainer: rf +0.078, xgb +0.089, mlp -0.167 (negative = domain-SHAP beats KS). TreeSHAP baseline: rf 0.389, xgb 0.356 (KS competitive, as in 13).

**Why it matters.** Decides the paper wording for the neural result: whether the notebook-13 finding (domain-SHAP beats KS for the MLP) is an explainer-geometry effect or a genuine neural-model effect. Either way it is reported, not smoothed over; it sharpens the scope of C2 (KS competitive) rather than overturning the dual-adds-nothing core.


## F020 — CICIDS cross-dataset test of the neural drift-localization boundary (with explainer control)
*Logged 2026-06-09 | context: `05_phase3_generalization/14_mlp_cicids_benchmark`*

**What we did.** Replicated the UNSW neural benchmark (13 / D030) on CICIDS2017, construction held identical (additive leave-one-family-out, Wasserstein anchor, KS / domain-SHAP / dual-IDS / perm-domain / random, RF + XGBoost + MLP), with the 13b explainer control inline (tree domain-SHAP also via PermutationExplainer). SHAP via shap_importance_any. D032.

**What we found.** Replication verdict: C2-REPLICATES-NEURAL-CICIDS; control verdict: NO-MLP-ADVANTAGE-CICIDS. MLP on Wasserstein (chance 0.122): KS 0.700, domain-SHAP 0.578 (KS-dom +0.122), dual 0.511 (dual-dom -0.067). Control KS-domainSHAP(Perm): rf +0.222, xgb +0.300, mlp +0.122.

**Why it matters.** Tests whether the notebook-13 neural boundary (a neural domain classifier localizes drift better than the cheap KS test) is cross-dataset robust or UNSW-specific. Either outcome sharpens the scope of C2 in the paper. Last planned experiment; next is paper polish, not more models.


## F021 — Paired significance table (tab:sig) made reproducible from released raw tables
*Logged 2026-06-11 | context: `99_paper_figures/15_significance_tests`*

**What we did.** Recomputed the five headline paired comparisons (Delta, seeded 10^4 bootstrap 95% CI, Wilcoxon signed-rank p, d_z) directly from 10b/07 raw tables; post-drift CICIDS days derived from the cold-start collapse in 06_baseline_metrics.csv. D033.

**What we found.** Against GT_in no explanation method significantly exceeds KS (all p>=0.50) and the dual model is indistinguishable from its component; KS beats random (p=0.002, d_z=1.12); the only large significant explanation advantage is against the explanation-derived truth GT_ex (Delta=+0.228, p<0.001, d_z=1.86). All Deltas reconcile with the released summaries.

**Why it matters.** tab:sig is load-bearing for the central circularity claim but its p/CI/d_z were not previously reproducible from the package. This notebook makes the whole table auditable and canonical (seeded bootstrap), closing the one reproducibility gap a reviewer could hit.

**What surprised us.** no


## F022 — Stream-replay harness validated; CICIDS adaptation headroom quantified
*Logged 2026-06-12 | context: `07_phase5_adaptation/16_stream_harness`*

**What we did.** Built the Phase-5 stream-replay harness (src/streaming/replay.py) and pre-registered the CICIDS operational stream (D034): warm-up train on Monday+Tuesday, replay Wednesday-Friday in 29 windows of 50,000 flows. Ran the two bracketing baselines, never-retrain (floor) and always-retrain (ceiling), on the full stream.

**What we found.** Verdict HARNESS-CHECK-FAILED. Novel attack families absent from training and present in replay: ['botnet', 'ddos', 'dos goldeneye', 'dos hulk', 'dos slowhttptest', 'dos slowloris', 'heartbleed', 'infiltration', 'infiltration - portscan', 'portscan', 'web attack - brute force', 'web attack - sql injection', 'web attack - xss']. Floor (frozen) mean recall 0.000; always-retrain ceiling mean recall 0.799; adaptation headroom (gap) 0.799. Gates G1=True, G2=True, G3=False, G4=True.

**Why it matters.** Establishes the reference trajectories every Phase-5 policy is measured against and confirms there is real headroom for adaptation to capture. The floor/ceiling gap is the quantity Objective 6 (KS-triggered, label-budgeted retraining) must recover cheaply; notebook 17 adds the KS monitor/trigger on this same stream.


## F023 — Label-free KS trigger characterised on the CICIDS stream (Objective 5)
*Logged 2026-06-12 | context: `07_phase5_adaptation/17_ks_trigger`*

**What we did.** Built the Objective-5 label-free KS drift monitor (src/monitoring/ks_monitor.py) and pre-registered it (D035): mean per-feature KS vs a held-out reference, a 3-sigma reference-calibrated trigger, monitored over a quiet (in-distribution) period then the full Wednesday-Friday drift period, scored against novel-family onsets.

**What we found.** Verdict KS-TRIGGER-VALID. tau=0.0119. Detection rate over drift windows 1.000; false-alarm rate over the quiet period 0.000; precision 1.000; mean per-onset detection latency 0.00 windows over 13 onsets. Mean drift score 0.201 on drift windows vs 0.004 on non-drift. Gates G1=True, G2=True, G3=True, G4=True.

**Why it matters.** Establishes whether the cheap label-free KS signal is an adequate operational trigger (Objective 5) and quantifies its latency and false-alarm cost. This is the controller notebook 18 uses to decide when to spend a label budget on retraining, and it operationalises C2: no explanation-based localisation is needed to decide when to adapt.


## F024 — KS-triggered budgeted retraining recovers the adaptation headroom cheaply (Obj 6)
*Logged 2026-06-12 | context: `07_phase5_adaptation/18_triggered_retraining`*

**What we did.** Closed the Objective-6 loop (src/adaptation/policies.py, D036): compared never / always-sliding / cumulative / periodic / KS-triggered-budgeted retraining on the full CICIDS Wed-Fri stream, with the triggered policy using an updating reference and an accumulating label pool. Swept the per-trigger label budget.

**What we found.** Verdict ADAPTATION-LOOP-CHECK-FAILED. Floor (never) recall on drift windows 0.000; ceiling (cumulative) 0.846; always-sliding 0.799. Headline triggered policy triggered_250: recovery fraction 0.988 at cost fraction 0.0048 (6,750 labels). Largest-budget trigger fired 27 of 29 windows. Gates G1=True, G2=False, G3=True, G4=True.

**Why it matters.** This is the Objective-6 result: a cheap label-free trigger plus a small label budget recovers most of the recall an unlimited-label retrainer achieves, at a fraction of the labelling cost -- the operational payoff of the thesis. It also confirms the nb17 design fix (updating reference) is what makes triggered retraining distinct from always-retrain. Notebook 19 turns this into the compute/label/latency accounting; notebook 20 replicates on UNSW.


## F025 — Operational accounting: labels, compute and the cheap detector false-positive cost (Obj 7)
*Logged 2026-06-12 | context: `07_phase5_adaptation/19_cost_latency`*

**What we did.** Re-ran the Phase-5 policies with full confusion-matrix instrumentation (src/adaptation/cost_eval.py, D037) to add the metric nb18 left open -- the triggered detector false-positive rate and alert volume -- alongside labels and compute, against always_sliding as the full-label reference.

**What we found.** Verdict COST-ACCOUNTING-VALID. triggered_250: recall 0.913, FPR 0.0080 (7,171 alerts), 6,750 labels, 7s compute — vs always_sliding recall 0.909, FPR 0.0019, 1,400,000 labels, 36s (labels 0.48%, compute 19.23%). Gates G1(FP)=True, G2(compute)=True, G3(joint)=True, G4=True.

**Why it matters.** Completes the Objective-7 trade-off across all three operational axes. Whether the cheap triggered detector keeps an acceptable false-positive rate decides if the nb18 recall headline is operationally real or whether cheap retraining trades labels for alert burden -- either way the honest cost picture for the thesis. Notebook 20 replicates on UNSW.


## F026 — Cross-dataset replication on UNSW-NB15 + trigger-necessity test (Phase 5)
*Logged 2026-06-12 | context: `07_phase5_adaptation/20_cross_dataset_replication`*

**What we did.** Replicated the Phase-5 adaptation loop on UNSW-NB15 with a leave-one-family-out stream (quiet stretch then novel-family drift) and added the always_cheap ablation to src/adaptation/cost_eval.py (D038), to test whether the operational finding generalises and whether the KS trigger earns its place over unconditional cheap retraining.

**What we found.** Verdict CROSS-DATASET-CHECK-FAILED. triggered_250 recall 0.783 vs always_sliding 0.873; trigger false-alarm rate on quiet windows 0.200. Necessity: trigger EARNS its place: fires 2/14 vs always_cheap 14, saves 3,000 labels at recall 0.783 vs 0.823. Gates G1=False, G2=False, G3=True, G4=True.

**Why it matters.** Shows whether cheap KS-triggered budgeted retraining is a general operational result or CICIDS-specific, and — via the quiet period UNSW provides — whether the trigger does real work (selectivity saving labels) or is incidental to cheap retraining. Either way it is the honest cross-dataset picture for the thesis.


## F027 — UNSW hard-regime sweep: regime-dependence of adaptation within one dataset (Phase 5)
*Logged 2026-06-12 | context: `07_phase5_adaptation/21_unsw_hard_regime`*

**What we did.** Swept warm-up breadth on UNSW-NB15 (1/2/4 seen attack families) to vary the drift regime on one dataset with features fixed (D039), testing whether CICIDS recall collapse + recovery reappear at narrow breadth, and reporting trigger false alarms with a Wilson CI.

**What we found.** Verdict REGIME-DEPENDENCE-NOT-SHOWN. Hardest breadth 1: frozen recall 0.630, triggered_2500 0.868, always_sliding 0.958. Gates G1=True (hard regime exists), G2=False (recovery replicates), G3 selectivity flag=True.

**Why it matters.** If recall recovery reappears at narrow breadth, the Phase-5 operational result is shown to be regime-dependent rather than CICIDS-specific, on one dataset with the confound removed — direct support for the C4 regime-map and a three-regime story (CICIDS catastrophic / UNSW mild / UNSW hard). If it does not, UNSW attacks are mutually detectable and that scope limit is itself reportable.


## F028 — Corrected-G2 confirmation: regime-dependence of adaptation across seeds (Phase 5)
*Logged 2026-06-12 | context: `07_phase5_adaptation/22_corrected_gate_confirm`*

**What we did.** Corrected nb21’s mis-specified G2 (which conflated cost-parity with regime recovery) to a ceiling-vs-frozen recovery test plus a sign-flip-of-benefit test, and confirmed it across 4 seeds (D040), preserving nb21’s original NOT-SHOWN result and reporting selectivity with Wilson CIs.

**What we found.** Corrected verdict REGIME-DEPENDENCE-CONFIRMED (all-seeds). Original nb21 G2 passes 1/4 seeds (preserved; it is the nb19 cost gap, not a regime result). Three-regime benefit (ceiling-frozen) goes negative in the mild regime and positive in the hard regime — the crossover — with the cheap policy recovering most but not all of the ceiling.

**Why it matters.** Establishes regime-dependence of adaptation on one dataset with the confound removed and a gate that tests the right question, confirmed across seeds rather than fitted to one — the defensible C4 result. Honest limits remain: UNSW will not go fully catastrophic (hard frozen ~0.63, not 0.00) and trigger selectivity is imperfect (reported with CIs).

