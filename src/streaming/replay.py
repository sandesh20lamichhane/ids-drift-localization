"""
Stream-replay harness for the Phase-5 operational adaptation study.

Replays a temporally ordered intrusion-detection stream window by window and
evaluates a retraining policy against it. Detection quality is recall on the
attack class per window. This module ships the two bracketing baselines used by
notebook 16 (never-retrain floor, always-retrain ceiling); notebooks 17-20
import StreamReplayHarness and add the KS trigger and label-budgeted policies.

Promoted from notebook 16 so every Phase-5 notebook shares one implementation.
"""
from __future__ import annotations
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score

RF_DEFAULT = dict(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)


def train_detector(X, y, rf_kw=None):
    """Fit a RandomForest attack detector on (X, y)."""
    rf = RandomForestClassifier(**(rf_kw or RF_DEFAULT))
    rf.fit(np.asarray(X), np.asarray(y))
    return rf


def recall_attack(y_true, y_pred):
    """Recall on the attack class (1). NaN when a window has no attacks."""
    y_true = np.asarray(y_true)
    if (y_true == 1).sum() == 0:
        return np.nan
    return recall_score(y_true, y_pred, pos_label=1, zero_division=0)


class StreamReplayHarness:
    """Hold an ordered stream and replay it under a retraining policy.

    Parameters
    ----------
    X_stream, y_stream : array-like
        Feature matrix and binary attack labels for the replay stream, already
        in chronological order.
    windows : list of (start, stop)
        Half-open row-index spans partitioning the stream in order.
    rf_kw : dict, optional
        RandomForest keyword arguments (defaults to RF_DEFAULT).
    """

    def __init__(self, X_stream, y_stream, windows, rf_kw=None):
        self.X = np.asarray(X_stream)
        self.y = np.asarray(y_stream)
        self.windows = list(windows)
        self.rf_kw = rf_kw or RF_DEFAULT

    def _window(self, i):
        a, b = self.windows[i]
        return self.X[a:b], self.y[a:b]

    def replay_never_retrain(self, detector):
        """Floor: one frozen detector scored on every window."""
        out = []
        for i in range(len(self.windows)):
            Xi, yi = self._window(i)
            out.append(recall_attack(yi, detector.predict(Xi)))
        return np.asarray(out, dtype=float)

    def replay_always_retrain(self, detector, buffer_windows=1):
        """Ceiling: before scoring window i, retrain on the most recent
        `buffer_windows` labeled windows (unlimited label budget)."""
        out = []
        current = detector
        for i in range(len(self.windows)):
            if i > 0:
                lo = max(0, i - buffer_windows)
                a = self.windows[lo][0]
                b = self.windows[i][0]
                current = train_detector(self.X[a:b], self.y[a:b], self.rf_kw)
            Xi, yi = self._window(i)
            out.append(recall_attack(yi, current.predict(Xi)))
        return np.asarray(out, dtype=float)
