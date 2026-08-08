"""
src/divergence/localization.py

Feature-level drift-localization helpers for Phase 1.

Given a frozen "main" model and a recently-trained "auxiliary" model, we score
each feature by how much the two models' SHAP importances disagree, and then
ask whether the top-scoring features match a ground-truth set of drifted
features. These are pure functions (no Drive paths, no globals) so they can be
unit-tested and reused by notebooks 07 (localization) and 08 (adaptation).

Scoring functions return a 1-D array of length n_features (higher = more
likely drifted). Evaluation functions compare a score vector against a
ground-truth index set.
"""
from __future__ import annotations
import numpy as np

try:
    import shap
except Exception:  # shap is optional at import time
    shap = None


# --------------------------------------------------------------------------- #
# SHAP importance
# --------------------------------------------------------------------------- #
def _to_class1(sv):
    """Normalise the several shapes shap.TreeExplainer returns for a binary
    classifier into a single (n_samples, n_features) array of class-1
    contributions."""
    if isinstance(sv, list):                       # [class0 (n,f), class1 (n,f)]
        return np.asarray(sv[1] if len(sv) > 1 else sv[0])
    arr = np.asarray(sv)
    if arr.ndim == 3:                              # (n, f, n_classes)
        return arr[:, :, 1] if arr.shape[2] > 1 else arr[:, :, 0]
    return arr                                     # already (n, f)


def shap_importance(model, X):
    """Mean absolute class-1 SHAP value per feature, normalised to sum to 1.

    Returns a 1-D np.ndarray of length n_features. Caller is responsible for
    subsampling X to a manageable size before calling (SHAP cost scales with
    n_samples).
    """
    if shap is None:
        raise ImportError('shap is not installed in this environment.')
    Xv = X.values if hasattr(X, 'values') else np.asarray(X)
    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(Xv, check_additivity=False)
    arr = _to_class1(sv)
    imp = np.abs(arr).mean(axis=0)
    total = imp.sum()
    return imp / total if total > 0 else imp


# --------------------------------------------------------------------------- #
# Prediction-disagreement importance (the D012 "do you even need SHAP" baseline)
# --------------------------------------------------------------------------- #
def permutation_disagreement_importance(main_model, aux_model, X, seed=42):
    """Score each feature by how much permuting it changes the disagreement
    rate between the two models' predictions. Normalised to sum to 1.

    No SHAP involved -- this is the cheap baseline the dual-model SHAP method
    must beat to justify its cost.
    """
    rng = np.random.default_rng(seed)
    Xv = (X.values if hasattr(X, 'values') else np.asarray(X)).copy()
    base = float(np.mean(main_model.predict(Xv) != aux_model.predict(Xv)))
    n_features = Xv.shape[1]
    scores = np.zeros(n_features)
    for f in range(n_features):
        saved = Xv[:, f].copy()
        Xv[:, f] = rng.permutation(saved)
        d = float(np.mean(main_model.predict(Xv) != aux_model.predict(Xv)))
        scores[f] = abs(d - base)
        Xv[:, f] = saved
    total = scores.sum()
    return scores / total if total > 0 else scores


# --------------------------------------------------------------------------- #
# Ground-truth construction
# --------------------------------------------------------------------------- #
def ks_drift_scores(X_ref, X_cur):
    """Per-feature two-sample KS statistic between a reference sample and a
    current sample. Higher = more input-distribution drift on that feature."""
    from scipy.stats import ks_2samp
    Xr = X_ref.values if hasattr(X_ref, 'values') else np.asarray(X_ref)
    Xc = X_cur.values if hasattr(X_cur, 'values') else np.asarray(X_cur)
    n = Xr.shape[1]
    return np.array([ks_2samp(Xr[:, f], Xc[:, f]).statistic for f in range(n)])


# --------------------------------------------------------------------------- #
# Top-K and evaluation
# --------------------------------------------------------------------------- #
def topk_indices(scores, k):
    """Indices of the top-k scores, descending. Stable tie-break by index."""
    scores = np.asarray(scores, dtype=float)
    return list(np.argsort(-scores, kind='stable')[:k])


def precision_at_k(scores, ground_truth_idx, k):
    """Fraction of the top-k scored features that lie in the ground-truth set."""
    if k == 0:
        return float('nan')
    top = set(topk_indices(scores, k))
    gt = {int(i) for i in ground_truth_idx}
    return len(top & gt) / k


def recall_at_k(scores, ground_truth_idx, k):
    """Fraction of the ground-truth features captured in the top-k."""
    gt = {int(i) for i in ground_truth_idx}
    if not gt:
        return float('nan')
    top = set(topk_indices(scores, k))
    return len(top & gt) / len(gt)


