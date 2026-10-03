# When Does SHAP-Based Drift Localization Beat a Simple Statistical Test?
### A Pre-Registered Evaluation Across Three Intrusion Detection Datasets

Sandesh Lamichhane, Usman Aijaz N
Department of Computer Science and Information Technology,
Yenepoya (Deemed to be University), Bengaluru, India

This repository contains the full pipeline, pre-registration documents and result
files for the paper. Every number in the manuscript traces to a file under
`reports/tables/` or `data/processed/` that a notebook below generates.

Archived release: Zenodo, [10.5281/zenodo.21856844](https://doi.org/10.5281/zenodo.21856844) (v1.0.1).

## What the paper tests
When a deployed IDS degrades under drift, can SHAP-based signals tell an operator
*which features* drifted, better than a label-free per-feature Kolmogorov–Smirnov
(KS) test? We compare KS, a conditional KS baseline, domain-classifier SHAP,
permutation importance, auxiliary-detector SHAP and a dual-model SHAP divergence on
the corrected CICIDS2017, UNSW-NB15 and the corrected CSE-CIC-IDS2018, with random
forest, XGBoost and MLP models. Drift is either real (leave-one-attack-family-out
injection) or planted on real flow vectors, so that the drifted features are known.

## Layout
- `notebooks/` — the pipeline, run in numeric order (Google Colab)
  - `00_setup/` — download, parquet conversion, CSE-CIC-IDS2018 conversion
  - `01_phase0_foundation/` — dataset characterization, frozen-detector baseline
  - `02_phase1_synthetic/` — P(X)-stability check of the concept arm
  - `03_phase1_cicids/` — CICIDS2017 localization, testbed (07e), identifiability (07g, 07h)
  - `04_phase2_multidataset/` — UNSW-NB15 geometry and benchmark
  - `05_phase3_generalization/` — MLP infrastructure, sweep, benchmarks, explainer control
  - `07_phase5_adaptation/` — streaming, triggers, cost (auxiliary study)
  - `08_phase6_cse2018/` — CSE-CIC-IDS2018 geometry, baseline, benchmark, controls
  - `09_revision/` — `28_known_gt_benchmark.ipynb`, planted-ground-truth benchmark
    across all three datasets (revision experiment)
  - `99_paper_figures/` — `15_significance_tests.ipynb` regenerates Table 3
- `src/` — shared helpers (loaders, localization, seeding)
- `reports/tables/`, `data/processed/` — result CSVs and JSON summaries
- `reports/advisor_notes/` — pre-registrations (`PREREG_*.md`), addenda A1–A6,
  decisions log, findings log, data cards
- `tests/` — smoke tests

## Pre-registration
Each experiment's predictions and gates were committed to this repository before it
was run; the commit hash is recorded in the corresponding notebook or addendum. The
revision benchmark is pre-registered in
`reports/advisor_notes/PREREG_known_gt.md`.

## Data
Datasets are **not** redistributed here. `notebooks/00_setup/02_download_data.ipynb`
fetches CICIDS2017 and the corrected releases (Engelen et al., 2021; Liu et al., 2022)
and UNSW-NB15; `05_convert_cse2018.ipynb` converts CSE-CIC-IDS2018.

## Reproduce
Open each notebook in Colab (high-RAM runtime recommended) and run all cells, in
numeric order. Long grids checkpoint their raw CSV and resume after a disconnect.

## License
Code: MIT. Dataset licenses remain with their original distributors.
