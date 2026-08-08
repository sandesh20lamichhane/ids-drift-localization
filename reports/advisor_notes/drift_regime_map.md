# Drift Regime Map — organizing principle for the thesis

**Status:** living conceptual note · **Owner:** (you) · **Place in repo:** `reports/advisor_notes/drift_regime_map.md`
**Role:** this is the spine. Experiments are organized under it; results are interpreted through it. It is not a results log (those are `findings_log.md`); it is the lens that says, for each experiment, *which method should win and why* before any number is read.

---

## 0. One-paragraph thesis

The experiments converged on a single governing variable — the **type** of drift — which predicts whether explanation-space methods (SHAP-based localization) add operational value over cheap, label-free statistics. Where drift changes the input distribution, a trivial input-distribution test localizes the change and explanations are redundant. Where drift changes the feature→label mapping while inputs stay stable, input statistics are blind and an explanation that reads the model's changed reliance is, in principle, the only thing that can localize it. The thesis is therefore not "our SHAP method wins" but **"explanation-space methods are condition-dependent, and the drift regime predicts whether they add value beyond cheap statistics."** The remaining scientific work is to establish that the *regime*, and not a confounding variable, is what drives the difference.

---

## 1. The governing variable: drift regime

Formal taxonomy (Gama et al. 2014; Webb et al. 2016):

- **Covariate / virtual drift:** P(X) changes, P(y|X) stable. The decision boundary is still correct; only the input density moved.
- **Real concept drift:** P(y|X) changes. The boundary itself moves; which features are decision-relevant can change. Past knowledge becomes invalid.
- **Prior shift:** P(y) changes (class balance). Already studied and ruled out as the failure driver here (F004): the failure is drift, not imbalance.

**Operational definition used in this thesis** (the axis that actually determines whether explanations earn their cost):

> *Can a label-free, model-free input-distribution test (e.g., per-feature KS, Monday-vs-day) detect and localize the change?*

- **Distributional regime — yes it can.** New or shifted input regions; KS on the inputs flags the drifted features without labels or a model.
- **Concept regime — no it cannot.** The feature→label mapping changes while input marginals stay roughly stable; input statistics are blind; localizing the change requires labels or model behaviour.

This operational axis is the through-line of the whole project: it *is* the axis on which an explanation could beat KS. If KS sees the drift, explanations are redundant for localizing it. If KS is blind, explanations are the only candidate.

**IDS caveat worth stating precisely.** A "new attack type" is often called concept drift loosely, but formally it is usually covariate-dominant: the new attack populates input regions the cold model never saw, so P(X) shifts and KS detects it. True concept drift in IDS — the *same* traffic pattern changing label, or feature relevance inverting, with stable marginals — is rare in raw network data. This is why the concept regime is hard to source from real datasets and must be constructed (see §6).

---

## 2. Where the evidence sits today

| Regime | Setting | Key findings | IDs |
|---|---|---|---|
| **Distributional** | CICIDS2017 day-stream (UNSW forthcoming) | Cold-start collapses under drift (not imbalance); KS ≥ SHAP on the stable ground truth; dual-model SHAP adds nothing over single across label budgets; permutation-based ground truth is itself unstable | F003, F004, F005, F006, F007, F008 |
| **Concept (relevance)** | Synthetic relevance-swap pilot | Dual-SHAP localization precision@K = 1.0 against a **known** ground truth | F001 |

Read plainly: on the regime we have studied at depth (real, distributional), explanations are redundant with cheap statistics. On the regime we touched only in the pilot (synthetic, concept), explanations succeeded. That contrast is the thesis — *if* it survives §3.

---

## 3. The central confound (read this before believing the map)

The two poles, as currently studied, differ on **two axes at once**:

1. **Drift type** — distributional (real data) vs concept (synthetic).
2. **Ground-truth availability** — unknown on real data (the entire 07c/07d story: KS, oracle-SHAP and oracle-permutation ground truths disagree and are unstable), vs known on synthetic (the relevance swap *defines* the true drifted features).

