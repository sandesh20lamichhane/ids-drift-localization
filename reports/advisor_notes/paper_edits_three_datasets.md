# Paper Edits — Three-Dataset Update (CSE-CIC-IDS2018)

Replacement text keyed to sections of the current paper. Numbers are from:
23 v2 (geometry), 24 (G-DRIFT), 25 (benchmark), 25b (control + regime
diagnostic). Anything in ⟨angle brackets⟩ needs a value from the extended
significance notebook (15) before submission.

---

## 1. Abstract — two sentence replacements

**Replace** "Across two benchmark datasets (CICIDS2017 and UNSW-NB15), three
model classes ..." **with:**

> Across three benchmark datasets (CICIDS2017, UNSW-NB15, and
> CSE-CIC-IDS2018), three model classes (random forest, XGBoost, and a
> multilayer perceptron), and a pre-registered evaluation protocol, the
> dual-model signal never beats its own single-model component, and for the
> tree models neither beats a Kolmogorov–Smirnov (KS) two-sample test that
> uses no labels and no explanations.

**Replace** "The one apparent exception ... does not replicate on CICIDS,
where the marginal shift is stronger and KS is competitive again, so the
neural advantage is drift-dependent rather than a robust property." **with:**

> The one systematic exception is a neural domain classifier, whose SHAP
> localized the drift better than KS on UNSW-NB15 and CSE-CIC-IDS2018 but
> not on CICIDS2017; an explainer control on all three datasets attributes
> the effect to the model, not the explainer, and a marginality analysis
> shows the boundary is governed by the strength of the injected marginal
> shift: the neural localizer's accuracy is regime-invariant (0.55–0.59)
> while KS tracks marginal strength (0.41–0.70), so the neural advantage
> appears exactly where the marginal signal is weak.

## 2. §I, contribution C2 bullet — replace the exception sentence

**Replace** "We report, rather than smooth over, the single non-replicating
exception ... drift-dependent, not a robust property (Sec. IV-G)." **with:**

> We report, and then characterize, the one systematic exception: on UNSW
> and CSE-CIC-IDS2018 a neural domain classifier's SHAP localized the
> Wasserstein drift better than KS, while on CICIDS, where the injected
> marginal shift is strong, KS wins. An explainer control on every dataset
> attributes the effect to the model class, and a per-arm marginality
> diagnostic shows the boundary tracks marginal-shift strength, not the
> dataset — a drift-marginality boundary of C2 rather than a refutation of
> it (Sec. IV-G).

## 3. §III-A — dataset paragraph addition (after the UNSW sentence)

> CSE-CIC-IDS2018 (improved release, same corrected-label lineage as our
> CICIDS2017 [27]) provides ten capture days over three weeks with novel
> attack families arriving gradually; after harmonization it shares the
> 82-feature CICFlowMeter schema with CICIDS2017 exactly. The first capture
> day (benign + FTP/SSH brute force) trains the frozen detector; five novel
> families (DoS, DDoS, Web, Infiltration, Bot) define the drift. The Web
> family is excluded from localization arms as underpowered (75 flows
> corpus-wide); all windows, arms, and gates were fixed in a pre-registered
> addendum before any benchmark contact.

## 4. §IV-A addition — one sentence after the CICIDS drift-premise result

> The premise replicates on CSE-CIC-IDS2018: the frozen detector's recall
> falls from 1.000 on its training day to at most 0.055 on every
> novel-family day (0.000 on most) while FPR stays below 3×10⁻⁵, imbalance
> controls move recall by ≤10⁻⁴, and — because the brute-force family
> reappears mid-week — the same frozen model scores recall 1.0 on returning
> known-family flows in the same traffic where it scores 0.0 on novel DoS
> flows, isolating family novelty, not general degradation, as the failure
> mode.

## 5. §IV-E addition — geometry sentence (after the UNSW-NB15 block)

