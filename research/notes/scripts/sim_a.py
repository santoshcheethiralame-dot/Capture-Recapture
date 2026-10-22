import numpy as np
rng=np.random.default_rng(1)
def chao1(counts):
    f1=(counts==1).sum(); f2=(counts==2).sum(); S=len(counts)
    return S+(f1*f1/(2*f2) if f2>0 else f1*(f1-1)/2)
def run(N=500,K=5,f=0.0,g=0.0,het=True,reps=300):
    out=[]
    for _ in range(reps):
        p=rng.beta(2,3,N) if het else np.full(N,0.4)
        D=rng.random((K,N))<p      # detections
        # sequential linking
        clusters=[]  # list of sets of run indices? track per cluster capture count & which individual id
        cl_of={}  # individual -> list of cluster ids
        cl_count=[]
        for k in range(K):
            for i in np.nonzero(D[k])[0]:
                if g>0 and len(cl_count)>0 and rng.random()<g:
                    c=rng.integers(len(cl_count)); cl_count[c]+=1; continue
                if i in cl_of and rng.random()>=f:
                    c=cl_of[i][rng.integers(len(cl_of[i]))]; cl_count[c]+=1
                else:
                    cl_of.setdefault(i,[]).append(len(cl_count)); cl_count.append(1)
        cnt=np.array(cl_count)
        # note: one cluster may be hit by >1 detection in same run via false match; ok
        # LP on runs 1,2 only: do separate linking for 2 runs
        n1=D[0].sum(); n2=D[1].sum()
        m_true=(D[0]&D[1]).sum()
        m_obs=0
        for i in np.nonzero(D[0]&D[1])[0]:
            if rng.random()>=f: m_obs+=1
        # false matches add spurious links among non-overlapping pairs: expected g*n1*n2/(N) approx ~ g*n2*(n1-m)/ (n1) ... approximate: each run2 detection not truly matched falsely joins a run1 cluster w.p. g
        extra=rng.binomial(n2-m_true, g) if g>0 else 0
        m=m_obs+extra
        lp=n1*n2/max(m,1)
        out.append((len(cnt),chao1(cnt),lp,chao1(cnt) ))
    a=np.array(out); return a[:,0].mean(),a[:,1].mean(),a[:,2].mean()
print("N=500, K=5, heterogeneous p~Beta(2,3). cols: observed clusters, Chao1, LP(2 runs)")
for f in [0,0.05,0.1,0.2,0.3]:
    r=run(f=f); print(f"false-non-match f={f:.2f}: S_obs={r[0]:.0f} Chao1={r[1]:.0f} LP={r[2]:.0f}")
for g in [0.01,0.02,0.05,0.1]:
    r=run(g=g); print(f"false-match g={g:.2f}: S_obs={r[0]:.0f} Chao1={r[1]:.0f} LP={r[2]:.0f}")
print("homogeneous p=0.4")
for f in [0,0.1]:
    r=run(f=f,het=False); print(f"f={f}: S_obs={r[0]:.0f} Chao1={r[1]:.0f} LP={r[2]:.0f}")
