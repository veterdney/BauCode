import sys,csv,json
sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/compare6')
import compare6 as C
R=C.build_all(); names=list(R)
# ---- ASSUMPTIONS (not in OBD) ----
A={ # name: life_y, moist_fire_pest(1-5), adapt(1-5), voc(1-5), moisture_buffer(1-5), cost_construction EUR/m2GFA
 names[0]:(100,5,2,4,1,820),
 names[1]:(80,4,5,4,2,880),
 names[2]:(100,5,2,5,3,790),
 names[3]:(80,4,3,3,4,940),
 names[4]:(80,3,4,3,5,980),
 names[5]:(60,2,5,4,5,900)}
UNIT={'Interior paint/wall covering':12,'Mineral render/plaster':65,'Wood fibre insulation':70,'Rock wool insulation':70,'EPS insulation':70,'Gypsum plasterboard':35}  # EUR per m2 wall per renewal, ASSUMPTION
rows={}
for n,v in R.items():
    e,s=v['ext'],v['struct']
    tot={k:e[k]+s[k] for k in C.KEYS}
    ev=e['events']; nev=len(ev)
    maint=sum(UNIT.get(l,0) for l,y in ev)*C.EW
    # layers renewed with the render share the 40-y cycle already counted
    life_gwp=tot['a13']+tot['c']
    ind={
     'dur_life':A[n][0],'dur_events':nev,'dur_mfp':A[n][1],'dur_adapt':A[n][2],
     'env_a13':tot['a13'],'env_life':life_gwp,'env_pen':tot['penrt'],'env_ren':tot['pert']/(tot['pert']+tot['penrt']),'env_rec':tot['sm_kg']/tot['mass'] if tot['mass'] else 0,'env_waste':tot['waste'],
     'wb_voc':A[n][3],'wb_mass':tot['mass'],'wb_buffer':A[n][4],'wb_ac':v['slab_mass'],
     'cost_con':A[n][5],'cost_maint':maint,'cost_op':0.0,
     'D':tot['d'],'U':e['U']}
    rows[n]=ind
HIGH={'dur_life':1,'dur_events':0,'dur_mfp':1,'dur_adapt':1,'env_a13':0,'env_life':0,'env_pen':0,'env_ren':1,'env_rec':1,'env_waste':0,'wb_voc':1,'wb_mass':1,'wb_buffer':1,'wb_ac':1,'cost_con':0,'cost_maint':0,'cost_op':0}
CRIT={'Durability':['dur_life','dur_events','dur_mfp','dur_adapt'],'Environment':['env_a13','env_life','env_pen','env_ren','env_rec','env_waste'],'Well-being':['wb_voc','wb_mass','wb_buffer','wb_ac'],'Cost':['cost_con','cost_maint','cost_op']}
S={n:{} for n in names}
for k,h in HIGH.items():
    v=[rows[n][k] for n in names]; lo,hi=min(v),max(v)
    for n in names: S[n][k]=50.0 if hi==lo else (100*(rows[n][k]-lo)/(hi-lo) if h else 100*(hi-rows[n][k])/(hi-lo))
P={n:{c:0.25*sum(S[n][k] for k in ks)/len(ks) for c,ks in CRIT.items()} for n in names}
T={n:sum(P[n].values()) for n in names}
rank={n:i+1 for i,n in enumerate(sorted(names,key=lambda n:-T[n]))}
json.dump(dict(rows=rows,S=S,P=P,T=T,rank=rank),open('analysis/compare6/results.json','w'),indent=1)
w=csv.writer(open('analysis/compare6/scores.csv','w',newline='',encoding='utf-8'))
w.writerow(['alternative','durability_pts','environment_pts','wellbeing_pts','cost_pts','total','rank'])
for n in names: w.writerow([n]+[round(P[n][c],2) for c in CRIT]+[round(T[n],2),rank[n]])
w=csv.writer(open('analysis/compare6/indicators_raw.csv','w',newline='',encoding='utf-8'))
w.writerow(['alternative']+list(HIGH)+['D_kgCO2e_m2GFA','U_ext'])
for n in names: w.writerow([n]+[round(rows[n][k],4) for k in HIGH]+[round(rows[n]['D'],2),rows[n]['U']])
w=csv.writer(open('analysis/compare6/indicators_scored.csv','w',newline='',encoding='utf-8'))
w.writerow(['alternative']+list(HIGH))
for n in names: w.writerow([n]+[round(S[n][k],1) for k in HIGH])
for n in names:
    print(f"{n[:46]:46}",' '.join(f"{c[:3]}={P[n][c]:5.2f}" for c in CRIT),f"T={T[n]:6.2f} r={rank[n]}")
print()
for k in HIGH: print(f"{k:11}",' '.join(f"{rows[n][k]:10.3f}" for n in names))
