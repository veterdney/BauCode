"""Step 2-3: wall assemblies -> per-m2 life-cycle GWP etc. from OBD 2024-II (A2 indicators).
Assumptions are explicit in ASSUMPTIONS below and mirrored in analysis/02-method.md."""
import sys, json, statistics as st, math, csv
sys.path.insert(0,'analysis')
from lib import *

STUDY=60          # years
U_TARGET=0.20     # W/m2K exterior walls (stricter than GEG 0.24, future-proof for decade retrofits)
RSI_RSE=0.17

# selector: (category regex, name regex, exclude regex, max density, min density)
def sel(cat,name=None,excl=None,dmax=None,dmin=None):
    out=[]
    for r in select(cat,name,excl):
        d=dens(r)
        if dmax and (d is None or d>dmax): continue
        if dmin and (d is None or d<dmin): continue
        # need at least one EoL module so lifecycle is not flattered by missing data
        if val(r,'C3') is None and val(r,'C4') is None: continue
        out.append(r)
    return out

L={ # name: (selector kwargs, lambda W/mK, life y, disassembly 1-5 (5 = easy, mono-material, mechanical), kind)
 'KVH studs':          (dict(cat='Solid structural timber \\(KVH\\)|Structural timber'),0.13,100,5),
 'Structural timber/CLT':(dict(cat='Structural timber|Glue-laminated timber board|Wood-based elements',name='CLT|cross|solid|spruce|timber|board|BSP|laminat',dmin=300),0.13,100,5),
 'Wood fibre insulation':(dict(cat='Wood fibre insulation boards|Wood fibre boards',dmax=300),0.040,60,5),
 'Wood fibre board (sheathing)':(dict(cat='Wood fibre boards|Wood fibre insulation',dmin=150,dmax=300),0.045,60,5),
 'Cellulose insulation':(dict(cat='Cellulose'),0.039,60,5),
 'Straw bale':(dict(cat='Straw bale'),0.052,60,5),
 'Hemp insulation':(dict(cat='Hemp',dmax=100),0.042,60,5),
 'Rock wool insulation':(dict(cat='Rock wool|Glass wool',dmax=200),0.036,60,3),
 'EPS insulation':(dict(cat='EPS'),0.035,60,2),
 'Fired brick':(dict(cat='Fired brick',dmax=1000),0.12,100,2),
 'Sand-lime brick':(dict(cat='Sand lime brick'),0.99,100,3),
 'Aerated concrete':(dict(cat='Aerated concrete'),0.10,100,2),
 'Concrete (ready-mixed)':(dict(cat='Ready mixed concrete',dmin=2000),2.0,100,1),
 'Gypsum plasterboard':(dict(cat='Gypsum plasterboard'),0.25,50,3),
 'Mineral render/plaster':(dict(cat='Renders and plasters',excl='lime|clay|gypsum'),0.80,40,2),
 'Clay/lime plaster':(dict(cat='Renders and plasters',name='lime|clay|loam|Kalk|Lehm'),0.80,60,4),
 'Clay panels':(dict(cat='Clay panels|adobe'),0.50,60,5),
 'Interior paint/wall covering':(dict(cat='Wall and ceiling covering'),0.0,12,3),
}
KIND_AREA={'Interior paint/wall covering'}

def cand(layer):
    kw,lam,life,dis=L[layer]
    return sel(**kw)

def per_m2(r,mod,thick,key='GWPtotal (A2)',area=False):
    v=val(r,mod,key)
    if v is None: return None
    if area:
        return v if r['Bezugseinheit']=='qm' else None
    m=per_m3(r,mod); return None if m is None else v*m*thick

def layer_stats(layer,thick):
    area=layer in KIND_AREA; res=[]
    for r in cand(layer):
        a=per_m2(r,'A1-A3',thick,area=area)
        if a is None: continue
        c=sum(x for x in (per_m2(r,m,thick,area=area) for m in ('C1','C2','C3','C4')) if x is not None)
        d=per_m2(r,'D',thick,area=area) or 0.0
        pe=per_m2(r,'A1-A3',thick,'PERT',area); pn=per_m2(r,'A1-A3',thick,'PENRT',area)
        poc=per_m2(r,'A1-A3',thick,'POCP (A2)',area); pm=per_m2(r,'A1-A3',thick,'PM (A2)',area)
        res.append(dict(uuid=r['UUID'],name=r['Name (en)'],typ=r['Typ'],valid=r['Gueltig bis'],owner=r['Declaration owner'],a13=a,c=c,d=d,pert=pe,penrt=pn,pocp=poc,pm=pm))
    return res

