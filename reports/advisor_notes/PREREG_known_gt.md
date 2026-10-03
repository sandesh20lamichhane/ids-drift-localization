# Pre-registration: known-ground-truth localization benchmark (notebook 28)

Status: DRAFT until committed. Commit this file, record the commit hash in
notebook 28 (`PREREG_GIT_HASH`), and only then run the notebook. If you can,
also deposit this file on OSF (osf.io/registries) for a third-party timestamp.

## 1. Purpose
The real-drift benchmark (notebooks 10b, 13, 14, 25) scores localizers against
GT_in, the per-feature Wasserstein-1 anchor. GT_in is a marginal statistic, so it
shares its modality with KS and may favour KS. This experiment plants the drifted
feature set S, so the answer key is known exactly and belongs to no localizer
family. It becomes the primary benchmark of the revised paper; the GT_in results
become secondary.

## 2. Design (fixed)
- Datasets: corrected CICIDS2017, UNSW-NB15, corrected CSE-CIC-IDS2018.
- Pool: 40,000 real rows per dataset (CSE-CIC-IDS2018: equal share per day), numeric,
  non-constant columns, z-scored. Planted features are drawn from non-degenerate
  features only (modal-value share <= 0.90, the 07h rule).
- Windows: 4,000 pre and 4,000 post rows, disjoint, drawn per seed.
- |S| = 10; precision@10; chance = 10/d.
- Arms:
  - covariate: a fraction q of post rows get +1.0 z-units on every feature in S.
  - dependency: a fraction q of post rows get their S-block copied, as a unit,
    from another random pool row. All marginals and the joint law of S are kept;
    only the dependence between S and the other features changes.
  - concept: P(X) fixed; synthetic median-split label rule moves from S1 to S2 = S
    (the 07e construction).
  - In covariate and dependency arms the label rule is on a set R disjoint from S,
    fixed across windows, so label relevance cannot reveal S.
- q in {0.10, 0.25, 0.50} for covariate and dependency; concept uses q = 1.
- Models: RF (phase-1 parameters), XGB (300 trees, depth 6), MLP (256-128-64).
- Seeds: {42, 1, 7, 13, 99}.
- Localizers: KS; cond-KS (KS on ridge residuals of x_j given x_{-j}, fitted on
  half the pre window); domain-SHAP; permutation importance of the domain
  classifier; aux-SHAP (detector trained on the post window); dual
  (|aux-SHAP - pre-SHAP|); random.

## 3. Predictions (written before any run)
- P1 (covariate): KS is at least as good as domain-SHAP for tree models
  (paired delta KS - domain-SHAP >= -0.05).
- P2 (dependency): domain-SHAP beats KS (delta > 0, Holm-adjusted p < 0.05), and
  KS is within 0.10 of chance.
- P3 (dependency): cond-KS beats KS (delta > 0, Holm p < 0.05).
- P4 (concept): aux-SHAP beats KS (delta > 0, Holm p < 0.05). We also predict,
  from the 07e result on CICIDS2017, that aux-SHAP's absolute precision on the
  concept arm stays below 0.50 on the two CIC datasets.
- P5 (all arms): dual does not beat aux-SHAP (delta <= +0.05).
- P6 (covariate): KS beats random (Holm p < 0.05). This is a sanity check.

## 4. Analysis (fixed)
Paired Wilcoxon signed-rank over dataset x q x model x seed pairs (P1 trees only),
seeded bootstrap 95% CI (10,000 resamples), paired effect size d_z, and Holm
correction across the six tests P1-P6. All rows of the summary table are reported
whatever their outcome. A failed prediction is reported as failed.

## 5. What would change the paper
- If P2 holds and P1 holds: the paper's message becomes "use KS for marginal
  (covariate) drift, and a domain classifier for dependency drift that leaves
  marginals unchanged". This is more useful than the current "KS is enough".
- If P2 fails: KS-style marginal tests plus a conditional test cover both regimes,
  and explanation-based localization has no regime where it is needed.
- If P4 holds with high absolute precision on real features, the redundancy
  argument (C3) must be softened further.

## 6. Deviations
Any change after commit is logged here with a date and reason.
