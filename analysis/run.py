"""Step 4-6: score, decade timeline, budget comparison, products. Writes CSVs ('.' decimal, ',' delimiter) + results.json."""
import sys, json, csv, statistics as st
sys.path.insert(0,'analysis')
from model import *

# Expert-judgement well-being scores 1(poor)-5(good): moisture buffering, low emissions/VOC, summer comfort, acoustics, moisture-damage robustness
WB={
 'X1':(4,3,4,3,3),'X2':(5,4,4,3,3),'X3':(4,5,3,4,4),'X4':(3,3,3,4,4),'X5':(2,4,3,4,5),'X6':(4,5,3,3,4),'X7':(5,5,5,3,2),'X8':(4,5,4,4,4),
 'P1':(2,3,2,3,4),'P2':(3,3,2,3,4),'P3':(4,5,4,5,5),'P4':(4,5,3,3,4),'P5':(5,4,3,3,3),'P6':(5,4,3,2,3),'P7':(4,5,4,5,5)}
# adaptability for interior walls (future reconfiguration per decade) 1-5
ADAPT={'P1':5,'P2':5,'P3':2,'P4':2,'P5':5,'P6':4,'P7':1}
def norm(vals,higher_better):
    lo,hi=min(vals),max(vals)
    return [0.5 if hi==lo else ((v-lo)/(hi-lo) if higher_better else (hi-v)/(hi-lo)) for v in vals]

def run(K,kind):
    R=[assess(n,a,kind) for n,a in K.items()]
    for r in R:
        key=r['name'].split()[0]
        r['renew']=r['pert']/(r['pert']+r['penrt']) if (r['pert']+r['penrt'])>0 else 0
        dl=[l['dis'] for l in r['layers'] if not l.get('missing') and l['layer']!='Interior paint/wall covering']
        r['dfd']=sum(dl)/len(dl)
        r['rep_share']=r['rep']/r['life_gwp'] if r['life_gwp']>0 else 0
        w=WB[key]; r['wb']=sum(w)/len(w)
        r['adapt']=ADAPT.get(key,None)
        r['health_proxy']=r['pocp']+0  # POCP A1-A3 incl. replacements (smog), data-based
        if kind=='ext': r['U']=U_TARGET if any(l['layer'] in('KVH studs',) for l in r['layers']) else r['U']
    c=norm([r['life_gwp'] for r in R],False)
    s1=norm([r['renew'] for r in R],True); s2=norm([r['dfd']+(r['adapt'] or 0)*0 for r in R],True); s3=norm([r['rep_share'] for r in R],False)
    s4=norm([r['pert'] and r['penrt'] for r in R],False)
    h1=norm([r['wb'] for r in R],True); h2=norm([r['pocp'] for r in R],False)
    for i,r in enumerate(R):
        r['S_carbon']=c[i]
        r['S_sust']=0.4*s1[i]+0.4*s2[i]+0.2*s3[i]
        wbn=h1[i]; r['S_well']=0.75*wbn+0.25*h2[i]
        if kind=='int':
            a=norm([x['adapt'] for x in R],True)[i]; r['S_sust']=0.3*s1[i]+0.3*s2[i]+0.2*s3[i]+0.2*a
        r['total']=(r['S_carbon']+r['S_sust']+r['S_well'])/3
        r['total_carbon_heavy']=0.5*r['S_carbon']+0.25*r['S_sust']+0.25*r['S_well']
        r['total_well_heavy']=0.25*r['S_carbon']+0.25*r['S_sust']+0.5*r['S_well']
    R.sort(key=lambda r:-r['total'])
    return R
EXTR=run(EXT,'ext'); INTR=run(INT,'int')
W=lambda p,rows,cols:csv.writer(open(p,'w',newline='',encoding='utf-8')).writerows([cols]+[[ (round(x,3) if isinstance(x,float) else x) for x in (r[c] for c in cols)] for r in rows])
cols=['name','kind','a13','c','rep','life_gwp','d','U','renew','dfd','rep_share','wb','adapt','pocp','S_carbon','S_sust','S_well','total','total_carbon_heavy','total_well_heavy']
W('analysis/results_wall_systems.csv',EXTR+INTR,cols)
rows=[]
for r in EXTR+INTR:
    for l in r['layers']:
        if l.get('missing'): rows.append([r['name'],l['layer'],'MISSING']+['']*10); continue
        rows.append([r['name'],l['layer'],'',l['thick'] if l['thick'] is None else round(l['thick'],3),l['mult'],l['life'],l['nrep'],l['n'],round(l['a13'],3),round(l['c'],3),round(l['d'],3),round(l['life_gwp'],3),l['dis']])
