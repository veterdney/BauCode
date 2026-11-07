"""Material catalogue. Facts (GWP, PE, SM, waste, density) come from OBD 2024-II via pools.
Every other attribute is an ASSUMPTION (flagged in report section 6)."""
import sys
sys.path.insert(0,'analysis'); sys.path.insert(0,'analysis/compare6')
import compare6 as C
from lib import select, dens, val, f

cands=C.cands
def apool(cat,name=None,excl=None):
    """area-declared (qm) products used per m2 directly"""
    return [r for r in select(cat,name,excl) if r['Bezugseinheit']=='qm' and val(r,'A1-A3') is not None and abs(val(r,'A1-A3'))<400]

POOLS={ # key: (kind, rows)
 'concrete':('vol',C.POOL['concrete']),'rebar':('kg',C.POOL['rebar']),'steel':('kg',C.POOL['steel']),'deck':('kg',C.POOL['deck']),
 'clt':('vol',C.POOL['CLT']),'kvh':('vol',C.POOL['KVH']),'osb':('vol',C.POOL['OSB']),'sandlime':('vol',C.POOL['sandlime']),
 'brick':('vol',cands('Fired brick',dmax=1000)),'aac':('vol',cands('Aerated concrete')),
 'eps':('vol',cands('EPS')),'xps':('vol',cands('XPS white')),'rockwool':('vol',cands('Rock wool|Glass wool',dmax=200)),
 'woodfibre':('vol',cands('Wood fibre insulation boards|Wood fibre boards',dmax=300)),'cellulose':('vol',cands('Cellulose')),
 'straw':('vol',cands('Straw bale')),'foamglass':('vol',cands('Foam glass')),
 'gypsum':('vol',cands('Gypsum plasterboard')),
 'mrender':('vol',cands('Renders and plasters',excl='lime|clay|gypsum|NHL')),'clay':('vol',cands('Renders and plasters',name='clay|loam|Lehm')),
 'lime':('vol',cands('Renders and plasters',name='lime|NHL|Kalk',excl='gypsum')),
 'screed':('vol',cands('Screed dry mortar')),'pumice':('vol',cands('Pumice|Granulate',name='fill|pumice|perlite')),
 'gravel':('vol',cands('Natural stone|Granulate',cap=1500,name='rock|stone|GLAPOR|gravel',excl='GLAPOR')),
 'paint':('area',apool('Wall and ceiling covering')),
 'vcl':('area',apool('Vapour barriers')),'foil':('area',apool('Sealing foils')),
 'roofmem':('area',apool('Bituminous sheet|TPO roofing|PVC sheet')),'tile':('area',apool('Ceramic roof tile')),
 'win_pvc':('area',[r for r in select('Plastic windows') if r['Bezugseinheit']=='qm' and not __import__('re').search('roof|lift|sliding',r['Name (en)'],__import__('re').I) and val(r,'A1-A3') is not None]),
 'win_wood':('area',[r for r in select('Timber windows','Wooden|Timber') if r['Bezugseinheit']=='qm' and not __import__('re').search('roof|lift|sliding',r['Name (en)'],__import__('re').I) and val(r,'A1-A3') is not None]),
}
# wood-concrete composite slab and steel-concrete composite: per m2 (OBD / assembled)
WCC=C.wcc_item()

