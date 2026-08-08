"""
Operational adaptation policies for the Phase-5 study (Objective 6).

Each policy replays an ordered stream window by window, scores recall on the
attack class with the current detector, and decides whether/how to retrain.
`label_cost` is the number of labels the policy spends (the expensive human
resource). The KS-triggered policy uses an UPDATING reference -- re-baselined to
the current window after each retrain, which is label-free -- so it fires on NEW
drift and then goes quiet. This is the design fix from notebook 17, without which
triggered retraining collapses into always-retrain on a continuously drifting
stream. Its labelled pool ACCUMULATES `budget` flows per trigger, so it retains
earlier families while spending only `budget` new labels each time.

Promoted from notebook 18 for notebooks 19-20.
"""
from __future__ import annotations
import numpy as np
from src.streaming.replay import train_detector, recall_attack
from src.monitoring.ks_monitor import per_feature_ks


def run_never(Xs, ys, windows, det):
    """Floor: one frozen detector scored on every window."""
    rec = [recall_attack(ys[a:b], det.predict(Xs[a:b])) for (a, b) in windows]
    return dict(policy='never', recall=np.asarray(rec, float),
                label_cost=0, n_retrains=0, triggers=[])


def run_always_sliding(Xs, ys, windows, det0, rf_kw, buffer_windows=1):
    """Ceiling A: retrain on the most recent labeled window every window."""
    rec, cost, nret, cur = [], 0, 0, det0
    for i, (a, b) in enumerate(windows):
        if i > 0:
            lo = max(0, i - buffer_windows)
            aa, bb = windows[lo][0], windows[i][0]
            cur = train_detector(Xs[aa:bb], ys[aa:bb], rf_kw)
            cost += (bb - aa); nret += 1
        rec.append(recall_attack(ys[a:b], cur.predict(Xs[a:b])))
    return dict(policy='always_sliding', recall=np.asarray(rec, float),
                label_cost=cost, n_retrains=nret, triggers=[])


def run_cumulative(Xs, ys, windows, det0, rf_kw):
    """Ceiling B (true upper bound): retrain on all stream data seen so far."""
    rec, cost, nret, cur = [], 0, 0, det0
    for i, (a, b) in enumerate(windows):
        if i > 0:
            bb = windows[i][0]
            cur = train_detector(Xs[0:bb], ys[0:bb], rf_kw)
            cost += bb; nret += 1
        rec.append(recall_attack(ys[a:b], cur.predict(Xs[a:b])))
    return dict(policy='cumulative', recall=np.asarray(rec, float),
                label_cost=cost, n_retrains=nret, triggers=[])


def run_periodic(Xs, ys, windows, det0, rf_kw, K):
    """Fixed-schedule baseline: retrain on the recent window every K windows."""
    rec, cost, nret, cur = [], 0, 0, det0
    for i, (a, b) in enumerate(windows):
        if i > 0 and (i % K == 0):
            aa, bb = windows[i - 1][0], windows[i][0]
            cur = train_detector(Xs[aa:bb], ys[aa:bb], rf_kw)
            cost += (bb - aa); nret += 1
        rec.append(recall_attack(ys[a:b], cur.predict(Xs[a:b])))
    return dict(policy=f'periodic_{K}', recall=np.asarray(rec, float),
                label_cost=cost, n_retrains=nret, triggers=[])


def run_triggered(Xs, ys, windows, det0, rf_kw, reference0, tau, budget, seed=42):
    """KS-triggered, label-budgeted retraining with an UPDATING reference.

    Prequential: window i is scored with the current detector, THEN if the
    monitor fires the policy labels `budget` flows from window i, appends them to
    an accumulating pool, retrains on the pool, and re-baselines the reference to
    window i (label-free). label_cost = n_triggers * budget.
    """
    rng = np.random.default_rng(seed)
    rec, cost, nret, triggers = [], 0, 0, []
    cur = det0
    ref = np.asarray(reference0)
    poolX, poolY = [], []
    for i, (a, b) in enumerate(windows):
        Xi, yi = Xs[a:b], ys[a:b]
        score = float(per_feature_ks(ref, Xi).mean())
        rec.append(recall_attack(yi, cur.predict(Xi)))   # score before adapting
        if score > tau:
            triggers.append(i)
            k = min(budget, len(Xi))
            idx = rng.choice(len(Xi), size=k, replace=False)
            poolX.append(Xi[idx]); poolY.append(yi[idx])
            cost += k; nret += 1
            cur = train_detector(np.concatenate(poolX), np.concatenate(poolY), rf_kw)
            ref = Xi   # updating reference (label-free)
    return dict(policy=f'triggered_{budget}', recall=np.asarray(rec, float),
                label_cost=cost, n_retrains=nret, triggers=triggers)
