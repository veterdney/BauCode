import sys, math, json, csv, collections
sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/levels'); sys.path.insert(0,'analysis/compare6')
from engine import *
from builds import ALT, PARTS, AREA, REQ_RW, RW_FRAMED
SC={'good':100,'caution':50,'critical':0}; ORDER=['good','caution','critical']
worst=lambda *r: max(r,key=ORDER.index)

# ---------- 1. instantiate ----------
inst=[]   # one record per layer instance
parts={}  # (alt,part) -> dict
for a,(aname,pp) in ALT.items():
    for p,spec in pp.items():
        lay=resolve(p,spec); recs=[]
        for i,x in enumerate(lay):
            m=M[x['mat']]; kg=x.get('kg')
            if x['mat']=='Steel frame': t_eff=kg/7850.0
            elif m.get('kind')=='area' or x['mat']=='Wood-concrete slab': t_eff=NOMT.get(x['mat'],0.001)
            else: t_eff=x['t']
            ind=indicators(x['mat'],x['t'],x['frac'],kg)
            life=x.get('life',m['life']); nrep=max(0,math.ceil(STUDY/life)-1)
            vol=t_eff*x['frac']
            if m.get('kind')=='area': cost0=m['cost']
            elif x['mat']=='Steel frame': cost0=m['cost']/7850.0*kg*7850/1000.0*0+ (m['cost']/7850.0)*kg  # EUR/m3 -> EUR/kg
            elif x['mat']=='Wood-concrete slab': cost0=m['costm2']
            elif x['mat']=='Composite slab steel-concrete': cost0=m['cost']*vol+ 22.0   # + deck/mesh installed (ASSUMPTION 22 EUR/m2)
            else: cost0=m['cost']*vol
            r=dict(alt=a,part=p,idx=i,mat=x['mat'],t=x['t'],frac=x['frac'],vol=vol,life=life,nrep=nrep,job=m['job'],
                   dur_life=life,dur_ren=nrep,dur_mfp=m['mfp'],
                   env_a13=ind['a13'],env_life=(ind['a13']+ind['c'])*(1+nrep),env_pen=ind['penrt']*(1+nrep),
                   env_ren=ind['pert']/(ind['pert']+ind['penrt']) if (ind['pert']+ind['penrt'])>0 else 0.0,
                   env_rec=ind['sm_kg']/ind['mass'] if ind['mass'] else 0.0,env_waste=ind['waste']*(1+nrep),
                   wb_voc=m['voc'],wb_buf=m['buf'],wb_mass=ind['mass'],wb_snd=m['snd'],
                   cost0=cost0,cost_ren=cost0*nrep,n=ind['n'],uuids=ind['uuids'][:25],mass=ind['mass'],D=ind['d'],pool=m['pool'],
                   move=m['move'],fire=m['fire'],joint=x.get('joint',m['joint']),lam=m['lam'])
            recs.append(r); inst.append(r)
        parts[(a,p)]=dict(alt=a,part=p,layers=recs,lay=lay)

# ---------- 2. Level 1 min-max per job ----------
HIGH={'dur_life':1,'dur_ren':0,'dur_mfp':1,'env_a13':0,'env_life':0,'env_pen':0,'env_ren':1,'env_rec':1,'env_waste':0,'wb_voc':1,'wb_buf':1,'wb_mass':1,'wb_snd':1,'cost0':0,'cost_ren':0}
CRIT={'Durability':['dur_life','dur_ren','dur_mfp'],'Environment':['env_a13','env_life','env_pen','env_ren','env_rec','env_waste'],'Well-being':['wb_voc','wb_buf','wb_mass','wb_snd'],'Cost':['cost0','cost_ren']}
byjob=collections.defaultdict(list)
for r in inst: byjob[r['job']].append(r)
for job,rs in byjob.items():
    for k,h in HIGH.items():
        v=[r[k] for r in rs]; lo,hi=min(v),max(v)
        for r in rs: r.setdefault('s',{})[k]=50.0 if hi-lo<1e-12 else (100*(r[k]-lo)/(hi-lo) if h else 100*(hi-r[k])/(hi-lo))
