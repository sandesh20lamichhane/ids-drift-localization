"""
Instrumented policy runner for the Phase-5 cost/latency accounting (Objective 7)
and the cross-dataset replication (notebook 20).

Records, per window, the full confusion counts (tp/fp/fn/tn), the retrain
wall-time, and the labels spent, so recall, precision, false-positive rate, alert
volume, compute, and labels all come from one pass. Retrain semantics match
policies.py (always/cumulative/periodic retrain before scoring window i;
triggered scores then retrains with an updating reference), so recall reproduces
notebook 18.

`always_cheap` is the trigger-necessity ablation: identical to `triggered` but it
fires on EVERY window (no KS gate). Comparing triggered vs always_cheap shows
whether the trigger saves anything by staying selective -- on a continuously
drifting stream it cannot; on a stream with quiet periods it should.

Promoted from notebook 19; extended in notebook 20.
"""
from __future__ import annotations
import time
import numpy as np
from src.streaming.replay import train_detector
from src.monitoring.ks_monitor import per_feature_ks


def confusion(y_true, y_pred):
    yt = np.asarray(y_true); yp = np.asarray(y_pred)
    tp = int(((yp == 1) & (yt == 1)).sum())
    fp = int(((yp == 1) & (yt == 0)).sum())
    fn = int(((yp == 0) & (yt == 1)).sum())
    tn = int(((yp == 0) & (yt == 0)).sum())
    return tp, fp, fn, tn


def run_instrumented(Xs, ys, windows, det0, rf_kw, policy,
                     reference0=None, tau=None, budget=None, K=None, seed=42):
    """Run one policy with full per-window instrumentation.

    policy in {'never','always_sliding','cumulative','periodic','triggered',
    'always_cheap'}. For 'triggered'/'always_cheap', `budget` labels are drawn
    from the current window and appended to an accumulating pool; 'always_cheap'
    fires every window, 'triggered' only when the KS score exceeds tau.
    """
    rng = np.random.default_rng(seed)
    rows = []
    labels = 0
    compute = 0.0
    cur = det0
    ref = None if reference0 is None else np.asarray(reference0)
    poolX, poolY, triggers = [], [], []

    for i, (a, b) in enumerate(windows):
        Xi, yi = Xs[a:b], ys[a:b]
        rt = 0.0
        spent = 0
        if policy == 'always_sliding' and i > 0:
            aa, bb = windows[i - 1][0], windows[i][0]
            t = time.time(); cur = train_detector(Xs[aa:bb], ys[aa:bb], rf_kw); rt = time.time() - t
            spent = bb - aa
        elif policy == 'cumulative' and i > 0:
            bb = windows[i][0]
            t = time.time(); cur = train_detector(Xs[0:bb], ys[0:bb], rf_kw); rt = time.time() - t
            spent = bb
        elif policy == 'periodic' and i > 0 and (i % K == 0):
            aa, bb = windows[i - 1][0], windows[i][0]
            t = time.time(); cur = train_detector(Xs[aa:bb], ys[aa:bb], rf_kw); rt = time.time() - t
            spent = bb - aa

        tp, fp, fn, tn = confusion(yi, cur.predict(Xi))   # score window i

        if policy in ('triggered', 'always_cheap'):
            fire = True
            if policy == 'triggered':
                score = float(per_feature_ks(ref, Xi).mean())
                fire = bool(score > tau)
            if fire:
                triggers.append(i)
                k = min(budget, len(Xi))
                idx = rng.choice(len(Xi), size=k, replace=False)
                poolX.append(Xi[idx]); poolY.append(yi[idx])
                t = time.time()
                cur = train_detector(np.concatenate(poolX), np.concatenate(poolY), rf_kw)
                rt = time.time() - t
                spent = k
                if policy == 'triggered':
                    ref = Xi

        labels += spent; compute += rt
        rows.append(dict(window=i, tp=tp, fp=fp, fn=fn, tn=tn,
                         retrained=(spent > 0), retrain_s=rt, labels=spent))

    name = policy
    if policy in ('triggered', 'always_cheap'):
        name = f'{policy}_{budget}'
    return dict(policy=name, per_window=rows, label_cost=labels,
                compute_s=compute, n_retrains=sum(r['retrained'] for r in rows),
                triggers=triggers)


def micro_metrics(rows, mask=None):
    """Micro-averaged recall / precision / FPR / F1 over selected windows."""
    sel = rows if mask is None else [r for r, m in zip(rows, mask) if m]
    tp = sum(r['tp'] for r in sel); fp = sum(r['fp'] for r in sel)
    fn = sum(r['fn'] for r in sel); tn = sum(r['tn'] for r in sel)
    rec = tp / (tp + fn) if (tp + fn) else float('nan')
    prec = tp / (tp + fp) if (tp + fp) else float('nan')
    fpr = fp / (fp + tn) if (fp + tn) else float('nan')
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else float('nan')
    return dict(recall=rec, precision=prec, fpr=fpr, f1=f1,
                tp=tp, fp=fp, fn=fn, tn=tn)
