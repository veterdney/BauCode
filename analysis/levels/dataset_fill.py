"""Fill earlier ASSUMPTIONS from data/Building material property dataset.csv (40 materials, M01-M40).
Rules: single value -> use it; range -> keep the earlier value if it lies inside the range, else midpoint.
Costs are converted from the dataset's unit to EUR per m3 of layer (or EUR/m2, EUR/kg) using the thickness named in the dataset.
Every change is logged to analysis/levels/dataset_fill_log.csv with the dataset's own provenance tag."""
import csv, os, math
DS='data/Building material property dataset.csv'
ROWS={r['material_id']:r for r in csv.DictReader(open(DS,encoding='utf-8'))}
# our material key -> dataset id; cost_div: thickness (m) the dataset's EUR/m2 refers to; None = already per m3 / per t
MAP={'RC':('M02',None),'Brick':('M05',0.365),'Sand-lime':('M06',0.175),'AAC':('M07',0.365),'CLT':('M14',None),'KVH':('M12',None),
 'Steel frame':('M09','t'),'EPS':('M18',0.15),'XPS':('M19',0.14),'Rock wool':('M20',0.16),'Wood fibre':('M23',0.18),'Cellulose':('M24',0.22),
 'Straw bale':('M26',0.42),'Foam glass':('M28',0.16),'Gypsum board':('M16',0.05),'OSB':('M15',0.02),'Mineral render':('M38',0.014),
 'Clay plaster':('M30',0.0175),'Lime plaster':('M29',0.015),'Screed':('M03',0.057),'Roof membrane':('M36','m2'),
 'Window PVC':('M37','m2'),'Window timber':('M37','m2')}
VOC={'L':5,'L-M':4,'M':3,'M-H':2,'H':1}
def f(x):
    try: return float(x)
    except: return None
def pick(old,lo,hi):
    if lo is None or hi is None: return old,'kept (no dataset value)'
    if lo==hi: return lo,'dataset single value'
    if lo<=old<=hi: return old,'kept: inside dataset range %g-%g'%(lo,hi)
    return (lo*hi)**.5 if lo>0 and hi>0 and hi/lo>20 else (lo+hi)/2,'dataset range midpoint'
def apply(M,log):
    def put(k,field,new,src,note):
        old=M[k].get(field)
        if new is None: return
        if isinstance(new,float): new=round(new,4)
        if old!=new: M[k][field]=new
        log.append([k,field,old,new,src,note,'changed' if old!=new else 'same'])
    for k,(mid,div) in MAP.items():
        d=ROWS[mid]; m=M[k]
        lam=pick(m['lam'],f(d['lambda_min_W_mK']),f(d['lambda_max_W_mK']))
        if m['lam']>0 and lam[0]: put(k,'lam',lam[0],mid+' '+d['lambda_prov'],lam[1])
        lo,hi=f(d['mu_min']),f(d['mu_max'])
        if m.get('mu') is not None and lo is not None and hi is not None and hi<1e4:
            mu=pick(m['mu'],lo,hi); put(k,'mu',mu[0],mid+' '+d['mu_prov'],mu[1])
        sl=f(d['service_life_years_used'])
        if sl and m.get('kind')!='area':
            if m['job']=='insulation' and sl<50: sl=50; note='dataset %s (ETICS context) -> 50 inside constructions; ETICS builds keep 40'%d['service_life_years_used']
            else: note='dataset service_life_years_used'
            put(k,'life',int(sl),mid+' '+d['service_life_prov'][:40],note)
        elif sl: put(k,'life',int(sl),mid+' '+d['service_life_prov'][:40],'dataset service_life_years_used')
        tl=f(d['technical_life_years'])
        if tl: put(k,'tech',int(tl),mid+' '+d['technical_life_prov'][:30],'dataset technical life, used for the durability indicator only')
        mr=f(d['R_D2'])
        if mr: put(k,'mfp',int(mr),mid+' '+d['moisture_resistance_prov'],'dataset R_D2 moisture resistance')
        r=d['iaq_outgassing_risk'].split(' ')[0]
        if r in VOC: put(k,'voc',VOC[r],mid+' '+d['iaq_prov'],'dataset IAQ risk %s'%d['iaq_outgassing_risk'])
        wb=f(d['R_WB3'])
        if wb: put(k,'buf',int(wb),mid+' '+d['wellbeing_prov'],'dataset R_WB3 sensory/hygric score')
        c=f(d['cost_mid_eur'])
        if c:
            if div is None: new=c; unit='EUR/m3'
            elif div=='t': new=c/1000.0*7850.0; unit='EUR/m3 steel (3750 EUR/t)'
            elif div=='m2': new=c; unit='EUR/m2'
            else: new=c/div; unit='EUR/m3 = %g EUR/m2 / %g m'%(c,div)
            if 'costm2' in m and k=='Wood-concrete slab': pass
            put(k,'cost',new,mid+' '+d['cost_prov'][:34],unit)
# U targets: GModG Anlage 1 reference building (new build), from the dataset
U_REF={'OW':f(ROWS['M18']['U_GModG_Anl1_reference_new_W_m2K']),'GS':f(ROWS['M02']['U_GModG_Anl1_reference_new_W_m2K'])}
U_REF['RF']=f(ROWS['M36']['U_GModG_Anl1_reference_new_W_m2K']) or 0.20
def write_log(log,path='analysis/levels/dataset_fill_log.csv'):
    w=csv.writer(open(path,'w',newline='',encoding='utf-8')); w.writerow(['material','field','old_assumption','new_value','dataset_row_and_provenance','rule','status']); w.writerows(log)
