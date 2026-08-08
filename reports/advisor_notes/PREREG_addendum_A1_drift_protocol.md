# PREREG Addendum A1 — CSE-CIC-IDS2018 Drift Protocol

Append to: `reports/advisor_notes/PREREG_cse2018.md`
**Commit BEFORE building or running notebooks 24/25.**
Date: ____________ · Git commit: ____________

## A1.0 Deviation recorded (data fix)

`attempted_category` (improved-release label metadata) was found inside the
feature matrix after Stage 2 conversion; it was excluded from the geometry
math by the Def.-3 screen (degenerate, top_frac 0.995), so notebook 23's
P1/P2 results are unaffected, but it is label-adjacent and must not reach
any detector. Action: added to the Stage-2 drop list; processed parquets
regenerated; notebook 23 re-run. Feature count: 83 → 82.
Logged in the deviations table of the main prereg.

## A1.1 Why 2018 needs its own protocol

CICIDS2017 has one benign day then a cliff; UNSW is a train/test corpus with
constructed streams. CSE-CIC-IDS2018 introduces novel attack families
gradually across nine days after the first. "Drift" must therefore be defined
before evaluation, or the choice of windows becomes a free parameter.

## A1.2 Family taxonomy (fixed)

Known-at-training family (present on the frozen-training day):
- **BruteForce** = {FTP-BruteForce, SSH-Bruteforce}

Novel families (arrive later; drift events):
- **DoS**   = {GoldenEye, Slowloris, SlowHTTPTest, Hulk}   (days thu_15_02, fri_16_02)
- **DDoS**  = {LOIC-HTTP, LOIC-UDP, HOIC}                  (tue_20_02, wed_21_02)
- **Web**   = {BruteForce-Web, BruteForce-XSS, SQL Injection} (thu_22_02, fri_23_02)
- **Infiltration**                                          (wed_28_02, thu_01_03)
- **Bot**                                                   (fri_02_03)

Exact label→family mapping is emitted by notebook 24 from the data card and
frozen as `reports/tables/24_family_map.csv`; any label not covered above is
assigned before, not after, benchmark runs.

## A1.3 Construction 1 — chronological day-stream (G-DRIFT; later Phase-5)

- Reference / frozen-training window: **wed_14_02** (benign + BruteForce).
  The frozen detector may legitimately know BruteForce; drift is defined by
  the arrival of the five novel families, mirroring the CICIDS cold-start.
- Post-drift evaluation: **per-day, multiple transitions** — each of the nine
  subsequent days is scored separately (recall, FPR) for frozen, balanced,
  downsampled, realistic, oracle. No pooling across days for the gate.
- **G-DRIFT (2018):** frozen attack-recall on novel-family flows drops by
  ≥ 0.30 relative to its BruteForce recall on the training day, on at least
  half of the novel-family days; imbalance controls move recall < 0.01.
  Per-family recall is reported for every day.
- Known caveat recorded in advance: Infiltration labels are documented as
  noisy in this corpus; oracle recall on wed_28_02/thu_01_03 may be low for
  label reasons, not drift reasons. Infiltration days therefore cannot by
  themselves decide G-DRIFT in either direction.

## A1.4 Construction 2 — additive leave-one-family-out (G-BENCH, P3–P6)

Identical design to the UNSW replication (thesis §7.7):
- Pre window: benign + BruteForce (from wed_14_02).
- For each novel family F ∈ {DoS, DDoS, Web, Infiltration, Bot}: post window
  = pre composition + injected flows of F (additive; benign base unchanged).
- Ground truth GT_in: per-feature Wasserstein-1 between pre and post windows,
  top-k set (k=10); GT_ex: domain-oracle SHAP (circularity measurement only).
- Localizers, models, seeds, metric, verdict margins: as main prereg §4–5.
- Pairs for significance: family(5) × model(3) × seed(3) = 45 per method
  pair on this dataset; pooled into Table IV.

## A1.5 What is NOT decided by this addendum

Whether the 2018 stream is also used for the Phase-5 adaptation loop
(paper #2, candidate notebook 28) — that gets its own addendum if pursued.

## A1.6 One-line summary for the paper's methods section

"On CSE-CIC-IDS2018 the frozen detector is trained on the first capture day
(benign + brute-force); drift is evaluated per-day against the arrival of
five novel attack families, and localization is benchmarked with the same
additive leave-one-family-out construction and Wasserstein anchor used for
UNSW-NB15, with all windows and gates fixed in this pre-registered addendum."
