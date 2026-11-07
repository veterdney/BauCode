"""Six structural alternatives, 500 m2 GFA, 50 y. Facts only from OBD 2024-II (analysis/products.csv). All else flagged ASSUMPTION."""
import sys, math, csv, json, statistics as st, re
sys.path.insert(0,'analysis')
import model as M
from lib import *
M.STUDY=50; STUDY=50; GFA=500
# extra wall layer: CLT (cross laminated timber) and steel/others handled as items
M.L['CLT']=(dict(cat='Glue-laminated timber|Plywood|Solid structural',name='cross.laminated|CLT|solid wood panel'),0.13,100,5)
M.L['KVH studs']=M.L['KVH studs']
KEYS=['a13','c','d','pert','penrt','sm_kg','waste','mass']
MODS=['A1-A3','C1','C2','C3','C4','D']
def getv(r,mod,key):
    return val(r,mod,key)
def cands(cat,name=None,excl=None,dmin=None,dmax=None,cap=1500,need_eol=True,unit_ok=None):
    out=[]
    for r in select(cat,name,excl):
        d=dens(r)
        if dmin and (d is None or d<dmin): continue
        if dmax and (d is None or d>dmax): continue
        if need_eol and val(r,'C3') is None and val(r,'C4') is None: continue
        if unit_ok and r['Bezugseinheit'] not in unit_ok: continue
        a=per_m3_val(r,'A1-A3')
        if a is None or abs(a)>cap: continue
        out.append(r)
    return out
def conv(r,mod,key,vol):
    v=val(r,mod,key)
    if v is None: return None
    m=per_m3(r,mod)
    return None if m is None else v*m*vol
def med(xs):
    xs=[x for x in xs if x is not None]
    return st.median(xs) if xs else 0.0
def item(rs,vol,mult=1.0):
    """indicators per m2 GFA for volume vol (m3 per m2 GFA) of the median product among rs"""
    d={}
    d['a13']=med([conv(r,'A1-A3','GWPtotal (A2)',vol) for r in rs])*mult
    d['c']=med([sum(x for x in (conv(r,m,'GWPtotal (A2)',vol) for m in ('C1','C2','C3','C4')) if x is not None) for r in rs])*mult
    d['d']=med([conv(r,'D','GWPtotal (A2)',vol) or 0.0 for r in rs])*mult
    d['pert']=med([conv(r,'A1-A3','PERT',vol) for r in rs])*mult
    d['penrt']=med([conv(r,'A1-A3','PENRT',vol) for r in rs])*mult
    d['sm_kg']=med([conv(r,'A1-A3','SM',vol) for r in rs])*mult
    d['waste']=med([sum(x for x in (conv(r,m,k,vol) for m in ('C1','C2','C3','C4') for k in ('HWD','NHWD')) if x is not None) for r in rs])*mult
    rho=med([dens(r) for r in rs]); d['mass']=rho*vol*mult
    d['n']=len(rs); d['rho']=rho
    d['uuids']=[r['UUID'] for r in rs][:60]
    return d
ADD=lambda a,b:{k:(a[k]+b[k] if k in('a13','c','d','pert','penrt','sm_kg','waste','mass') else a.get(k)) for k in a}
Z=lambda:dict(a13=0,c=0,d=0,pert=0,penrt=0,sm_kg=0,waste=0,mass=0)

# --- product pools ---
POOL={
 'concrete':cands('Ready mixed concrete',dmin=2000,cap=1500,unit_ok=('m3','kg')),
 'rebar':cands('Steel reinforcing bar|Steel reinforcement mesh',dmin=7000,cap=10**7),
 'steel':cands('Structural steel profile',name='Sections and merchant|Structural Steel',excl='wire|Painted|Galvanized|XCarb|plate',dmin=7000,cap=10**7),
 'deck':cands('Steel sheets',dmin=7000,cap=10**7,need_eol=False),
 'CLT':cands('Glue-laminated timber|Plywood|Solid structural',name='cross.laminated|CLT',dmin=300,cap=1500),
 'KVH':cands('Solid structural timber \\(KVH\\)|Structural timber',dmin=300,cap=1500),
 'OSB':cands('Oriented strand',dmin=300,cap=1500),
 'sandlime':cands('Sand lime brick',cap=1500),
}
# wood-concrete composite slab: declared per m2
wcc=[r for r in select('Ceilings','Wood-concrete')]
def wcc_item():
    r=wcc[0]; q=f(r['Bezugsgroesse']) or 1
    d={'a13':val(r,'A1-A3','GWPtotal (A2)')/q,'c':sum(val(r,m,'GWPtotal (A2)') or 0 for m in('C1','C2','C3','C4'))/q,'d':(val(r,'D','GWPtotal (A2)') or 0)/q,
       'pert':val(r,'A1-A3','PERT')/q,'penrt':val(r,'A1-A3','PENRT')/q,'sm_kg':val(r,'A1-A3','SM') or 0,'waste':sum(val(r,m,k) or 0 for m in('C1','C2','C3','C4') for k in('HWD','NHWD')),
       'mass':f(r['Flaechengewicht (kg/m2)']) or 274,'n':1,'rho':None,'uuids':[r['UUID']]}
    return d

