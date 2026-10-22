N = 2000, 200 replicates. Cells show median N_hat/N - 1.

### 1. Heterogeneous catchability (logit-normal, mean p about 0.2)

| Scenario | Seen (S/N) | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|
| sigma=0.0, K=2 | 33% | -1% | +0% | -1% | n/a | -52% | -52% |
| sigma=0.0, K=5 | 63% | -1% | -0% | -0% | +1% | -4% | +12% |
| sigma=0.0, K=10 | 87% | +0% | +0% | -0% | +0% | +13% | +16% |
| sigma=1.0, K=2 | 37% | -33% | -33% | -33% | n/a | -48% | -48% |
| sigma=1.0, K=5 | 62% | -33% | -25% | -17% | -12% | -13% | -3% |
| sigma=1.0, K=10 | 79% | -33% | -17% | -8% | -5% | +0% | +5% |
| sigma=2.0, K=2 | 41% | -48% | -48% | -48% | n/a | -46% | -46% |
| sigma=2.0, K=5 | 59% | -48% | -39% | -28% | -26% | -25% | -18% |
| sigma=2.0, K=10 | 71% | -48% | -29% | -18% | -16% | -14% | -9% |

### 2. Heavy tail (Zipf-like catchability, p_i = 0.9 i^-alpha)

| Scenario | Seen (S/N) | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|
| alpha=0.5, K=5 | 17% | -58% | -44% | -31% | -27% | -71% | -62% |
| alpha=0.5, K=10 | 30% | -58% | -36% | -19% | -9% | -49% | -33% |
| alpha=0.5, K=20 | 49% | -57% | -27% | -9% | +1% | -21% | -2% |
| alpha=1.0, K=5 | 1% | -99% | -97% | -95% | -95% | -98% | -97% |
| alpha=1.0, K=10 | 3% | -99% | -95% | -89% | -89% | -95% | -94% |
| alpha=1.0, K=20 | 5% | -99% | -93% | -83% | -81% | -92% | -89% |

### 3. Dependent catchers (K=6, family-shared effects, tau=1.5)

| Scenario | Seen (S/N) | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|
| 1 family | 64% | -45% | -33% | -22% | -19% | -17% | -10% |
| 2 families | 73% | -8% | -19% | -13% | -10% | -5% | +2% |
| 3 families | 77% | -8% | -13% | -9% | -6% | +1% | +7% |
| 6 families | 81% | -7% | -4% | -2% | +1% | +9% | +16% |

### 4. Identity errors (K=6, sigma=1)

| Scenario | Seen (S/N) | Chapman (2 occ.) | Mt (Darroch) | Chao2 | iChao2 | Jackknife-1 | Jackknife-2 |
|---|---|---|---|---|---|---|---|
| ghosts=0%, merges=0% | 67% | -33% | -24% | -14% | -10% | -9% | +1% |
| ghosts=5%, merges=0% | 72% | -26% | -14% | +1% | +8% | +2% | +17% |
| ghosts=15%, merges=0% | 82% | -8% | +11% | +43% | +55% | +24% | +49% |
| ghosts=0%, merges=5% | 64% | -36% | -27% | -18% | -14% | -13% | -4% |
| ghosts=0%, merges=15% | 60% | -43% | -34% | -26% | -22% | -20% | -13% |
