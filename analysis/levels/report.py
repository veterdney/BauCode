import sys, os, csv, random, collections, json, copy
sys.path.insert(0,'analysis/levels'); sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/compare6')
from score import *
OUT='analysis/levels/report'; os.makedirs(OUT,exist_ok=True)
CR=['Durability','Environment','Well-being','Cost','Compatibility']
F=lambda x,n=1:f"{x:.{n}f}"
ALTN={a:ALT[a][0] for a in ALT}
SHORT={1:'RC + EPS',2:'Steel + mineral wool',3:'Masonry',4:'Timber-concrete',5:'Solid timber',6:'Timber frame + straw'}
def layer_name(r):
    t=r['t']; return f"{r['mat']}" if r['mat'] in('Paint/covering','VCL','Sealing foil','Roof membrane','Roof tile','Window PVC','Window timber','Steel frame') else f"{r['mat']}"
def thick(r):
    if r['mat']=='Steel frame': return 'steel studs'
    if M[r['mat']].get('kind')=='area' or r['mat']=='Wood-concrete slab': return 'area product' if r['mat']!='Wood-concrete slab' else '~200 (composite)'
    return f"{r['t']*1000:.0f}"+(f" ×{r['frac']:.2f}" if r['frac']<1 else '')
def src(r):
    return f"OBD pool `{r['pool']}` n={r['n']} (GWPtotal(A2), PERT/PENRT, SM, HWD/NHWD, Rohdichte); [A] life, ratings, cost"
# well-being weights per layer (needed for loss attribution)
for (a,p),P in parts.items():
    recs=P['layers']
    if len(recs)==1: recs[0]['wbw']=1.0
    else:
        rest=sum(r['vol'] for r in recs[1:]); recs[0]['wbw']=0.5
        for r in recs[1:]: r['wbw']=0.5*r['vol']/rest
    for r in recs: r['loss']=P['w']*0.2*(r['vs']*(100-r['sc']['Durability'])+r['vs']*(100-r['sc']['Environment'])+r['wbw']*(100-r['sc']['Well-being'])+r['vs']*(100-r['sc']['Cost']))

# ---------- CSVs ----------
w=csv.writer(open(f'{OUT}/scores_alternatives.csv','w',newline='',encoding='utf-8'))
w.writerow(['alt','name','score_weighted','score_unweighted','rank_weighted','rank_unweighted']+[f'pts_{c}_weighted' for c in CR]+['life_GWP_kgCO2e_per_m2GFA','A1A3_GWP_kgCO2e_per_m2GFA','cost_50y_EUR_per_m2GFA'])
for a in ALT:
    r=RES[a]; w.writerow([a,r['name'],round(r['weighted'],2),round(r['unweighted'],2),r['rank'],r['rank_u']]+[round(r['crit_w'][c],2) for c in CR]+[round(r['life_gwp'],1),round(r['a13'],1),round(r['cost'],1)])
w=csv.writer(open(f'{OUT}/scores_parts.csv','w',newline='',encoding='utf-8'))
w.writerow(['alt','part','score','weight_share']+[f'pts_{c}' for c in CR]+['U_W_m2K','Rw_dB'])
for (a,p),P in parts.items(): w.writerow([a,p,round(P['score'],2),round(P['w'],4)]+[round(P['pts'][c],2) for c in CR]+[round(P['U'],3) if P['U'] else '',round(P['rw'],1) if P['rw'] else ''])
w=csv.writer(open(f'{OUT}/scores_layers.csv','w',newline='',encoding='utf-8'))
w.writerow(['alt','part','idx','layer','thickness_m','fraction','volume_share','life_y','renewals_50y','score_Durability','score_Environment','score_Well-being','score_Cost','L1_mean','a13_kgCO2e_m2','life_gwp_kgCO2e_m2','penrt_MJ_m2','renewable_share','recycled_share','waste_kg_m2','cost0_EUR_m2','cost_renewals_EUR_m2','mass_kg_m2','n_EPDs','OBD_UUIDs'])
for r in inst: w.writerow([r['alt'],r['part'],r['idx'],r['mat'],round(r['t'],4) if isinstance(r['t'],float) else r['t'],r['frac'],round(r['vs'],4),r['life'],r['nrep']]+[round(r['sc'][c],1) for c in CRIT]+[round(r['L1'],1),round(r['env_a13'],3),round(r['env_life'],3),round(r['env_pen'],2),round(r['env_ren'],3),round(r['env_rec'],3),round(r['env_waste'],3),round(r['cost0'],2),round(r['cost_ren'],2),round(r['mass'],2),r['n'],' '.join(r['uuids'])])
w=csv.writer(open(f'{OUT}/scores_interfaces.csv','w',newline='',encoding='utf-8'))
w.writerow(['alt','part','layer_A','layer_B','moisture','structural','fire_acoustics','disassembly','rating','score','note'])
for (a,p),P in parts.items():
    for i in P['ifs']: w.writerow([a,p,i['A'],i['B'],i['checks']['moisture'],i['checks']['structural'],i['checks']['fireacoustic'],i['checks']['disassembly'],i['rating'],round(i['score'],1),i['note']])

