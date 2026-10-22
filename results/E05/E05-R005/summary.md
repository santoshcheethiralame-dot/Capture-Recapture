# E05-R005 pilot (declared; separate seeds)

320 injections (20 per cell x combination); wall time 39 s on 4 workers. Pilot output: informs feasibility and cost only.

## Cost per injection (seconds, mean)

| Step | mean s | max s |
|---|---|---|
| inject | 0.0018 | 0.0043 |
| b50 | 0.0007 | 0.0027 |
| b200 | 0.0006 | 0.0030 |
| mi | 0.0183 | 0.0483 |
| mi_labelled | 0.0059 | 0.0148 |
| nof1 | 0.1130 | 0.1130 |

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

| cell | f | g | pattern | naive | b (n_v=50) | b (n_v=200) | MI (mixture) | MI (labelled, n_v=200) | nof1 (median) | f̂ (n_v=200) |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 0.1 | 0.0 | uniform | +35% | +1% | +0% | +7% | -0% | -18% | 0.094 |
| base | 0.1 | 0.0 | score | +38% | +2% | +2% | +8% | +1% | -22% | 0.097 |
| base | 0.1 | 0.05 | uniform | +25% | -5% | -6% | +1% | -5% | +8% | 0.087 |
| base | 0.1 | 0.05 | score | +30% | -5% | -5% | +1% | -4% | -25% | 0.092 |
| base | 0.0 | 0.05 | uniform | -6% | -6% | -6% | -26% | -6% | -21% | 0.000 |
| base | 0.0 | 0.05 | score | -6% | -6% | -6% | -25% | -6% | +11% | 0.000 |
| base | 0.3 | 0.0 | uniform | +143% | -1% | +2% | +35% | +5% | -19% | 0.305 |
| base | 0.3 | 0.0 | score | +169% | +13% | +10% | +34% | +8% | -20% | 0.304 |
| ln2 | 0.1 | 0.0 | uniform | +59% | -1% | -1% | +9% | -1% | -39% | 0.100 |
| ln2 | 0.1 | 0.0 | score | +63% | +5% | +3% | +11% | +1% | -39% | 0.095 |
| ln2 | 0.1 | 0.05 | uniform | +48% | -6% | -7% | +3% | -7% | -38% | 0.095 |
| ln2 | 0.1 | 0.05 | score | +57% | -2% | -3% | +8% | -4% | -40% | 0.093 |
| ln2 | 0.0 | 0.05 | uniform | -6% | -6% | -6% | -28% | -6% | -40% | 0.000 |
| ln2 | 0.0 | 0.05 | score | -6% | -6% | -6% | -27% | -6% | -40% | 0.000 |
| ln2 | 0.3 | 0.0 | uniform | +259% | -1% | +3% | +42% | +7% | -29% | 0.301 |
| ln2 | 0.3 | 0.0 | score | +316% | +17% | +18% | +63% | +12% | -43% | 0.299 |
