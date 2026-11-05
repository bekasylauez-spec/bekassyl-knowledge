import lib,ab,math
from lib import *
X0,Y0=0,450000
s=Sheet('2.1','Схема расположения\Pэлементов','Тест',X0,Y0,'A1',100,True)
PX,PY=X0+12000,Y0+16000
axis('1',(PX,PY+26000),(PX,PY-2500))
axis('А',(PX+47000,PY),(PX-2500,PY),vertical=False)
dim((PX,PY-1000),(PX+6800,PY-1000),(PX,PY-2000))
dim((PX-1000,PY),(PX-1000,PY+6200),(PX-2000,PY),math.pi/2)
rect(PX+6600,PY-200,PX+44400,PY+200,layer=L_CONT)
hatch([[(PX+6600,PY-200),(PX+44400,PY-200),(PX+44400,PY+200),(PX+6600,PY+200)]])
note('См-1','',(PX+10400,PY+600),(PX+10000,PY+200))
plev('-4,000',(PX+20000,PY+3000))
section('1',(PX-1500,PY+3000),(PX+47000,PY+3000))
s.notes(['Общие указания см. лист 1.1.','Тест примечания.'])
lib.dump('ops/t1.json')
print(ab.run(lib.OPS,'t1',600))