# ---------- per-alternative files ----------
def layers_table(P):
    o=["| # | Layer | mm | Vol. share | Durab. | Envir. | Well-b. | Cost | Contribution (vol. × mean) | Data source |","|---|---|---|---|---|---|---|---|---|---|"]
    for r in P['layers']:
        o.append(f"| {r['idx']+1} | {layer_name(r)} | {thick(r)} | {100*r['vs']:.1f} % | {F(r['sc']['Durability'],0)} | {F(r['sc']['Environment'],0)} | {F(r['sc']['Well-being'],0)} | {F(r['sc']['Cost'],0)} | {F(r['contrib'])} | {src(r)} |")
    return o
def compat_table(P):
    o=["| Interface (A / B) | Moisture | Structural | Fire & acoustics | Disassembly | Rating | Fix if needed |","|---|---|---|---|---|---|---|"]
    for i in P['ifs']:
        c=i['checks']; fx='; '.join(i['fixes']) if i['rating']!='good' else '-'
        o.append(f"| {i['A']} / {i['B']} | {c['moisture']} | {c['structural']} | {c['fireacoustic']} | {c['disassembly']} | **{i['rating']}** | {fx} |")
    wh=P['whole']; c=wh['checks']
    o.append(f"| **Whole build-up** | {c['moisture']} | {c['structural']} | {c['fireacoustic']} | {c['disassembly']} | **{wh['rating']}** | Glaser: {wh['glaser']}; fire: {wh['fire']}; sound: {wh['sound']} |")
    return o
def prose(a,p,P):
    recs=P['layers']; best=max(recs,key=lambda r:r['L1']); worstl=min(recs,key=lambda r:r['L1'])
    bad=[i for i in P['ifs'] if i['rating']!='good']; wi=min(P['ifs'],key=lambda i:i['score']) if P['ifs'] else None
    s=[]
    if P['U']: s.append(f"Build-up reaches U = {P['U']:.3f} W/m²K (target {P['Utarget']}, λ and μ values are [A]); steady-state Glaser check: {P['whole']['glaser']}.")
    else: s.append(f"No U-value target applies; {P['snd_note']}.")
    s.append(f"Layers work together as follows: {', '.join(r['mat'] for r in recs)} (inside to outside); strongest layer is {best['mat']} (mean score {best['L1']:.0f}), weakest is {worstl['mat']} ({worstl['L1']:.0f}, lowest in {min(worstl['sc'],key=worstl['sc'].get)}).")
    if wi: s.append(f"Weakest link: {wi['A']} / {wi['B']} ({wi['rating']}, score {wi['score']:.0f}){' – '+wi['fixes'][0] if wi['fixes'] else ''}.")
    else: s.append("Single-layer part: no interfaces to assess.")
    if bad: s.append(f"{len(bad)} of {len(P['ifs'])} interfaces are not rated good; the most frequent issue can be removed by: {P['ifs'][P['ifs'].index(wi)]['fixes'][0] if wi and wi['fixes'] else 'detailing'}.")
    s.append(f"Part score {P['score']:.1f}/100 (Durability {P['pts']['Durability']:.1f}, Environment {P['pts']['Environment']:.1f}, Well-being {P['pts']['Well-being']:.1f}, Cost {P['pts']['Cost']:.1f}, Compatibility {P['pts']['Compatibility']:.1f} of 20).")
    return ' '.join(s)
