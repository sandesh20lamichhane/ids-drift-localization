"""
CSE-CIC-IDS2018 loader — append to src/data/loaders.py (or import from here).

Follows the module's schema contract exactly: every loader returns
(X, y, meta) with meta columns (attack_category, attempted, source_file).
2018 has no Engelen '*-Attempted' annotation unless the corrected (Liu et
al. 2022) release is used; on the original CSVs `attempted` is all-False.

Day ordering is chronological across the ~3-week capture, which is what the
streaming/drift experiments require.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

# Reuse the module-level PROCESSED / _split_features_labels_meta /
# _read_parquet_or_raise from loaders.py when merging this in.

# Chronological capture-day order. Keys are our canonical short names;
# values document the dominant attack activity (for the drift narrative).
CSE2018_DAY_ORDER = [
    'wed_14_02',   # FTP-BruteForce, SSH-Bruteforce          (frozen-training day)
    'thu_15_02',   # DoS GoldenEye, DoS Slowloris
    'fri_16_02',   # DoS SlowHTTPTest, DoS Hulk
    'tue_20_02',   # DDoS LOIC-HTTP, LOIC-UDP  (file has 4 extra ID columns)
    'wed_21_02',   # DDOS HOIC, LOIC-UDP
    'thu_22_02',   # Brute Force -Web / -XSS, SQL Injection
    'fri_23_02',   # Brute Force -Web / -XSS, SQL Injection
    'wed_28_02',   # Infiltration
    'thu_01_03',   # Infiltration
    'fri_02_03',   # Bot
]


def load_cse_cic_ids2018(
    day: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Load CSE-CIC-IDS2018 (harmonized parquet, produced by
    notebooks/00_setup/05_convert_cse2018).

    Args:
        day: one of CSE2018_DAY_ORDER, or None for all days concatenated
             chronologically.

    Returns:
        (X, y, meta) — see module docstring of loaders.py.
    """
    src = PROCESSED / 'cse_cic_ids2018'
    if day is not None:
        day = day.lower()
        if day not in CSE2018_DAY_ORDER:
            raise ValueError(
                f'Unknown day {day!r}; expected one of {CSE2018_DAY_ORDER}'
            )
        df = _read_parquet_or_raise(src / f'{day}.parquet')
        return _split_features_labels_meta(df)

    dfs = []
    for d in CSE2018_DAY_ORDER:
        path = src / f'{d}.parquet'
        if path.exists():
            dfs.append(pd.read_parquet(path))
    if not dfs:
        raise FileNotFoundError(
            f'No CSE-CIC-IDS2018 day files found in {src}. '
            f'Run notebooks/00_setup/05_convert_cse2018 first.'
        )
    df = pd.concat(dfs, ignore_index=True)
    return _split_features_labels_meta(df)


def cse2018_day_stream() -> Iterator[tuple[str, pd.DataFrame, pd.Series, pd.DataFrame]]:
    """Yield CSE-CIC-IDS2018 days chronologically (streaming experiments)."""
    for day in CSE2018_DAY_ORDER:
        try:
            X, y, meta = load_cse_cic_ids2018(day=day)
            yield day, X, y, meta
        except FileNotFoundError:
            continue


# Merge into the registry in loaders.py:
# DATASET_LOADERS['cse_cic_ids2018'] = load_cse_cic_ids2018
