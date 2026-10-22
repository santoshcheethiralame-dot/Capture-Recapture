import sys, numpy as np
from scipy.optimize import minimize
import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'pilot'))
from estimators import chao2, ichao2, jackknife, darroch_mt
rng=np.random.default_rng(7)
N=2000; R=200
sig=lambda x:1/(1+np.exp(-x))
def fcount(X):
    X=X[X.sum(1)>0]; return X,np.bincount(X.sum(1),minlength=X.shape[1]+1)
# ---------- A. nested / shared-threshold runs (SAE-width-like)
print("== A. nested runs: p_ij = sigmoid(k*(u_i - c_j)), u~N(0,1), c_j spread over [-1,2], K=6. median Nhat/N-1")
for k in (1,3,10,30):
    res={n:[] for n in ("Chao2","JK2","Mt","S/N")}
    for _ in range(R):
        u=rng.standard_normal(N); c=np.linspace(-1,2,6)
        X=(rng.random((N,6))<sig(k*(u[:,None]-c[None,:]))).astype(np.int8)
        X,_=fcount(X)
        res["Chao2"].append(chao2(X)/N-1); res["JK2"].append(jackknife(X,2)/N-1); res["Mt"].append(darroch_mt(X)/N-1); res["S/N"].append(len(X)/N)
    print(f"k={k:2d} "+"  ".join(f"{n}={np.median(v):+.2f}" for n,v in res.items()))
# ---------- B. CI coverage for Chao2 lognormal CI (Chao 1987 form, using bias-corrected f0)
def chao_ci(X):
    X,f=fcount(X); K=X.shape[1]; S=len(X)
    f1,f2=f[1],f[2]; f0=(K-1)/K*f1*(f1-1)/(2*(f2+1))
    if f0<=0: return S,S
    r=f1/(f2+1)
    var=f2*(0.25*r**4+r**3+0.5*r**2) if f2>0 else f1*(f1-1)/2+f1*(2*f1-1)**2/4-f1**4/(4*S)
    var=max(var,1e-9)
    C=np.exp(1.96*np.sqrt(np.log(1+var/f0**2)))
    return S+f0/C,S+f0*C
print("== B. coverage of nominal-95% lognormal Chao CI, target = N vs target = population Chao2 bound")
def popbound(p,K):
    q1=K*p*(1-p)**(K-1); q2=(K*(K-1)/2)*p**2*(1-p)**(K-2); S=(1-(1-p)**K).sum()
    return S+(K-1)/K*q1.sum()**2/(2*q2.sum())
for name,s in (("homog",0.0),("sig=1",1.0),("sig=2",2.0)):
    for K in (3,5,10):
        covN=covB=0;wid=[]
        for _ in range(R):
            p=sig(-1.5+s*rng.standard_normal(N))
            X=(rng.random((N,K))<p[:,None]).astype(np.int8)
            lo,hi=chao_ci(X); b=popbound(p,K)
            covN+=(lo<=N<=hi); covB+=(lo<=b<=hi); wid.append((hi-lo)/N)
        print(f"{name:5s} K={K:2d} cover(N)={covN/R:.2f} cover(bound)={covB/R:.2f} median width/N={np.median(wid):.2f}")
# ---------- C. Huggins/Alho conditional likelihood with a covariate
def huggins(X,z):
    Xs=X[X.sum(1)>0]; zs=z[X.sum(1)>0]; K=X.shape[1]; y=Xs.sum(1)
    def nll(b):
        p=sig(b[0]+b[1]*zs); p=np.clip(p,1e-9,1-1e-9)
        return -np.sum(y*np.log(p)+(K-y)*np.log(1-p)-np.log(1-(1-p)**K))
    b=minimize(nll,[-1,0.1],method="BFGS").x
    p=sig(b[0]+b[1]*zs); return np.sum(1/(1-(1-p)**K))
print("== C. Huggins HT vs Chao2 / JK2: logit p = -2 + 1.5 z + tau*e (z observed covariate, e unobserved), K=5, median Nhat/N-1")
for tau in (0.0,1.0,2.0):
    for K in (3,5):
        hs=[];cs=[];js=[]
        for _ in range(R):
            z=rng.standard_normal(N); p=sig(-2+1.5*z+tau*rng.standard_normal(N))
            X=(rng.random((N,K))<p[:,None]).astype(np.int8)
            try: hs.append(huggins(X,z)/N-1)
            except Exception: pass
            cs.append(chao2(X)/N-1); js.append(jackknife(X,2)/N-1)
        print(f"tau={tau} K={K}: Huggins={np.median(hs):+.2f} Chao2={np.median(cs):+.2f} JK2={np.median(js):+.2f}")
# ---------- C2. covariate heavy-tail: p_i depends on rank via z=log(rank); covariate observed only for caught
print("== C2. Zipf alpha=0.7 with covariate z=log(rank) exactly in the model (logit link misspecified?), K=10")
hs=[];cs=[]
for _ in range(R//2):
    rank=np.arange(1,N+1); p=0.9*rank**(-0.7); z=np.log(rank)
    X=(rng.random((N,10))<p[:,None]).astype(np.int8)
    try: hs.append(huggins(X,z)/N-1)
    except Exception: pass
    cs.append(chao2(X)/N-1)
print(f"Huggins(logit, z=log rank)={np.median(hs):+.2f}  Chao2={np.median(cs):+.2f}")
# ---------- D. ghosts and coverage/extrapolation
def inc_cov(X):
    X,f=fcount(X); K=X.shape[1]; U=X.sum(); f1,f2=f[1],f[2]
    return 1-f1/U*((K-1)*f1/((K-1)*f1+2*f2)) if f1>0 else 1.0
print("== D. ghost (false non-match) rate vs estimated coverage; truth = coverage with no ghosts, lognormal sigma=1, K=6")
for g in (0,0.05,0.15):
    est=[];tru=[]
    for _ in range(R):
        p=sig(-1.5+1.0*rng.standard_normal(N)); X=(rng.random((N,6))<p[:,None]).astype(np.int8)
        seen=X.sum(1)>0; tru.append(p[seen].sum()/p.sum())
        gh=(rng.random(X.shape)<g)&(X==1); X2=X.copy(); X2[gh]=0
        G=np.zeros((gh.sum(),6),dtype=np.int8); G[np.arange(len(G)),np.nonzero(gh)[1]]=1
        est.append(inc_cov(np.vstack([X2,G])))
    print(f"ghost={g:.2f} est coverage={np.mean(est):.3f} true={np.mean(tru):.3f}")
