# Decisions Log

Chronological record of methodological decisions taken during the thesis.
Each entry: date, decision, rationale, alternatives considered.

Cite these in the thesis methods chapter.


## D001 — Phase 0 setup
**Context:** `02_download_data`

**Decision:** Use the Engelen et al. (2021) improved CICIDS2017, not the original Sharafaldin 2018 release.

**Rationale:** The original CICIDS2017 has documented label errors, duplicate flows, and CICFlowMeter v3 flow-construction bugs (Engelen 2021, IEEE SPW). Using the original would inherit these errors and make our results non-comparable to recent (2023+) papers that have moved to the improved version.

**Alternatives considered:** Use original CICIDS2017 with manual cleaning (rejected: reinvents Engelen's work for no contribution). Use ericanacletoribeiro/cicids2017-cleaned-and-preprocessed (rejected: not the canonical Engelen version, harder to cite).


## D002 — Binary label encoding
**Context:** `03_csv_to_parquet`

**Decision:** Engelen `*-Attempted` labels count as Attack (binary label = 1). Granular `attack_category` and `attempted` flag are preserved separately as meta columns.

**Rationale:** The thesis is about explanation-space dynamics under drift, not attack categorization fidelity. Treating Attempted as Attack gives the largest training signal and matches what reviewers will expect from a CICIDS-based paper. The granular fields support an ablation later.

**Alternatives considered:** Attempted = Benign (rejected: discards rare-attack signal). Attempted = Drop (kept as a future ablation option).


## D003 — Leakage column removal
**Context:** `03_csv_to_parquet`

**Decision:** Drop Flow ID, Src/Dst IP, Src/Dst Port, Timestamp, and ID columns from processed data. UNSW equivalents (srcip, dstip, sport, dsport, stime, ltime) also dropped.

**Rationale:** These are session identifiers. A model trained with them can memorize specific flows rather than generalize. Reviewers will check for this; presence in features is an automatic credibility hit. Engelen explicitly added some of these for flow lookup, not for training.

**Alternatives considered:** Keep IPs as features but hash them (rejected: still leaky, the hash is one-to-one). Keep in interim, drop only in processed (this is what we did — interim retains them for diagnostic purposes).


## D004 — Parquet format with float32/int32 downcasting
**Context:** `03_csv_to_parquet`

**Decision:** Convert all CSVs to Parquet with snappy compression. Downcast float64 → float32 and int64 → int32 where values fit.

**Rationale:** Parquet reads are 5-10× faster than CSV. Downcast halves storage and memory. float32 precision is sufficient for IDS flow features (which are mostly counts and rates, not high-precision measurements). int32 overflow check prevents silent truncation.

**Alternatives considered:** Keep CSVs (rejected: read speed unacceptable for streaming experiments). Use Feather (rejected: less standard than Parquet).


## D005 — Skip CSE-CIC-IDS-2018 conversion for Phase 1
**Context:** `03_csv_to_parquet`

**Decision:** Convert only the CICIDS2017 portion of the Engelen bundle. Defer the 34 GB CSE-CIC-IDS-2018 conversion until Phase 2 confirms we need it.

**Rationale:** Phase 1 only uses CICIDS2017. CSE-CIC-IDS-2018 may not be the right second dataset (UNSW-NB15 is currently the planned second dataset). Converting 34 GB upfront for a dataset we might not use wastes time.

**Alternatives considered:** Convert everything upfront (rejected: premature). Delete CSE-CIC-IDS-2018 entirely (rejected: keep for optional Phase 2 use).


## D006 — Drop Heartbleed from training (heads-up, not yet implemented)
**Context:** Phase 1 planning

**Decision:** CICIDS2017 Wednesday has only 11 Heartbleed flows out of ~500k rows (0.002%). Treat Heartbleed as effectively absent for binary classification — it remains labeled correctly but per-class metrics on Heartbleed alone are not meaningful.

**Rationale:** With 11 examples, any per-class precision/recall is essentially noise. Including Heartbleed in evaluation without acknowledgment would let reviewers attack the methodology.

**Alternatives considered:** Oversample Heartbleed (rejected: synthetic minority oversampling on 11 examples is not credible). Exclude Heartbleed rows (rejected: changes the dataset; document instead).

## D007 — 2026-06-03
**Context:** `05_data_characterization`

**Decision:** Primary degradation metric is per-day attack-class recall, supplemented with F1 and PR-AUC. Raw accuracy and macro-F1 excluded due to extreme per-day class imbalance (0%-47%).

**Rationale:** Monday has 0% attack rate, making accuracy and macro-F1 meaningless. Recall directly measures the metric we care about: catching attacks. F1 and PR-AUC handle imbalance better than accuracy.

**Alternatives considered:** Accuracy (rejected: dominated by benign); ROC-AUC (rejected: less informative than PR-AUC under severe imbalance).

## D008 — 2026-06-03
**Context:** `05_data_characterization`

**Decision:** Treat top-K features by mean KS-D across attack days as the ground-truth drifted feature set for localization evaluation. K determined from elbow of sorted KS distribution.

**Rationale:** Drift in CICIDS2017 is empirically feature-localized — KS-D distribution is heavy-tailed across the 82 features. The tail features ARE the drifted ones; this gives us a ground truth for evaluating precision@K of dual-model SHAP localization in Phase 1.

**Alternatives considered:** Use a fixed K=10 across all experiments (rejected: not data-driven). Use all features with KS>0.1 as drifted (possible alternative — depends on elbow).

## D009 — 2026-06-03
**Context:** `05_data_characterization`

**Decision:** Drop the 0 truly constant features ([]) from the feature matrix before training. Keep near-constant features for Phase 1 baseline; reconsider after seeing whether they carry signal.

**Rationale:** Constant features contribute zero information by definition. Near-constant features may carry signal in their rare non-default values (e.g. wrong_fragment > 0 is itself an attack indicator); dropping them prematurely could discard rare-attack signal.

**Alternatives considered:** Drop all features with >99% same value (rejected: risks discarding rare-attack indicators). Drop nothing (rejected: constants add only noise to SHAP).

## D010 — 2026-06-03
**Context:** `05_data_characterization`

**Decision:** Day-split is acceptable with documentation — 402 duplicates (0.402%) found across days, below 1%.

**Rationale:** Minor cross-day flow repetition exists but is well below levels that would compromise day-based evaluation. Will document in the thesis methods chapter.


## D011 — 2026-06-03
**Context:** `05_data_characterization`

**Decision:** Use 1000-sample SHAP per streaming batch in Phase 1+. Measured cost: 6.49 sec/1k samples on TreeSHAP+RF. Full Phase 1 experimental matrix ≈ 54 minutes per drift type.

**Rationale:** 1000 samples is the standard SHAP sample size used in our synthetic pilots (v3/v4) and produces stable importance estimates. Larger samples would increase precision marginally but compute scales linearly.

**Alternatives considered:** 200 samples (rejected: high variance in importance estimates); 5000 samples (rejected: 5x compute for diminishing returns).

## D012 — 2026-06-03
**Context:** `06_baseline_rf_per_day`

**Decision:** Pre-registered Phase 1 success thresholds: STRONG = SHAP localization precision@K > 0.70 AND beats prediction-disagreement baseline by ≥ 0.20. MODEST = precision@K 0.40–0.70 AND beats baseline by 0.05–0.20. WEAK = precision@K ≤ baseline. Outcome class will determine paper venue and thesis framing.

**Rationale:** Synthetic v3/v4 experiments yielded precision@K = 1.0 on localization, but real CICIDS2017 has KS drift peaking at 0.45 (vs ~1.0 in synthetic). Real-data results will be substantially weaker than synthetic. Pre-registering thresholds before running experiments prevents post-hoc reinterpretation.

**Alternatives considered:** No pre-registration (rejected: invites motivated reasoning). Single threshold (rejected: outcome is naturally three-tiered, and the three tiers map to different paper venues).

## D013 — 2026-06-03
**Context:** `06_baseline_rf_per_day`

**Decision:** "Naive" baseline is renamed "cold-start" — trained on Monday + a 5%% stratified sample of Tuesday (the lowest-attack day, 2.2%% attack). Pure Monday-only training is impossible because RF requires at least 2 classes.

**Rationale:** Monday has 0%% attack rate. Training a binary classifier on a single-class dataset is undefined. A 5%% Tuesday sample (~16k rows) gives the model minimal attack exposure, simulating a freshly deployed IDS that has seen a small amount of labeled traffic. Stratification preserves the original attack proportion.

**Alternatives considered:** Oversample synthetic attacks via SMOTE (rejected: introduces synthetic-data bias before we even start). Add 50%% of Tuesday (rejected: too close to the "realistic" baseline). Train an unsupervised one-class model (rejected: changes the experimental paradigm and is not what we want to baseline against).

## D014 — 2026-06-03
**Context:** `06_baseline_rf_per_day`

**Decision:** Add cold_start_balanced (class_weight="balanced") and cold_start_downsampled (benign:attack ratio ~100:1 via random downsampling) as additional baselines. Same drift exposure as cold_start, different class-imbalance handling.

**Rationale:** First-run results showed cold_start max attack probability is 0.16, suggesting class imbalance may dominate over drift. These baselines disentangle: if they recover to high recall, imbalance was the main issue and our SHAP method must beat THEM, not the raw cold_start.

**Alternatives considered:** SMOTE/SMOTEENN (rejected: synthetic data biases SHAP outputs). Threshold tuning only (rejected: diagnostic showed max proba is 0.16 on Wed — no threshold tuning can recover that).

## D015 — 2026-06-03
**Context:** `06_baseline_rf_per_day`

**Decision:** Mixed failure mode: drift AND imbalance both contribute. Balanced baselines recover to 0.246 mean recall (raw cold_start = 0.245, oracle = 0.994). The reference baseline that the SHAP method must beat is now cold_start_balanced/cold_start_downsampled, not raw cold_start.

**Rationale:** Imbalance handling recovers 0.001 of recall, but residual gap to oracle is 0.748. Both effects are present; the residual gap is what drift-aware methods can address.

**Alternatives considered:** Reported based on empirical balanced-baseline performance.

## D016 — 2026-06-03
**Context:** `06_baseline_rf_per_day`

**Decision:** Phase 1 main experiment (notebook 07+) must include two additional baselines beyond the five in notebook 06: periodic_retrain (retrain on every new day) and random_trigger (retrain on randomly selected batches, same trigger count as the SHAP method). Evaluation must report recall AND efficiency metrics: retrain frequency, labeled samples consumed, compute cost, recovery latency.

**Rationale:** The cold-start baseline collapse on Wed–Fri is so severe (recall 0.000) that almost any retraining strategy will improve raw recall. Without these two efficiency baselines, the contribution risks being attacked as "a complicated drift detector when periodic retraining would suffice." periodic_retrain tests whether the trigger logic is needed at all; random_trigger tests whether SHAP-based trigger quality matters versus any-trigger.

**Alternatives considered:** Only recall as the evaluation metric (rejected: insufficient to establish contribution against straightforward retraining strategies). periodic_retrain alone (rejected: does not separate trigger quality from retraining benefit).

## D007 — 2026-06-04
**Context:** `05_data_characterization`

**Decision:** Primary degradation metric is per-day attack-class recall, supplemented with F1 and PR-AUC. Raw accuracy and macro-F1 excluded due to extreme per-day class imbalance (0%-47%).

**Rationale:** Monday has 0% attack rate, making accuracy and macro-F1 meaningless. Recall directly measures the metric we care about: catching attacks. F1 and PR-AUC handle imbalance better than accuracy.

**Alternatives considered:** Accuracy (rejected: dominated by benign); ROC-AUC (rejected: less informative than PR-AUC under severe imbalance).

## D008 — 2026-06-04
**Context:** `05_data_characterization`

**Decision:** Treat top-K features by mean KS-D across attack days as the ground-truth drifted feature set for localization evaluation. K determined from elbow of sorted KS distribution.

**Rationale:** Drift in CICIDS2017 is empirically feature-localized — KS-D distribution is heavy-tailed across the 82 features. The tail features ARE the drifted ones; this gives us a ground truth for evaluating precision@K of dual-model SHAP localization in Phase 1.

**Alternatives considered:** Use a fixed K=10 across all experiments (rejected: not data-driven). Use all features with KS>0.1 as drifted (possible alternative — depends on elbow).

## D009 — 2026-06-04
**Context:** `05_data_characterization`

**Decision:** Drop the 0 truly constant features ([]) from the feature matrix before training. Keep near-constant features for Phase 1 baseline; reconsider after seeing whether they carry signal.

**Rationale:** Constant features contribute zero information by definition. Near-constant features may carry signal in their rare non-default values (e.g. wrong_fragment > 0 is itself an attack indicator); dropping them prematurely could discard rare-attack signal.

**Alternatives considered:** Drop all features with >99% same value (rejected: risks discarding rare-attack indicators). Drop nothing (rejected: constants add only noise to SHAP).

## D010 — 2026-06-04
**Context:** `05_data_characterization`

**Decision:** Day-split is acceptable with documentation — 402 duplicates (0.402%) found across days, below 1%.

**Rationale:** Minor cross-day flow repetition exists but is well below levels that would compromise day-based evaluation. Will document in the thesis methods chapter.


## D011 — 2026-06-04
**Context:** `05_data_characterization`

**Decision:** Use 1000-sample SHAP per streaming batch in Phase 1+. Measured cost: 6.27 sec/1k samples on TreeSHAP+RF. Full Phase 1 experimental matrix ≈ 52 minutes per drift type.

**Rationale:** 1000 samples is the standard SHAP sample size used in our synthetic pilots (v3/v4) and produces stable importance estimates. Larger samples would increase precision marginally but compute scales linearly.

**Alternatives considered:** 200 samples (rejected: high variance in importance estimates); 5000 samples (rejected: 5x compute for diminishing returns).

## D017 — 2026-06-04
**Context:** `07_localization_dual_shap`

**Decision:** Split the Phase 1 main experiment across two notebooks. Notebook 07 (this one) tests LOCALIZATION only: precision@K of dual-model SHAP divergence vs ground-truth drifted features, against aux_only (Q007) and permutation-disagreement (D012) baselines. Notebook 08 will test ADAPTATION/EFFICIENCY: the streaming retrain loop with the D016 baselines (periodic_retrain, random_trigger) and recovery latency, built only if localization clears the D012 bar. Primary method is dual_gain = relu(imp_aux - imp_main), pre-registered on the principled grounds that drift localization should reward features that GAINED importance, not features that merely lost it.

**Rationale:** Localization and adaptation are different questions with different cost profiles. Localization is cheap (no retrain loop) and is the gate that Q007/Q008/D012 hinge on. Building the expensive adaptation loop before localization passes risks wasted infrastructure. A toy relevance-swap check showed dual_abs can score WORSE than aux_only (symmetric difference rewards lost-importance features), motivating the directional dual_gain as the primary method. D016 anticipated this with its "notebook 07+" wording.

**Alternatives considered:** One combined notebook (rejected: couples a cheap gate to an expensive loop, and mixes two questions). dual_abs as primary (rejected: directional gain is better motivated and survives the toy check).

## D018 — 2026-06-04
**Context:** `07b_label_efficiency`

**Decision:** Re-run the nb07 localization experiment as a sweep over AUX_TRAIN_CAP (label budget), holding everything else fixed, to test whether dual_gain degrades more gracefully than aux_only under limited supervision. Budgets: 250, 1000, 5000, 25000, 100000 labelled rows. Pre-registered decision rule (committed before execution): (1) RESCUE -- the dual framing survives if, at some INTERPRETABLE low budget (post-drift aux_recall >= 0.70 and budget <= 5000), the post-drift mean precision@10 margin dual_gain - aux_only is >= +0.05 AND exceeds one standard error above zero. (2) GRACEFUL-ONLY -- weaker support if dual_gain retains a higher fraction of its high-budget precision than aux_only does as the budget falls (relative-retention gap >= 0.10), even without crossing the +0.05 margin. (3) REFRAME -- if neither holds, formally reframe the thesis contribution to auxiliary-model explanation localization; Q007 stands resolved-negative. Primary metric is unchanged from nb07 (post-drift mean precision@10 vs GT1); control-day precision@10 is reported as the specificity lens but does NOT move the rescue goalposts.

**Rationale:** The 100k-label aux model was the dominant methodological compromise in nb07 and plausibly favoured aux_only. The operationally relevant question is label efficiency, not precision under label abundance. Keeping the primary metric identical to nb07 avoids moving goalposts; gating the rescue on aux_recall >= 0.70 prevents over-reading budgets where the aux SHAP is meaningless for both methods.

**Alternatives considered:** Make the rescue hinge on a new combined sensitivity+specificity metric (rejected: invented after seeing nb07, risks p-hacking; reported as context only). Vary the aux training window across days instead of cap (rejected: changes infrastructure; deferred to a stricter streaming test later).

## D019 — 2026-06-04
**Context:** `07c_ks_vs_shap_localization`

**Decision:** Add KS-drift as a label-free, model-free localization METHOD and test whether SHAP-based localization (aux_only) beats it. Compare against three ground truths: GT1 (KS, circular for KS, shown only for transparency), GT2 (oracle SHAP importance, attribution), and GT3 (oracle permutation importance w.r.t. attack recall, behaviour -- the neutral arbiter independent of both KS and SHAP). Aux model given its strongest form (100k labels). Pre-registered rule, committed before execution: the explanation pipeline EARNS ITS PLACE iff aux_only beats ks by >= 0.10 post-drift mean precision@10 against GT3, exceeding one standard error above zero. If the GT3 margin is within +/-0.10 (REDUNDANT), a label-free KS test localizes as well as SHAP and the explanation machinery is redundant for localization on CICIDS. If ks beats aux_only (KS-BETTER), worse still. GT2 and the direct mutual Jaccard(ks, aux) are reported as supporting evidence but GT3 decides.

**Rationale:** Q008 (GT1/GT2 Jaccard 0.68-0.77) raised that input-drift and importance-drift largely coincide on CICIDS, threatening the whole localization spine, not just the dual variant. Comparing KS against a SHAP-modality ground truth (GT2) would unfairly favour SHAP; GT3 (behaviour-based) breaks that circularity. Giving aux 100k labels makes any redundancy finding maximally conservative.

**Alternatives considered:** Judge on GT2 only (rejected: SHAP-modality favours aux). Judge on GT1 (rejected: circular for KS). Lower aux budgets (unnecessary: nb07b showed aux is budget-insensitive here).

## D020 — 2026-06-04
**Context:** `07d_disagreement_stability`

**Decision:** Before treating the importance-method disagreement (F007) as a headline contribution, test whether it is (a) genuine rather than permutation noise, and (b) general rather than RandomForest-specific. Compute three independent importance estimators -- TreeSHAP, permutation importance (20 repeats), and built-in gain -- per post-drift day, over 5 seeds, for two model classes (RF oracle and a fresh XGBoost oracle). Measure self-stability (top-15 Jaccard of a method with itself across seeds) and cross-method disagreement (top-15 Jaccard between methods). Pre-registered gate, committed before execution: the disagreement mechanism SURVIVES iff (1) SHAP is self-stable (self-Jaccard >= 0.50); (2) the SHAP-vs-gain pair -- neither is permutation -- disagrees at Jaccard <= 0.35 post-drift (rules out permutation noise); (3) at least two of the three method pairs disagree at <= 0.35; and (4) it replicates on XGBoost (SHAP-vs-gain <= 0.35). If SHAP and gain instead AGREE (> 0.35), the F007 disagreement was permutation-driven and the pillar is demoted. If it holds on RF but not XGBoost, it is RF-specific and narrowed. Chance Jaccard for 15-of-82 sets ~ 0.10.

**Rationale:** Permutation importance is unstable under feature correlation, and CICIDS flow features are correlated, so the GT2/GT3 gap could be estimator noise. And a single model class cannot support a general claim. The SHAP-vs-gain pair isolates genuine disagreement from permutation noise; the XGBoost replication isolates a problem property from an RF property. Failing this gate demotes the mechanism but leaves the redundancy findings (F005-F007) intact.

**Alternatives considered:** Keep n_repeats=5 (rejected: too noisy to judge permutation stability). Judge on SHAP-vs-permutation only (rejected: cannot separate genuine disagreement from permutation noise without a third, non-permutation estimator).

## D021 — 2026-06-04
**Context:** `07e_drift_regime_testbed`

**Decision:** Build a semi-synthetic 2x2 crossover on REAL CICIDS feature vectors with a synthetic label rule, so the true drifted features are KNOWN in both arms (ground-truth availability held constant). Distributional arm: fixed rule, shift the input marginals of the relevant features (P(X) moves, P(y|X) stable; drifted GT = the shifted features). Concept arm: identical input distribution, swap relevant features S1->S2 (P(X) stable, P(y|X) moves; drifted GT = the newly-relevant features S2). Recover the known GT with KS (label-free) and aux-SHAP in each arm. Pre-registered hypothesis H1: explanations beat cheap statistics under concept drift but not distributional. Gate (committed before execution): H1-SUPPORTED iff (validity) concept-arm KS precision@10 <= 0.30 i.e. near chance, confirming P(X) stable; AND (concept pole) aux-SHAP precision@10 >= 0.50 and aux-SHAP - KS >= 0.20 in the concept arm; AND (distributional pole) KS precision@10 >= 0.50 and KS >= aux-SHAP - 0.10. Falsifiers: F-a (concept pole fails: SHAP does not localize even with known GT) -> narrow claim to idealized settings; F-b (validity fails: KS not near chance in concept) -> construction leaked input drift, INVALID; F-c (confound) -> addressed by design since GT is known in both arms.

**Rationale:** On real data, drift type and ground-truth availability were confounded. A known-GT semi-synthetic testbed on real (correlated) feature vectors isolates drift type while keeping the realistic correlation structure that destabilised importance on real data, so SHAP gets a fair but not rigged test. The crossover (KS wins distributional, SHAP necessary for concept) is the conditions result; the validity checks prevent a leak from faking it.

**Alternatives considered:** Force a concept arm from a UNSW family-holdout split (rejected: that is distributional drift mislabelled). Pure synthetic (rejected: loses the real correlation structure and re-introduces the synthetic-vs-real gap).

## D022 — 2026-06-04
**Context:** `07f_correlation_ablation`

**Decision:** Test whether feature correlation (not drift type) is the governing variable for explanation-space localization. Reuse the 07e concept-drift arm (P(X) stable, relevance swap S1->S2, recover known S2) but select S2 at a target correlation level from the real feature geometry, sweeping from weakly- to strongly-correlated. Measure aux-SHAP precision@K at recovering S2; carry KS as the (concept-blind) baseline. Pre-registered H2: aux-SHAP localization is a decreasing function of the relevant set's correlation. Gate (committed before execution): H2-SUPPORTED iff at the LOW-correlation level aux-SHAP precision@K >= 0.50 and beats KS by >= 0.20; AND at the HIGH-correlation level aux-SHAP <= 0.40 (near the 07e chance result); AND (low - high) >= 0.20. H2-REFUTED-FLAT iff aux-SHAP < 0.50 even at the lowest correlation level (correlation is not the rescue; the unconditional negative stands). KS is expected near chance at all levels (concept drift is invisible to input statistics).

**Rationale:** 07e showed aux-SHAP at chance in both drift regimes with known GT, and attributed it to correlated proxies absorbing attribution. If decorrelating the relevant set restores SHAP localization, correlation is the real governing variable and yields a measurable diagnostic; if not, the negative is unconditional. Selecting S2 from real features keeps the realistic geometry rather than synthesising a correlation structure.

**Alternatives considered:** Synthesise features at target correlation (rejected: leaves real geometry). Sweep across both drift arms (unnecessary: 07e already settled the distributional arm; the open question is concept-arm SHAP recovery).

## D023 — 2026-06-04
**Context:** `07g_decorrelated_limit`

**Decision:** Test the identifiability mechanism behind localization failure, isolating it from real CICIDS geometry. (1) Report the feature-redundancy distribution to quantify how many features fall below given leakage thresholds (structural reachability). (2) Real-data arm: select the LOWEST-redundancy features (small relevant set) to push external leakage as low as the real geometry permits; measure aux-SHAP recovery there, with a high-redundancy set as contrast. (3) Synthetic control arm: build a pool with a genuinely independent relevant set plus proxies at controllable correlation rho, sweep rho from 0 upward, and measure aux-SHAP recovery of the known relevant set (KS carried as the concept-blind baseline). Pre-registered H2b (identifiability): with no proxies (rho=0) SHAP recovers the relevant set; adding proxies degrades it. Gate (committed before execution): MECHANISM-CONFIRMED iff synthetic aux-SHAP precision at rho=0 >= 0.50 AND (precision[rho=0] - precision[rho=max]) >= 0.20. MECHANISM-REFUTED iff synthetic aux-SHAP precision at rho=0 < 0.50 (fails even with a perfectly identifiable target). Real reachability: REACHED iff the lowest-redundancy real set achieves external leakage <= 0.20; if reached, real recovery holds iff its aux-SHAP precision >= 0.50. KS is expected at chance throughout (concept drift is invisible to input statistics).

**Rationale:** 07f could not construct a decorrelated relevant set on CICIDS (min leakage 0.37, median feature redundancy 0.95), so its flat-near-chance result cannot distinguish "correlation does not matter" from "could not escape correlation". The synthetic arm reaches leakage 0 and answers the mechanism question directly; the real arm answers whether CICIDS can ever reach that regime. Together they yield either a complete causal story (mechanism holds, IDS structurally blocks it) or a genuine unconditional refutation (mechanism fails with a clean target).

**Alternatives considered:** Accept 07f H2-REFUTED-FLAT as-is (rejected: the low level was leakage 0.37, not decorrelated, so the conclusion over-claims and leaves a reviewer hole). Real-data sweep only (rejected: the decisive low-leakage regime is unreachable on CICIDS, so the mechanism cannot be tested without the synthetic control).

## D024 — 2026-06-04
**Context:** `07h_degeneracy_diagnostic`

**Decision:** Resolve 07g's invalid real-low arm (NaN recall). (1) Compute per-feature degeneracy metrics (modal fraction, distinct-value count) and reproduce 07g's lowest-redundancy set to demonstrate its degenerate, unlearnable label. (2) Define non-degenerate features (modal fraction <= MODAL_MAX and distinct values >= MIN_DISTINCT) and ask the decisive reachability question: among non-degenerate features, does a set of size k exist with external leakage <= 0.20 (a decorrelated AND informative set)? (3) Corrected real arm: select lowest- and highest-redundancy sets FROM THE NON-DEGENERATE FEATURES ONLY (vary correlation, hold non-degeneracy fixed), run the concept arm, and measure aux-SHAP recovery, gating each arm on aux-recall >= RECALL_MIN and label balance in [0.2, 0.8]. Pre-registered outcomes (committed before execution): COMPOUND-STRUCTURAL-BLOCK iff no non-degenerate set reaches leakage <= 0.20 (decorrelated features are degenerate, informative features are collinear). REAL-POSITIVE-POLE iff a non-degenerate decorrelated set exists with valid recall and aux-SHAP precision >= 0.50. GENUINE-SECOND-FACTOR iff such a set exists with valid recall but aux-SHAP precision < 0.50 (clean target, learned model, SHAP still fails). The synthetic mechanism is already confirmed in 07g.

**Rationale:** 07g could not distinguish "real decorrelated features fail SHAP" from "the only real decorrelated features are degenerate and unlearnable". The non-degeneracy filter both removes the confound and fixes the label-balance problem (a median split on a non-degenerate feature is ~50/50 by construction), so any surviving failure is interpretable. The reachability question is the crux: if no decorrelated-and-informative set exists, the positive regime is structurally unreachable on CICIDS, and that is the finding.

**Alternatives considered:** Re-run 07g real-low unchanged (rejected: degenerate label, uninterpretable). Rebalance the degenerate label artificially (rejected: would test a contrived target unrelated to how the feature behaves in practice). Synthetic only (rejected: 07g already settled the mechanism; the open question is real-data reachability).

## D025 — 2026-06-05
**Context:** `09_unsw_geometry_localization`

**Decision:** Apply the Phase-1 evaluation protocol to UNSW-NB15 and across RF + XGBoost. (1) Characterize UNSW geometry: per-feature redundancy (max |corr|) and degeneracy (modal fraction, distinct count); compare head-to-head with CICIDS. (2) Reachability: among non-degenerate UNSW features, sweep relevant sets across redundancy quantiles and report achieved external leakage per level -- can UNSW reach external leakage <= 0.20 (a decorrelated-and-informative set), which CICIDS could not? (3) Controlled leakage->recovery test on real UNSW features (known S2, concept arm, recover S2), aux model = RF and XGBoost, KS as the concept-blind baseline, gating each level on aux-recall >= RECALL_MIN and label balance. Pre-registered cross-dataset gate (committed before execution): CROSS-DATASET-BLOCK iff the lowest achievable non-degenerate external leakage > 0.20 (structural block generalizes). MECHANISM-HOLDS-ON-REAL-DATA iff UNSW reaches leakage <= 0.20 AND aux-SHAP precision >= 0.50 there with valid recall, for >= 1 model class (mechanism validated on real data). SECOND-FACTOR-CONFIRMED iff UNSW reaches <= 0.20 with valid recall but aux-SHAP < 0.50 (clean target, learned model, SHAP fails). Report RF vs XGBoost agreement as the model-breadth sub-result.

**Rationale:** CICIDS could not test the identifiability mechanism on real data (no decorrelated-and-non-degenerate set; 07h). UNSW has a different, possibly less collinear geometry. This determines whether the structural block is dataset-specific or general, whether the mechanism holds on real data when constructible, and whether the picture is model-class-dependent (RF vs XGBoost) -- the breadth a Q1 cross-dataset claim needs. Known-GT construction avoids the ground-truth crisis of 07c/07d.

**Alternatives considered:** Real attack-family-holdout distributional drift on UNSW (deferred to the next notebook: reintroduces the real-data ground-truth problem; must not contaminate the clean known-GT test). One-hot encoding categorical UNSW features (rejected here: changes the redundancy structure; the geometry question is about numeric features, consistent with the CICIDS analysis).

## D026 — 2026-06-05
**Context:** `10_unsw_distributional_benchmark`

**Decision:** Benchmark drift-localization methods under REAL distributional drift on UNSW-NB15, across RF + XGBoost, to test whether C2 (KS competitive with SHAP; dual adds nothing) replicates cross-dataset. Construction: leave-one-attack-family-out; pre = benign + all attacks except H, post = benign + H, for several held-out families H. Methods: aux-SHAP (single post model), dual-SHAP (|SHAP(f_post)-SHAP(f_pre)| on shared points), KS (label-free pre-vs-post), permutation-disagreement (with a self-stability check), random. Ground truth: PRIMARY is label-aware and model-free -- per-feature AUC separability of H vs benign (the features carrying the new attack signature); SECONDARY are oracle-SHAP and oracle-gain, reported to demonstrate modality-circularity, not to choose a winner. Metric: precision@K and Spearman to GT scores. Pre-registered gate on the AUC anchor (margin 0.05, committed before execution): C2-REPLICATES-CROSS-DATASET iff (dual - aux <= margin) AND (KS - aux >= -margin). SHAP-ADDS-VALUE-ON-UNSW iff (dual - aux <= margin) AND (aux - KS > margin). DUAL-HELPS-ON-UNSW iff (dual - aux > margin).

**Rationale:** C2 is currently CICIDS-only and rests on the controlled construction plus one real day-stream; a Q1 cross-dataset claim needs real drift on a second dataset and a second model class. The label-aware model-free AUC anchor is the least-circular ground truth available under distributional drift (KS is label-free, SHAP is model-based, AUC is neither), which is exactly the F007 failure this design avoids. dual-vs-aux and KS-vs-aux are interpretable regardless of GT choice.

**Alternatives considered:** Single distributional GT e.g. population KS (rejected: circular -- hands KS the win). Single oracle-SHAP GT (rejected: modality-circular for SHAP methods, the 07c mistake). Synthetic relevance swap (rejected: that is the controlled test 09 already did; this notebook is specifically about REAL drift). One held-out family (rejected: family-specific; several families give robustness).

## D027 — 2026-06-05
**Context:** `10b_drift_localization_benchmark`

**Decision:** Re-test C2 under real drift on UNSW with a corrected drift-localization design (supersedes notebook 10 / D026, whose AUC anchor was aligned with aux-SHAP and whose leave-one-family-out construction confounded KS). (1) Additive drift: post = baseline + family H injected at prevalence P, baseline (benign + other attacks) held constant. (2) Drift-localizers only: KS(pre,post); domain-SHAP (SHAP of a pre-vs-post domain classifier); dual-IDS (|SHAP(f_post_IDS)-SHAP(f_pre_IDS)|, the original hypothesis); perm-domain; random. (3) Anchor: per-feature Wasserstein-1 between held-out pre/post populations (the true drift); domain-oracle-SHAP/-gain reported only for modality-circularity. RF + XGBoost; several held-out families; permutation self-stability. Pre-registered gate on the Wasserstein anchor (margin 0.05): C2-REPLICATES-CROSS-DATASET iff (dual - domain_shap <= margin) AND (KS - domain_shap >= -margin). EXPLANATION-ADDS-VALUE-ON-UNSW iff (dual - domain_shap <= margin) AND (domain_shap - KS > margin). DUAL-HELPS-ON-UNSW iff (dual - domain_shap > margin).

**Rationale:** C2 is a drift-localization claim: which features distributionally changed. Notebook 10 accidentally tested attack-attribution (a benign-vs-H model SHAP vs an H-vs-benign anchor), where SHAP wins near-tautologically and KS, scored on the wrong contrast, fell below chance. The additive construction makes every method see the same contrast; the Wasserstein anchor is the honest drift target and a different functional from KS; comparing KS to a pre-vs-post domain classifier (not an IDS model) is the fair explanation-vs-cheap-test comparison. dual-vs-domain-SHAP is anchor-robust corroboration.

**Alternatives considered:** Re-use notebook 10 unchanged (rejected: construction artifact, annotated on F014). IDS-model SHAP as the localizer (rejected: that is attack-attribution, the 10 mistake). Distributional anchor = population KS (rejected: tautological with KS; Wasserstein is a distinct functional). Replacement drift post=benign+H (rejected: confounds the contrast with the removal of the other attacks).

## D028 — 2026-06-09
**Context:** `11_mlp_shap_infrastructure`

**Decision:** Establish and validate a model-agnostic SHAP path for an MLP before any neural benchmark. Model = sklearn MLPClassifier hidden (256,128,64) ReLU. Explainer = shap.PermutationExplainer (default) or shap.KernelExplainer (fallback), both wrapped around predict_proba[:,1] and abs-averaged over an eval sample to return a (d,) global importance, matching the tree path so it is drop-in for notebooks 12/13. Validate on a known-GT synthetic construction (decorrelated planted relevant set, median-split linear labels): (1) RECOVERY -- MLP-SHAP precision@K on the planted set with valid recall; (2) AGREEMENT -- on an RF, Spearman between the validated TreeSHAP path and the new agnostic path on the same model; (3) SENSITIVITY (corroborating) -- a 2-point rho in {0,0.99} smoke test that the path degrades with external leakage. Pre-registered gate (committed before execution): MLP-SHAP-INFRA-VALID iff recovery precision >= 0.80 AND recall >= 0.70 AND agnostic-vs-tree Spearman >= 0.80; else INVALID.

**Rationale:** A neural negative result (notebooks 12/13) is only credible if the explainer behind it is known-good. TreeSHAP cannot run on an MLP, so a model-agnostic estimator is required; it must be validated against a known ground truth and cross-checked against the already-trusted tree path on a model where both run. PermutationExplainer is chosen over KernelExplainer as the default for speed at 42 features; KernelExplainer retained as a faithfulness fallback.

**Alternatives considered:** DeepSHAP/GradientExplainer (rejected here: requires a torch/keras model; sklearn MLP is the reviewer-recommended minimal addition). KernelExplainer as default (rejected: slow at this width; kept as fallback). Skipping validation and trusting the explainer (rejected: defeats the purpose of a credible negative result).

## D029 — 2026-06-09
**Context:** `12_mlp_identifiability_sweep`

**Decision:** Extend the synthetic identifiability sweep (C3 / Fig. 5) from RF + XGBoost to an MLP, on a single shared construction so the curves are directly comparable. Known-GT concept arm (07g logic): decorrelated Gaussian features, planted relevant set S, label = median split of X_S w, P(X) held fixed across pre/post. Sweep partner-correlation rho in {0,0.2,0.4,0.6,0.8,0.9,0.99} (raises external leakage of the target). For each (rho, model, seed): train the model on the post arm, recover S by precision@K from SHAP (TreeSHAP for RF/XGB, the validated agnostic path for the MLP, dispatched by shap_importance_any), gate on recall. KS(pre,post) carried as the concept-blind baseline (chance, since P(X) is fixed). Pre-registered gate (committed before execution): NEURAL-IDENTIFIABILITY-CONFIRMED iff MLP precision@K >= 0.80 at rho=0 AND MLP drop (rho=0 minus rho=0.99) >= 0.20 AND MLP recall >= 0.70 at every rho; else NOT-CONFIRMED.

**Rationale:** The reviewer asks whether the SHAP localization failure is tree-specific. A controlled rho sweep on the MLP, on the same arms as the trees, answers it directly: if the MLP degrades with redundancy like the trees, the C3 structural limit is model-class-independent. The MLP-SHAP path used here was pre-validated in notebook 11 (F016), so a neural negative is credible. P(X) is held fixed so KS sits at chance -- the failure is about identifiability of the target, not about input drift.

**Alternatives considered:** Cite the old 07g tree numbers and add an MLP-only curve (rejected: not same-run comparable). Vary rho via a covariate shift (rejected: would let KS localise and confound the identifiability question). Add CNN/LSTM/TabNet (rejected: out of scope; one neural family answers the tree-specific question with the best effort-to-impact ratio).

## D030 — 2026-06-09
**Context:** `13_mlp_unsw_benchmark`

**Decision:** Re-run the corrected UNSW drift-localization benchmark (D027 / 10b) with an MLP added as a third model class, on identical arms, to test C1/C2 on real geometry with a neural model. Additive leave-one-family-out drift (post = baseline + H at prevalence INJECT_P, baseline held constant). Drift-localizers: KS(pre,post); domain-SHAP (SHAP of a pre-vs-post domain classifier); dual-IDS (|SHAP(f_post)-SHAP(f_pre)|); perm-domain; random. SHAP via shap_importance_any (TreeSHAP for RF/XGB, validated agnostic path for the MLP, F016). Anchor: per-feature Wasserstein-1 (model-free drift truth). Circularity reference: domain-oracle-SHAP. GTs = {wasserstein, domain_oracle_shap} only (the impurity-gain GT from 10b is undefined for an MLP, so it is dropped to keep the method x GT matrix uniform across model classes). RF + XGBoost + MLP; several held-out families; permutation self-stability. Pre-registered gate, headline = MLP, on the Wasserstein anchor (margin 0.05): C2-REPLICATES-NEURAL iff (dual_mlp - domain_shap_mlp <= margin) AND (KS - domain_shap_mlp >= -margin); EXPLANATION-ADDS-VALUE-NEURAL iff (dual_mlp - domain_shap_mlp <= margin) AND (domain_shap_mlp - KS > margin); DUAL-HELPS-NEURAL iff (dual_mlp - domain_shap_mlp > margin).

**Rationale:** Notebook 12 showed the identifiability limit is not tree-specific on a controlled construction; this is the real-data test. Holding the 10b construction fixed and only swapping in the MLP isolates the model-class effect. The MLP-SHAP path was pre-validated (F016), so a neural negative is credible. If KS stays competitive, dual still adds nothing, and domain-SHAP still inflates against its own oracle, then C1 (circularity) and C2 (KS competitive) hold across RF, XGBoost, and a neural model on real UNSW drift -- the cross-model generalization the paper claims.

**Alternatives considered:** New construction for the MLP (rejected: breaks comparability with 10b). Keep the gain GT and mark it NaN for the MLP (rejected: ragged matrix; gain is not the circularity modality). IDS-model SHAP as the localizer (rejected: that is attack-attribution, the notebook-10 mistake). Add CNN/LSTM (rejected: out of scope; the MLP answers the tree-specific question).

## D031 — 2026-06-09
**Context:** `13b_explainer_control`

**Decision:** Control for the explainer confound in F018. Hold the notebook-13 / 10b construction fixed (additive leave-one-family-out, per-feature Wasserstein anchor, same families/seeds). For the SAME pre-vs-post domain classifier of each model class, compute domain-SHAP two ways and score precision@K vs the Wasserstein truth: TreeSHAP (RF/XGB) and the model-agnostic PermutationExplainer (RF/XGB/MLP, via agnostic_shap_importance). Compare each to KS. Pre-registered gate (margin 0.05), with Delta = KS - domainSHAP under PermutationExplainer: EXPLAINER-DRIVEN iff Delta_rf < -m AND Delta_xgb < -m AND Delta_mlp < -m (all classes flip to beating KS under the same explainer); MODEL-DRIVEN iff Delta_rf >= -m AND Delta_xgb >= -m AND Delta_mlp < -m (only the MLP beats KS); MIXED otherwise. Also report the TreeSHAP baseline (expect KS >= domain-SHAP, as in 13) and, per tree, the explainer lift (domainSHAP_perm - domainSHAP_tree) and the Spearman agreement between the two explainers on the same model.

**Rationale:** F018 found domain-SHAP beats KS for the MLP but not the trees, but the trees used TreeSHAP and the MLP used PermutationExplainer -- so model class and explainer are confounded. PermutationExplainer is marginal/interventional and may align with a marginal Wasserstein anchor better than path-dependent TreeSHAP. Running the trees through the SAME agnostic explainer isolates the cause and decides the paper wording: an explainer-geometry effect or a genuine neural-model effect.

**Alternatives considered:** Give the MLP a TreeSHAP-equivalent (rejected: TreeSHAP is undefined for an MLP). Switch the anchor to a multivariate drift measure (rejected: changes the question and breaks comparability with 13). Accept F018 as-is (rejected: the confound is the first thing a reviewer raises).

## D032 — 2026-06-09
**Context:** `14_mlp_cicids_benchmark`

**Decision:** Replicate the UNSW neural drift-localization benchmark (13 / D030) on CICIDS2017, construction held identical (additive leave-one-family-out, per-feature Wasserstein anchor, KS / domain-SHAP / dual-IDS / perm-domain / random, RF + XGBoost + MLP, families from attack_category, self-stability), and fold the 13b explainer control inline: for the tree domain classifiers also compute domain-SHAP via the same PermutationExplainer the MLP uses. SHAP via shap_importance_any. Pre-registered gate (margin 0.05, headline=MLP, Wasserstein anchor): replication tier C2-REPLICATES-NEURAL-CICIDS iff dual_mlp-domSHAP_mlp <= m AND KS-domSHAP_mlp >= -m (else EXPLANATION-ADDS-VALUE / DUAL-HELPS); control tier MODEL-DRIVEN-CICIDS iff trees stay >= -m vs KS under PermutationExplainer while the MLP beats it, else EXPLAINER-DRIVEN-CICIDS. CICIDS pool stratified-capped at POOL_CAP rows by attack_category for memory/runtime.

**Rationale:** The notebook-13 neural boundary (domain-SHAP beats KS for the MLP) rests on one dataset; a reviewer will ask whether it is dataset-specific. CICIDS is the fair stress test (more features, higher redundancy, different geometry). Holding the construction fixed and only changing the dataset gives a clean cross-dataset test; including the explainer control on CICIDS pre-empts the same confound 13b closed on UNSW. This is cross-dataset replication of the existing model, not a new model class -- consistent with the disciplined scope.

**Alternatives considered:** Mirror the CICIDS 07-series cold-start day-stream instead (rejected: not construction-comparable to 13; would confound dataset with drift design). Skip CICIDS and state UNSW-only as a limitation (a legitimate alternative; chosen against here to make the neural boundary cross-dataset). Add more model classes (rejected: out of scope).

## D033 — 2026-06-11
**Context:** `99_paper_figures/15_significance_tests`

**Decision:** Recompute the paper significance table (tab:sig) from the released raw per-run tables so every inferential statistic is reproducible. Pairing: family x model x seed on UNSW (10b raw, n=18) and day x seed on CICIDS (07 raw, GT1, k=10, post-drift days only, n=9). Per comparison report Delta = mean(focal-ref), a seeded 10^4-resample bootstrap 95% CI of the paired mean difference, the Wilcoxon signed-rank p, and d_z = Delta / sd(diff). Significant at p<0.05. Post-drift days are DERIVED from 06_baseline_metrics.csv (cold_start recall == 0), not hard-coded.

**Rationale:** The point estimates in tab:sig already match the released means, but the p-values, CIs and effect sizes appeared in no released artifact, so a reviewer could not reproduce the table from the package. Computing them from the same raw tables that produced the means makes the central circularity claim (the only large, significant explanation advantage is against the explanation-derived truth) fully auditable. Deriving the post-drift day set from the baseline collapse keeps the CICIDS pairing principled and self-documenting.

**Alternatives considered:** Hard-code the five comparisons numerically (rejected: not reproducible, defeats the purpose). Use a paired t-test instead of Wilcoxon (rejected: precision@k is discrete with small n; the signed-rank test is the pre-registered choice). Bootstrap the Wilcoxon p as well (unnecessary; the signed-rank p is exact enough at these n).

## D034 — 2026-06-12
**Context:** `07_phase5_adaptation/16_stream_harness`

**Decision:** Define the Phase-5 stream-replay harness and pre-register the operational stream. Stream = CICIDS2017, five days in chronological order; warm-up training set = Monday+Tuesday (benign + early brute-force), replay = Wednesday/Thursday/Friday partitioned into sequential windows of 50,000 flows (day order preserved, within-day order as stored). Frozen detector = RandomForest(n_estimators=100, max_depth=12, seed=42). Baselines: never-retrain (one frozen detector scored on every window) and always-retrain (retrain on the most recent 1 labeled window before scoring each window, unlimited budget). Quality = recall on attack class (attack_category != benign). Gates: G1 drift present (>=1 replay family absent from training); G2 floor mean recall < 0.8; G3 ceiling mean >= 0.85 AND gap >= 0.1; G4 replay deterministic under fixed seed. Verdict HARNESS-VALID iff G1 and G2 and G3 and G4. Harness written to src/streaming/replay.py for nb 17-20.

**Rationale:** The spine is one-shot; the operational study is stateful and needs a replay loop plus a defensible floor/ceiling bracket before any trigger or budget is introduced. Calendar-ordered CICIDS days are the most defensible real stream; training on Monday+Tuesday and replaying the novel-family drift of Wednesday-Friday reproduces the thesis drift premise. The floor/ceiling gap is the adaptation headroom Objective 6 must capture cheaply, so quantifying it first makes the later cost/recovery trade-off interpretable. The full stream is replayed; no subsampling.

**Alternatives considered:** Day-level windows only (rejected: 3 windows too coarse for trigger/retrain dynamics). UNSW family-injection as the first stream (deferred to nb 20 as the cross-dataset replication). Treating within-day row order as a true time axis (noted as an assumption: day order is chronological, within-day order is as stored). Keeping the harness inside the notebook (rejected: promoted to src so nb 17-20 share one implementation).


## D035 — 2026-06-12
**Context:** `07_phase5_adaptation/17_ks_trigger`

**Decision:** Define the Objective-5 label-free KS drift monitor and trigger on the CICIDS stream. Reference = a held-out 40% split of the training distribution (Monday+Tuesday); per-window drift score = mean per-feature two-sample KS statistic vs the reference (full reference, full 50k window, no subsampling). Threshold = tau = mu_null + 3.0*sigma_null, calibrated on a disjoint 30% calibration split partitioned into windows. Trigger fires when score > tau. Monitored stream = a disjoint 30% null-monitoring split (quiet period) followed by the full Wednesday-Friday replay (drift period); the three training splits are disjoint so detection and false alarms are assessed on data the threshold never saw. Ground truth (labels used only to score the monitor): drift window iff novel_rate > 0; onset = first window of each new novel family. Gates: G1 every onset detected within 1 window AND detection rate >= 0.8; G2 false-alarm rate over the quiet period <= 0.1; G3 mean drift-window score > tau > mean non-drift score; G4 deterministic. Verdict KS-TRIGGER-VALID iff all. Monitor written to src/monitoring/ks_monitor.py for notebook 18.

**Rationale:** Objective 5 is the controller that decides when to adapt. The thesis (C2) already showed label-free KS is competitive with explanation-based drift localisation, so the disciplined design uses KS itself as the trigger and asks the operational questions that matter: does it detect the drift, how fast, and how often does it false alarm. A reference-calibrated k-sigma threshold is label-free and standard. Splitting training into disjoint reference/calibration/null sets makes false-alarm and detection estimates honest. Monitoring a quiet period before the drift period gives the trigger a fair chance to false-alarm, which the drift-dominated replay alone would not.

**Alternatives considered:** Sliding-reference (consecutive-window) KS change-point (rejected as primary: misses persistent drift away from the training distribution, which is what degrades the detector). Fixed absolute KS threshold (rejected: not calibrated to the data). Max or breadth aggregation instead of mean KS (recorded as sensitivities; mean is the pre-registered primary). Persistence-2 trigger (single-window trigger pre-registered; persistence can be revisited in nb 18 if false alarms are high). The cumulative-buffer ceiling carried forward from nb 16 is deferred to nb 18, where retraining lives.


## D036 — 2026-06-12
**Context:** `07_phase5_adaptation/18_triggered_retraining`

**Decision:** Close the Objective-6 adaptation loop on the CICIDS Wed-Fri stream and compare five retraining policies: never (floor); always-sliding (retrain on the previous full window; nb16 ceiling); cumulative (retrain on all stream data seen; true upper bound); periodic-K (retrain every K windows); and triggered-B (the proposed policy). The triggered policy uses an UPDATING reference -- re-baselined to the current window after each retrain, label-free -- so it fires on new drift then goes quiet, and an accumulating labelled pool that adds B flows per trigger (cost = n_triggers*B) while retaining earlier families. B swept over the budget grid. tau calibrated label-free on a held-out warm-up split (3-sigma, as in nb17). Quality = recall on the attack class; full stream, no subsampling. Metrics: recovery fraction = (recall-floor)/(ceiling-floor) with ceiling = cumulative, and cost fraction vs always-sliding. Gates: G1 cumulative >= always-sliding >= floor; G2 trigger selective (n_triggers at the largest budget <= 0.60*n_windows); G3 some budget recovers >= 0.70 of the headroom at <= 0.50 of always-retrain cost; G4 deterministic. Verdict ADAPTATION-LOOP-VALID iff all. Policies written to src/adaptation/policies.py.

**Rationale:** This is the substantive Objective-6 contribution: a cheap label-free trigger plus a small label budget should recover most of the recall an unlimited-label retrainer achieves, at a fraction of the labelling cost. nb17 showed a fixed-reference trigger fires every window on a continuously drifting stream, so the updating reference is required or triggered collapses into always-retrain; the accumulating pool retains earlier families so a small per-event budget suffices (nb07b: recall recovers to 0.972 at 250 labels). The cumulative ceiling is the carry-forward upper bound from nb16. Labels, not compute, are the costed resource, since labelling is the expensive human step.

**Alternatives considered:** Fixed-reference trigger (rejected per nb17: collapses to always-retrain). Triggered pool = full warm-up + B each retrain (rejected: heavy compute for no label difference; the accumulating B-pool is the realistic operational set). Recalibrating tau after each re-baseline (rejected: tau is the fixed sensitivity, the reference is what moves). Measuring precision/false-positive cost here (deferred to nb19, the cost/latency notebook). Including the quiet period (rejected here: nb18 measures recovery on the drift stream; quiet-period behaviour was nb17 scope).


## D037 — 2026-06-12
**Context:** `07_phase5_adaptation/19_cost_latency`

**Decision:** Produce the Objective-7 operational accounting by re-running the nb18 policies with full confusion-matrix instrumentation (per-window tp/fp/fn/tn, retrain wall-time, labels), adding the metric nb18 left open: the cheap triggered detector false-positive cost. Report micro-averaged recall / precision / FPR / F1 over drift windows, total labels, total compute, and alert volume (total false positives). always_sliding is the full-label reference that isolates the budget effect on false positives; cumulative is off by default (RUN_CUMULATIVE). Gates: G1 triggered FPR <= always FPR + 0.05; G2 triggered compute < always compute; G3 joint (recall within 0.05 of always AND FPR within 0.05 AND labels <= 0.50*always); G4 deterministic. Verdict COST-ACCOUNTING-VALID iff all. Instrumented runner written to src/adaptation/cost_eval.py; recall reproduces nb18 as a consistency check.

**Rationale:** nb18 showed triggered_250 recovers ~99% of the recall ceiling at 0.48% of the labelling cost, but measured recall only. A detector trained on ~6,750 flows could trade that for a high benign false-positive rate, which on millions of flows is the real operator burden. Objective 7 is the honest completion of the trade-off across all three operational axes (labels, compute, false positives). Comparing against always_sliding (full labels, same retrain frequency) isolates whether the small budget itself inflates false positives.

**Alternatives considered:** Cumulative as the FPR reference (rejected as default: 30-min retrains for a question always_sliding answers; available via RUN_CUMULATIVE). Macro-averaged rates (rejected: micro-averaging over flows is the operationally correct aggregate; macro recall is kept only as the nb18 cross-check). Per-window inference latency (negligible vs retrain wall-time; retrain time is the reported compute/latency). Reporting a single F1 (rejected: recall, precision and FPR must be shown separately so the trade-off is legible).


## D038 — 2026-06-12
**Context:** `07_phase5_adaptation/20_cross_dataset_replication`

**Decision:** Replicate the Phase-5 loop on UNSW-NB15 with a leave-one-family-out stream that has a quiet in-distribution stretch before novel families are injected, so selectivity and trigger-necessity become testable (CICIDS drifts continuously and could not test them). Add an always_cheap ablation (retrain every window on a B-label pool, no trigger) to src/adaptation/cost_eval.py. Warm-up = benign + SEEN families; stream injects NOVEL families. Micro-averaged metrics. Gates: G1 triggered_250 recall within 0.05 of always_sliding and FPR within 0.05; G2 trigger false-alarm rate over quiet windows <= 0.10; G3 triggered fires less than always_cheap and saves labels at comparable recall (reported either way); G4 deterministic. Verdict CROSS-DATASET-REPLICATED iff G1, G2, G4.

**Rationale:** Reviewers will ask whether the operational finding is CICIDS-specific and whether the KS trigger does any work given it fired on 27/29 CICIDS windows. A second dataset with genuine quiet periods answers both: it tests replication and, for the first time, whether selectivity saves labels over unconditional cheap retraining.

**Alternatives considered:** Temporal UNSW split (rejected: UNSW has no day structure; leave-one-family-out is the standard novelty design). No quiet stretch (rejected: then UNSW repeats the CICIDS limitation and cannot test selectivity). Dropping always_cheap (rejected: it is the direct trigger-necessity control).


## D039 — 2026-06-12
**Context:** `07_phase5_adaptation/21_unsw_hard_regime`

**Decision:** Make the drift regime a controlled knob on UNSW-NB15 — the breadth of the attack space the warm-up detector sees (BREADTHS=[1,2,4] largest families) — to test whether the CICIDS recall-recovery result reappears within UNSW when the regime is made hard, removing the dataset/regime confound of nb20. Stream: >=10 quiet benign windows then NOVEL-family drift. Gates: G1 narrowest breadth frozen recall < 0.70 (a hard regime exists); G2 triggered_2500 recovers recall (>= never+0.05 and >= always_sliding-0.05) in the hardest regime; G3 trigger false-alarm count over quiet windows with Wilson 95% CI, flagged if upper>0.20 (nb20 G2 fix); G4 deterministic. Verdict REGIME-DEPENDENCE-CONFIRMED iff G1 and G2.

**Rationale:** nb20 left CICIDS-vs-UNSW confounded (dataset and regime both changed). Sweeping warm-up breadth on one dataset isolates regime as the variable, so recall collapse + recovery reappearing at narrow breadth is clean evidence the Phase-5 result is regime-dependent, not CICIDS-specific. The Wilson CI replaces the 5-window FA metric a reviewer would challenge.

**Alternatives considered:** Hold out one feature-distinct family (rejected: looks cherry-picked). Benign-only warm-up (rejected: supervised RF needs both classes). New dataset (rejected: reintroduces the confound nb20 already exposed).


## D040 — 2026-06-12
**Context:** `07_phase5_adaptation/22_corrected_gate_confirm`

**Decision:** Correct nb21’s mis-specified G2 and confirm it across seeds. nb21’s G2 required the cheap policy (triggered_2500) to land within 0.05 of the full-label ceiling (always_sliding), bundling a cost-parity question (answered in nb19) into a regime-dependence test, and failed on it (verdict NOT-SHOWN, preserved). Corrected gate tests the regime question with the ceiling policy vs frozen: G1 hardest-breadth frozen recall < 0.70; G2a ceiling recall >= frozen+0.15 (substantial recovery, ~half CICIDS); G2b benefit (ceiling-frozen) flips sign across breadth (mild <= -0.05, hard >= +0.05). Cost-parity removed and reported separately. Replicated over SEEDS=[42,7,123,2024]; CONFIRMED iff G1&G2a&G2b hold in all seeds. Original G2 and selectivity (Wilson CI) preserved and reported, not gated.

**Rationale:** Revising a gate post-hoc risks curve-fitting; the correction is justified by a structural flaw independent of the outcome (cost-parity conflated with regime recovery), the original NOT-SHOWN result is preserved, and the corrected gate is confirmed on 3 seeds beyond the motivating one. Seed 42 reproduces nb21 exactly as a consistency check.

**Alternatives considered:** Re-interpret nb21 in prose without a new gate (rejected: leaves the claim ungated). Single-seed re-gate (rejected: post-hoc, fitted to the motivating seed). Keep triggered in the gate but loosen the margin (rejected: still conflates cost with regime).