for r in inst:
    r['sc']={c:sum(r['s'][k] for k in ks)/len(ks) for c,ks in CRIT.items()}; r['L1']=sum(r['sc'].values())/4

# ---------- 3. compatibility ----------
def is_ins(m): return M[m]['job']=='insulation'
def struct_rule(a,b):
    A,B=a['mat'],b['mat']; ca,cb=a['move'],b['move']; pair={A,B}
    if 'Roof membrane' in pair and ('EPS' in pair):
        return 'caution','membrane on EPS needs a separation layer (solvent/plasticiser)'
    if (ca=='mineral' and M[A]['job']=='plaster' or cb=='mineral' and M[B]['job']=='plaster') and (M[A]['job']=='insulation' and ca in('polymer','soft','timber') or M[B]['job']=='insulation' and cb in('polymer','soft','timber')):
        if 'Straw bale' in pair: return 'caution','lime plaster directly on straw: crack risk, needs weather protection and mesh at junctions'
        return 'caution','render on a soft/polymer/timber base: different movement, reinforcement mesh needed'
    if {ca,cb}=={'mineral','timber'} and ('structure' in (a['job'],b['job'])):
        return 'caution','mineral/timber contact: shrinkage and creep differ'
    if {ca,cb}=={'steel','timber'}: return 'caution','steel/timber: thermal expansion and moisture movement differ'
    if 'Wood-concrete slab' in pair: return 'caution','composite action depends on shear connectors; shrinkage differences'
    if ca=='polymer' and cb=='mineral' and (M[A]['job']=='insulation' and M[B]['job'] in('structure',) or M[B]['job']=='insulation' and M[A]['job'] in('structure',)):
        return 'caution','polymer insulation bonded to rigid mineral base: thermal expansion'
    return 'good',''
JR={'cast':0,'bonded':1,'mech':2,'loose':3}
def disasm_rule(a,b):
    ja,jb=a['joint'],b['joint']
    pair_struct=(a['job']=='structure' and b['job']=='structure')
    def eff(j,r): return 'loose' if (j=='cast' and not pair_struct) else j
    ja,jb=eff(ja,a),eff(jb,b); j=min(ja,jb,key=lambda x:JR[x])
    ja0,jb0=a['mat'],b['mat']
    if (M[ja0]['move']=='polymer' or M[jb0]['move']=='polymer') and (M[ja0]['job']=='plaster' or M[jb0]['job']=='plaster'):
        return 'critical','plaster/render bonded to polymer insulation: not separable into clean fractions'
    if j=='cast': return 'critical','cast-in joint (e.g. composite slab, rebar)'
    if j=='bonded': return 'caution','bonded/plastered joint: only demolition or cutting'
    return 'good',''
def fire_rate(a,p,lay):
    mats=[l['mat'] for l in lay]; reasons=[]; rt='good'
    gyp=sum(l['t'] for l in lay if l['mat']=='Gypsum board')+sum(l['t'] for l in lay if l['mat'] in('Clay plaster','Lime plaster','Mineral render'))*0.0
    if p in('OW','RF'):
        ext=[l for l in lay if M[l['mat']]['job']=='insulation']
        comb=[l['mat'] for l in ext if M[l['mat']]['fire'] in('E','D')]
        if comb and p=='OW': rt=worst(rt,'caution'); reasons.append(f"combustible external insulation ({', '.join(sorted(set(comb)))}): fire barriers at openings needed (GK 3)")
    timber_frame=any(m=='KVH' for m in mats) and not any(m=='CLT' for m in mats)
    if timber_frame and p in('OW','IL','IP','FL','RF'):
        if gyp<0.025 and not (p=='IP' and False):
            rt=worst(rt,'caution'); reasons.append('timber frame with <25 mm gypsum lining: REI/EI 30 needs test evidence or extra lining')
    clt=[l for l in lay if l['mat']=='CLT']
    if clt and max(l['t'] for l in clt)<0.09:
        rt=worst(rt,'caution'); reasons.append('CLT <90 mm: charring leaves too little section for REI 30 without lining')
    if p=='OW' and a==6: reasons.append('plastered straw bale: tested F30-F90 only with plaster in place')
    return rt,'; '.join(reasons) or 'non-combustible or protected build-up meets REI/EI 30 (GK 3, assumed)'