So the observed pattern — "explanations redundant under real distributional drift; explanations succeed under synthetic concept drift" — could be caused by drift type **or** by ground-truth availability. Explanations may have "won" on synthetic simply because a trustworthy target existed there and nowhere else.

**Consequence:** the conditions claim is, as of now, a **hypothesis, not a result.** It becomes a result only when drift type is varied with ground-truth availability held constant. Designing that instrument is the next real task (§6).

**Also to verify before relying on the concept anchor:** confirm the synthetic pilot held the input marginals P(X) stable across the relevance swap. If the swap also shifted marginals, the pilot is not a clean concept-drift anchor and KS could have localized it too — which would weaken the anchor rather than strengthen it.

---

## 4. Governing hypothesis (pre-registered, falsifiable)

**H1.** Under controlled conditions with a known ground truth in *every* arm, explanation-space localization beats cheap label-free statistics under **concept** drift but not under **distributional** drift.

Pre-registered falsifiers (any one demotes the conditions claim):

- **F-a.** Explanations remain redundant or unstable under controlled concept drift with known GT → narrow the claim to "explanations localize only in idealized synthetic settings," not a regime law.
- **F-b.** KS (or another cheap statistic) localizes well under controlled concept drift too → explanations redundant regardless of regime.
- **F-c.** Explanations win whenever GT is known, *regardless of regime* → the governing variable is ground-truth availability, not drift type, and the whole framing changes.

H1 is held to the same standard as D018/D020: stated before the deciding experiment, with the failure routes named. The reason the project is in a strong position is that it kept doing this; the concept pole is not the place to stop.

---

## 5. The regime map (predictions + evidence status)

| Regime | Predicted winner | Mechanism | Evidence status |
|---|---|---|---|
| Distributional (P(X) shift) | Cheap statistics (KS) | Input shift is directly observable without labels; explanations re-derive it at higher cost | **Supported** on CICIDS (F005–F008); replication on UNSW + XGBoost pending |
| Concept (P(y|X) shift, stable marginals) | Explanation-space localization | Input stats are blind to a mapping change; a model-relative signal is required | **Hypothesized** (F001 on synthetic, but confounded — §3); controlled test pending |

The left column is close to established; the right column is the open question. The thesis lives or dies on whether the right column survives a confound-controlled test.

---

## 6. Implications for evaluation design

1. **Classify every experiment by regime first.** Before reading which method won, state which regime the setting instantiates (using the §1 operational test). A method "losing" in the wrong regime is uninformative.
2. **Ground truth must be modality-aware, and permutation importance is out as a localization GT.** 07c showed the GT choice silently picks the winner (the GT3 contamination), and 07d showed permutation importance is the unstable estimator (self-Jaccard ≈ 0.58 vs SHAP ≈ 0.92). Do not reinstate a permutation-based ground truth on UNSW. Permutation stays in only as a *studied method* whose instability is itself a reported finding.
3. **The instrument that breaks the confound (ARM B).** A semi-synthetic testbed built on *real* feature vectors with a **known, constructed label rule**, so the true important features are known in every arm. From the same rule, induce drift two ways: (i) shift the input marginals → distributional; (ii) change which features drive the label / move the boundary → concept. Ground-truth availability is now identical across arms, so a difference in explanation performance is attributable to **drift type**. This is the only design that earns the conditions title; family-holdout splits do not (they are distributional regardless of how they are labelled).
4. **UNSW is a second distributional dataset, honestly.** Family/protocol holdout shifts P(X); KS catches it. Use UNSW to test whether the *redundancy* pattern generalizes across datasets and model classes — not to manufacture a concept arm it cannot honestly provide.

---

## 7. Thesis structure implied by the map

