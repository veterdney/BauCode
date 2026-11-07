"""Step 1: collapse OBD 2024-II rows (one per UUID x module) to one record per latest-version product.
Output: analysis/products.csv  (A2 indicators, per declared unit, plus density/thickness for conversion)."""
import csv, json, sys
csv.field_size_limit(10**9)
SRC='data/OBD_2024_II_2026-11-07T11_09_31.csv'
KEEP=['A1-A3','A4','A5','B4','C1','C2','C3','C4','D']
def num(s):
    try: return float(s.replace(',','.'))
    except: return None
meta={}; mod={}
for row in csv.DictReader(open(SRC,encoding='latin-1',newline=''),delimiter=';'):
    u=row['UUID']; v=row['Version']
    if u in meta and meta[u]['Version']>v: continue
    if u not in meta or meta[u]['Version']<v:
        meta[u]={k:row[k] for k in ['UUID','Version','Name (en)','Name (de)','Kategorie (en)','Typ','Referenzjahr','Gueltig bis','Bezugsgroesse','Bezugseinheit','Schuettdichte (kg/m3)','Flaechengewicht (kg/m2)','Rohdichte (kg/m3)','Schichtdicke (m)','Laengengewicht (kg/m)','Stueckgewicht (kg)','Umrechungsfaktor auf 1kg','biogener Kohlenstoffgehalt in kg','Declaration owner','Konformitaet']}
        mod[u]={}
    if row['Modul'] in KEEP and not row['Szenario']:
        mod[u][row['Modul']]={k:num(row[k]) for k in ['GWPtotal (A2)','GWPbiogenic (A2)','GWPfossil (A2)','PERT','PENRT','PERM','PENRM','AP (A2)','EPfreshwater (A2)','POCP (A2)','HTPc (A2)','HTPnc (A2)','PM (A2)','ODP (A2)','ADPE (A2)','WDP (A2)','RSF','SM','HWD','NHWD']}
    elif row['Modul'] in KEEP and row['Modul'] not in mod[u]:
        mod[u][row['Modul']]={k:num(row[k]) for k in ['GWPtotal (A2)','GWPbiogenic (A2)','GWPfossil (A2)','PERT','PENRT','PERM','PENRM','AP (A2)','EPfreshwater (A2)','POCP (A2)','HTPc (A2)','HTPnc (A2)','PM (A2)','ODP (A2)','ADPE (A2)','WDP (A2)','RSF','SM','HWD','NHWD']}
out=[]
for u,m in meta.items():
    d=dict(m)
    for mo,vals in mod[u].items():
        for k,x in vals.items(): d[f'{mo}|{k}']=x
    out.append(d)
keys=sorted({k for d in out for k in d})
w=csv.DictWriter(open('analysis/products.csv','w',newline='',encoding='utf-8'),fieldnames=keys)
w.writeheader(); w.writerows(out); print(len(out),'products')
