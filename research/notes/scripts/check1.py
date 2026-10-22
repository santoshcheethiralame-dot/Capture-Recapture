import sys, numpy as np
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'pilot'))
from estimators import chao2, ichao2, jackknife, chapman
rng=np.random.default_rng(1)
N=2000
def cap(p,K): return (rng.random((len(p),K))<p[:,None]).astype(np.int8)
def lognorm(sig,mu=-1.5): return 1/(1+np.exp(-(mu+sig*rng.standard_normal(N))))
def zipf(a): return 0.9*np.arange(1,N+1)**(-a)
# --- 1. estimable target: population Chao lower bound (expected f's) vs N
def pop_bound(p,K):
    q1=K*p*(1-p)**(K-1); q2=(K*(K-1)/2)*p**2*(1-p)**(K-2)
    S=1-(1-p)**K
    f1,f2,S=q1.sum(),q2.sum(),S.sum()
    return S+(K-1)/K*f1**2/(2*f2), S
print("== population-level Chao2 lower bound (no sampling noise), N=2000")
for name,p in [("lognorm s=1",lognorm(1.0)),("lognorm s=2",lognorm(2.0)),("zipf a=.5",zipf(.5)),("zipf a=1",zipf(1.0))]:
    for K in (5,10,20):
        b,S=pop_bound(p,K); print(f"{name:12s} K={K:2d} S/N={S/N:.2f} bound/N={b/N:.2f}")
# --- 2. coverage and extrapolation, zipf alpha=1 and lognorm s=2
def inc_cov(X):
    X=X[X.sum(1)>0]; K=X.shape[1]; f=np.bincount(X.sum(1),minlength=K+1); U=X.sum()
    f1,f2=f[1],f[2]
    return 1-f1/U*((K-1)*f1/((K-1)*f1+2*f2)) if (f1>0) else 1.0
def true_cov(p,seen,K):
    # fraction of detection mass (prob. a random capture belongs to seen) -- incidence-weighted
    w=K*p*(1-p)**(K-1)  # not used
    return p[seen].sum()/p.sum()
print("== sample coverage (incidence, Chao-Jost) vs true detection-mass coverage")
for name,p in [("lognorm s=2",lognorm(2.0)),("zipf a=.5",zipf(.5)),("zipf a=1",zipf(1.0))]:
    for K in (5,10):
        est=[];tru=[]
        for _ in range(100):
            X=cap(p,K); seen=X.sum(1)>0
            est.append(inc_cov(X)); tru.append(true_cov(p,seen,K))
        print(f"{name:12s} K={K:2d} est={np.mean(est):.3f} true={np.mean(tru):.3f}")
# --- 3. extrapolation: new items found when going from K to 2K (and to 3K), truth vs Chao-style extrapolation (Chao2 + coverage form)
def extrap(X,m):
    X=X[X.sum(1)>0]; K=X.shape[1]; S=len(X); f=np.bincount(X.sum(1),minlength=K+1)
    f0=(K-1)/K*f[1]*(f[1]-1)/(2*(f[2]+1))
    if f[1]==0 or f0<=0: return S
    return S+f0*(1-(1-f[1]/(K*f0+f[1]))**m)  # Chao 2014 Eq. (incidence): f0[1-(1-Q1/(T Q0+Q1))^(t)]
print("== predicted vs true new items seen when adding K more runs (zipf/lognorm)")
for name,p in [("lognorm s=2",lognorm(2.0)),("zipf a=.5",zipf(.5)),("zipf a=1",zipf(1.0))]:
    for K in (5,10):
        tru=[];pre=[]
        for _ in range(100):
            X=cap(p,2*K); seen_a=X[:,:K].sum(1)>0; seen_b=X.sum(1)>0
            tru.append(seen_b.sum()-seen_a.sum())
            pre.append(extrap(X[:,:K],K)-seen_a.sum())
        print(f"{name:12s} K={K:2d}->{2*K}: true new={np.mean(tru):7.1f} predicted={np.mean(pre):7.1f}")
