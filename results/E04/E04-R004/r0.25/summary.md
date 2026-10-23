# E04 SAE arm (PILOT)

K = 8, 200 replicates per level, tau = 0.7, p_split = 0.2, p_absorb = 0.1, |r| = 0.25.

| N_true | clusters / N_true | without splits | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.250 ± 0.065 | 1.170 | 2.76 | 0.99 | 0.98 | 0.935 | 0.144 | 0.145 | 0 |
| 3 | 2.110 ± 0.035 | 1.188 | 3.56 | 1.21 | 1.22 | 0.894 | 0.137 | 0.136 | 0 |
| 10 | 2.165 ± 0.020 | 1.201 | 7.93 | 1.26 | 1.20 | 0.875 | 0.143 | 0.143 | 0 |

| ID | estimate | verdict |
|---|---|---|
| H4a (N_true = 1) | mean clusters / N_true = 2.250 (MCSE 0.065) | **not supported** |
| H4a (N_true = 3) | mean clusters / N_true = 2.110 (MCSE 0.035) | **not supported** |
| H4a (N_true = 10) | mean clusters / N_true = 2.165 (MCSE 0.020) | **not supported** |
| H4a, freeze option 2 (N_true = 1) | mean clusters / N_true without split latents = 1.170 | **supported** |
| H4a, freeze option 2 (N_true = 3) | mean clusters / N_true without split latents = 1.188 | **supported** |
| H4a, freeze option 2 (N_true = 10) | mean clusters / N_true without split latents = 1.201 | **inconclusive** |
| H4a (pooled) | mean clusters / N_true = 2.175 | **not supported** |
| H4c (N_true = 1) | Chao2 / N_true 2.76 uncorrected, 0.99 corrected | **supported** |
| H4c (N_true = 3) | Chao2 / N_true 3.56 uncorrected, 1.21 corrected | **supported** |
| H4c (N_true = 10) | Chao2 / N_true 7.93 uncorrected, 1.26 corrected | **supported** |
