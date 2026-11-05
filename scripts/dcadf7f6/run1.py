import lib,ab,pv,sys,importlib
from common import ROW_Y,A1W
lib.OPS.clear()
lib.op(t='eraseregion',win=[-100,ROW_Y-100,A1W+100,ROW_Y+59500],mode='intersect')
import s21; s21.build(0,ROW_Y)
r=ab.run(lib.OPS,'s21',900); print(r[-1500:])
print(pv.plot([('2.1',(0,ROW_Y,A1W,ROW_Y+59400))])); print(pv.png('2.1',80))
