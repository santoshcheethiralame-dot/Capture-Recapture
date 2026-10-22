# E01-R009 (exploratory): de-adaptation A3a / A3b

500 replicates per cell or arm; wall 5 s.

## Run level: coverage, mean(estimate − C) (MCSE)

| cell | naive Ĉ | A3a | A3b |
|---|---|---|---|
| base | +0.0013 (0.0007) | -0.3020 (0.0015) | +nan (nan) |
| beh0.5 | -0.1478 (0.0010) | -0.4357 (0.0018) | +nan (nan) |
| beh2 | +0.0708 (0.0006) | -0.0818 (0.0009) | +nan (nan) |

## Attempt level: discovery rate of the next attempt, median log(estimate / truth) [10th, 90th pct]

| arm | blind spots found (mean) | Chao (naive) | A3a | A3b |
|---|---|---|---|---|
| non-adaptive | 17.3 | +0.27 [-0.64, +1.60] (n=483) | +1.98 [+1.19, +3.26] (n=483) | +2.17 [+0.72, +3.68] (n=461) |
| adaptive c=3 | 17.3 | -0.48 [-1.54, +0.91] (n=481) | +1.60 [+0.62, +2.86] (n=481) | +2.09 [+0.03, +4.37] (n=449) |
| adaptive c=10 | 17.2 | -0.89 [-1.83, +0.21] (n=489) | +0.61 [-0.32, +2.04] (n=489) | +2.19 [-0.01, +4.83] (n=305) |
