import lib,ab,pv,sys,importlib,json
from common import ROW_Y
# sheet slots: name -> (module, X0, fmt w,h, scale)
SL=json.load(open('slots.json',encoding='utf-8'))
def go(names, plot=True):
    lib.OPS.clear()
    for n in names:
        m,X0,W,H=SL[n][:4]
        lib.op(t='eraseregion',win=[X0+5,ROW_Y+5,X0+W-5,ROW_Y+H-5],mode='intersect')
        mod=importlib.import_module(m); mod.build(X0,ROW_Y)
    r=ab.run(lib.OPS,'run',1200); errs=[l for l in ab.log().splitlines() if 'ERR' in l or 'errors' in l or 'GUARD' in l]; print('\n'.join(errs[-15:]))
    if plot:
        items=[(n,(SL[n][1],ROW_Y,SL[n][1]+SL[n][2],ROW_Y+SL[n][3])) for n in names]
        meds=[pv.MED[(SL[n][2],SL[n][3])] for n in names]
        print(pv.plot(items,meds))
        for n in names: print(pv.png(n,80))
if __name__=='__main__': go(sys.argv[1].split(','))