for a in ALT:
    o=[f"# Alternative {a}: {ALTN[a]}",'',f"Weighted score **{RES[a]['weighted']:.1f}/100** (rank {RES[a]['rank']}), unweighted {RES[a]['unweighted']:.1f}. Method: see `README.md`. Scores are 0–100 (100 = best). Layer scores are min–max normalised among all layers with the same job across all six alternatives.",'']
    for p,pn in PARTS.items():
        P=parts[(a,p)]
        o+= [f"## {a}{p.lower()}. {pn} — {P['score']:.1f}/100 (share of building volume {100*P['w']:.1f} %)",'',f"**Layer table** (inside to outside; floors and ground slab top to bottom)",'']+layers_table(P)+['','**Compatibility table**','']+compat_table(P)+['',prose(a,p,P),'']
    open(f'{OUT}/alt-{a}.md','w').write('\n'.join(o))

# ---------- sensitivity (recompute from raw layer indicators) ----------
def recompute(mod=None,use_compat=True,w_unweighted=False):
    I=[dict(r) for r in inst]
    if mod: mod(I)
    byj=collections.defaultdict(list)
    for r in I: byj[r['job']].append(r)
    for job,rs in byj.items():
        for k,h in HIGH.items():
            v=[r[k] for r in rs]; lo,hi=min(v),max(v)
            for r in rs: r.setdefault('s2',{})[k]=50.0 if hi-lo<1e-12 else (100*(r[k]-lo)/(hi-lo) if h else 100*(hi-r[k])/(hi-lo))
    score={}
    for a in ALT:
        pts=[]; ws=[]
        for p in PARTS:
            P=parts[(a,p)]; rs=[r for r in I if r['alt']==a and r['part']==p]
            sc=lambda r,c:sum(r['s2'][k] for k in CRIT[c])/len(CRIT[c])
            V=sum(r['vol'] for r in rs); d=sum(r['vol']/V*sc(r,'Durability') for r in rs); e=sum(r['vol']/V*sc(r,'Environment') for r in rs); co=sum(r['vol']/V*sc(r,'Cost') for r in rs)
            if len(rs)==1: wb=sc(rs[0],'Well-being')
            else:
                rest=sum(r['vol'] for r in rs[1:]); wb=0.5*sc(rs[0],'Well-being')+0.5*sum(r['vol']/rest*sc(r,'Well-being') for r in rs[1:])
            tot=(d+e+wb+co+(P['crit']['Compatibility'] if use_compat else 0))/(5 if use_compat else 4)
            pts.append(tot); ws.append(P['vol_gfa'])
        score[a]=sum(x*y for x,y in zip(pts,ws))/sum(ws) if not w_unweighted else sum(pts)/len(pts)
    return score
def rk(sc): return {a:i+1 for i,a in enumerate(sorted(sc,key=lambda a:-sc[a]))}
SCEN={}
SCEN['Base']=recompute()
SCEN['No compatibility criterion (4 criteria)']=recompute(use_compat=False)
SCEN['Unweighted parts']=recompute(w_unweighted=True)
def neutral(I):
    for r in I: r['dur_mfp']=3; r['wb_voc']=3; r['wb_buf']=3; r['wb_snd']=3
SCEN['All assumed ratings neutral (3)']=recompute(neutral)
def nocost(I):
    for r in I: r['cost0']=1.0; r['cost_ren']=1.0
SCEN['Cost criterion neutral']=recompute(nocost)
def shortlife(I):
    for r in I: r['dur_life']=r['dur_life']*(0.7 if r['mat'] in('CLT','KVH','OSB','Straw bale','Wood fibre','Cellulose','Wood-concrete slab','Window timber','Clay plaster') else 1.0)
SCEN['Service lives of timber/bio-based layers and timber windows -30 %']=recompute(shortlife)
random.seed(7); win=collections.Counter(); top3=collections.Counter(); N=400
for _ in range(N):
    fc={m:random.uniform(0.8,1.2) for m in M}; fl={m:random.uniform(0.8,1.2) for m in M}; dr={m:random.choice((-1,0,1)) for m in M}
    def mc(I):
        for r in I:
            r['cost0']*=fc[r['mat']]; r['cost_ren']*=fc[r['mat']]; r['dur_life']*=fl[r['mat']]
            for k in ('dur_mfp','wb_voc','wb_buf','wb_snd'): r[k]=min(5,max(1,r[k]+random.choice((-1,0,1))))
    s=recompute(mc); o_=sorted(s,key=lambda a:-s[a]); win[o_[0]]+=1
    for a in o_[:3]: top3[a]+=1

