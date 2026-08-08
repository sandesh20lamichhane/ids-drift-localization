"""
KS drift monitor for the Phase-5 operational adaptation study (Objective 5).

A label-free monitor: it compares each incoming window's feature marginals to a
fixed reference (a held-out half of the detector's training distribution) with
the two-sample Kolmogorov-Smirnov statistic, aggregates to a per-window drift
score (mean KS across features), and fires when the score exceeds a
reference-calibrated threshold tau = mu_null + k * sigma_null (a k-sigma
control-chart rule). No labels are used by the monitor; labels enter only when
its triggers are scored against novel-family onsets in the notebook.

Promoted from notebook 17 so notebook 18 drives retraining from one trigger.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import ks_2samp


def per_feature_ks(reference, window):
    """Per-feature two-sample KS statistics (reference vs window)."""
    R = np.asarray(reference)
    W = np.asarray(window)
    out = np.empty(R.shape[1], dtype=float)
    for j in range(R.shape[1]):
        out[j] = ks_2samp(R[:, j], W[:, j]).statistic
    return np.nan_to_num(out)


class KSMonitor:
    """Label-free KS drift monitor with a reference-calibrated trigger."""

    def __init__(self, reference):
        self.reference = np.asarray(reference)
        self.tau = None
        self.calibration = None

    def drift_score(self, window):
        """Window drift score = mean per-feature KS vs the reference."""
        ks = per_feature_ks(self.reference, window)
        return float(ks.mean()), ks

    def calibrate(self, cal_windows, k=3.0):
        """Set tau from in-distribution windows: tau = mu + k * sigma."""
        scores = [self.drift_score(cw)[0] for cw in cal_windows]
        mu = float(np.mean(scores))
        sd = float(np.std(scores))
        self.tau = mu + k * sd
        self.calibration = dict(mu=mu, sd=sd, k=k, tau=self.tau,
                                null_scores=[float(s) for s in scores])
        return self.calibration

    def fired(self, score):
        if self.tau is None:
            raise RuntimeError('call calibrate() before fired()')
        return bool(score > self.tau)
