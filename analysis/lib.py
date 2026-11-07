import csv, statistics as st, re
ROWS=list(csv.DictReader(open('analysis/products.csv',encoding='utf-8')))
def f(x):
    try: return float(x)
    except: return None
def dens(r):
    return f(r['Rohdichte (kg/m3)']) or f(r['Schuettdichte (kg/m3)'])
def per_m3(r,mod):
    """indicator-basis conversion helper: returns multiplier to get value per m3 of material, or None"""
    u=r['Bezugseinheit']; q=f(r['Bezugsgroesse']) or 1; d=dens(r)
    if u=='m3': return 1/q
    if u=='kg':
        fac=f(r['Umrechungsfaktor auf 1kg'])
        return d/q if d else None
    if u=='qm':
        t=f(r['Schichtdicke (m)'])
        return 1/(q*t) if t else None
    return None
def val(r,mod,key='GWPtotal (A2)'):
    return f(r.get(f'{mod}|{key}',''))
def per_m3_val(r,mod,key='GWPtotal (A2)'):
    v=val(r,mod,key); m=per_m3(r,mod)
    return None if v is None or m is None else v*m
def select(catpat,namepat=None,excl=None):
    out=[]
    for r in ROWS:
        if re.search(catpat,r['Kategorie (en)'],re.I) and (not namepat or re.search(namepat,r['Name (en)'],re.I)) and not (excl and re.search(excl,r['Name (en)'],re.I)):
            if val(r,'A1-A3') is not None and per_m3(r,'A1-A3'): out.append(r)
    return out
