# E04 SAE arm (PILOT)

K = 8, 200 replicates per level, tau = 0.7, p_split = 0.2, p_absorb = 0.1, |r| = 0.5, split recurrence = 0.5.

| N_true | clusters / N_true | without splits | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.210 ± 0.119 | 1.190 | 5.12 | 0.91 | 0.91 | 0.863 | 0.335 | 0.335 | 0 |
| 3 | 3.288 ± 0.066 | 1.198 | 8.70 | 0.88 | 0.87 | 0.806 | 0.338 | 0.339 | 0 |
| 10 | 3.261 ± 0.036 | 1.194 | 14.08 | 0.83 | 0.82 | 0.803 | 0.344 | 0.346 | 0 |

| ID | estimate | verdict |
|---|---|---|
| H4a (N_true = 1) | mean clusters / N_true = 3.210 (MCSE 0.119) | **not supported** |
| H4a (N_true = 3) | mean clusters / N_true = 3.288 (MCSE 0.066) | **not supported** |
| H4a (N_true = 10) | mean clusters / N_true = 3.261 (MCSE 0.036) | **not supported** |
| H4a, freeze option 2 (N_true = 1) | mean clusters / N_true without split latents = 1.190 | **supported** |
| H4a, freeze option 2 (N_true = 3) | mean clusters / N_true without split latents = 1.198 | **supported** |
| H4a, freeze option 2 (N_true = 10) | mean clusters / N_true without split latents = 1.194 | **supported** |
| H4a (pooled) | mean clusters / N_true = 3.253 | **not supported** |
| H4c (N_true = 1) | Chao2 / N_true 5.12 uncorrected, 0.91 corrected | **supported** |
| H4c (N_true = 3) | Chao2 / N_true 8.70 uncorrected, 0.88 corrected | **supported** |
| H4c (N_true = 10) | Chao2 / N_true 14.08 uncorrected, 0.83 corrected | **supported** |