def sound_rate(a,p,lay,recs):
    req=REQ_RW[p]
    if req is None: return 'good',None,'no airborne requirement (ground contact)'
    if (a,p) in RW_FRAMED and RW_FRAMED[(a,p)] is not None: rw=RW_FRAMED[(a,p)]; how='framed/double-leaf value [A]'
    else:
        m_=sum(r['mass'] for r in recs if r['job'] in('structure','plaster','board','screed','cover')and r['mat']!='Steel frame')
        rw=32.4*math.log10(max(m_,10))-26
        if p=='FL' and any(l['mat']=='Screed' for l in lay) and any(M[l['mat']]['job']=='insulation' for l in lay): rw+=4; how=f'mass law, m\'={m_:.0f} kg/m2, +4 dB floating screed [A]'
        else: how=f'mass law R=32.4 lg m\'-26, m\'={m_:.0f} kg/m2'
    if p=='WI': rw=36 if a<=3 else 34; how='window Rw assumed [A]'
    rt='good' if rw>=req else ('caution' if rw>=req-5 else 'critical')
    return rt,rw,f'est. Rw {rw:.0f} dB vs required {req} dB ({how})'
def fix_text(check,pair=None,extra=''):
    return {'moisture':'raise sd of the inner vapour control layer (>= 10 m) or move insulation outward; verify by hygrothermal simulation (DIN EN 15026)',
            'structural':'insert separation/slip layer, reinforcement mesh and movement joints',
            'fire':'add a >= 25 mm non-combustible lining or mineral-wool fire barriers',
            'sound':'add decoupled lining or mass; use double-leaf build-up',
            'disassembly':'use mechanical fixings (screws, rails) instead of adhesive or plaster'}[check]
for (a,p),P in parts.items():
    lay,recs=P['lay'],P['layers']
    # thermal / glaser
    gl=None
    if p in PART_RS:
        Rsi,Rse,Ut=PART_RS[p]; st_=stack_of(lay); gl=glaser(st_,Rsi,Rse); P['U']=gl['U']; P['Utarget']=Ut; P['stack']=st_
    else: P['U']=None; P['Utarget']=None
    frt,fnote=fire_rate(a,p,lay); srt,rw,snote=sound_rate(a,p,lay,recs)
    P['rw']=rw; P['fire_note']=fnote; P['snd_note']=snote
    # map stack interface index -> layer interface
    ifs=[]
    for k in range(len(lay)-1):
        A,B=recs[k],recs[k+1]
        # moisture rating
        mr='good'; mnote=''
        if gl:
            # find which stack boundary this layer interface corresponds to
            bi=None
            for si,s in enumerate(P['stack'][:-1]):
                if max(s['idxs'])==k: bi=si+1
            if bi is not None and gl['ifc'][bi]:
                mr=gl['ifc'][bi][1]; mnote=f"pv/ps={gl['ifc'][bi][0]:.2f}"
            elif P['stack'] and k in sum([s['idxs'] for s in P['stack']],[]) and bi is None: mr='good'; mnote='inside one thermal layer'
        if mr=='good' and (A['move']=='timber' or B['move']=='timber' or 'Straw bale' in (A['mat'],B['mat'])) and gl and gl['maxratio']>=0.8:
            mr='caution'; mnote+=' bio-based layers close to saturation: dynamic simulation advised'
        sr,sn=struct_rule(A,B); dr,dn=disasm_rule(A,B)
        checks=dict(moisture=mr,structural=sr,fireacoustic=worst(frt,srt),disassembly=dr)
        rating=worst(*checks.values()); sc=sum(SC[v] for v in checks.values())/4
        fixes=[]
        if mr!='good': fixes.append('moisture: '+fix_text('moisture'))
        if sr!='good': fixes.append('structural: '+sn)
        if checks['fireacoustic']!='good': fixes.append(('fire: '+fix_text('fire')) if frt!='good' else ('sound: '+fix_text('sound')))
        if dr!='good': fixes.append('disassembly: '+dn)
        ifs.append(dict(A=A['mat'],B=B['mat'],checks=checks,rating=rating,score=sc,note='; '.join(x for x in (mnote,sn,dn) if x),fixes=fixes))
    # whole build-up
    mw=worst(*[i['checks']['moisture'] for i in ifs]) if ifs else 'good'
    sw=worst(*[i['checks']['structural'] for i in ifs]) if ifs else 'good'
    dw=sum(SC[i['checks']['disassembly']] for i in ifs)/len(ifs) if ifs else 100
    dwr='good' if dw>=75 else ('caution' if dw>=40 else 'critical')
    whole=dict(checks=dict(moisture=mw,structural=sw,fireacoustic=worst(frt,srt),disassembly=dwr),
               score=(SC[mw]+SC[sw]+SC[worst(frt,srt)]+dw)/4,glaser=gl['note'] if gl else 'n/a (interior / ground contact part)',fire=fnote,sound=snote)
    whole['rating']=worst(*whole['checks'].values())
    P['ifs']=ifs; P['whole']=whole
    P['c5']=(sum(i['score'] for i in ifs)/len(ifs) if ifs else 100.0)*0.5+whole['score']*0.5 if ifs else whole['score']

