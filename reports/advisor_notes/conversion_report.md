# CSV → Parquet Conversion Report
Generated: 2026-06-04T12:08:53
## Conversion decisions
- **Binary label encoding:** BENIGN/Normal → 0, all attacks (including Engelen `*-Attempted` variants) → 1. The granular category is preserved in `attack_category`; the attempted flag is preserved in `attempted`.
- **Leakage columns dropped from processed:** Flow ID, Src/Dst IP, Src/Dst Port, Timestamp, ID, and UNSW equivalents (srcip, dstip, sport, dsport, stime, ltime). These are session identifiers that would let a model memorize specific flows.
- **NaN handling:** rows with any NaN in feature columns are dropped. `inf` values are converted to NaN first (then dropped).
- **Dtype:** float64 -> float32, int64 -> int32 where safe. Categorical strings encoded as int32 codes.
- **Schema contract (every processed file):** features as float32/int32, `label` int8 {0,1}, `attack_category` categorical, `attempted` bool, `source_file` categorical.

## cicids2017_interim

### friday.csv
- rows: 547557
- cols: 92
- csv_mb: 271.98
- parquet_mb: 90.92

### monday.csv
- rows: 371624
- cols: 92
- csv_mb: 198.25
- parquet_mb: 72.66

### thursday.csv
- rows: 362076
- cols: 92
- csv_mb: 180.74
- parquet_mb: 63.45

### tuesday.csv
- rows: 322078
- cols: 92
- csv_mb: 170.13
- parquet_mb: 62.93

### wednesday.csv
- rows: 496641
- cols: 92
- csv_mb: 277.80
- parquet_mb: 89.35

## cicids2017_processed

### friday.parquet
- rows_in: 547557
- rows_out: 547557
- rows_dropped_nan: 0
- parquet_mb: 62.28
- class_balance:
    - `0`: 288544
    - `1`: 259013
- attack_categories:
    - `BENIGN`: 288544
    - `Portscan`: 159066
    - `DDoS`: 95144
    - `Botnet`: 4803

### monday.parquet
- rows_in: 371624
- rows_out: 371621
- rows_dropped_nan: 3
- parquet_mb: 49.13
- class_balance:
    - `0`: 371621
- attack_categories:
    - `BENIGN`: 371621

### thursday.parquet
- rows_in: 362076
- rows_out: 362075
- rows_dropped_nan: 1
- parquet_mb: 42.63
- class_balance:
    - `0`: 288171
    - `1`: 73904
- attack_categories:
    - `BENIGN`: 288171
    - `Infiltration - Portscan`: 71767
    - `Web Attack - Brute Force`: 1365
    - `Web Attack - XSS`: 673
    - `Infiltration`: 81
    - `Web Attack - SQL Injection`: 18

### tuesday.parquet
- rows_in: 322078
- rows_out: 322078
- rows_dropped_nan: 0
- parquet_mb: 42.45
- class_balance:
    - `0`: 315106
    - `1`: 6972
- attack_categories:
    - `BENIGN`: 315106
    - `FTP-Patator`: 3984
    - `SSH-Patator`: 2988

### wednesday.parquet
- rows_in: 496641
- rows_out: 496640
- rows_dropped_nan: 1
- parquet_mb: 61.98
- class_balance:
    - `0`: 319119
    - `1`: 177521
- attack_categories:
    - `BENIGN`: 319119
    - `DoS Hulk`: 159049
    - `DoS GoldenEye`: 7647
    - `DoS Slowloris`: 5706
    - `DoS Slowhttptest`: 5108
    - `Heartbleed`: 11

## unsw_nb15

### UNSW_NB15_training-set.csv
- rows_out: 82332
- parquet_mb: 4.63
- class_balance:
    - `1`: 45332
    - `0`: 37000
- attack_categories:
    - `Normal`: 37000
    - `Generic`: 18871
    - `Exploits`: 11132
    - `Fuzzers`: 6062
    - `DoS`: 4089
    - `Reconnaissance`: 3496
    - `Analysis`: 677
    - `Backdoor`: 583
    - `Shellcode`: 378
    - `Worms`: 44

### UNSW_NB15_testing-set.csv
- rows_out: 175341
- parquet_mb: 9.87
- class_balance:
    - `1`: 119341
    - `0`: 56000
- attack_categories:
    - `Normal`: 56000
    - `Generic`: 40000
    - `Exploits`: 33393
    - `Fuzzers`: 18184
    - `DoS`: 12264
    - `Reconnaissance`: 10491
    - `Analysis`: 2000
    - `Backdoor`: 1746
    - `Shellcode`: 1133
    - `Worms`: 130

## nsl_kdd

### KDDTrain+.txt
- rows_out: 125973
- parquet_mb: 2.21
- class_balance:
    - `0`: 67343
    - `1`: 58630
- attack_categories:
    - `Normal`: 67343
    - `neptune`: 41214
    - `satan`: 3633
    - `ipsweep`: 3599
    - `portsweep`: 2931
    - `smurf`: 2646
    - `nmap`: 1493
    - `back`: 956
    - `teardrop`: 892
    - `warezclient`: 890
    - `pod`: 201
    - `guess_passwd`: 53
    - `buffer_overflow`: 30
    - `warezmaster`: 20
    - `land`: 18
    - `imap`: 11
    - `rootkit`: 10
    - `loadmodule`: 9
    - `ftp_write`: 8
    - `multihop`: 7

### KDDTest+.txt
- rows_out: 22544
- parquet_mb: 0.45
- class_balance:
    - `1`: 12833
    - `0`: 9711
- attack_categories:
    - `Normal`: 9711
    - `neptune`: 4657
    - `guess_passwd`: 1231
    - `mscan`: 996
    - `warezmaster`: 944
    - `apache2`: 737
    - `satan`: 735
    - `processtable`: 685
    - `smurf`: 665
    - `back`: 359
    - `snmpguess`: 331
    - `saint`: 319
    - `mailbomb`: 293
    - `snmpgetattack`: 178
    - `portsweep`: 157
    - `ipsweep`: 141
    - `httptunnel`: 133
    - `nmap`: 73
    - `pod`: 41
    - `buffer_overflow`: 20