# --- wall build-ups (reuse model.build for thicknesses) ---
def wall_item(asm,area):
    layers=M.build(asm,'ext'); tot=Z(); rep=Z(); R=M.RSI_RSE; evs=[]; cost_ev=0.0
    for l in layers:
        n=l['layer']; area_l=n in M.KIND_AREA
        rs=[r for r in M.cand(n) if (per_m3_val(r,'A1-A3') is not None) or area_l]
        if area_l:
            rs=[r for r in rs if r['Bezugseinheit']=='qm' and abs(val(r,'A1-A3'))<200]
            vol=1.0; it=dict(a13=med([val(r,'A1-A3','GWPtotal (A2)') for r in rs]),c=med([sum(x for x in (val(r,m,'GWPtotal (A2)') for m in('C1','C2','C3','C4')) if x is not None) for r in rs]),d=med([val(r,'D','GWPtotal (A2)') or 0 for r in rs]),
                 pert=med([val(r,'A1-A3','PERT') for r in rs]),penrt=med([val(r,'A1-A3','PENRT') for r in rs]),sm_kg=0,waste=med([sum(x for x in (val(r,m,k) for m in('C1','C2','C3','C4') for k in('HWD','NHWD')) if x is not None) for r in rs]),mass=0.3,n=len(rs),rho=None,uuids=[r['UUID'] for r in rs])
            for k in ('a13','c','d','pert','penrt','sm_kg','waste','mass'): it[k]*=l['mult']
        else:
            rs=[r for r in rs if abs(per_m3_val(r,'A1-A3'))<1500]
            it=item(rs,l['thick'],l['mult'])
        nrep=max(0,math.ceil(STUDY/l['life'])-1)
        for k in KEYS: tot[k]+=it[k]*(1+nrep)*area
        for k in ('a13','c'): rep[k]+=it[k]*nrep*area
        for k in ('pert','penrt','waste','sm_kg'): pass
        lam=M.L[n][1]
        if lam>0 and l['thick'] and n!='KVH studs': R+=l['thick']/lam
        for y in range(l['life'],STUDY,l['life']): evs.append((n,y))
        tot.setdefault('layers',[]).append((n,round(l['thick'] or 0,3),l['mult'],l['life'],nrep,it['n']))
        tot['uuids']=tot.get('uuids',[])+it['uuids'][:20]
        # layer mass counts once
        tot['mass']-=it['mass']*nrep*area
    tot['events']=evs; tot['U']=round(1/R,3) if not any(a[0]=='KVH studs' for a in asm) else M.U_TARGET
    return tot

