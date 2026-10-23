# E04 SAE arm (PILOT)

K = 8, 200 replicates per level, tau = 0.7, p_split = 0.2, p_absorb = 0.1, |r| = 0.5.

| N_true | clusters / N_true | without splits | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.355 ± 0.130 | 1.230 | 6.22 | 0.74 | 0.74 | 0.815 | 0.312 | 0.312 | 0 |
| 3 | 3.500 ± 0.080 | 1.187 | 12.30 | 0.76 | 0.75 | 0.756 | 0.340 | 0.340 | 0 |
| 10 | 3.486 ± 0.040 | 1.188 | 30.84 | 0.74 | 0.74 | 0.744 | 0.346 | 0.347 | 0 |

| ID | estimate | verdict |
|---|---|---|
| H4a (N_true = 1) | mean clusters / N_true = 3.355 (MCSE 0.130) | **not supported** |
| H4a (N_true = 3) | mean clusters / N_true = 3.500 (MCSE 0.080) | **not supported** |
| H4a (N_true = 10) | mean clusters / N_true = 3.486 (MCSE 0.040) | **not supported** |
| H4a, freeze option 2 (N_true = 1) | mean clusters / N_true without split latents = 1.230 | **inconclusive** |
| H4a, freeze option 2 (N_true = 3) | mean clusters / N_true without split latents = 1.187 | **supported** |
| H4a, freeze option 2 (N_true = 10) | mean clusters / N_true without split latents = 1.188 | **supported** |
| H4a (pooled) | mean clusters / N_true = 3.447 | **not supported** |
| H4c (N_true = 1) | Chao2 / N_true 6.22 uncorrected, 0.74 corrected | **supported** |
| H4c (N_true = 3) | Chao2 / N_true 12.30 uncorrected, 0.76 corrected | **supported** |
| H4c (N_true = 10) | Chao2 / N_true 30.84 uncorrected, 0.74 corrected | **supported** |
