import logging; logging.disable(logging.CRITICAL)
import ezdxf, collections, pickle
d=ezdxf.readfile('w/main.dxf'); m=d.modelspace()
ins=[e for e in m if e.dxftype()=='INSERT' and e.dxf.layer in ('_АР_Монолит','оси')]
c=collections.Counter((e.dxf.layer,e.dxf.name) for e in ins); print(c.most_common(20))
# axes inserts
for e in ins:
    if e.dxf.layer=='оси':
        at={a.dxf.tag:a.dxf.text for a in e.attribs}
        print('AX',e.dxf.name,[round(v) for v in e.dxf.insert][:2],round(e.dxf.rotation),at)
