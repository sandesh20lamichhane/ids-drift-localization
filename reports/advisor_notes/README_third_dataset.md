# Third Dataset (CSE-CIC-IDS2018 improved) — File Placement & Workflow

Goes in: `reports/advisor_notes/README_third_dataset.md`

Good news discovered in your tree: the data is **already downloaded** and it is
the **improved/corrected release** (`CSECICIDS2018_improved/`, same
Engelen-group format as your `CICIDS2017_improved/`). No download step; the
prereg version box is pre-ticked.

---

## 1. Where every file goes

| File (delivered)              | Destination in your repo                                   |
|-------------------------------|------------------------------------------------------------|
| `PREREG_cse2018.md`           | `reports/advisor_notes/PREREG_cse2018.md`                  |
| `05_convert_cse2018.ipynb`    | `notebooks/00_setup/05_convert_cse2018.ipynb`              |
| `23_cse2018_geometry.ipynb`   | `notebooks/08_phase6_cse2018/23_cse2018_geometry.ipynb` (new folder) |
| `loaders_cse2018.py`          | NOT a standalone file — paste its two functions + registry line into `src/data/loaders.py` (repo rule 1: logic lives in src/, notebooks orchestrate) |
| `README_third_dataset.md`     | `reports/advisor_notes/README_third_dataset.md` (this file) |

New folder to create: `notebooks/08_phase6_cse2018/` — keeps your phase
numbering intact (06_phase4_mechanism and 07_phase5_adaptation exist; this is
Phase 6). Notebooks 24 and 25 will live here too (see §4).

## 2. Run order

1. **Commit the prereg first.** Fill date + `git rev-parse HEAD` into
   `PREREG_cse2018.md`, commit. Everything downstream cites this commit.
2. Merge the loader block into `src/data/loaders.py`
   (+ `DATASET_LOADERS['cse_cic_ids2018'] = load_cse_cic_ids2018`).
   Add one contract test to `tests/test_smoke.py` (template in §5).
3. Run `notebooks/00_setup/05_convert_cse2018.ipynb` top to bottom.
   - **Section 4 is the safety gate**: it diff-checks the harmonized 2018
     schema against your real processed 2017 schema and *asserts* if any 2017
     feature is missing. Do not comment the assert out; fix the mapping.
   - Expect ~30–60 min on Colab (chunked reads; the big days are several GB).
4. Run `notebooks/08_phase6_cse2018/23_cse2018_geometry.ipynb`.
   Its Section 6 verdict routes you:
   - `UNREACHABLE-REGIME-CONFIRMED` → proceed to §4 below (notebooks 24, 25).
   - `DECORRELATED-TARGET-REACHABLE` → STOP; prereg addendum for the
     C4-promotion experiment first (this is the more exciting branch).

## 3. Documentation produced (what lands where)

Inside the notebooks (markdown cells): purpose, prereg linkage, per-cell
rationale, and the decision rules — same style as your existing notebooks.

MD/CSV/JSON artifacts written automatically on run:

| Artifact | Path | Role |
|---|---|---|
| Data card + conversion report | `reports/advisor_notes/data_card_cse2018.md` (+ `conversion_report_cse2018.md/.json`) | audit trail; cite in thesis Ch. 4 |
| Per-day composition table | `reports/tables/23_cse2018_composition.csv` | paper Table I analog for 2018 |
| Geometry row (gate output) | `data/processed/phase6_23_cse2018_geometry.json` + `reports/tables/23_cse2018_geometry.csv` | P1/P2 verdicts, leakage floor |
| Three-dataset geometry table | `reports/tables/23_three_dataset_geometry.csv` | extends `09_unsw_vs_cicids_geometry.csv` |
| Redundancy histogram | `reports/figures/23_cse2018_redundancy_hist.{png,pdf}` | thesis/paper figure |
| Findings-log entries | `reports/advisor_notes/findings_log.md` | via `log_finding` stubs (last cell of each notebook — fill numbers, uncomment, run) |

## 4. Next notebooks (build after the geometry verdict)

- `notebooks/08_phase6_cse2018/24_cse2018_baseline.ipynb` — clone of
  `01_phase0_foundation/06_baseline_rf_per_day.ipynb` with
  `load_dataset('cse_cic_ids2018')`, frozen-training day `wed_14_02`,
  imbalance controls, per-day recall → **G-DRIFT gate**.
- `notebooks/08_phase6_cse2018/25_cse2018_benchmark.ipynb` — clone of
  `04_phase2_multidataset/10b` + `05_phase3_generalization/13/14`:
  additive leave-one-family-out streams over families {DoS, DDoS, Web,
  Infiltration, Bot}; localizers KS / domain-SHAP / dual / permutation /
  random; RF + XGB + MLP; seeds {42, 1, 7}; Wasserstein anchor → **G-BENCH,
  P3–P6**. Outputs feed `99_paper_figures/15_significance_tests.ipynb`
  (pairs grow from n=18 to ~33).

## 5. Small housekeeping in the same pass

- `tests/test_smoke.py` — add:
  ```python
  def test_cse2018_contract():
      from src.data.loaders import load_dataset
      X, y, meta = load_dataset('cse_cic_ids2018', day='wed_14_02')
      assert set(meta.columns) == {'attack_category', 'attempted', 'source_file'}
      assert y.dtype == 'int8' and not X.isna().any().any()
  ```
- Delete/rotate `.kaggle/kaggle.json` (API credential in the repo).
- `thesis/PROJECT_RECOR.md`, `PROJECT_RECORD(1..7).md` — keep only the latest,
  archive the rest outside the repo (they will confuse a repo reviewer).
- Optional: add `__pycache__/` to `.gitignore` if not already effective.

## 6. Paper-edit checklist (after notebook 25 passes its gates)

- Abstract + §I: "two benchmark datasets" → "three benchmark datasets".
- Table I: add 2018 composition (from `23_cse2018_composition.csv`).
- §IV-E paragraph: add the 2018 geometry sentence (from the geometry row).
- Tables II/III: new row-block; Table IV: pooled significance re-run.
- Table V (claims map): add 2018 to C2/C3 evidence.
- Threats to validity: all three datasets share the flow-feature paradigm;
  packet/sequence representations remain future work.
