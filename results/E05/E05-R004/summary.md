# E05-R004 pilot (declared; separate seeds)

320 injections (20 per cell x combination); wall time 40 s on 4 workers. Pilot output: informs feasibility and cost only.

## Cost per injection (seconds, mean)

| Step | mean s | max s |
|---|---|---|
| inject | 0.0018 | 0.0055 |
| b50 | 0.0007 | 0.0015 |
| b200 | 0.0006 | 0.0037 |
| mi | 0.0185 | 0.0479 |
| nof1 | 0.1206 | 0.1206 |

## Failures (non-finite estimates)

| Estimate | failures |
|---|---|
| naive_chao2 | 0 / 320 |
| b50_chao2 | 0 / 320 |
| b200_chao2 | 0 / 320 |
| mi_chao2 | 0 / 320 |
| nof1 | 0 / 320 |
| naive_lp | 0 / 320 |
| b200_lp | 0 / 320 |
| f200_dct | 0 / 320 |

## Pilot bias of Chao2 relative to the oracle Chao2 (mean of est/oracle − 1)

| cell | f | g | pattern | naive | b (n_v=50) | b (n_v=200) | MI | nof1 | f̂ (n_v=200) |
|---|---|---|---|---|---|---|---|---|---|
| base | 0.1 | 0.0 | uniform | +35% | +1% | +0% | +7% | +151% | 0.094 |
| base | 0.1 | 0.0 | score | +38% | +2% | +2% | +8% | +181% | 0.097 |
| base | 0.1 | 0.05 | uniform | +25% | -5% | -6% | +1% | +40868% | 0.087 |
| base | 0.1 | 0.05 | score | +30% | -5% | -5% | +1% | +4% | 0.092 |
| base | 0.0 | 0.05 | uniform | -6% | -6% | -6% | -26% | -6% | 0.000 |
| base | 0.0 | 0.05 | score | -6% | -6% | -6% | -25% | +102% | 0.000 |
| base | 0.3 | 0.0 | uniform | +143% | -1% | +2% | +35% | +366% | 0.305 |
| base | 0.3 | 0.0 | score | +169% | +13% | +10% | +34% | +1871% | 0.304 |
| ln2 | 0.1 | 0.0 | uniform | +59% | -1% | -1% | +9% | +18% | 0.100 |
| ln2 | 0.1 | 0.0 | score | +63% | +5% | +3% | +11% | +21% | 0.095 |
| ln2 | 0.1 | 0.05 | uniform | +48% | -6% | -7% | +3% | +3% | 0.095 |
| ln2 | 0.1 | 0.05 | score | +57% | -2% | -3% | +8% | +14% | 0.093 |
| ln2 | 0.0 | 0.05 | uniform | -6% | -6% | -6% | -28% | -27% | 0.000 |
| ln2 | 0.0 | 0.05 | score | -6% | -6% | -6% | -27% | +279% | 0.000 |
| ln2 | 0.3 | 0.0 | uniform | +259% | -1% | +3% | +42% | +42% | 0.301 |
| ln2 | 0.3 | 0.0 | score | +316% | +17% | +18% | +63% | -29% | 0.299 |
