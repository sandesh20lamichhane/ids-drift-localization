# When Does SHAP-Based Drift Localization Beat a Simple Statistical Test?
### A Pre-Registered Evaluation Across Three Intrusion Detection Datasets

Sandesh Lamichhane, Usman Aijaz N
Department of Computer Science and Information Technology,
Yenepoya (Deemed to be University), Bengaluru, India

This repository contains the full pipeline, pre-registration documents and result
files for the paper. Every number in the manuscript traces to a file under
`reports/tables/` or `data/processed/` that a notebook below generates; the map
further down says which.

Archived on Zenodo: [10.5281/zenodo.21856843](https://doi.org/10.5281/zenodo.21856843)
(this DOI always resolves to the latest version). Release v1.1.0 is the version that
accompanies the revised paper and includes the revision benchmark
(`notebooks/09_revision/`); v1.0.1 ([10.5281/zenodo.21856844](https://doi.org/10.5281/zenodo.21856844))
is the earlier submission snapshot.

## What the paper tests
When a deployed IDS degrades under drift, can SHAP-based signals tell an operator
*which features* drifted, better than a label-free per-feature Kolmogorov–Smirnov
(KS) test? We compare KS, a conditional KS baseline, domain-classifier SHAP,
permutation importance, auxiliary-detector SHAP and a dual-model SHAP divergence on
the corrected CICIDS2017, UNSW-NB15 and the corrected CSE-CIC-IDS2018, with random
forest, XGBoost and MLP models. Drift is either real (leave-one-attack-family-out
injection, or the dated attack days of CICIDS2017) or planted on real flow vectors,
so that the drifted features are known.

## Where each result in the paper comes from

| Paper element | Notebook | Output files |
|---|---|---|
| Fig. 1, P(X) stability of the concept arm | `02_phase1_synthetic/f001_pxstability_check` | `data/processed/f001_pxstability.json` |
| Fig. 2, drift premise (recall collapse) | `01_phase0_foundation/06_baseline_rf_per_day` | `reports/tables/06_baseline_metrics.csv`, `phase1_06_baseline.json` |
| Sec. 4.2, planted ground truth (CICIDS2017 testbed) | `03_phase1_cicids/07e_drift_regime_testbed` | `phase1_07e_regime_testbed.json` |
| Sec. 4.2, planted ground truth (three datasets, pre-registered) | `09_revision/28_known_gt_benchmark` | `28_known_gt_raw.csv`, `28_known_gt_summary.csv`, `28_known_gt_tests.csv` |
| Fig. 3, dual vs. auxiliary SHAP | `03_phase1_cicids/07_localization_dual_shap` | `07_localization_raw.csv`, `phase1_07_localization.json` |
| Fig. 4, ground-truth modality | `03_phase1_cicids/07c_ks_vs_shap_localization` | `phase1_07c_ks_vs_shap.json` |
| Fig. 5, instability vs. disagreement | `03_phase1_cicids/07d_disagreement_stability` | `phase1_07d_disagreement.json` |
| Fig. 6, identifiability under redundancy | `03_phase1_cicids/07g_decorrelated_limit`, `07h_degeneracy_diagnostic`, `05_phase3_generalization/12_mlp_identifiability_sweep` | `phase1_07g_*.json`, `phase1_07h_*.json`, `phase3_12_*.json` |
| Redundancy geometry table (Sec. 4.6) | `07h_degeneracy_diagnostic` (CICIDS2017), `04_phase2_multidataset/09_unsw_geometry_localization`, `08_phase6_cse2018/23_cse2018_geometry` | `phase1_07h_*.json`, `phase2_09_unsw_geometry.json`, `phase6_23_cse2018_geometry.json` |
| Cross-model benchmark table (Sec. 4.7) | `04_phase2_multidataset/10b_drift_localization_benchmark`, `05_phase3_generalization/13_mlp_unsw_benchmark`, `14_mlp_cicids_benchmark`, `08_phase6_cse2018/25_cse2018_benchmark` | `13_mlp_unsw_model_summary.csv`, `14_cicids_raw.csv`, `25_cse2018_model_summary.csv` |
| Figs. 7–8, UNSW-NB15 and CSE-CIC-IDS2018 benchmarks | `13_mlp_unsw_benchmark`, `25_cse2018_benchmark` | `reports/figures/13_*.pdf`, `reports/figures/25_*.pdf` |
| Fig. 9, CSE-CIC-IDS2018 redundancy | `23_cse2018_geometry` | `reports/figures/23_cse2018_redundancy_hist.pdf` |
| Fig. 10, explainer control and drift marginality | `05_phase3_generalization/13b_explainer_control`, `08_phase6_cse2018/25b_cse2018_explainer_control` | `phase3_13b_*.json`, `phase6_25b_*.json` |
| Significance table (Sec. 4.10) | `99_paper_figures/15b_significance_tests_three_datasets` | `15_significance_tabsig.csv`, `15_significance_pairs.csv`, `15_tabsig.tex` |
| Significance table, Holm-adjusted p column | `99_paper_figures/15c_holm_correction.py` | `15_significance_tabsig_holm.csv` |

Tables are under `reports/tables/`, JSON summaries under `data/processed/`, figures
under `reports/figures/`. Figure and section numbers follow the revised manuscript.

## Layout
- `notebooks/` — the pipeline, run in numeric order (Google Colab)
  - `00_setup/` — download, parquet conversion, CSE-CIC-IDS2018 conversion
  - `01_phase0_foundation/` — dataset characterization, frozen-detector baseline
  - `02_phase1_synthetic/` — P(X)-stability check of the concept arm
  - `03_phase1_cicids/` — CICIDS2017 localization, testbed (07e), identifiability (07g, 07h)
  - `04_phase2_multidataset/` — UNSW-NB15 geometry and benchmark
  - `05_phase3_generalization/` — MLP infrastructure, sweep, benchmarks, explainer control
  - `07_phase5_adaptation/` — streaming, triggers, cost. Thesis material, not used in the paper.
  - `08_phase6_cse2018/` — CSE-CIC-IDS2018 geometry, baseline, benchmark, controls
    (notebooks 26–27 here are thesis material, not used in the paper)
  - `09_revision/` — `28_known_gt_benchmark.ipynb`, planted-ground-truth benchmark
    across all three datasets (revision experiment)
  - `99_paper_figures/` — significance tests. `15_significance_tests` is the
    earlier two-dataset version; `15b_significance_tests_three_datasets` produces
    the significance table; `15c_holm_correction.py` adds its Holm column.
- `src/` — shared helpers (loaders, localization, seeding)
- `reports/tables/`, `data/processed/` — result CSVs and JSON summaries
- `reports/figures/` — every figure, PDF and PNG
- `reports/advisor_notes/` — pre-registrations (`PREREG_*.md`), addenda A1–A6,
  decisions log, findings log, data cards
- `tests/` — smoke tests

## Pre-registration
Each experiment's predictions and gates were committed to this repository before it
was run; the commit hash is recorded in the corresponding notebook or addendum. The
revision benchmark is pre-registered in `reports/advisor_notes/PREREG_known_gt.md`
at commit `431365b`, before notebook 28 was run. The executed notebook differs from
the committed one only in the line that records that hash.

## Data
Datasets are **not** redistributed here and remain subject to their distributors'
terms. `notebooks/00_setup/02_download_data.ipynb` fetches CICIDS2017 and the
corrected releases (Engelen et al., 2021; Liu et al., 2022) and UNSW-NB15;
`05_convert_cse2018.ipynb` converts CSE-CIC-IDS2018.

## Reproduce
The notebooks were run on Google Colab (high-RAM runtime) with this repository placed
at `/content/drive/MyDrive/phd_thesis`:

```python
from google.colab import drive
drive.mount('/content/drive')
!git clone https://github.com/sandesh20lamichhane/ids-drift-localization /content/drive/MyDrive/phd_thesis
%cd /content/drive/MyDrive/phd_thesis
!pip install -q -r requirements.txt
```

Then open each notebook and run all cells, in numeric order. Long grids checkpoint
their raw CSV and resume after a disconnect.

The helpers in `src/` read the root from the `THESIS_ROOT` environment variable when
it is set, so the result files can also be inspected outside Colab:

```bash
pip install -r requirements.txt pytest
THESIS_ROOT=$PWD python -m pytest tests
python notebooks/99_paper_figures/15c_holm_correction.py   # recomputes the Holm column
```

## License
Code: MIT (see `LICENSE`). Dataset licenses remain with their original distributors.