> CSE-CIC-IDS2018 is the most redundant of the three: of 82 features 60 are
> non-degenerate, median pairwise redundancy is 0.969, no decorrelated
> non-degenerate size-5 target exists, and the external-leakage floor is
> 0.365. The newest and largest corpus therefore lies furthest from the
> decorrelated validity regime.

Update the in-text floor list wherever it appears: "external-leakage floor
0.25–0.44" → "0.25–0.44 (CICIDS 0.248, CSE-CIC-IDS2018 0.365, UNSW 0.440)".

## 6. §IV-F — add the 2018 replication paragraph (end of section)

> A second replication on CSE-CIC-IDS2018 (four additive leave-one-family-
> out arms — DoS, DDoS, Infiltration, Bot — same construction, anchor,
> localizers, and seeds; chance 0.122) reproduces the pattern: against the
> model-free Wasserstein truth, KS scores 0.425 while domain-SHAP scores
> 0.367 (RF) and 0.225 (XGB); the dual signal again adds nothing
> (dual−domain-SHAP = +0.017, −0.050, −0.058 for RF, XGB, MLP), and the
> modality-circularity inflation reappears at +0.425 (RF) and +0.433 (XGB)
> — quantitatively matching the +0.42 measured on UNSW. Domain-SHAP is
> again more self-stable than permutation importance (0.43–0.60 vs
> 0.18–0.31). ⟨Paired significance over the pooled family×model×seed pairs:
> from notebook 15 re-run.⟩

## 7. §IV-G — REWRITE (this is the section the new results change)