# ---------- 4. Level 2 ----------
for (a,p),P in parts.items():
    recs=P['layers']; V=sum(r['vol'] for r in recs)
    for r in recs: r['vs']=r['vol']/V
    crit={}
    for c in ('Durability','Environment','Cost'): crit[c]=sum(r['vs']*r['sc'][c] for r in recs)
    if len(recs)==1: crit['Well-being']=recs[0]['sc']['Well-being']
    else:
        rest=sum(r['vol'] for r in recs[1:]) or 1
        crit['Well-being']=0.5*recs[0]['sc']['Well-being']+0.5*sum(r['vol']/rest*r['sc']['Well-being'] for r in recs[1:])
    crit['Compatibility']=P['c5']
    P['crit']=crit; P['pts']={c:20*v/100 for c,v in crit.items()}; P['score']=sum(P['pts'].values()); P['V']=V
    for r in recs: r['contrib']=r['vs']*r['L1']
    P['vol_gfa']=V*AREA[p]
# ---------- 5. Level 3 ----------
RES={}
for a,(aname,pp) in ALT.items():
    W=sum(parts[(a,p)]['vol_gfa'] for p in pp)
    for p in pp: parts[(a,p)]['w']=parts[(a,p)]['vol_gfa']/W
    wt=sum(parts[(a,p)]['w']*parts[(a,p)]['score'] for p in pp); un=sum(parts[(a,p)]['score'] for p in pp)/len(pp)
    wc={c:sum(parts[(a,p)]['w']*parts[(a,p)]['pts'][c] for p in pp) for c in parts[(a,'OW')]['pts']}
    uc={c:sum(parts[(a,p)]['pts'][c] for p in pp)/len(pp) for c in parts[(a,'OW')]['pts']}
    life=sum(r['env_life']*AREA[p] for p in pp for r in parts[(a,p)]['layers'])
    a13=sum(r['env_a13']*AREA[p] for p in pp for r in parts[(a,p)]['layers'])
    cost=sum((r['cost0']+r['cost_ren'])*AREA[p] for p in pp for r in parts[(a,p)]['layers'])
    RES[a]=dict(name=aname,weighted=wt,unweighted=un,crit_w=wc,crit_u=uc,life_gwp=life,a13=a13,cost=cost,W=W)
rank={a:i+1 for i,a in enumerate(sorted(RES,key=lambda a:-RES[a]['weighted']))}
for a in RES: RES[a]['rank']=rank[a]; RES[a]['rank_u']=sorted(RES,key=lambda x:-RES[x]['unweighted']).index(a)+1
if __name__=='__main__':
    for a in RES:
        r=RES[a]; print(a,r['name'][:40],f"W={r['weighted']:.1f} U={r['unweighted']:.1f} r={r['rank']} ru={r['rank_u']} gwp={r['life_gwp']:.0f} cost={r['cost']:.0f}",{c[:3]:round(v,1) for c,v in r['crit_w'].items()})
    for p in PARTS:
        print(p,[ (a,round(parts[(a,p)]['score'],1),round(parts[(a,p)]['U'],3) if parts[(a,p)]['U'] else '-') for a in ALT])
