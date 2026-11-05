import lib,ab,pv,sys,json
import col_tpl
from common import ROW_Y
X=[803225+i*29700 for i in range(3)]
sel=[int(a) for a in sys.argv[1].split(',')] if len(sys.argv)>1 else [0,1,2]
lib.OPS.clear()
for i in sel:
    lib.op(t='eraseregion',win=[X[i]+5,ROW_Y+5,X[i]+29695,ROW_Y+20995],mode='intersect')
    col_tpl.build(X[i],ROW_Y,col_tpl.COLS[i],'4.%d'%(i+1))
r=ab.run(lib.OPS,'col',1500); print('\n'.join([l for l in ab.log().splitlines() if 'ERR' in l or 'errors' in l or 'not found' in l][-25:]))
items=[('4.%d'%(i+1),(X[i],ROW_Y,X[i]+29700,ROW_Y+21000)) for i in sel]
print(pv.plot(items,['ISO без полей A2 (594.00 x 420.00 мм)']*len(items)))
for n,w in items: print(pv.png(n,90))
