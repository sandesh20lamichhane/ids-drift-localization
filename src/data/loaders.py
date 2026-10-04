"""
Unified dataset loaders for the thesis.

All loaders return a consistent tuple: (X, y, meta) where
    X    : pd.DataFrame of features (float32 / int32, no NaN)
    y    : pd.Series of binary labels (int8, 0=benign, 1=attack)
    meta : pd.DataFrame with auxiliary columns
           - attack_category : categorical, granular attack name
           - attempted       : bool, True for Engelen `*-Attempted` flows
           - source_file     : categorical, origin filename

Loaders read from `data/processed/` (Parquet, fast). If you need raw or
interim data, read directly from those directories — that's a deliberate
escape hatch, not part of the regular API.

Example:
    from src.data.loaders import load_cicids2017, cicids2017_day_stream

    X, y, meta = load_cicids2017()                    # all 5 days concatenated
    X_wed, y_wed, meta_wed = load_cicids2017(day='wednesday')

    for day_name, X, y, meta in cicids2017_day_stream():
        # Streaming experiments iterate days in chronological order
        ...
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

# -----------------------------------------------------------------------------
# Paths

THESIS_ROOT = Path(os.environ.get('THESIS_ROOT', '/content/drive/MyDrive/phd_thesis'))
PROCESSED = THESIS_ROOT / 'data' / 'processed'

# CICIDS2017 weekday order for streaming experiments (chronological).
# Monday is benign-only, used as a "pre-drift" baseline. Drift begins Tuesday
# (brute force), peaks Wednesday (DoS), continues Thursday (Web/Infiltration),
# ends Friday (Botnet + DDoS). This ordering matters for the drift narrative.
CICIDS2017_DAY_ORDER = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

# Columns that are NOT features (the schema contract from conversion).
META_COLUMNS = ('label', 'attack_category', 'attempted', 'source_file')

# Columns that must end up as `category` dtype after a load.
# pd.concat demotes categoricals to object — we re-cast in
# _split_features_labels_meta to enforce the schema contract.
CATEGORICAL_META_COLUMNS = ('attack_category', 'source_file')


# -----------------------------------------------------------------------------
# Internal helpers

def _split_features_labels_meta(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Split a processed DataFrame into (X, y, meta) per the schema contract.

    Raises:
        ValueError: if any contract column is missing.
    """
    missing = [c for c in META_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f'Processed dataset is missing contract columns {missing}. '
            f'Did stage-2 conversion complete? Columns present: {list(df.columns)[:20]}'
        )
    feature_cols = [c for c in df.columns if c not in META_COLUMNS]
    X = df[feature_cols].copy()
    y = df['label'].astype('int8').copy()
    meta = df[list(META_COLUMNS[1:])].copy()  # exclude label, include the rest

    # Restore categorical dtype — pd.concat (in load_*() below) demotes
    # categoricals to object when concatenating multiple parquet files.
    # We re-cast here to enforce the schema contract on every return.
    for col in CATEGORICAL_META_COLUMNS:
        if col in meta.columns and not isinstance(meta[col].dtype, pd.CategoricalDtype):
            meta[col] = meta[col].astype('category')

    return X, y, meta


def _read_parquet_or_raise(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f'Parquet not found: {path}\n'
            f'Run notebooks/00_setup/03_csv_to_parquet.ipynb to generate.'
        )
    return pd.read_parquet(path)


# -----------------------------------------------------------------------------
# CICIDS2017 (Engelen-improved) — PRIMARY DATASET

