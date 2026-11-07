"""Three-level scoring engine. See report for method. Run from repo root."""
import sys, math, statistics as st
sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/levels'); sys.path.insert(0,'analysis/compare6')
import compare6 as C
from materials import M, POOLS, WCC, NOMT
from lib import val, f
STUDY=50
KEYS=['a13','c','d','pert','penrt','sm_kg','waste','mass']

def med(xs):
    xs=[x for x in xs if x is not None]; return st.median(xs) if xs else 0.0
def area_item(rows):
    d={}
    q=lambda r:(f(r['Bezugsgroesse']) or 1)
    d['a13']=med([val(r,'A1-A3','GWPtotal (A2)')/q(r) for r in rows])
    d['c']=med([sum(x for x in (val(r,m,'GWPtotal (A2)') for m in ('C1','C2','C3','C4')) if x is not None)/q(r) for r in rows])
    d['d']=med([(val(r,'D','GWPtotal (A2)') or 0)/q(r) for r in rows])
    d['pert']=med([(val(r,'A1-A3','PERT') or 0)/q(r) for r in rows]); d['penrt']=med([(val(r,'A1-A3','PENRT') or 0)/q(r) for r in rows])
    d['sm_kg']=med([(val(r,'A1-A3','SM') or 0)/q(r) for r in rows])
    d['waste']=med([sum(x for x in (val(r,m,k) for m in ('C1','C2','C3','C4') for k in ('HWD','NHWD')) if x is not None)/q(r) for r in rows])
    d['mass']=med([f(r['Flaechengewicht (kg/m2)']) for r in rows]) or 0.3
    d['n']=len(rows); d['uuids']=[r['UUID'] for r in rows]
    return d
def add(a,b):
    o={k:a[k]+b[k] for k in KEYS}; o['n']=min(a['n'],b['n']); o['uuids']=a['uuids']+b['uuids']; return o
def indicators(mat,t,frac,kg=None):
    m=M[mat]; pool=m['pool']
    if pool=='WCC':
        d={k:WCC[k] for k in KEYS}; d['n']=1; d['uuids']=WCC['uuids']; return d
    kind,rows=POOLS[pool]; assert rows,pool
    if kind=='area': return area_item(rows)
    if mat=='Steel frame':
        return C.item(rows,kg/7850.0)
    vol=t*frac
    d=C.item(rows,vol)
    if 'rho' in m and d['rho'] and pool not in ('pumice',):
        fct=m['rho']/d['rho']
        for k in ('a13','c','d','pert','penrt','sm_kg','waste'): d[k]*=fct
        d['mass']=m['rho']*vol
    if m.get('rebar'):
        d=add(d,C.item(POOLS['rebar'][1],m['rebar']*vol/7850.0))
    if mat=='Composite slab steel-concrete':
        d=add(d,C.item(POOLS['deck'][1],m['deck']/7850.0)); d=add(d,C.item(POOLS['rebar'][1],m['mesh']/7850.0))
    return d
def L(mat,t,frac=1.0,**o): return dict(mat=mat,t=t,frac=frac,**o)

