"""
v3 KS drift trigger: benign-only reference + strengthened null + persistence.

Validated by notebook 26 v3 (PREREG A5, verdict ARTIFACT-FIXED-V3): zero quiet
false fires AND zero exceedances at every breadth, onset latency exactly 1,
and triggered_2500 recall +0.10 to +0.145 ABOVE the legacy trigger (false
fires poison the accumulating label pool with benign-only retrains; v3 never
false-fires, so it reaches drift onset with a clean pool).

Mechanisms (all pre-registered in A5, derived from the v1/v2 failure analyses):
- Reference: benign-only rows (removes the initialization composition
  artifact of the mixed warm-up reference — A3).
- Threshold: tau_eff = max( max of >=6 genuinely disjoint null windows,
  empirical PERM_Q quantile of N_PERM permutation draws from the pooled
  benign calibration + burn-in rows ). The quantile form is the corrected
  version of the v1 bootstrap (overlap biases a sigma estimate, not an
  empirical quantile); the disjoint-max term guards the quantile's tail.
- Persistence: FIRE only on k_persist consecutive exceedances
  (Western-Electric run rule); isolated noise-band crossings are non-events;
  costs at most k_persist - 1 windows of latency on a contiguous drift.

Retrain / label-pool / moving-reference semantics are copied verbatim from
cost_eval.run_instrumented's 'triggered' branch so results remain comparable
with notebooks 18-22; the ONLY behavioural change is the fire condition.

Promoted from notebook 26 v3 (the nb17 promotion pattern).
"""
from __future__ import annotations
import time
import numpy as np

from src.streaming.replay import train_detector
from src.monitoring.ks_monitor import per_feature_ks


def _windows_of(n, size):
    b = list(range(0, n, size)) + [n]
    return [(b[i], b[i + 1]) for i in range(len(b) - 1)]


def tau_v3(reference, cal_pool, burn_windows, window_size,
           n_perm=200, perm_q=0.999, seed=42):
    """A5.2 threshold: max( max of disjoint nulls, permutation quantile ).

    Args:
        reference: benign-only monitor reference (fixed).
        cal_pool: benign-only calibration rows (disjoint from reference).
        burn_windows: list of arrays — the burn-in stream windows consumed
            as additional genuine Phase-I nulls (neither monitored nor
            counted downstream).
        window_size: monitored window size (null windows must match it).
        n_perm / perm_q: permutation-null draws and the empirical quantile.
        seed: RNG seed for the permutation draws.

    Returns dict with tau_eff, tau_disjoint, tau_perm, n_disjoint,
    disjoint_scores.
    """
    reference = np.asarray(reference)
    cal_pool = np.asarray(cal_pool)
    disjoint = [cal_pool[a:b] for (a, b) in _windows_of(len(cal_pool), window_size)
                if b - a == window_size] + [np.asarray(w) for w in burn_windows]
    d_scores = [float(per_feature_ks(reference, w).mean()) for w in disjoint]
    pool = np.vstack([cal_pool] + [np.asarray(w) for w in burn_windows])
    rng = np.random.default_rng(seed)
    p_scores = []
    for _ in range(n_perm):
        idx = rng.choice(len(pool), size=window_size, replace=False)
        p_scores.append(float(per_feature_ks(reference, pool[idx]).mean()))
    tau_disjoint = max(d_scores)
    tau_perm = float(np.quantile(p_scores, perm_q))
    return dict(tau_eff=max(tau_disjoint, tau_perm),
                tau_disjoint=tau_disjoint, tau_perm=tau_perm,
                n_disjoint=len(d_scores),
                disjoint_scores=d_scores)


def run_triggered_persist(Xs, ys, windows, det0, rf_kw, reference0, tau,
                          budget, k_persist=2, seed=42):
    """Triggered policy with a k-consecutive persistence rule.

    Identical to cost_eval.run_instrumented(policy='triggered') except the
    fire condition: the trigger FIRES only after `k_persist` consecutive
    windows exceed `tau`. Exceedances are recorded separately from fires.

    Returns the run_instrumented-shaped dict plus an 'exceedances' list;
    per_window rows additionally carry 'score' and 'exceed'.
    """
    rng = np.random.default_rng(seed)
    rows, triggers, exceedances = [], [], []
    labels = 0
    compute = 0.0
    cur = det0
    ref = np.asarray(reference0)
    poolX, poolY = [], []
    streak = 0
    for i, (a, b) in enumerate(windows):
        Xi, yi = Xs[a:b], ys[a:b]
        rt = 0.0
        spent = 0
        pred = cur.predict(Xi)
        tp = int(((pred == 1) & (yi == 1)).sum())
        fp = int(((pred == 1) & (yi == 0)).sum())
        fn = int(((pred == 0) & (yi == 1)).sum())
        tn = int(((pred == 0) & (yi == 0)).sum())

        score = float(per_feature_ks(ref, Xi).mean())
        exceed = bool(score > tau)
        if exceed:
            exceedances.append(i)
        streak = streak + 1 if exceed else 0
        if streak >= k_persist:
            triggers.append(i)
            k = min(budget, len(Xi))
            idx = rng.choice(len(Xi), size=k, replace=False)
            poolX.append(Xi[idx])
            poolY.append(yi[idx])
            t = time.time()
            cur = train_detector(np.concatenate(poolX), np.concatenate(poolY), rf_kw)
            rt = time.time() - t
            spent = k
            ref = Xi
            streak = 0
        labels += spent
        compute += rt
        rows.append(dict(window=i, tp=tp, fp=fp, fn=fn, tn=tn,
                         retrained=(spent > 0), retrain_s=rt, labels=spent,
                         score=score, exceed=exceed))
    return dict(policy=f'triggered_persist_{budget}', per_window=rows,
                label_cost=labels, compute_s=compute,
                n_retrains=len(triggers), triggers=triggers,
                exceedances=exceedances)