def load_cicids2017(
    day: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Load CICIDS2017 (Engelen-improved).

    Args:
        day: One of {'monday','tuesday','wednesday','thursday','friday'},
             or None to load all five days concatenated in chronological order.

    Returns:
        (X, y, meta) — see module docstring.
    """
    src = PROCESSED / 'cicids2017'
    if day is not None:
        day = day.lower()
        if day not in CICIDS2017_DAY_ORDER:
            raise ValueError(
                f'Unknown day {day!r}; expected one of {CICIDS2017_DAY_ORDER}'
            )
        df = _read_parquet_or_raise(src / f'{day}.parquet')
        return _split_features_labels_meta(df)

    # Load all days in chronological order
    dfs = []
    for d in CICIDS2017_DAY_ORDER:
        path = src / f'{d}.parquet'
        if path.exists():
            dfs.append(pd.read_parquet(path))
    if not dfs:
        raise FileNotFoundError(
            f'No CICIDS2017 day files found in {src}. '
            f'Run notebooks/00_setup/03_csv_to_parquet.ipynb first.'
        )
    df = pd.concat(dfs, ignore_index=True)
    return _split_features_labels_meta(df)


def cicids2017_day_stream() -> Iterator[tuple[str, pd.DataFrame, pd.Series, pd.DataFrame]]:
    """
    Yield CICIDS2017 days in chronological order, one at a time.

    Use for streaming/drift experiments — each iteration is one "batch period."

    Yields:
        (day_name, X, y, meta) tuples in Monday → Friday order.
    """
    for day in CICIDS2017_DAY_ORDER:
        try:
            X, y, meta = load_cicids2017(day=day)
            yield day, X, y, meta
        except FileNotFoundError:
            # Skip missing days rather than erroring — useful during development
            continue


# -----------------------------------------------------------------------------
# UNSW-NB15

def load_unsw_nb15(
    partition: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Load UNSW-NB15.

    Args:
        partition: 'train', 'test', or None for both concatenated.

    Returns:
        (X, y, meta) — see module docstring. `meta['source_file']`
        identifies which partition each row came from.
    """
    src = PROCESSED / 'unsw_nb15'
    files = sorted(src.glob('*.parquet'))
    if not files:
        raise FileNotFoundError(
            f'No UNSW-NB15 parquet files in {src}. '
            f'Run notebooks/00_setup/03_csv_to_parquet.ipynb first.'
        )

    if partition is not None:
        partition = partition.lower()
        if partition not in ('train', 'test'):
            raise ValueError(f"partition must be 'train', 'test', or None")
        matching = [f for f in files if partition in f.name.lower() or
                    ('training' in f.name.lower() and partition == 'train') or
                    ('testing' in f.name.lower() and partition == 'test')]
        if not matching:
            raise FileNotFoundError(
                f'No UNSW {partition!r} partition found. Available: {[f.name for f in files]}'
            )
        df = pd.concat([pd.read_parquet(f) for f in matching], ignore_index=True)
    else:
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    return _split_features_labels_meta(df)


# -----------------------------------------------------------------------------
# NSL-KDD

def load_nsl_kdd(
    partition: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Load NSL-KDD.

    Args:
        partition: 'train', 'test', or None for both concatenated.

    Returns:
        (X, y, meta) — see module docstring.
    """
    src = PROCESSED / 'nsl_kdd'
    files = sorted(src.glob('*.parquet'))
    if not files:
        raise FileNotFoundError(
            f'No NSL-KDD parquet files in {src}. '
            f'Run notebooks/00_setup/03_csv_to_parquet.ipynb first.'
        )

    if partition is not None:
        partition = partition.lower()
        if partition not in ('train', 'test'):
            raise ValueError(f"partition must be 'train', 'test', or None")
        # KDDTrain+ / KDDTest+ naming
        keyword = 'train' if partition == 'train' else 'test'
        matching = [f for f in files if keyword in f.name.lower()]
        if not matching:
            raise FileNotFoundError(
                f'No NSL-KDD {partition!r} partition found. Available: {[f.name for f in files]}'
            )
        df = pd.concat([pd.read_parquet(f) for f in matching], ignore_index=True)
    else:
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    return _split_features_labels_meta(df)


# -----------------------------------------------------------------------------
# CSE-CIC-IDS2018 (improved) — THIRD DATASET (Phase 6)

# Chronological capture-day order (2018-02-14 ... 2018-03-02). Dominant attack
# activity noted for the drift narrative; wed_14_02 (FTP/SSH brute force +
# benign) is the frozen-training day, mirroring the CICIDS2017 cold-start design.
CSE2018_DAY_ORDER = [
    'wed_14_02',   # FTP-BruteForce, SSH-Bruteforce  (frozen-training day)
    'thu_15_02',   # DoS GoldenEye, DoS Slowloris
    'fri_16_02',   # DoS SlowHTTPTest, DoS Hulk
    'tue_20_02',   # DDoS LOIC-HTTP, LOIC-UDP
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
    Load CSE-CIC-IDS2018 (improved release), harmonized parquet produced by
    notebooks/00_setup/05_convert_cse2018.ipynb.

    Args:
        day: one of CSE2018_DAY_ORDER, or None for all ten days concatenated
             in chronological order.

    Returns:
        (X, y, meta) — see module docstring.
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

    # Load all days in chronological order
    dfs = []
    for d in CSE2018_DAY_ORDER:
        path = src / f'{d}.parquet'
        if path.exists():
            dfs.append(pd.read_parquet(path))
    if not dfs:
        raise FileNotFoundError(
            f'No CSE-CIC-IDS2018 day files found in {src}. '
            f'Run notebooks/00_setup/05_convert_cse2018.ipynb first.'
        )
    df = pd.concat(dfs, ignore_index=True)
    return _split_features_labels_meta(df)


def cse2018_day_stream() -> Iterator[tuple[str, pd.DataFrame, pd.Series, pd.DataFrame]]:
    """
    Yield CSE-CIC-IDS2018 days in chronological order, one at a time.

    Use for streaming/drift experiments — each iteration is one "batch period."

    Yields:
        (day_name, X, y, meta) tuples in wed_14_02 -> fri_02_03 order.
    """
    for day in CSE2018_DAY_ORDER:
        try:
            X, y, meta = load_cse_cic_ids2018(day=day)
            yield day, X, y, meta
        except FileNotFoundError:
            # Skip missing days rather than erroring — useful during development
            continue


# -----------------------------------------------------------------------------
# Dataset registry — for code that needs to iterate over datasets generically

DATASET_LOADERS = {
    'cicids2017': load_cicids2017,
    'unsw_nb15': load_unsw_nb15,
    'nsl_kdd': load_nsl_kdd,
    'cse_cic_ids2018': load_cse_cic_ids2018,
}


def load_dataset(
    name: str,
    **kwargs,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Generic loader by name. Useful for config-driven experiment scripts.

    Example:
        X, y, meta = load_dataset('cicids2017', day='wednesday')
    """
    if name not in DATASET_LOADERS:
        raise ValueError(
            f'Unknown dataset {name!r}. Available: {list(DATASET_LOADERS)}'
        )
    return DATASET_LOADERS[name](**kwargs)