# ---------- Glaser (DIN 4108-3 steady state) ----------
def ps(T): return 610.5*math.exp(17.269*T/(237.3+T)) if T>=0 else 610.5*math.exp(21.875*T/(265.5+T))
D0=2.0e-10; S90=90*86400
def glaser(stack,Rsi,Rse):
    """stack: list of dict(name,R,sd) inside->outside. returns per-interface list of (ratio, rating) and summary"""
    Ti,Te=20.0,-5.0; pi=0.5*ps(Ti); pe=0.8*ps(Te)
    Rt=Rsi+Rse+sum(l['R'] for l in stack); sdt=sum(max(l['sd'],0.01) for l in stack)
    th=[Ti-(Ti-Te)*Rsi/Rt]; sdc=[0.0]; r=Rsi
    for l in stack:
        r+=l['R']; th.append(Ti-(Ti-Te)*r/Rt); sdc.append(sdc[-1]+max(l['sd'],0.01))
    ratios=[(pi-(pi-pe)*sdc[k]/sdt)/ps(th[k]) for k in range(len(stack)+1)]
    out=[None]*(len(stack)+1); Mc=Me=0.0
    kstar=max(range(1,len(stack)),key=lambda k:ratios[k]) if len(stack)>1 else None
    for k in range(1,len(stack)):
        rt='good'
        if ratios[k]>=0.9: rt='caution'
        out[k]=[ratios[k],rt]
    note='no condensation'
    if kstar and ratios[kstar]>1.0:
        pc=ps(th[kstar]); sdi=sdc[kstar]; sde=sdt-sdc[kstar]
        Mc=S90*D0*((pi-pc)/sdi-(pc-pe)/sde)
        pss=0.7*ps(12.0); Me=S90*D0*((ps(12.0)-pss)/sdi+(ps(12.0)-pss)/sde)
        if Mc>0:
            lim=1.0 if min(stack[kstar-1].get('buf',1),stack[kstar].get('buf',1))>=4 or max(stack[kstar-1].get('buf',1),stack[kstar].get('buf',1))>=4 else 0.5
            rt='caution' if (Mc<=lim and Me>=Mc) else 'critical'
            out[kstar]=[ratios[kstar],rt]; note=f'condensation {Mc:.3f} kg/m2 vs evaporation {Me:.3f} kg/m2 at plane {kstar}'
    return dict(ifc=out,Mc=Mc,Me=Me,note=note,Rt=Rt,U=1.0/Rt,kstar=kstar,maxratio=max(ratios[1:-1]) if len(stack)>1 else 0)

# ---------- build-up resolution ----------
PART_RS={'OW':(0.13,0.04,0.20),'RF':(0.10,0.04,0.14),'GS':(0.17,0.0,0.25)}
import os
if os.environ.get('MATERIAL_DATASET','1')=='1':
    from dataset_fill import U_REF
    PART_RS={'OW':(0.13,0.04,U_REF['OW']),'RF':(0.10,0.04,U_REF['RF']),'GS':(0.17,0.0,U_REF['GS'])}   # GModG Anlage 1 reference building
def resolve(part,spec):
    lay=[dict(x) for x in spec]
    # thermal groups: consecutive layers with frac<1 and same t, or a solve layer
    if part in PART_RS:
        Rsi,Rse,U=PART_RS[part]; Rreq=1/U-Rsi-Rse
        # find solve group
        sidx=[i for i,x in enumerate(lay) if x['t']=='solve']
        if sidx:
            Rfix=0.0; grp=set()
            for i in sidx:
                grp.add(i)
            for i,x in enumerate(lay):
                if x['t']=='same': grp.add(i)
            lam_eq=sum(M[lay[i]['mat']]['lam']*lay[i]['frac'] for i in grp)
            for i,x in enumerate(lay):
                if i in grp: continue
                m=M[x['mat']]
                if m['lam']>0 and isinstance(x['t'],(int,float)): Rfix+=x['t']/m['lam']
            d=max(0.0,(Rreq-Rfix))*lam_eq
            d=math.ceil(d*100-1e-9)/100.0   # round up to 10 mm
            for i in grp: lay[i]['t']=d
    for x in lay:
        if x['t'] in ('solve','same'): raise ValueError(x)
    return lay
def stack_of(lay):
    """collapse parallel frac layers into one thermal/diffusion layer"""
    out=[]; i=0
    while i<len(lay):
        idxs=[i]; x=lay[i]
        while x['frac']<1 and i+1<len(lay) and lay[i+1]['t']==x['t'] and lay[i+1]['frac']<1 and sum(lay[j]['frac'] for j in idxs)<0.999:
            i+=1; idxs.append(i)
        grp=[lay[j] for j in idxs]
        lam=sum(M[g['mat']]['lam']*g['frac'] for g in grp)/sum(g['frac'] for g in grp)
        main=max(grp,key=lambda g:g['frac']); m=M[main['mat']]
        if m.get('kind')=='area': R=0.0; sd=x.get('sd',m['sd'])
        else:
            tt=x['t']; R=tt/lam if lam>0 else 0.0; sd=m['mu']*tt
        out.append(dict(name='+'.join(g['mat'] for g in grp),R=R,sd=min(sd,1e5),idxs=idxs,mat=main['mat'],buf=M[main['mat']]['buf']))
        i+=1
    return out
