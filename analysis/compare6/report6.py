import sys,json,random,csv
sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/compare6')
import compare6 as C
D=json.load(open('analysis/compare6/results.json')); rows,S,P,T,rank=D['rows'],D['S'],D['P'],D['T'],D['rank']
names=list(rows); R=C.build_all()
json.dump({'pools':{k:[r['UUID'] for r in p] for k,p in C.POOL.items()},'wood_concrete_composite':[r['UUID'] for r in C.wcc[:1]],
 'ext_wall':{n:{'layers':R[n]['ext']['layers'],'uuids':sorted(set(R[n]['ext']['uuids']))} for n in names}},open('analysis/compare6/sources_uuids.json','w'),indent=1)
# sensitivity: perturb assumption-based indicators
HIGH={'dur_life':1,'dur_events':0,'dur_mfp':1,'dur_adapt':1,'env_a13':0,'env_life':0,'env_pen':0,'env_ren':1,'env_rec':1,'env_waste':0,'wb_voc':1,'wb_mass':1,'wb_buffer':1,'wb_ac':1,'cost_con':0,'cost_maint':0,'cost_op':0}
CRIT={'Durability':['dur_life','dur_events','dur_mfp','dur_adapt'],'Environment':['env_a13','env_life','env_pen','env_ren','env_rec','env_waste'],'Well-being':['wb_voc','wb_mass','wb_buffer','wb_ac'],'Cost':['cost_con','cost_maint','cost_op']}
ASSUMED=['dur_life','dur_mfp','dur_adapt','wb_voc','wb_buffer','cost_con','cost_maint']
def total(r):
    S2={}
    for k,h in HIGH.items():
        v=[r[n][k] for n in names]; lo,hi=min(v),max(v)
        for n in names: S2.setdefault(n,{})[k]=50.0 if hi==lo else (100*(r[n][k]-lo)/(hi-lo) if h else 100*(hi-r[n][k])/(hi-lo))
    return {n:sum(0.25*sum(S2[n][k] for k in ks)/len(ks) for ks in CRIT.values()) for n in names}
random.seed(1); win={n:0 for n in names}; top3={n:0 for n in names}; N=2000
for _ in range(N):
    r={n:dict(rows[n]) for n in names}
    for n in names:
        for k in ('dur_mfp','dur_adapt','wb_voc','wb_buffer'): r[n][k]=min(5,max(1,r[n][k]+random.choice((-1,0,1))))
        r[n]['dur_life']*=random.uniform(0.8,1.2); r[n]['cost_con']*=random.uniform(0.85,1.15); r[n]['cost_maint']*=random.uniform(0.7,1.3)
    t=total(r); o=sorted(names,key=lambda n:-t[n]); win[o[0]]+=1
    for n in o[:3]: top3[n]+=1
# scenarios
def scen(f):
    r={n:dict(rows[n]) for n in names}; f(r); return total(r)
env_only=sorted(names,key=lambda n:rows[n]['env_life'])
neutral=scen(lambda r:[r[n].update(dur_life=90,dur_mfp=3,dur_adapt=3,wb_voc=3,wb_buffer=3,cost_con=870,cost_maint=r[n]['cost_maint']) for n in names])
nocost=scen(lambda r:[r[n].update(cost_con=870) for n in names])
f1=lambda x:f"{x:.1f}"
out=[]
w=out.append
SRC="data/OBD_2024_II_2026-11-07T11_09_31.csv (processed to analysis/products.csv)"
w("# Comparative scoring of six structural systems — 500 m² residential, Germany, 50 years\n")
w("Scope per m² gross floor area (GFA): **structure** (slabs, bearing walls/frame) **+ opaque exterior envelope** (0.6 m² per m² GFA, U = 0.20 W/m²K for every alternative).")
w("Windows, services, partitions, floor finishes and foundations are identical in function and excluded.")
w("Facts come only from the Ökobaudat 2024-II export (`"+SRC+"`).")
w("Everything not in that data set is marked **ASSUMPTION** and listed in section 6.\n")
w("**Read this first:** the data set contains no cost, service-life, VOC, moisture-buffering or fire data.")
w("Only the Environment criterion and two Well-being indicators (thermal mass, acoustic mass) are data-driven.")
w("Durability and Cost, and two Well-being indicators, rest on assumptions. The ranking is therefore a transparent model, not a measured result.\n")
w("## 1. Summary\n")
w("| Rank | Alternative | Durability /25 | Environment /25 | Well-being /25 | Cost /25 | **Total /100** |\n|---|---|---|---|---|---|---|")
for n in sorted(names,key=lambda n:rank[n]): w(f"| {rank[n]} | {n} | {P[n]['Durability']:.1f} | {P[n]['Environment']:.1f} | {P[n]['Well-being']:.1f} | {P[n]['Cost']:.1f} | **{T[n]:.1f}** |")
w("\nFiles: `scores.csv`, `indicators_raw.csv`, `indicators_scored.csv` (comma-separated, `.` decimal).\n")
w("## 2. Score contribution\n")
w("Share = criterion points ÷ total. Largest loss = 25 minus points; the criterion with the biggest loss is shown.\n")
w("| Alternative | Durability | Environment | Well-being | Cost | Costs the most points |\n|---|---|---|---|---|---|")
for n in sorted(names,key=lambda n:rank[n]):
    sh=[100*P[n][c]/T[n] for c in P[n]]; loss=max(P[n],key=lambda c:25-P[n][c])
    w(f"| {n} | {sh[0]:.0f} % | {sh[1]:.0f} % | {sh[2]:.0f} % | {sh[3]:.0f} % | {loss} (−{25-P[n][loss]:.1f}) |")
open('analysis/compare6/report_part1.md','w').write('\n'.join(out))
print('\n'.join(out[-12:]))
print('\nSENS winners',{n[:12]:round(100*win[n]/N) for n in names},'top3',{n[:12]:round(100*top3[n]/N) for n in names})
print('neutral',{n[:3]:round(v,1) for n,v in neutral.items()}); print('nocost',{n[:3]:round(v,1) for n,v in nocost.items()})
json.dump(dict(win={n:win[n]/N for n in names},top3={n:top3[n]/N for n in names},neutral=neutral,nocost=nocost),open('analysis/compare6/sensitivity.json','w'),indent=1)