def jaccard(idx_a, idx_b):
    """Jaccard overlap between two index sets."""
    a, b = {int(i) for i in idx_a}, {int(i) for i in idx_b}
    if not a and not b:
        return float('nan')
    return len(a & b) / len(a | b)


def random_precision_expectation(gt_size, n_features):
    """E[precision@k] for a uniformly random ranker = gt_size / n_features
    (independent of k under sampling without replacement)."""
    return gt_size / n_features


# --------------------------------------------------------------------------- #
# Model-agnostic SHAP importance (validated in notebook 11 / D028 / F016)
#
# TreeSHAP (shap_importance, above) cannot run on non-tree models such as an
# MLP. The functions below provide a model-agnostic SHAP path so the neural
# breadth notebooks (12 = identifiability sweep, 13 = UNSW benchmark) use the
# SAME importance contract as the tree path: a 1-D array of length n_features,
# normalised to sum to 1. Validated against a known decorrelated planted
# target and cross-checked against shap_importance on a random forest
# (Spearman ~0.89); see notebook 11.
#
# Normalisation is a positive rescaling and does not change feature ranks, so
# precision@k / Spearman are identical to the unnormalised values validated in
# notebook 11.
# --------------------------------------------------------------------------- #
_TREE_MODEL_NAMES = {
    'RandomForestClassifier', 'RandomForestRegressor',
    'ExtraTreesClassifier', 'ExtraTreesRegressor',
    'GradientBoostingClassifier', 'GradientBoostingRegressor',
    'HistGradientBoostingClassifier', 'HistGradientBoostingRegressor',
    'DecisionTreeClassifier', 'DecisionTreeRegressor',
    'XGBClassifier', 'XGBRegressor', 'XGBRFClassifier',
    'LGBMClassifier', 'LGBMRegressor',
    'CatBoostClassifier', 'CatBoostRegressor',
}


def is_tree_model(model):
    """True if `model` is a tree/forest/boosting model TreeExplainer supports.

    Name-based so it needs no optional imports (xgboost/lightgbm/catboost may
    be absent from the environment).
    """
    return any(c.__name__ in _TREE_MODEL_NAMES for c in type(model).__mro__)


def agnostic_shap_importance(model, X_eval, X_bg, backend='permutation',
                             eval_n=400, bg_n=100, seed=42, kernel_kmeans=50):
    """Model-agnostic mean-|SHAP| importance per feature, normalised to sum 1.

    For any model exposing predict_proba (e.g. sklearn MLPClassifier). Returns
    a 1-D np.ndarray of length n_features, matching shap_importance's contract
    so it is a drop-in for the tree path.

    backend : 'permutation' (shap.PermutationExplainer, fast) or 'kernel'
              (shap.KernelExplainer, classic/slower fallback).
    X_bg    : background sample for the masker (rows subsampled to bg_n).
    eval_n  : eval rows subsampled for the global importance estimate.
    """
    if shap is None:
        raise ImportError('shap is not installed in this environment.')
    if not hasattr(model, 'predict_proba'):
        raise ValueError('agnostic_shap_importance needs a predict_proba model.')
    Xe_all = X_eval.values if hasattr(X_eval, 'values') else np.asarray(X_eval)
    Xb_all = X_bg.values if hasattr(X_bg, 'values') else np.asarray(X_bg)
    rng = np.random.default_rng(seed)
    Xb = Xb_all[rng.choice(len(Xb_all), size=min(bg_n, len(Xb_all)), replace=False)]
    Xe = Xe_all[rng.choice(len(Xe_all), size=min(eval_n, len(Xe_all)), replace=False)]

    def f(Z):
        return model.predict_proba(np.asarray(Z))[:, 1]

    if backend == 'kernel':
        expl = shap.KernelExplainer(f, shap.kmeans(Xb, min(bg_n, kernel_kmeans)))
        sv = np.asarray(expl.shap_values(Xe, nsamples='auto', silent=True))
    else:
        expl = shap.PermutationExplainer(f, Xb)
        sv = np.asarray(expl(Xe, max_evals=2 * Xe.shape[1] + 1, silent=True).values)
    imp = np.abs(sv).mean(axis=0)
    total = imp.sum()
    return imp / total if total > 0 else imp


def shap_importance_any(model, X_eval, X_bg=None, **kwargs):
    """Dispatch SHAP importance by model type.

    Tree models -> TreeSHAP (shap_importance); everything else -> the
    model-agnostic path (agnostic_shap_importance), which requires a background
    set X_bg. Returns a 1-D array of length n_features, normalised to sum 1.
    """
    if is_tree_model(model):
        return shap_importance(model, X_eval)
    if X_bg is None:
        raise ValueError('a non-tree model needs a background set X_bg.')
    return agnostic_shap_importance(model, X_eval, X_bg, **kwargs)
