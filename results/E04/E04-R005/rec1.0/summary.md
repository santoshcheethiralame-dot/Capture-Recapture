# E04 SAE arm (PILOT)

K = 8, 200 replicates per level, tau = 0.7, p_split = 0.2, p_absorb = 0.1, |r| = 0.5, split recurrence = 1.0.

| N_true | clusters / N_true | without splits | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.385 ± 0.057 | 1.145 | 2.55 | 1.53 | 1.53 | 0.971 | 0.286 | 0.286 | 0 |
| 3 | 2.383 ± 0.032 | 1.168 | 3.03 | 1.32 | 1.31 | 0.941 | 0.283 | 0.283 | 0 |
| 10 | 2.396 ± 0.017 | 1.178 | 3.33 | 1.21 | 1.20 | 0.939 | 0.287 | 0.289 | 0 |

| ID | estimate | verdict |
|---|---|---|
| H4a (N_true = 1) | mean clusters / N_true = 2.385 (MCSE 0.057) | **not supported** |
| H4a (N_true = 3) | mean clusters / N_true = 2.383 (MCSE 0.032) | **not supported** |
| H4a (N_true = 10) | mean clusters / N_true = 2.396 (MCSE 0.017) | **not supported** |
| H4a, freeze option 2 (N_true = 1) | mean clusters / N_true without split latents = 1.145 | **supported** |
| H4a, freeze option 2 (N_true = 3) | mean clusters / N_true without split latents = 1.168 | **supported** |
| H4a, freeze option 2 (N_true = 10) | mean clusters / N_true without split latents = 1.178 | **supported** |
| H4a (pooled) | mean clusters / N_true = 2.388 | **not supported** |
| H4c (N_true = 1) | Chao2 / N_true 2.55 uncorrected, 1.53 corrected | **inconclusive** |
| H4c (N_true = 3) | Chao2 / N_true 3.03 uncorrected, 1.32 corrected | **supported** |
| H4c (N_true = 10) | Chao2 / N_true 3.33 uncorrected, 1.21 corrected | **supported** |