# ---------- README ----------
o=[]; A=o.append
A("# Three-level scoring of six structural systems — 500 m² residential, Germany, 2–3 storeys, 50 years\n")
A("Level 1: layer (material) · Level 2: building part (incl. layer compatibility) · Level 3: whole building. All scores 0–100, 100 = best.\n")
A("Facts come only from the Ökobaudat 2024-II CSV (`data/OBD_2024_II_2026-11-07T11_09_31.csv`, reduced to `analysis/products.csv`): GWP (`GWPtotal (A2)`), PERT, PENRT, SM, HWD, NHWD, density, modules A1-A3 and C1–C4.")
A("The data set has **no** cost, service-life, VOC, moisture-buffering, sound, fire or vapour-resistance data. These are marked **[A]** (ASSUMPTION) and listed in section 6.")
A("Read the ranking as a transparent model: the Environment criterion and part of Well-being are data-driven; Durability, Cost, Compatibility and the rest of Well-being rest on assumptions.\n")
A("Files: `alt-1.md` … `alt-6.md` (all layer and compatibility tables), `scores_*.csv` (comma-separated, `.` decimal): alternatives, parts, layers, interfaces.\n")
A("## 1. Summary\n")
A("Points per criterion are the volume-weighted mean of the part points (each criterion max 20, total max 100).\n")
A("| Rank | Alternative | Weighted total | Unweighted | Durability /20 | Environment /20 | Well-being /20 | Cost /20 | Compatibility /20 |\n|---|---|---|---|---|---|---|---|---|")
for a in sorted(RES,key=lambda a:RES[a]['rank']):
    r=RES[a]; A(f"| {r['rank']} | {a}. {r['name']} | **{r['weighted']:.1f}** | {r['unweighted']:.1f} (rank {r['rank_u']}) | "+' | '.join(F(r['crit_w'][c]) for c in CR)+" |")
dif=[(a,RES[a]['weighted']-RES[a]['unweighted']) for a in ALT]
A(f"\nVolume weighting changes the totals by {min(d for _,d in dif):+.1f} to {max(d for _,d in dif):+.1f} points. Ranks differ between weighted and unweighted for: "+', '.join(f"{a} ({RES[a]['rank']} vs {RES[a]['rank_u']})" for a in ALT if RES[a]['rank']!=RES[a]['rank_u'])+". Ground slab, outer wall, roof and floor carry most of the volume weight; windows carry 1–2 %.\n")
A("Part scores (0–100):\n")
A("| Part | "+' | '.join(f"{a}. {SHORT[a]}" for a in ALT)+" |\n|---|"+"---|"*6)
for p,pn in PARTS.items(): A(f"| {pn} | "+' | '.join(F(parts[(a,p)]['score']) for a in ALT)+" |")
A("\nWeights (share of building material volume, per alternative):\n")
A("| Part | "+' | '.join(str(a) for a in ALT)+" |\n|---|"+"---|"*6)
for p,pn in PARTS.items(): A(f"| {pn} | "+' | '.join(f"{100*parts[(a,p)]['w']:.0f} %" for a in ALT)+" |")
A("\nKey data per m² GFA (structure + envelope + windows; windows' volume is small by construction):\n")
A("| Alternative | GWP A1–A3 (kgCO₂e) | GWP life cycle 50 y (kgCO₂e) | Cost incl. renewals 50 y (€, [A]) |\n|---|---|---|---|")
for a in ALT: A(f"| {a}. {SHORT[a]} | {RES[a]['a13']:.0f} | {RES[a]['life_gwp']:.0f} | {RES[a]['cost']:.0f} |")
A("\n## 2. Layer and compatibility tables\n")
A("One file per alternative, one section per building part: `alt-1.md` … `alt-6.md`. Each section has the layer table, the compatibility table and a short explanation.\n")
A("## 3. Inner vs. outer wall\n")
A("| Alt | Outer wall (in→out) | Load-bearing inner wall | Partition | Room-facing layer, 50 % of well-being weight (OW / IL / IP) |\n|---|---|---|---|---|")
def lst(P): return ' / '.join(f"{r['mat']}{'' if M[r['mat']].get('kind')=='area' else ' '+str(int(round(r['t']*1000)))}" for r in P['layers'] if r['mat']!='Paint/covering' and r['mat']!='Steel frame')
def wbtop(P):
    rs=sorted(P['layers'],key=lambda r:-(r['sc']['Well-being']*(0.5 if r['idx']==0 else 0.5*r['vol']/sum(x['vol'] for x in P['layers'][1:]) if len(P['layers'])>1 else 1)))
    return rs[0]['mat']
