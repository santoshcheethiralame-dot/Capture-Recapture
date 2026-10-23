# E04 SAE arm (PILOT)

K = 8, 200 replicates per level, tau = 0.7, p_split = 0.2, p_absorb = 0.1, |r| = 0.5.

| N_true | clusters / N_true | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |
|---|---|---|---|---|---|---|---|---|
| 1 | 3.405 ± 0.123 | 6.20 | 0.75 | 0.75 | 0.812 | 0.316 | 0.316 | 0 |
| 3 | 3.590 ± 0.076 | 12.78 | 0.72 | 0.72 | 0.748 | 0.351 | 0.352 | 0 |
| 10 | 3.529 ± 0.043 | 31.98 | 0.74 | 0.74 | 0.741 | 0.348 | 0.348 | 0 |

| ID | estimate | verdict |
|---|---|---|
| H4a (N_true = 1) | mean clusters / N_true = 3.405 (MCSE 0.123) | **not supported** |
| H4a (N_true = 3) | mean clusters / N_true = 3.590 (MCSE 0.076) | **not supported** |
| H4a (N_true = 10) | mean clusters / N_true = 3.529 (MCSE 0.043) | **not supported** |
| H4a (pooled) | mean clusters / N_true = 3.508 | **not supported** |
| H4c (N_true = 1) | Chao2 / N_true 6.20 uncorrected, 0.75 corrected | **supported** |
| H4c (N_true = 3) | Chao2 / N_true 12.78 uncorrected, 0.72 corrected | **supported** |
| H4c (N_true = 10) | Chao2 / N_true 31.98 uncorrected, 0.74 corrected | **supported** |
