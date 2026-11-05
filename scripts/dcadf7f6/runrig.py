import lib,ab,pv,sys
import rig_tpl
from common import ROW_Y
X=[892325+i*29700 for i in range(len(rig_tpl.RIGS))]
sel=[int(a) for a in sys.argv[1].split(',')] if len(sys.argv)>1 else list(range(len(rig_tpl.RIGS)))
lib.OPS.clear()
for i in sel:
    lib.op(t='eraseregion',win=[X[i]+5,ROW_Y+5,X[i]+29695,ROW_Y+20995],mode='intersect')
    import place; st=len(lib.OPS); rig_tpl.build(X[i],ROW_Y,rig_tpl.RIGS[i],'6.%d'%(i+1)); place.resolve(lib.OPS,st)
r=ab.run(lib.OPS,'rig',2000); print('\n'.join([l for l in ab.log().splitlines() if 'ERR' in l or 'errors' in l][-25:]))
items=[('6.%d'%(i+1),(X[i],ROW_Y,X[i]+29700,ROW_Y+21000)) for i in sel]
print(pv.plot(items,['ISO без полей A2 (594.00 x 420.00 мм)']*len(items)))
for n,w in items: print(pv.png(n,90))