Suggested replacement for the final two paragraphs of IV-G ("But it does
not replicate on CICIDS. ... reliably beat the cheap test."):

> The third dataset resolves the boundary. On CSE-CIC-IDS2018 the MLP
> domain-SHAP again beats KS (0.550 vs 0.425, KS−domain-SHAP = −0.125)
> while KS remains competitive for both tree models (+0.058, +0.200), and
> the same explainer control again attributes the effect to the model:
> under an identical PermutationExplainer the trees still do not beat KS
> (+0.058, +0.267; TreeSHAP–permutation Spearman 0.977, 0.976) whereas the
> MLP does (−0.108). Across the three datasets the pattern is now
> mechanistic rather than anecdotal: the MLP domain-SHAP is essentially
> regime-invariant (0.589 on UNSW, 0.578 on CICIDS, 0.550 on
> CSE-CIC-IDS2018), while KS tracks the marginal strength of the injected
> drift (0.411, 0.700, 0.425 respectively) — so the neural localizer wins
> exactly where the marginal signal is weak (UNSW, CSE-CIC-IDS2018) and
> loses where it is strong (CICIDS). A per-arm diagnostic within
> CSE-CIC-IDS2018 corroborates the same gradient in miniature: the MLP's
> advantage over KS falls from +0.233 (DoS, weakest injected marginality by
> top-10 per-feature KS, 0.351) through +0.167 (DDoS) and +0.100 (Bot) to
> exactly 0.000 on Infiltration, the most marginal arm (0.451) — four
> points at precision@10 granularity, so we read this as corroboration of
> the cross-dataset gradient, not an independent law. The neural advantage
> is therefore not drift-*dataset*-dependent but drift-*marginality*-
> dependent: a characterized boundary of C2. The core claims are untouched
> by it — the dual signal adds nothing for any model on any dataset, KS is
> competitive with every tree-based explanation localizer everywhere, and
> the circularity artifact reproduces at +0.43 on the third dataset.

Also update the section title if desired: "Adding a neural model: a
drift-dependent boundary" → "Adding a neural model: a drift-marginality
boundary".

## 8. Table III — add the 2018 row-block

| Data | Model | KS | dom-SHAP | dual | KS−dom | dual−dom |
|---|---|---|---|---|---|---|
| CSE2018 (0.122) | RF  | 0.425 | 0.367 | 0.383 | +0.058 | +0.017 |
|                 | XGB | 0.425 | 0.225 | 0.175 | +0.200 | −0.050 |
|                 | MLP | 0.425 | 0.550 | 0.492 | −0.125 | −0.058 |

Caption edit: "KS−dom is positive (KS competitive) everywhere except the
MLP on UNSW; on CICIDS that one exception disappears." → "KS−dom is
positive (KS competitive) for every tree model on every dataset; the MLP
exceeds KS on UNSW and CSE-CIC-IDS2018 but not CICIDS — the marginality
boundary of Sec. IV-G."

## 9. Table IV — new rows (values from the notebook-15 re-run)

- KS vs domain-SHAP (2018, trees): ⟨Δ, CI, p, d_z⟩
- dual vs domain-SHAP (2018, all models): ⟨Δ, CI, p, d_z⟩
- domain-SHAP(MLP) vs KS (2018, GT_in): ⟨Δ, CI, p, d_z⟩  ← new row type;
  n = 4 families × 3 seeds = 12 pairs
- domain-SHAP vs KS against GT_ex (2018, circularity): ⟨…⟩

## 10. Table V (claims map) — add to the Evidence column

- C1: "+0.43 circularity replication (Fig. 25-analog; Table II-analog 2018)"
  — dataset column gains CSE2018.
- C2: Table III 2018 block; explainer control ×3 datasets.
- C3: geometry row (82/60/0.969/0.365).

## 11. §V-B Threats — replace the two neural caveats paragraph's opening

**Replace** "Second, that edge is not cross-dataset robust: it appears on
UNSW ... and vanishes on CICIDS ..." **with:**

> Second, the boundary of that edge is now characterized rather than
> merely observed: across three datasets the neural localizer's accuracy is
> flat while KS varies with the marginal strength of the injected families,
> and the within-dataset per-arm gradient on CSE-CIC-IDS2018 matches. The
> characterization rests on three datasets and four arms at precision@10
> granularity; we present it as a mechanism-consistent boundary, not a
> fitted predictive rule. Whether it holds under genuinely multivariate,
> marginally-weak drift remains the question this work scopes but does not
> settle.

Add to the shared-limitations sentence: "all three datasets share the
CICFlowMeter/flow-feature paradigm; packet- and sequence-level
representations remain future work."

## 12. §V-C Implications — add one clause

After "...the cheaper signal is also the better-justified default for
always-on deployment," add:

> with one now-characterized exception: when the operator has reason to
> suspect weak-marginal drift — the regime where a per-feature test has
> little to see — a neural domain classifier is the better localizer, at
> the cost of window-level model fitting and per-instance attribution
> compute; the two tree-based explanation localizers never justify that
> cost on any dataset we measured.

## 13. §VI Conclusion — replace the exception sentence

**Replace** "the one place an explanation localizer beat the cheap test —
a neural domain classifier on UNSW — did not survive a second dataset,
making the neural advantage drift-dependent rather than robust." **with:**

> the one systematic exception — a neural domain classifier — beat the
> cheap test precisely in the weak-marginal-drift regime (UNSW,
> CSE-CIC-IDS2018) and not in the strong (CICIDS2017), with explainer
> controls on all three datasets attributing the effect to the model; the
> findings hold across three datasets and three model classes.

## 14. Remaining pipeline before these edits are final

1. Extend `99_paper_figures/15_significance_tests.ipynb` with the 2018
   pairs (fills every ⟨…⟩ above): KS-vs-dom trees n=24 (2 models × 4
   families × 3 seeds), dual-vs-dom n=36, MLP-dom-vs-KS n=12, circularity
   n=36.
2. Figures: `25_cse2018_benchmark` → Fig. 8/9-analog; `25b_regime_
   diagnostic` → new small figure in IV-G (optionally overlay the three
   cross-dataset points on the same axes).
3. Decisions log: append the notebook-25 and 25b decisions under the true
   next free IDs (both collided with existing D031/D032 and were skipped).
4. Findings log: F0XX entries for 23v2/24/25/25b.
5. Thesis: the same content lands as a new section in the multi-dataset
   chapter + one paragraph in the synthesis chapter; the A1/A2 addenda are
   already thesis-ready appendices.
