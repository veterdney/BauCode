import csv, statistics as st, re, math
PRODUCTS_CSV='analysis/products.csv'
ROWS=None   # loaded on first use by all_rows(); importing this module needs no data file
def load_rows(path=PRODUCTS_CSV):
    with open(path,encoding='utf-8') as fh: return list(csv.DictReader(fh))
def all_rows():
    global ROWS
    if ROWS is None: ROWS=load_rows()
    return ROWS
def f(x):
    try: return float(x)
    except: return None
def dens(r):
    return f(r['Rohdichte (kg/m3)']) or f(r['Schuettdichte (kg/m3)'])
def ref_quantity(r):
    """declared reference quantity (Bezugsgroesse) -> (q, None) or (None, error code); never defaults"""
    raw=r.get('Bezugsgroesse')
    if raw is None or str(raw).strip()=='': return None,'REF_QTY_BLANK'
    q=f(raw)
    if q is None: return None,'REF_QTY_NOT_NUMERIC'
    if not math.isfinite(q): return None,'REF_QTY_NOT_FINITE'
    if q<=0: return None,'REF_QTY_NOT_POSITIVE'
    return q,None
def per_m3_checked(r,mod=None):
    """(multiplier to get value per m3 of material, None) or (None, error code)"""
    q,err=ref_quantity(r)
    if err: return None,err
    u=r['Bezugseinheit']; d=dens(r)
    if u=='m3': return 1/q,None
    if u=='kg':
        return (d/q,None) if d else (None,'DENSITY_REQUIRED')
    if u=='qm':
        t=f(r['Schichtdicke (m)'])
        return (1/(q*t),None) if t else (None,'THICKNESS_REQUIRED')
    return None,'UNIT_UNSUPPORTED'
def per_m3(r,mod):
    """indicator-basis conversion helper: returns multiplier to get value per m3 of material, or None"""
    return per_m3_checked(r,mod)[0]
def val(r,mod,key='GWPtotal (A2)'):
    return f(r.get(f'{mod}|{key}',''))
def per_m3_val(r,mod,key='GWPtotal (A2)'):
    v=val(r,mod,key); m=per_m3(r,mod)
    return None if v is None or m is None else v*m
LENGTH_TO_M={'m':1.0,'cm':0.01,'mm':0.001}
def to_metres(value,unit):
    """layer thickness -> (metres, None) or (None, error code)"""
    # type first: a dict/list unit is unhashable and would raise TypeError on the membership test
    if not isinstance(unit,str) or unit not in LENGTH_TO_M: return None,'THICKNESS_UNIT_UNSUPPORTED'
    v=f(value) if not isinstance(value,bool) else None
    if v is None or not math.isfinite(v) or v<=0: return None,'THICKNESS_INVALID'
    return v*LENGTH_TO_M[unit],None
def layer_mass_kg(area_m2,thickness_m,density):
    return area_m2*thickness_m*density
def select(catpat,namepat=None,excl=None,rows=None):
    out=[]
    for r in (rows if rows is not None else all_rows()):
        if re.search(catpat,r['Kategorie (en)'],re.I) and (not namepat or re.search(namepat,r['Name (en)'],re.I)) and not (excl and re.search(excl,r['Name (en)'],re.I)):
            if val(r,'A1-A3') is not None and per_m3(r,'A1-A3'): out.append(r)
    return out
