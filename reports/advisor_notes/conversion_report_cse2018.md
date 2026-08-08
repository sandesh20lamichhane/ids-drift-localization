# CSE-CIC-IDS2018 (improved) — Data Card & Conversion Report (v2)
Generated: 2026-07-07T16:31:18

## Version note (A1.0)
- v2 regeneration: `attempted_category` (improved-release label metadata) added to the leakage drop list after it was found in the v1 feature matrix. Feature count 83 -> 82. See PREREG Addendum A1.0.

## Provenance
- Source: improved/corrected CSE-CIC-IDS2018 release (Engelen-group format, matching our CICIDS2017_improved).
- Location: `/content/drive/MyDrive/phd_thesis/data/raw/cicids2017_improved/CSECICIDS2018_improved`

## Pre-registered decisions (PREREG_cse2018.md)
- Per-day cap: 1,500,000 rows, stratified by attack_category, seed 42.
- Binary label: BENIGN -> 0; all attacks incl. `*- Attempted` -> 1 (identical to notebook 03 rule for CICIDS2017).
- Leakage columns dropped: flow_id, src_ip, dst_ip, source_ip, destination_ip, src_port, dst_port, source_port, destination_port, timestamp, id, srcip, dstip, sport, dsport, stime, ltime, attempted_category.
- inf -> NaN -> row dropped; features float32.

## Schema check vs CICIDS2017
- shared features: 82
- 2018-only: []
- 2017-only: []

## Per-day composition
| day       |   flows |   attack_rate |   attack_categories |
|:----------|--------:|--------------:|--------------------:|
| wed_14_02 | 1500000 |         0.049 |                   2 |
| thu_15_02 | 1499999 |         0.007 |                   2 |
| fri_16_02 | 1500000 |         0.258 |                   2 |
| tue_20_02 | 1500000 |         0.048 |                   2 |
| wed_21_02 | 1500000 |         0.156 |                   2 |
| thu_22_02 | 1500001 |         0     |                   3 |
| fri_23_02 | 1500000 |         0     |                   3 |
| wed_28_02 | 1500000 |         0.008 |                   3 |
| thu_01_03 | 1500001 |         0.006 |                   3 |
| fri_02_03 | 1500000 |         0.023 |                   1 |

### wed_14_02
- rows_in: 5,898,350 | nan-dropped: 1 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1426873, 'FTP-BruteForce': 49172, 'SSH-BruteForce': 23955}

### thu_15_02
- rows_in: 5,410,102 | nan-dropped: 14 | rows_out: 1,499,999 | features: 82
- categories: {'BENIGN': 1489566, 'DoS GoldenEye': 7447, 'DoS Slowloris': 2986}

### fri_16_02
- rows_in: 7,390,266 | nan-dropped: 8 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1112578, 'DoS Hulk': 366005, 'FTP-BruteForce': 21417}

### tue_20_02
- rows_in: 6,054,702 | nan-dropped: 8 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1428104, 'DDoS-LOIC-HTTP': 71679, 'DDoS-LOIC-UDP': 217}

### wed_21_02
- rows_in: 6,962,593 | nan-dropped: 6 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1266424, 'DDoS-HOIC': 233166, 'DDoS-LOIC-UDP': 410}

### thu_22_02
- rows_in: 6,071,153 | nan-dropped: 2 | rows_out: 1,500,001 | features: 82
- categories: {'BENIGN': 1499949, 'Web Attack - Brute Force': 36, 'Web Attack - XSS': 11, 'Web Attack - SQL': 5}

### fri_23_02
- rows_in: 5,976,481 | nan-dropped: 4 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1499942, 'Web Attack - Brute Force': 31, 'Web Attack - XSS': 19, 'Web Attack - SQL': 8}

### wed_28_02
- rows_in: 6,568,726 | nan-dropped: 4 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1488618, 'Infiltration - NMAP Portscan': 11358, 'Infiltration - Dropbox Download': 14, 'Infiltration - Communication Victim Attacker': 10}

### thu_01_03
- rows_in: 6,551,401 | nan-dropped: 7 | rows_out: 1,500,001 | features: 82
- categories: {'BENIGN': 1490877, 'Infiltration - NMAP Portscan': 9075, 'Infiltration - Communication Victim Attacker': 37, 'Infiltration - Dropbox Download': 12}

### fri_02_03
- rows_in: 6,311,371 | nan-dropped: 3 | rows_out: 1,500,000 | features: 82
- categories: {'BENIGN': 1465970, 'Botnet Ares': 34030}