csv.writer(open('analysis/results_layers.csv','w',newline='',encoding='utf-8')).writerows([['system','layer','flag','thickness_m','area_or_frame_factor','service_life_y','replacements_in_60y','n_epds','A1_A3_kgCO2e_m2','C1_C4_kgCO2e_m2','D_kgCO2e_m2','life_A1_C_kgCO2e_m2','disassembly_1to5']]+rows)
# decade timeline: new build 2026 + replacement events per decade
tl=[]
import math as _m
for r in EXTR+INTR:
    b={w:0.0 for w in range(10,70,10)}
    for y,v in r['events'].items(): b[min(60,_m.ceil(y/10)*10)]+=v   # event falls into the next decade renovation window
    tl.append([r['name'],round(r['a13']+r['c'],3)]+[round(b[w],3) for w in range(10,70,10)])
csv.writer(open('analysis/results_decade_timeline.csv','w',newline='',encoding='utf-8')).writerows([['system','build_2026','window_2036','window_2046','window_2056','window_2066','window_2076','window_2086']]+tl)
# budgets
B={}
for y in (2026,2036,2046):
    d=json.load(open(f'analysis/budget_de_res_{y}.json'))['selected_year_budget']; B[y]=d
csv.writer(open('analysis/results_budget_de_residential.csv','w',newline='',encoding='utf-8')).writerows([['year','embodied_per_m2','operational_per_m2','total_per_m2']]+[[y,b['embodied_per_m2'],b['operational_per_m2'],b['total_per_m2']] for y,b in B.items()])
# share of embodied budget: ext 0.6 m2 wall / m2 GFA, int 0.8 (assumption)
share=[]
for r in EXTR+INTR:
    f=0.6 if r['kind']=='ext' else 0.8
    build=(r['a13']+r['c'])*f
    share.append([r['name'],round(build,2),round(100*build/B[2026]['embodied_per_m2'],2),round(100*build/B[2036]['embodied_per_m2'],2),round(100*build/B[2046]['embodied_per_m2'],2)])
csv.writer(open('analysis/results_budget_share.csv','w',newline='',encoding='utf-8')).writerows([['system','wall_GWP_per_m2_GFA_A1_C','pct_of_embodied_budget_2026','pct_2036','pct_2046']]+share)
# product shortlist for top-3 of each class
pr=[]
for R in (EXTR,INTR):
    for r in R[:3]:
        asm=(EXT if r['kind']=='ext' else INT)[r['name']]
        for l in r['layers']:
            if l.get('missing'): continue
            th=l['thick'] if l['layer'] not in KIND_AREA else 1.0
            c=layer_stats(l['layer'],th)
            c=[s for s in c if abs(s['a13']/th)<(1500 if l['layer'] not in KIND_AREA else 200) and str(s['valid'])>='2026']
            c.sort(key=lambda s:s['a13']+s['c'])
            for rank,s in enumerate(c[:3],1):
                pr.append([r['name'],l['layer'],rank,s['name'],s['uuid'],s['typ'],s['valid'],s['owner'][:60],round((s['a13']+s['c'])*l['mult'],3),round(s['a13']*l['mult'],3)])
csv.writer(open('analysis/results_products.csv','w',newline='',encoding='utf-8')).writerows([['system','layer','rank','product_en','uuid','dataset_type','valid_until','declaration_owner','A1_C_kgCO2e_m2_wall','A1_A3_kgCO2e_m2_wall']]+pr)
json.dump([{k:v for k,v in r.items() if k!='layers'} for r in EXTR+INTR],open('analysis/results.json','w'),indent=1,default=str)
for R in (EXTR,INTR):
    for r in R: print(f"{r['name'][:50]:50} life={r['life_gwp']:6.1f} sust={r['S_sust']:.2f} well={r['S_well']:.2f} carb={r['S_carbon']:.2f} TOT={r['total']:.2f} cH={r['total_carbon_heavy']:.2f} wH={r['total_well_heavy']:.2f}")
    print()
