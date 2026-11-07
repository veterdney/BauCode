"""Layer build-ups, inside -> outside (floors/ground slab: top -> bottom). Thicknesses in m. ASSUMPTION: all build-ups, areas, requirements."""
from engine import L
S='solve'
PARTS={'OW':'Outer wall','IL':'Inner wall, load-bearing','IP':'Inner wall, partition','FL':'Floor slab / ceiling','RF':'Roof','GS':'Foundation / ground slab','WI':'Windows'}
# part area per m2 GFA (ASSUMPTION: 2.5 storeys, 200 m2 footprint, 20 % glazing)
AREA={'OW':0.68,'IL':0.35,'IP':0.50,'FL':0.60,'RF':0.40,'GS':0.40,'WI':0.17}
REQ_RW={'OW':40,'IL':53,'IP':35,'FL':54,'RF':40,'GS':None,'WI':32}   # dB, DIN 4109 style (ASSUMPTION)
ALT={
1:('Reinforced concrete frame + EPS ETICS',{
 'OW':[L('Paint/covering',0),L('RC',0.20),L('EPS',S,life=40),L('Mineral render',0.010,life=40)],
 'IL':[L('Paint/covering',0),L('RC',0.20),L('Paint/covering',0)],
 'IP':[L('Paint/covering',0),L('Mineral render',0.010),L('AAC',0.10),L('Mineral render',0.010),L('Paint/covering',0)],
 'FL':[L('Screed',0.05),L('Rock wool',0.03),L('RC',0.22),L('Paint/covering',0)],
 'RF':[L('Paint/covering',0),L('RC',0.20),L('VCL',0,sd=100),L('EPS',S),L('Roof membrane',0),L('Gravel',0.05)],
 'GS':[L('Screed',0.05),L('Sealing foil',0),L('RC',0.25),L('XPS',S),L('Gravel',0.15)],
 'WI':[L('Window PVC',0),L('Sealing foil',0)]}),
2:('Steel frame + composite slabs + mineral wool',{
 'OW':[L('Gypsum board',0.025),L('Paint/covering',0),L('VCL',0),L('Rock wool',0.10),L('Steel frame',0,kg=3.0),L('Gypsum board',0.015),L('Rock wool',S,life=40),L('Mineral render',0.010,life=40)],
 'IL':[L('Paint/covering',0),L('Gypsum board',0.025),L('Rock wool',0.10),L('Steel frame',0,kg=3.0),L('Gypsum board',0.025),L('Paint/covering',0)],
 'IP':[L('Paint/covering',0),L('Gypsum board',0.025),L('Rock wool',0.075),L('Steel frame',0,kg=2.2),L('Gypsum board',0.025),L('Paint/covering',0)],
 'FL':[L('Screed',0.05),L('Rock wool',0.03),L('Composite slab steel-concrete',0.09),L('Gypsum board',0.025),L('Paint/covering',0)],
 'RF':[L('Paint/covering',0),L('Gypsum board',0.025),L('Composite slab steel-concrete',0.09),L('VCL',0,sd=100),L('Rock wool',S),L('Roof membrane',0),L('Gravel',0.05)],
 'GS':[L('Screed',0.05),L('Sealing foil',0),L('RC',0.25),L('XPS',S),L('Gravel',0.15)],
 'WI':[L('Window PVC',0),L('Sealing foil',0)]}),
3:('Monolithic masonry (clay block / sand-lime) + mineral insulation',{
 'OW':[L('Paint/covering',0),L('Lime plaster',0.015),L('Brick',0.365),L('Rock wool',S,life=40),L('Mineral render',0.010,life=40)],
 'IL':[L('Paint/covering',0),L('Lime plaster',0.010),L('Sand-lime',0.175),L('Lime plaster',0.010),L('Paint/covering',0)],
 'IP':[L('Paint/covering',0),L('Lime plaster',0.010),L('Sand-lime',0.115),L('Lime plaster',0.010),L('Paint/covering',0)],
 'FL':[L('Screed',0.05),L('Rock wool',0.03),L('RC',0.20),L('Paint/covering',0)],
 'RF':[L('Paint/covering',0),L('RC',0.20),L('VCL',0,sd=100),L('Rock wool',S),L('Roof membrane',0),L('Gravel',0.05)],
 'GS':[L('Screed',0.05),L('Sealing foil',0),L('RC',0.25),L('XPS',S),L('Gravel',0.15)],
 'WI':[L('Window PVC',0),L('Sealing foil',0)]}),
4:('Timber-concrete hybrid (CLT walls + composite slabs)',{
 'OW':[L('CLT',0.10),L('Rock wool',S,life=40),L('Mineral render',0.010,life=40)],
 'IL':[L('Gypsum board',0.015),L('CLT',0.10),L('Rock wool',0.06),L('Gypsum board',0.025)],
 'IP':[L('Paint/covering',0),L('Gypsum board',0.025),L('KVH',0.075,0.12),L('Rock wool',0.075,0.88),L('Gypsum board',0.025),L('Paint/covering',0)],
 'FL':[L('Screed',0.05),L('Rock wool',0.03),L('Wood-concrete slab',0.20)],
 'RF':[L('CLT',0.14),L('VCL',0,sd=100),L('Rock wool',S),L('Roof membrane',0),L('Gravel',0.05)],
 'GS':[L('Screed',0.05),L('Sealing foil',0),L('RC',0.25),L('Foam glass',S),L('Gravel',0.15)],
 'WI':[L('Window timber',0),L('Sealing foil',0)]}),
5:('Solid timber (CLT) + wood-fibre insulation',{
 'OW':[L('CLT',0.10),L('Wood fibre',S,life=40),L('Mineral render',0.010,life=40)],
 'IL':[L('CLT',0.10),L('Wood fibre',0.06),L('Gypsum board',0.025)],
 'IP':[L('CLT',0.08)],
 'FL':[L('Screed',0.05),L('Wood fibre',0.03),L('Dry fill',0.06),L('CLT',0.18)],
 'RF':[L('CLT',0.14),L('VCL',0),L('Wood fibre',S),L('Roof tile',0)],
 'GS':[L('Screed',0.05),L('Sealing foil',0),L('RC',0.25),L('Foam glass',S),L('Gravel',0.15)],
 'WI':[L('Window timber',0),L('Sealing foil',0)]}),
6:('Timber frame + straw infill + clay plaster',{
 'OW':[L('Clay plaster',0.020),L('KVH','same',0.08),L('Straw bale',S,0.92),L('Lime plaster',0.025,life=40)],
 'IL':[L('Clay plaster',0.020),L('OSB',0.015),L('KVH',0.14,0.12),L('Wood fibre',0.14,0.88),L('OSB',0.015),L('Clay plaster',0.020)],
 'IP':[L('Clay plaster',0.015),L('KVH',0.06,0.12),L('Wood fibre',0.06,0.88),L('Clay plaster',0.015)],
 'FL':[L('Gypsum board',0.025),L('Wood fibre',0.03),L('Dry fill',0.08),L('OSB',0.022),L('KVH',0.20,0.10),L('Cellulose',0.20,0.90),L('Gypsum board',0.015)],
 'RF':[L('Gypsum board',0.015),L('VCL',0),L('KVH','same',0.08),L('Cellulose',S,0.92),L('Wood fibre',0.04),L('Roof tile',0)],
 'GS':[L('Screed',0.05),L('Sealing foil',0),L('RC',0.20),L('Foam glass',S),L('Gravel',0.15)],
 'WI':[L('Window timber',0),L('Sealing foil',0)]}),
}
# Rw (dB) for framed / double-leaf build-ups where the mass law does not apply (ASSUMPTION, typical tested values; verify per DIN 4109-33)
RW_FRAMED={(2,'OW'):48,(2,'IL'):53,(2,'IP'):48,(4,'IL'):56,(4,'IP'):48,(5,'IL'):53,(6,'IL'):50,(6,'IP'):40,(6,'FL'):52,(4,'RF'):None,(4,'OW'):44,(5,'OW'):44,(6,'OW'):45,(6,'RF'):45}
