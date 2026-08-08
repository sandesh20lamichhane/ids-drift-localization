# Data Card — Phase 0 Datasets

**Generated:** 2026-06-04
**Drive root:** `/content/drive/MyDrive/phd_thesis`

## Datasets in scope

### 1. CICIDS2017 (Engelen-improved) — PRIMARY

- **Source:** Kaggle mirror `ernie55ernie/improved-cicids2017-and-csecicids2018`
- **Canonical origin:** Engelen, Rimmer, Joosen (2021), WTMC, Distrinet-KU Leuven
  https://intrusion-detection.distrinet-research.be/WTMC2021/
- **Local path:** `data/raw/cicids2017_improved/CICIDS2017_improved/`
- **Files:** 5 day-named CSVs (monday.csv ... friday.csv)
- **Size:** ~1.1 GB combined
- **Columns:** 91 (original CICIDS2017 had 79–85)
- **Label column:** `Label`
- **Attack-category column:** `Attempted Category` (Engelen-specific)
- **Verified Engelen-signature:** `*-Attempted` labels present, `Attempted Category` column present
- **Citation:**
  Engelen, G., Rimmer, V., Joosen, W. (2021). Troubleshooting an Intrusion
  Detection Dataset: the CICIDS2017 Case Study. IEEE Security and Privacy
  Workshops (SPW), pp. 7–12.
- **Use in thesis:** Phase 1 replication, Phase 2 primary dataset, Phase 3 primary dataset

### 2. CSE-CIC-IDS-2018 (Engelen-improved) — RESERVE

- **Source:** Same Kaggle dataset bundle
- **Local path:** `data/raw/cicids2017_improved/CSECICIDS2018_improved/`
- **Files:** 10 date-named CSVs (Feb 14, 2018 → Mar 2, 2018)
- **Size:** ~34 GB combined
- **Use in thesis:** Reserve for Phase 2 cross-dataset generalization (if needed)

### 3. UNSW-NB15

- **Source:** Kaggle `mrwellsdavid/unsw-nb15`
- **Local path:** `data/raw/unsw_nb15/`
- **Size:** ~605 MB
- **Citation:**
  Moustafa, N., Slay, J. (2015). UNSW-NB15: A Comprehensive Data Set for
  Network Intrusion Detection Systems. MilCIS, IEEE.
- **Use in thesis:** Phase 2 cross-dataset generalization (primary second dataset)

### 4. NSL-KDD

- **Source:** Kaggle `hassan06/nslkdd`
- **Local path:** `data/raw/nsl_kdd/`
- **Size:** ~107 MB
- **Citation:**
  Tavallaee, M., Bagheri, E., Lu, W., Ghorbani, A. A. (2009). A Detailed
  Analysis of the KDD CUP 99 Data Set. IEEE Symposium on Computational
  Intelligence for Security and Defense Applications.
- **Use in thesis:** Pipeline sanity check, debugging on small data

## Known issues / preprocessing required

- All CICIDS-style datasets have `inf` and `NaN` values in some flow-rate columns
  (Flow Bytes/s, Flow Packets/s when duration is zero). Drop or impute before training.
- Class imbalance is severe across all datasets (benign typically >> attack).
- Some columns have leading or trailing whitespace in headers — strip before use.

## Licenses / terms of use

- CICIDS2017: see UNB CIC dataset terms — academic use permitted, citation required
- Engelen improved version: same terms as original, additional Engelen 2021 citation required
- UNSW-NB15: academic use permitted, citation required
- NSL-KDD: open academic use