A_=lambda **k:dict(k)
# ext wall assemblies (0.6 m2 per m2 GFA assumed)
EXTW={
 'RC+EPS':[('Interior paint/wall covering','area',1,None),('Concrete (ready-mixed)',0.20,1,None),('EPS insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'Light steel + mineral wool':[('Gypsum plasterboard',0.025,1,None),('Interior paint/wall covering','area',1,None),('Rock wool insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'Masonry + rock wool':M.EXT['X3 Monolithic brick + rock-wool top-up'],
 'CLT + rock wool':[('CLT',0.10,1,None),('Rock wool insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'CLT + wood fibre':[('CLT',0.10,1,None),('Wood fibre insulation','solve',1,40),('Mineral render/plaster',0.01,1,40)],
 'Timber post + straw + clay':M.EXT['X7 Timber post + straw bale + clay/lime plaster'],
}
M.L['Concrete (ready-mixed)']=M.L['Concrete (ready-mixed)']
EW=0.6   # m2 ext wall per m2 GFA   ASSUMPTION
IW=0.4   # m2 interior bearing wall per m2 GFA ASSUMPTION
def comb(*xs):
    t=Z()
    for x in xs:
        for k in t: t[k]+=x[k]
    return t
def sc(d,f):
    return {k:(v*f if k in('a13','c','d','pert','penrt','sm_kg','waste','mass') else v) for k,v in d.items()}
def vol_item(pool,vol): return item(POOL[pool],vol)
def steel_item(pool,kg): return item(POOL[pool],kg/7850.0)
# structure per m2 GFA -- quantities are ASSUMPTIONS
S={}
def build_all():
    out={}
    # 1 RC frame
    ew=wall_item(EXTW['RC+EPS'],EW)
    s=[sc(vol_item('concrete',0.22),1),steel_item('rebar',0.22*110),sc(vol_item('concrete',0.20*IW),1),steel_item('rebar',0.20*IW*80)]
    out['1 RC frame + EPS ETICS']=dict(ext=ew,struct=comb(*s),slab_mass=0.22*2400,slab_rho=2400,desc='slab 0.22 m3 concrete + 110 kg/m3 rebar; bearing walls 0.20 m RC')
    # 2 steel frame
    ew=wall_item(EXTW['Light steel + mineral wool'],EW)
    s=[steel_item('steel',28),vol_item('concrete',0.09),steel_item('deck',9),steel_item('rebar',3),vol_item('concrete',0.02),steel_item('rebar',0.02*100)]
    out['2 Steel frame + composite slab + mineral wool']=dict(ext=ew,struct=comb(*s),slab_mass=0.09*2400+9+3,slab_rho=None,desc='28 kg/m2 steel sections; composite slab 90 mm concrete + deck 9 kg/m2 + mesh 3 kg/m2; stair core 0.02 m3')
    # 3 masonry
    ew=wall_item(EXTW['Masonry + rock wool'],EW)
    s=[vol_item('concrete',0.20),steel_item('rebar',0.20*100),vol_item('sandlime',0.175*IW)]
    out['3 Monolithic masonry + mineral insulation']=dict(ext=ew,struct=comb(*s),slab_mass=0.20*2400,slab_rho=2400,desc='slab 0.20 m3 concrete + 100 kg/m3 rebar; bearing walls sand-lime 175 mm')
    # 4 timber-concrete hybrid
    ew=wall_item(EXTW['CLT + rock wool'],EW)
    s=[wcc_item(),sc(vol_item('CLT',0.10*IW),1)]
    out['4 Timber-concrete hybrid (CLT walls + composite slab)']=dict(ext=ew,struct=comb(*s),slab_mass=wcc_item()['mass'],slab_rho=None,desc='wood-concrete composite slab (OBD, 274 kg/m2); CLT interior walls 100 mm')
    # 5 solid timber
    ew=wall_item(EXTW['CLT + wood fibre'],EW)
    s=[vol_item('CLT',0.18),sc(vol_item('CLT',0.10*IW),1)]
    out['5 Solid timber (CLT) + wood-fibre']=dict(ext=ew,struct=comb(*s),slab_mass=0.18*470,slab_rho=470,desc='CLT slab 180 mm; CLT interior walls 100 mm')
    # 6 timber frame straw
    ew=wall_item(EXTW['Timber post + straw + clay'],EW)
    s=[vol_item('KVH',0.07),vol_item('OSB',0.022),vol_item('KVH',0.14*0.12*IW),vol_item('OSB',0.015*2*IW)]
    out['6 Timber frame + straw + clay plaster']=dict(ext=ew,struct=comb(*s),slab_mass=0.07*500+0.022*620,slab_rho=500,desc='timber joist slab 0.07 m3 KVH + 22 mm OSB; stud walls 12% KVH + OSB both sides')
    return out
if __name__=='__main__':
    R=build_all()
    for n,v in R.items():
        e,s_=v['ext'],v['struct']
        print(f"{n[:50]:50} ext a13={e['a13']:7.1f} c={e['c']:6.1f} | struct a13={s_['a13']:7.1f} c={s_['c']:6.1f}  U={e['U']}  pools n={ {k:len(p) for k,p in POOL.items()} if n.startswith('1') else ''}")
