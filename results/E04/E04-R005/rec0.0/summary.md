# E04 SAE arm (PILOT)

K = 8, 200 replicates per level, tau = 0.7, p_split = 0.2, p_absorb = 0.1, |r| = 0.5, split recurrence = 0.0.

| N_true | clusters / N_true | without splits | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.630 ± 0.129 | 1.150 | 6.96 | 0.70 | 0.70 | 0.789 | 0.343 | 0.343 | 0 |
| 3 | 3.573 ± 0.077 | 1.172 | 12.69 | 0.73 | 0.73 | 0.748 | 0.355 | 0.355 | 0 |
| 10 | 3.586 ± 0.041 | 1.192 | 33.18 | 0.72 | 0.73 | 0.735 | 0.359 | 0.358 | 0 |

| ID | estimate | verdict |
|---|---|---|
| H4a (N_true = 1) | mean clusters / N_true = 3.630 (MCSE 0.129) | **not supported** |
| H4a (N_true = 3) | mean clusters / N_true = 3.573 (MCSE 0.077) | **not supported** |
| H4a (N_true = 10) | mean clusters / N_true = 3.586 (MCSE 0.041) | **not supported** |
| H4a, freeze option 2 (N_true = 1) | mean clusters / N_true without split latents = 1.150 | **supported** |
| H4a, freeze option 2 (N_true = 3) | mean clusters / N_true without split latents = 1.172 | **supported** |
| H4a, freeze option 2 (N_true = 10) | mean clusters / N_true without split latents = 1.192 | **supported** |
| H4a (pooled) | mean clusters / N_true = 3.596 | **not supported** |
| H4c (N_true = 1) | Chao2 / N_true 6.96 uncorrected, 0.70 corrected | **supported** |
| H4c (N_true = 3) | Chao2 / N_true 12.69 uncorrected, 0.73 corrected | **supported** |
| H4c (N_true = 10) | Chao2 / N_true 33.18 uncorrected, 0.72 corrected | **supported** |