# ASSUMPTION attributes: lam W/mK, mu (-), sd_fixed m (area layers), life y, mfp 1-5, voc 1-5, buf 1-5, snd 1-5, cost EUR/m3 (vol) or EUR/m2 (area) or EUR/kg,
# job, move class, fire class (EN 13501-1), joint default
M={ #name: pool, kind, lam, mu, life, mfp, voc, buf, snd, cost, job, move, fire, joint, rho_assumed(if no OBD density)
 'RC':            dict(pool='concrete',rebar=110,lam=2.0,mu=80,life=100,mfp=5,voc=5,buf=2,snd=5,cost=470,job='structure',move='mineral',fire='A1',joint='cast'),
 'Brick':     dict(pool='brick',lam=0.12,mu=8,life=100,mfp=5,voc=5,buf=3,snd=3,cost=420,job='structure',move='mineral',fire='A1',joint='bonded'),
 'Sand-lime':     dict(pool='sandlime',lam=0.99,mu=20,life=100,mfp=5,voc=5,buf=3,snd=5,cost=380,job='structure',move='mineral',fire='A1',joint='bonded'),
 'AAC':           dict(pool='aac',lam=0.10,mu=8,life=100,mfp=4,voc=5,buf=4,snd=3,cost=330,job='structure',move='mineral',fire='A1',joint='bonded'),
 'CLT':           dict(pool='clt',lam=0.13,mu=50,life=100,mfp=3,voc=3,buf=5,snd=3,cost=850,job='structure',move='timber',fire='D',joint='mech'),
 'KVH':           dict(pool='kvh',lam=0.13,mu=50,life=100,mfp=3,voc=4,buf=5,snd=2,cost=650,job='structure',move='timber',fire='D',joint='mech'),
 'Steel frame':   dict(pool='steel',kg=True,lam=50,mu=1e6,life=100,mfp=4,voc=5,buf=1,snd=2,cost=14800,job='structure',move='steel',fire='A1',joint='mech'),
 'Composite slab steel-concrete':dict(pool='concrete',deck=9,mesh=3,lam=1.6,mu=80,life=100,mfp=4,voc=4,buf=2,snd=4,cost=470,job='structure',move='mineral',fire='A1',joint='cast'),
 'Wood-concrete slab':dict(pool='WCC',lam=0.8,mu=60,life=100,mfp=4,voc=3,buf=3,snd=4,cost=0,costm2=150,job='structure',move='timber',fire='D',joint='cast'),
 'EPS':           dict(pool='eps',lam=0.035,mu=40,life=60,mfp=3,voc=3,buf=1,snd=1,cost=140,job='insulation',move='polymer',fire='E',joint='bonded'),
 'XPS':           dict(pool='xps',lam=0.035,mu=100,life=60,mfp=4,voc=3,buf=1,snd=1,cost=250,job='insulation',move='polymer',fire='E',joint='loose'),
 'Rock wool':     dict(pool='rockwool',lam=0.036,mu=1,life=60,mfp=4,voc=3,buf=2,snd=4,cost=180,job='insulation',move='soft',fire='A1',joint='mech'),
 'Wood fibre':    dict(pool='woodfibre',lam=0.040,mu=5,life=60,mfp=3,voc=4,buf=4,snd=4,cost=300,job='insulation',move='timber',fire='E',joint='mech'),
 'Cellulose':     dict(pool='cellulose',lam=0.039,mu=2,life=60,mfp=3,voc=4,buf=4,snd=4,cost=200,job='insulation',move='soft',fire='E',joint='loose'),
 'Straw bale':    dict(pool='straw',lam=0.052,mu=2,life=60,mfp=2,voc=5,buf=5,snd=3,cost=180,job='insulation',move='soft',fire='E',joint='loose'),
 'Foam glass':    dict(pool='foamglass',lam=0.045,mu=1e5,life=100,mfp=5,voc=5,buf=1,snd=2,cost=900,job='insulation',move='mineral',fire='A1',joint='loose'),
 'Gypsum board':  dict(pool='gypsum',lam=0.25,mu=8,life=50,mfp=2,voc=4,buf=3,snd=3,cost=1440,job='board',move='board',fire='A2',joint='mech'),
 'OSB':           dict(pool='osb',lam=0.13,mu=50,life=100,mfp=2,voc=2,buf=3,snd=2,cost=450*1.0,job='board',move='timber',fire='D',joint='mech'),
 'Mineral render':dict(pool='mrender',lam=0.80,mu=20,life=40,mfp=4,voc=4,buf=3,snd=3,cost=4600,job='plaster',move='mineral',fire='A1',joint='bonded'),
 'Clay plaster':  dict(pool='clay',lam=0.80,mu=8,life=60,mfp=2,voc=5,buf=5,snd=3,cost=2250,job='plaster',move='mineral',fire='A1',joint='bonded'),
 'Lime plaster':  dict(pool='lime',lam=0.80,mu=10,life=40,mfp=4,voc=5,buf=4,snd=3,cost=2800,job='plaster',move='mineral',fire='A1',joint='bonded'),
 'Paint/covering':dict(pool='paint',kind='area',lam=0,sd=0.1,life=12,mfp=3,voc=2,buf=2,snd=1,cost=10,job='finish',move='membrane',fire='B',joint='bonded'),
 'VCL':           dict(pool='vcl',kind='area',lam=0,sd=10,life=50,mfp=3,voc=4,buf=1,snd=1,cost=4,job='membrane',move='membrane',fire='E',joint='mech'),
 'Sealing foil':  dict(pool='foil',kind='area',lam=0,sd=20,life=50,mfp=3,voc=4,buf=1,snd=1,cost=3,job='membrane',move='membrane',fire='E',joint='mech'),
 'Roof membrane': dict(pool='roofmem',kind='area',lam=0,sd=100,life=30,mfp=4,voc=3,buf=1,snd=1,cost=25,job='membrane',move='polymer',fire='E',joint='loose'),
 'Gravel':        dict(pool='gravel',rho=1600,lam=2.0,mu=1,life=50,mfp=5,voc=5,buf=1,snd=3,cost=80,job='cover',move='mineral',fire='A1',joint='loose'),
 'Roof tile':     dict(pool='tile',kind='area',lam=0,sd=0.5,life=60,mfp=5,voc=5,buf=1,snd=2,cost=45,job='cover',move='mineral',fire='A1',joint='mech'),
 'Screed':        dict(pool='screed',lam=1.2,mu=25,life=60,mfp=4,voc=4,buf=2,snd=4,cost=400,job='screed',move='mineral',fire='A1',joint='loose'),
 'Dry fill':      dict(pool='pumice',rho=400,lam=0.12,mu=3,life=100,mfp=4,voc=5,buf=3,snd=4,cost=150,job='screed',move='mineral',fire='A1',joint='loose'),
 'Window PVC':    dict(pool='win_pvc',kind='area',lam=0,sd=0,life=35,mfp=4,voc=3,buf=1,snd=3,cost=520,job='window',move='polymer',fire='E',joint='mech'),
 'Window timber': dict(pool='win_wood',kind='area',lam=0,sd=0,life=35,mfp=3,voc=4,buf=1,snd=3,cost=780,job='window',move='timber',fire='D',joint='mech'),
}
# nominal thickness (m) used only for the volume share of area-declared layers (ASSUMPTION)
NOMT={'Paint/covering':0.001,'VCL':0.0005,'Sealing foil':0.0005,'Roof membrane':0.003,'Roof tile':0.015,'Window PVC':0.07,'Window timber':0.07,'Wood-concrete slab':0.20}

# Fill earlier assumptions from the Building material property dataset (switch off with MATERIAL_DATASET=0 to reproduce the baseline)
import os
FILL_LOG=[]
if os.environ.get('MATERIAL_DATASET','1')=='1':
    import dataset_fill
    dataset_fill.apply(M,FILL_LOG)
