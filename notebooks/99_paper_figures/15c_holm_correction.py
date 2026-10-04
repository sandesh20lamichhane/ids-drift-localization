"""Holm-adjusted p-values for the significance table (tab:sig) of the paper.

Reads the ten paired comparisons written by 15b_significance_tests_three_datasets.ipynb
(reports/tables/15_significance_tabsig.csv) and adds the Holm step-down correction
across all ten Wilcoxon p-values. Runs anywhere, no Colab or Drive needed:

    python notebooks/99_paper_figures/15c_holm_correction.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / 'reports' / 'tables'
ALPHA = 0.05


def holm(p):
    """Holm step-down adjusted p-values, returned in the input order."""
    p = np.asarray(p, dtype=float)
    m = len(p)
    adjusted = np.empty(m)
    running = 0.0
    for rank, i in enumerate(np.argsort(p)):
        running = max(running, (m - rank) * p[i])
        adjusted[i] = min(1.0, running)
    return adjusted


def main():
    tab = pd.read_csv(TABLES / '15_significance_tabsig.csv')
    tab['p_holm'] = holm(tab['p'])
    tab['significant_holm'] = tab['p_holm'] < ALPHA
    out = TABLES / '15_significance_tabsig_holm.csv'
    tab.to_csv(out, index=False)
    print(tab[['comparison', 'n', 'delta', 'p', 'p_holm', 'significant_holm']]
          .to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print(f'\nsaved {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
