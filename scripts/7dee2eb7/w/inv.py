import ezdxf, sys, collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter(e.dxftype() for e in m); print(c.most_common(30))
lc=collections.Counter(e.dxf.layer for e in m); print(lc.most_common(60))
print('layouts',[l.name for l in d.layouts])
bc=collections.Counter(e.dxf.name for e in m.query('INSERT')); print(bc.most_common(40))
# texts sample
import re
ts=[(e.dxf.insert[0],e.dxf.insert[1],e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text) for e in m.query('TEXT MTEXT')]
print(len(ts))
for t in ts:
  if re.search(r'(?i)лист|плит|арм|Пм|ПЛ|схем|отм',t[2]): print(round(t[0]),round(t[1]),t[2][:90])