for a in ALT: A(f"| {a}. {SHORT[a]} | {lst(parts[(a,'OW')])} | {lst(parts[(a,'IL')])} | {lst(parts[(a,'IP')])} | {parts[(a,'OW')]['layers'][0]['mat']} / {parts[(a,'IL')]['layers'][0]['mat']} / {parts[(a,'IP')]['layers'][0]['mat']} |")
A("\nWhy they differ: outer walls must carry weather, insulation (U ≤ 0.20 W/m²K [A]) and moisture control, so they have an outside render or plaster, a thick insulation layer and a vapour-diffusion order that dries outward; inner walls have no U target and instead need mass or lining for sound (separating wall Rw ≥ 53 dB [A]), fire (REI/EI 30 [A]) and thermal mass, and their two faces are both room-facing.")
A("\nPart scores outer vs. inner (0–100):\n")
A("| Alt | Outer wall | Inner load-bearing | Partition | Well-being points OW /20 | IL /20 | IP /20 |\n|---|---|---|---|---|---|---|")
for a in ALT: A(f"| {a}. {SHORT[a]} | {F(parts[(a,'OW')]['score'])} | {F(parts[(a,'IL')]['score'])} | {F(parts[(a,'IP')]['score'])} | {F(parts[(a,'OW')]['pts']['Well-being'])} | {F(parts[(a,'IL')]['pts']['Well-being'])} | {F(parts[(a,'IP')]['pts']['Well-being'])} |")
ow=sorted(ALT,key=lambda a:-parts[(a,'OW')]['pts']['Well-being']); il=sorted(ALT,key=lambda a:-parts[(a,'IL')]['pts']['Well-being'])
_o=', '.join("%d (%.1f)"%(x,parts[(x,'OW')]['pts']['Well-being']) for x in ow); _i=', '.join("%d (%.1f)"%(x,parts[(x,'IL')]['pts']['Well-being']) for x in il)
A("\nOuter-wall well-being points rank "+_o+"; load-bearing inner wall: "+_i+".")
A("The room-facing layer carries 50 % of the weight, so clay plaster (alternative 6) wins on both walls (VOC 5 and buffering 5 [A]); paint on a plastered or concrete surface scores low on buffering [A]. Differences between alternatives 4 and 5 on the outer wall come from the layers behind the same bare CLT (rock wool vs. wood fibre, buffering 2 vs. 4 [A]).\n")
A("## 4. Score contribution\n")
A("Share of each criterion in the weighted total, and the part and layer that cost the most points (loss = weight × shortfall from 100).\n")
A("| Alt | Durab. | Envir. | Well-b. | Cost | Compat. | Part costing most | Layer costing most |\n|---|---|---|---|---|---|---|---|")
for a in ALT:
    r=RES[a]; tot=r['weighted']; sh=[100*r['crit_w'][c]/tot for c in CR]
    pl=max(PARTS,key=lambda p:parts[(a,p)]['w']*(100-parts[(a,p)]['score']))
    ly=max([x for p in PARTS for x in parts[(a,p)]['layers']],key=lambda x:x['loss'])
    A(f"| {a}. {SHORT[a]} | "+' | '.join(f"{x:.0f} %" for x in sh)+f" | {PARTS[pl]} (−{parts[(a,pl)]['w']*(100-parts[(a,pl)]['score']):.1f}) | {ly['mat']} in {PARTS[ly['part']].lower()} (−{ly['loss']:.2f}) |")
