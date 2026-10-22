N = 2000, 200 replicates. Cells show median N_hat/N - 1.
'Chao2 bound' is Chao2 computed from expected frequency counts with no
sampling noise: the most Chao2 can deliver. Blank where it does not apply.

### 1. Heterogeneous catchability (logit-normal, mean p about 0.2)

| Scenario | Seen (S/N) | Chao2 bound | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|---|
| sigma=0.0, K=2 | 33% |  | -0% | +1% | -0% | n/a | -52% | -52% |
| sigma=0.0, K=5 | 64% | -0% | -1% | +1% | -0% | +2% | -4% | +12% |
| sigma=0.0, K=10 | 87% | +0% | -1% | +0% | +0% | +0% | +13% | +16% |
| sigma=1.0, K=2 | 37% |  | -33% | -33% | -33% | n/a | -48% | -48% |
| sigma=1.0, K=5 | 62% | -17% | -33% | -25% | -17% | -12% | -14% | -3% |
| sigma=1.0, K=10 | 79% | -8% | -33% | -17% | -8% | -4% | +0% | +6% |
| sigma=2.0, K=2 | 41% |  | -48% | -48% | -48% | n/a | -46% | -46% |
| sigma=2.0, K=5 | 59% | -29% | -49% | -38% | -28% | -26% | -25% | -18% |
| sigma=2.0, K=10 | 71% | -19% | -48% | -29% | -18% | -15% | -14% | -8% |

### 2. Heavy tail (Zipf-like catchability, p_i = 0.9 i^-alpha)

| Scenario | Seen (S/N) | Chao2 bound | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|---|
| alpha=0.5, K=5 | 17% | -30% | -57% | -44% | -30% | -25% | -71% | -62% |
| alpha=0.5, K=10 | 30% | -18% | -59% | -36% | -19% | -9% | -48% | -33% |
| alpha=0.5, K=20 | 49% | -9% | -57% | -26% | -10% | -1% | -21% | -2% |
| alpha=1.0, K=5 | 1% | -93% | -99% | -97% | -95% | -95% | -98% | -97% |
| alpha=1.0, K=10 | 3% | -88% | -99% | -95% | -89% | -88% | -95% | -94% |
| alpha=1.0, K=20 | 5% | -80% | -99% | -93% | -82% | -81% | -92% | -89% |

### 3. Catcher families (K=6, family-shared individual effects, tau=1.5)

| Scenario | Seen (S/N) | Chao2 bound | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|---|
| 1 family | 64% |  | -45% | -33% | -21% | -19% | -17% | -10% |
| 2 families | 73% |  | -6% | -19% | -13% | -10% | -5% | +2% |
| 3 families | 77% |  | -7% | -13% | -9% | -6% | +1% | +7% |
| 6 families | 81% |  | -6% | -4% | -2% | +0% | +9% | +16% |

### 4. Identity errors (K=6, sigma=1)

| Scenario | Seen (S/N) | Chao2 bound | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|---|
| ghosts=0%, merges=0% | 67% |  | -33% | -23% | -14% | -10% | -9% | +1% |
| ghosts=5%, merges=0% | 72% |  | -26% | -14% | +1% | +8% | +2% | +16% |
| ghosts=15%, merges=0% | 82% |  | -8% | +10% | +42% | +53% | +24% | +48% |
| ghosts=0%, merges=5% | 64% |  | -37% | -27% | -18% | -14% | -13% | -4% |
| ghosts=0%, merges=15% | 60% |  | -42% | -33% | -26% | -23% | -20% | -13% |

### 5. Coverage and short-range extrapolation (100 replicates)

Coverage = share of total detection mass held by individuals already seen.
'New items' = individuals first seen when K more runs are added.

| Scenario | Seen (S/N) | Coverage (est.) | Coverage (true) | New items (true) | New items (pred.) |
|---|---|---|---|---|---|
| logit-normal sigma=2, K=5 | 59% | 0.895 | 0.890 | 230 | 186 |
| logit-normal sigma=2, K=10 | 71% | 0.951 | 0.950 | 191 | 162 |
| Zipf alpha=0.5, K=5 | 17% | 0.278 | 0.276 | 261 | 256 |
| Zipf alpha=0.5, K=10 | 30% | 0.424 | 0.427 | 379 | 375 |
| Zipf alpha=1, K=5 | 1% | 0.351 | 0.331 | 24 | 21 |
| Zipf alpha=1, K=10 | 3% | 0.424 | 0.414 | 39 | 37 |
