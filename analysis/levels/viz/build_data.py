import sys,json
sys.path.insert(0,'analysis/levels'); sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/compare6')
from score import *
import subprocess
sens=json.load(open('analysis/levels/report/sensitivity.json'))
KM={'Durability':'D','Environment':'E','Well-being':'W','Cost':'C','Compatibility':'K'}
d={'alts':[],'parts':list(PARTS.items()),'sens':sens}
SHORT={1:'RC + EPS ETICS',2:'Steel + mineral wool',3:'Masonry',4:'Timber–concrete',5:'Solid timber',6:'Timber frame + straw'}
for a in ALT:
    r=RES[a]; al=dict(id=a,name=r['name'],short=SHORT[a],life=round(r['life_gwp'],1),a13=round(r['a13'],1),cost=round(r['cost'],0),parts={})
    for p in PARTS:
        P=parts[(a,p)]
        al['parts'][p]=dict(w=round(P['w'],4),crit={KM[c]:round(v,2) for c,v in P['crit'].items()},U=round(P['U'],3) if P['U'] else None,Ut=P['Utarget'],rw=round(P['rw'],1) if P['rw'] else None,
          glaser=P['whole']['glaser'],fire=P['fire_note'],snd=P['snd_note'],whole=P['whole']['rating'],
          layers=[dict(m=l['mat'],t=round(l['t']*1000) if isinstance(l['t'],float) and l['mat'] not in('Steel frame',) else 0,fr=l['frac'],vs=round(l['vs'],4),life=l['life'],nrep=l['nrep'],
             sc=[round(l['sc'][c],1) for c in('Durability','Environment','Well-being','Cost')],a13=round(l['env_a13'],2),lg=round(l['env_life'],2),cost=round(l['cost0']+l['cost_ren'],1),pool=l['pool'],n=l['n']) for l in P['layers']],
          ifs=[dict(A=i['A'],B=i['B'],c=[i['checks']['moisture'],i['checks']['structural'],i['checks']['fireacoustic'],i['checks']['disassembly']],r=i['rating'],s=round(i['score']),fx=i['fixes'],note=i['note']) for i in P['ifs']])
    d['alts'].append(al)
import csv as _c
d['base']={r['alt']:dict(w=float(r['score_weighted']),rk=int(r['rank_weighted']),life=float(r['life_GWP_kgCO2e_per_m2GFA']),cost=float(r['cost_50y_EUR_per_m2GFA'])) for r in _c.DictReader(open('analysis/levels/baseline/scores_alternatives.csv'))}
d['fill']=[r for r in _c.DictReader(open('analysis/levels/dataset_fill_log.csv')) if r['status']=='changed']
d['fill']=[[r['material'],r['field'],r['old_assumption'],r['new_value'],r['dataset_row_and_provenance'].split(' ')[0],r['rule']] for r in d['fill']]
json.dump(d,open('analysis/levels/viz/data.json','w'),separators=(',',':'))
print(len(open('analysis/levels/viz/data.json').read()))
