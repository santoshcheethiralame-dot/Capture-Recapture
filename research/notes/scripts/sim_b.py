import numpy as np
from scipy.optimize import linear_sum_assignment
rng=np.random.default_rng(2)
def chao1(c):
    f1=(c==1).sum(); f2=(c==2).sum(); S=len(c)
    return S+(f1*f1/(2*f2) if f2>0 else f1*(f1-1)/2)
def unit(x): return x/np.linalg.norm(x,axis=1,keepdims=True)
def sim(N=400,d=64,K=5,sigma=0.35,reps=20,taus=(0.3,0.5,0.6,0.7,0.8,0.9),dens=0.0):
    res={t:[] for t in taus}; truth_S=[]
    for _ in range(reps):
        # correlated true features (superposition-like): add shared component to raise confusability
        base=rng.standard_normal((N,d)); shared=rng.standard_normal((1,d))
        T=unit(base+dens*shared*3)
        p=rng.beta(2,3,N)
        runs=[]
        for k in range(K):
            idx=np.nonzero(rng.random(N)<p)[0]
            est=unit(T[idx]+sigma*rng.standard_normal((len(idx),d))/np.sqrt(d)*np.sqrt(d)/np.sqrt(d)*1.0)
            runs.append((idx,est))
        truth_S.append(len(set(np.concatenate([r[0] for r in runs]))))
        for tau in taus:
            # union-find over all detections
            offs=np.cumsum([0]+[len(r[0]) for r in runs]); M=offs[-1]
            par=np.arange(M)
            def find(x):
                while par[x]!=x:
                    par[x]=par[par[x]]; x=par[x]
                return x
            for a in range(K):
                for b in range(a+1,K):
                    C=runs[a][1]@runs[b][1].T
                    r,c=linear_sum_assignment(-C)
                    for i,j in zip(r,c):
                        if C[i,j]>=tau:
                            ra,rb=find(offs[a]+i),find(offs[b]+j)
                            if ra!=rb: par[ra]=rb
            roots=np.array([find(x) for x in range(M)])
            _,cnt=np.unique(roots,return_counts=True)
            res[tau].append((len(cnt),chao1(cnt)))
    print(f"N={N} d={d} sigma={sigma} dens={dens}: mean true #discovered={np.mean(truth_S):.0f}")
    for tau in taus:
        a=np.array(res[tau]); print(f"  tau={tau:.2f}: clusters={a[:,0].mean():.0f}  Chao1={a[:,1].mean():.0f}")
sim(sigma=0.5)
sim(sigma=1.0)
sim(sigma=1.0,dens=0.7)
