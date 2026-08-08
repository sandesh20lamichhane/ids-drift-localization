# Explanation-Space Drift Localization in IDS - Reproduction Package

Companion repository for the papers "When Does SHAP-Based Drift Localization Beat a
Simple Statistical Test?" and "Selectivity Buys Accuracy", and the MSc thesis they
descend from (Sandesh Lamichhane, Yenepoya, 2026).

## Environment
Google Colab (hi-RAM), Python 3.12. `pip install -r requirements.txt`.
Repo root expected at /content/drive/MyDrive/phd_thesis (edit ROOT otherwise).

## Reproduction
1. Data: download CICIDS2017-improved, UNSW-NB15, CSE-CIC-IDS2018-improved from
   official sources (see reports/advisor_notes/data_card_*.md); place under
   data/raw/. Datasets are NOT redistributed here.
2. Run notebooks/00_setup converters (raw->interim->processed parquet).
3. Run notebooks in numeric order per phase. Each experiment asserts its
   pre-registration, logs a decision ID, writes a summary JSON to data/processed/,
   and prints its pre-registered verdict.
4. notebooks/99_paper_figures/15_significance_tests.ipynb regenerates the
   significance table from released raw CSVs.

## Seeds
Global seed 42 (src/utils/seeding). Multi-seed: {42,1,7} localization,
{42,7,123,2024} regime/trigger. Bootstrap: seed 42, 10^4 resamples.

## Map (paper section -> notebooks)
Premise: 06/24 | Dual falsification: 07/10b | Circularity + stability: 07/10b/25 |
Identifiability: 08/09/23 | Cross-model: 13/13b/14 | Third dataset: 05v2/23-25 |
Neural boundary: 25b | Significance: 15v2 | Envelope: 16-19 | Regime: 20-22 |
Trigger hardening: 26 (v1-v3) | Regime under v3: 27.
Pre-registrations and both FAILED predictions: reports/advisor_notes/.

## Credential hygiene
No credentials are stored in this repository; Kaggle authentication is provided
at runtime by the user and saved only to a git-ignored location.