- **C1 — Evaluation protocol.** Modality-aware ground truths, self-stability checks, cheap-baseline anchoring, and regime classification. Its value is demonstrated by what it caught: the GT3 modality contamination and the permutation-instability artifact.
- **C2 — Distributional-regime benchmark.** CICIDS + UNSW, RandomForest + XGBoost: explanation-space localization is redundant with cheap statistics. (Replication is the breadth phase.)
- **C3 — Concept-regime study.** Synthetic anchor + the controlled semi-synthetic testbed (ARM B): the confound-controlled test of H1.
- **C4 — The regime map + recommendation.** The synthesis: which regime makes explanations worth their cost, how to tell which regime you are in, and what to use when you are not in it.

Operational/adaptation validation (the old nb08) is optional support for C2/C4, not thesis-defining.

---

## 8. Status ledger (honest)

| Claim | Status | Basis |
|---|---|---|
| Drift, not class imbalance, is the failure mode (distributional) | Established | F003, F004 |
| Dual-model SHAP adds nothing over single-model for localization | Established | F005, F006 |
| Under distributional drift, KS is competitive-to-better than SHAP on the stable GT | Supported | F007 (corrected reading) |
| The F007 near-chance "disagreement" was permutation-importance instability, not a deep cross-method disagreement | Supported | F008 / 07d (perm self ≈ 0.58; SHAP–gain agree ≈ 0.54 on RF) |
| Cross-method importance agreement is model-dependent (RF vs XGBoost) | Suggestive only — not load-bearing | 07d single signal (0.543 vs 0.247); needs stability treatment before use |
| Explanations beat cheap statistics under concept drift | Hypothesized, confounded | F001 (synthetic, known GT — see §3) |
| Drift *regime* (not GT-availability) is the governing variable | Open — the central test (ARM B) | — |

---

## 9. Open questions feeding the next steps

- **Q (confound):** Does H1 survive ARM B with ground truth held constant? (The deciding experiment.)
- **Q (anchor integrity):** Did the synthetic pilot hold P(X) stable across the relevance swap? (Verify before citing it as the concept anchor.)
- **Q (model-dependence):** Is the RF-vs-XGBoost importance-agreement gap real, or an artifact of "gain" meaning different things across model families? (Confirm before it is anything more than a footnote.)
- **Q (existence):** Is there *any* real (non-synthetic) IDS scenario that instantiates concept drift with stable marginals? If not, that limitation is itself a reportable finding about the field.

---

*This note supersedes the informal "dual-model SHAP localization" framing. The hypothesis weakened; the evaluation framework and the regime map became the contribution. Update the status ledger as ARM B and the breadth phase report in.*

## Resolution update — Phase 1 localization closed (post-07h)  (2026-06-05)

**Governing-variable row (S8 ledger) -- RESOLVED, with qualification.**

Drift *type* is **not** the governing variable (07e/F009: aux-SHAP at chance in both drift
regimes on real correlated geometry, construction valid). The candidate was feature
correlation / target identifiability. Resolution across 07f-07h:

- **Controlled (synthetic) setting:** explanation-localization recovery **is** governed by
  target identifiability (proxy availability) -- no proxies -> recovery (precision 1.000),
  proxies -> monotone degradation (07g/F011). Mechanism confirmed.
- **Real CICIDS:** this variable **cannot be exercised**. The only decorrelated features are
  degenerate/constant (unlearnable) and the informative features are collinear (median
  redundancy 0.95), so **no identifiable localization target exists** (07h/F012); and among
  non-degenerate features external leakage does **not** predict recovery (still confounded
  with degeneracy; the correlated set localized better).

**Net:** identifiability explains both the synthetic success and the real-data failure, but
does **not** yield a validated, dataset-agnostic predictive diagnostic. The redundancy +
distributional-health diagnostic is *mechanism-motivated*, pending a clean leakage->recovery
test on a less-collinear dataset (UNSW) in the breadth phase. The positive-shaped search on
CICIDS is closed.