A("\n## 5. Conclusion\n")
bw=min(RES,key=lambda a:RES[a]['rank']);
A(f"**Best overall: alternative {bw}, {ALTN[bw]}** — {RES[bw]['weighted']:.1f} weighted, {RES[bw]['unweighted']:.1f} unweighted. It also leads after volume weighting is removed.\n")
A("Best when one criterion matters most (weighted points /20):\n")
A("| Priority | Best alternative | Points | Runner-up |\n|---|---|---|---|")
for c in CR:
    o2=sorted(ALT,key=lambda a:-RES[a]['crit_w'][c]); A(f"| {c} | {o2[0]}. {SHORT[o2[0]]} | {RES[o2[0]]['crit_w'][c]:.1f} | {o2[1]}. {SHORT[o2[1]]} ({RES[o2[1]]['crit_w'][c]:.1f}) |")
A("\nInterfaces rated **critical** (each needs the named fix; scores above are before the fix):\n")
A("| Alt | Part | Interface | Failing check(s) | Fix |\n|---|---|---|---|---|")
_n=0
for (a,p),P in parts.items():
    for i in P['ifs']:
        if i['rating']=='critical':
            ch=', '.join(k for k,v in i['checks'].items() if v=='critical'); _n+=1
            A(f"| {a} | {PARTS[p]} | {i['A']} / {i['B']} | {ch} | {'; '.join(i['fixes'])[:260]} |")