def insulation_thickness(R_other,lam,frame_frac=0.0,lam_frame=0.13):
    lam_eq=(1-frame_frac)*lam+frame_frac*lam_frame
    need=1/U_TARGET-RSI_RSE-R_other
    return max(0.0,round(need*lam_eq,3)),lam_eq

def lifecycle(stats_choice,life,thick,pick):
    pass

# ---------- assemblies ----------
# layer spec: (layer name, thickness m | 'solve', area-multiplier or frame fraction, life override|None, role)
EXT={
 'X1 Timber frame + wood-fibre insulation':[('Gypsum plasterboard',0.0125,1,None),('Interior paint/wall covering','area',1,None),('KVH studs','frame',0.12,None),('Wood fibre insulation','solve',0.88,None),('Wood fibre board (sheathing)',0.06,1,40),('Mineral render/plaster',0.01,1,40)],
 'X2 Solid timber (CLT) + wood-fibre ETICS':[('Structural timber/CLT',0.10,1,None),('Wood fibre insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'X3 Monolithic brick + rock-wool top-up':[('Clay/lime plaster',0.015,1,None),('Interior paint/wall covering','area',1,None),('Fired brick',0.365,1,None),('Rock wool insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'X4 Sand-lime brick + EPS ETICS':[('Mineral render/plaster',0.01,1,None),('Interior paint/wall covering','area',1,None),('Sand-lime brick',0.175,1,None),('EPS insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'X5 Reinforced concrete + rock-wool ETICS':[('Interior paint/wall covering','area',1,None),('Concrete (ready-mixed)',0.20,1,None),('Rock wool insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'X6 Aerated concrete + rock-wool top-up':[('Mineral render/plaster',0.01,1,None),('Interior paint/wall covering','area',1,None),('Aerated concrete',0.30,1,None),('Rock wool insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'X7 Timber post + straw bale + clay/lime plaster':[('Clay/lime plaster',0.02,1,None),('KVH studs','frame',0.08,None),('Straw bale','solve',0.92,None),('Clay/lime plaster',0.02,1,None)],
 'X8 Monolithic brick + wood-fibre top-up':[('Clay/lime plaster',0.015,1,None),('Interior paint/wall covering','area',1,None),('Fired brick',0.365,1,None),('Wood fibre insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
}
INT={
 'P1 Timber stud + rock wool + 2x2 plasterboard':[('Gypsum plasterboard',0.05,1,None),('Interior paint/wall covering','area',2,None),('KVH studs','frame_int',0.10,None),('Rock wool insulation',0.075,0.9,None)],
 'P2 Timber stud + cellulose + 2x2 plasterboard':[('Gypsum plasterboard',0.05,1,None),('Interior paint/wall covering','area',2,None),('KVH studs','frame_int',0.10,None),('Cellulose insulation',0.075,0.9,None)],
 'P3 Sand-lime brick 115 + plaster':[('Sand-lime brick',0.115,1,None),('Mineral render/plaster',0.01,2,None),('Interior paint/wall covering','area',2,None)],
 'P4 Aerated concrete 100 + plaster':[('Aerated concrete',0.10,1,None),('Mineral render/plaster',0.01,2,None),('Interior paint/wall covering','area',2,None)],
 'P5 Clay panels + timber stud + hemp/wood-fibre + clay plaster':[('Clay panels',0.044,1,None),('KVH studs','frame_int',0.10,None),('Wood fibre insulation',0.06,0.9,None),('Clay/lime plaster',0.01,2,None)],
 'P6 Solid timber panel 80':[('Structural timber/CLT',0.08,1,None)],
 'P7 Fired brick 115 + lime plaster':[('Fired brick',0.115,1,None),('Clay/lime plaster',0.015,2,None),('Interior paint/wall covering','area',2,None)],
}

def build(asm,kind):
    layers=[]; Rother=0.0; frame=None
    # first pass: fixed layers for R
    solve_frac=None; frame_t=None
    for name,t,m,life in asm:
        if t=='solve': solve_frac=m
    frame_f=None
    for name,t,m,life in asm:
        if t=='frame': frame_f=m
    fixed=[(n,t,m,l) for n,t,m,l in asm if isinstance(t,float)]
    for n,t,m,l in fixed:
        lam=L[n][1]
        if lam>0: Rother+=t/lam
    solve=[a for a in asm if a[1]=='solve']
    depth=0
    if solve:
        n,_,m,l=solve[0]; lam=L[n][1]
        ff=frame_f or 0
        depth,lam_eq=insulation_thickness(Rother,lam,ff)
        # insulation share of that depth
    for n,t,m,l in asm:
        life=l or L[n][2]
        if t=='area': th=None; mult=m
        elif t=='solve': th=depth; mult=m
        elif t=='frame': th=depth; mult=m   # studs sit in insulation depth, m = frame fraction
        elif t=='frame_int': th=0.075; mult=m
        else: th=t; mult=m
        layers.append(dict(layer=n,thick=th,mult=mult,life=life))
    return layers

def U_of(layers):
    R=RSI_RSE
    ins=None
    for l in layers:
        lam=L[l['layer']][1]
        if lam>0 and l['thick']:
            if l['layer']=='KVH studs': continue
            R+=l['thick']*(l['mult'] if l['mult']<1 and l['layer'] in('Wood fibre insulation','Straw bale') else 1)/ lam if False else l['thick']/lam
    return R

def assess(name,asm,kind):
    layers=build(asm,kind); out=[]; tot=dict(a13=0,c=0,d=0,rep=0,pert=0,penrt=0,pocp=0,pm=0,mass_ok=0); events={}
    Rfix=RSI_RSE; 
    for l in layers:
        n=l['layer']; area=n in KIND_AREA
        th=l['thick'] if not area else 1.0
        st_=layer_stats(n,th)
        st_=[s for s in st_ if abs(s['a13']/ (th if not area else 1))<(1500 if not area else 200)] if st_ else st_
        if not st_: out.append(dict(layer=n,missing=True)); continue
        med=lambda k: st.median([s[k] for s in st_ if s[k] is not None]) if any(s[k] is not None for s in st_) else 0.0
        a,c,d=med('a13')*l['mult'],med('c')*l['mult'],med('d')*l['mult']
        pert,penrt,pocp,pm=[med(k)*l['mult'] for k in ('pert','penrt','pocp','pm')]
        nrep=max(0,math.ceil(STUDY/l['life'])-1)
        life_gwp=(a+c)*(1+nrep); rep=(a+c)*nrep
        tot['a13']+=a; tot['c']+=c; tot['d']+=d*(1+nrep); tot['rep']+=rep
        tot['pert']+=pert*(1+nrep); tot['penrt']+=penrt*(1+nrep); tot['pocp']+=pocp*(1+nrep); tot['pm']+=pm*(1+nrep)
        yrs=[y for y in range(l['life'],STUDY,l['life'])]
        for y in yrs: events[y]=events.get(y,0)+a+c
        out.append(dict(layer=n,thick=l['thick'],mult=l['mult'],life=l['life'],n=len(st_),a13=a,c=c,d=d,nrep=nrep,life_gwp=life_gwp,dis=L[n][3],
                        best=min(st_,key=lambda s:s['a13']+s['c'])['name'],best_val=min(s['a13']+s['c'] for s in st_)*l['mult']))
    # U-value
    R=RSI_RSE
    for o in out:
        if o.get('missing'): continue
        lam=L[o['layer']][1]
        if lam>0 and o['thick'] and o['layer']!='KVH studs':
            R+=o['thick']/lam
    # frame bridging (timber frame/straw): approximate with parallel path on insulation depth
    lifecycle=tot['a13']+tot['c']+tot['rep']
    return dict(name=name,kind=kind,layers=out,a13=tot['a13'],c=tot['c'],rep=tot['rep'],life_gwp=lifecycle,d=tot['d'],pert=tot['pert'],penrt=tot['penrt'],
                pocp=tot['pocp'],pm=tot['pm'],events=events,U=round(1/R,3))