A(f"\n{_n} of {sum(len(P['ifs']) for P in parts.values())} interfaces are critical; the count per alternative is in `scores_interfaces.csv`.\n")
# mix: best part per part
mix={p:max(ALT,key=lambda a:parts[(a,p)]['score']) for p in PARTS}
vol={p:parts[(mix[p],p)]['vol_gfa'] for p in PARTS}; Wm=sum(vol.values())
mixscore=sum(vol[p]/Wm*parts[(mix[p],p)]['score'] for p in PARTS)
gs_best=max(ALT,key=lambda a:parts[(a,'GS')]['score'])
base6=RES[bw]['weighted']
mix2={p:(gs_best if p=='GS' else bw) for p in PARTS}
vol2={p:parts[(mix2[p],p)]['vol_gfa'] for p in PARTS}; W2=sum(vol2.values()); mix2score=sum(vol2[p]/W2*parts[(mix2[p],p)]['score'] for p in PARTS)
A("\n**Best mix.** Taking the best-scoring build-up for each part:\n")
A("| Part | Taken from | Part score |\n|---|---|---|")
for p,pn in PARTS.items(): A(f"| {pn} | {mix[p]}. {SHORT[mix[p]]} | {parts[(mix[p],p)]['score']:.1f} |")
A(f"\nVolume-weighted score of this mix: **{mixscore:.1f}** vs {base6:.1f} for the best single system ({bw}). The gain of {mixscore-base6:+.1f} points comes only from the outer wall ({mix['OW']}) and the window ({mix['WI']}); a mix needs junction details (different movement, airtightness, thermal bridges) that this model does not score, so it is an upper bound and not worth the added complexity.")
A(f"Foundation: all six alternatives use a reinforced concrete ground slab; alternatives 4, 5 and 6 insulate it with foam glass and score highest ({parts[(gs_best,'GS')]['score']:.1f} for alternative {gs_best}). Alternative {bw} therefore already is the concrete-foundation, timber-superstructure combination; swapping in another system's ground slab changes nothing material ({mix2score:.1f}).\n")
A("## 6. Assumptions, data gaps, sensitivity\n")
A("None of the following is in the OBD data set.\n")
A("| # | ASSUMPTION | Value used | Reason |\n|---|---|---|---|")
rows=[("Building geometry per m² GFA","outer wall 0.68, windows 0.17, inner load-bearing wall 0.35, partitions 0.50, floor/ceiling 0.60, roof 0.40, ground slab 0.40 m²","2–3 storeys, ~200 m² footprint, 20 % glazing; no plan given"),
("U-value targets","outer wall 0.20, roof 0.14, ground slab 0.25 W/m²K; windows not solved","stricter than GEG reference values (0.28/0.20/0.35) so the walls need no early retrofit"),
("Thermal conductivity λ","rock wool 0.036, EPS/XPS 0.035, wood fibre 0.040, cellulose 0.039, straw 0.052, foam glass 0.045, brick 0.12, RC 2.0, CLT/KVH 0.13","no λ in OBD; typical declared values"),
("Vapour resistance μ / sd","e.g. RC 80, brick 8, CLT 50, EPS 40, rock wool 1, wood fibre 5, straw 2; VCL sd 10 m (pitched) or 100 m (flat roof), roof membrane sd 100 m","no μ in OBD; Glaser steady state, Berlin-type design climate per DIN 4108-3 (−5 °C/80 %, 20 °C/50 %, 90 d)"),
("Layer thicknesses and build-ups","see alt-*.md","typical practice; thickness of insulation solved and rounded up to 10 mm"),
("Fire requirement","REI/EI 30 (Gebäudeklasse 3)","2–3 storeys, ≤ 7 m; GK 4 would need REI 60 and change timber ratings"),
("Sound requirement","Rw ≥ 53 dB separating wall, 54 dB floor, 40 dB outer wall/roof, 35 dB partition, 32 dB window","DIN 4109 style; estimated by mass law R = 32.4 lg m′ − 26 (+4 dB floating screed), or typical framed values for lightweight walls"),
("Service lives (y)","structure 100 (CLT/KVH 100, composite slabs 100), render/ETICS 40, plasterboard 50, paint 12, membranes 30–50, windows 35","no service-life field in OBD"),
("Ratings 1–5 for moisture/fire/pest, VOC, buffering, sound contribution","per material in `materials.py`","qualitative judgement; OBD has no emissions or hygric data"),
("Cost (€/m³, €/m², € per renewal)","e.g. RC 470 €/m³, CLT 850, rock wool 180, render 4,600 (≈ 55 €/m²), plastic window 520 €/m², timber window 780 €/m²","no cost data in OBD; indicative German installed prices"),
("Operating-cost effect","none (equal for all alternatives)","same GEG standard, floor plan and U-values; not included as an indicator"),
("Level-2 criterion weights","five criteria × 20 pts; interface = mean of four checks (good 100, caution 50, critical 0); criterion 5 = mean of interface mean and whole-build-up score","prescribed by the brief"),
("Gravel and fill","natural-stone EPD scaled to 1,600 kg/m³ bulk density; pumice fill EPD","no gravel EPD in OBD"),
("Clay block","fired brick EPD 'Brick (unfilled)' 365 mm; sand-lime brick for inner walls","clay-block unit EPD not found by name; swap allowed"),
("Hempcrete","straw bale used in alternative 6","no hempcrete wall EPD in OBD (hemp stone: 2 EPDs)"),
("Wood-concrete slab","one OBD EPD, 274 kg/m²","only one in OBD")]
for i,(x,y,z) in enumerate(rows,1): A(f"| {i} | {x} | {y} | {z} |")
A("\n**Data gaps in OBD:** `SM` is empty for most bio-based EPDs (recycled share looks 0); steel sections 3 EPDs, straw 2, cellulose 2, fired brick 3, roof tile 1, timber window 1, composite slab 1; EPDs mix generic, average and specific datasets and are medians; biogenic carbon (negative A1–A3, positive C3) is shown without dynamic accounting; windows are whole-unit EPDs, so frame, glazing and sealant cannot be scored separately; mass-law sound estimates ignore decoupling.\n")
A("**Sensitivity** (rank of each alternative, weighted score in brackets):\n")
A("| Scenario | "+' | '.join(str(a) for a in ALT)+" |\n|---|"+"---|"*6)
for n,s in SCEN.items():
    r=rk(s); A(f"| {n} | "+' | '.join(f"{r[a]} ({s[a]:.1f})" for a in ALT)+" |")
A(f"\nMonte Carlo ({N} draws: cost ±20 %, service life ±20 % per material, each 1–5 rating ±1): first place — "+', '.join(f"{a}: {100*win[a]/N:.0f} %" for a in ALT)+"; top three — "+', '.join(f"{a}: {100*top3[a]/N:.0f} %" for a in ALT)+".")
open(f'{OUT}/README.md','w').write('\n'.join(o))
json.dump(dict(scen={n:s for n,s in SCEN.items()},win=dict(win),top3=dict(top3),mix=mix,mixscore=mixscore,mix2score=mix2score),open(f'{OUT}/sensitivity.json','w'),indent=1)
print('\n'.join(o[o.index('## 1. Summary'):][:60]))
