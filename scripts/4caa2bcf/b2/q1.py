import ezdxf, re, collections
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
cnt=collections.Counter(e.dxftype() for e in m); print(cnt.most_common(20))
ls=collections.Counter(e.dxf.layer for e in m); print(ls.most_common(40))
txt=[]
for e in m:
    t=None
    if e.dxftype()=='TEXT': t=e.dxf.text; p=e.dxf.insert
    elif e.dxftype()=='MTEXT': t=e.plain_text(); p=e.dxf.insert
    if t: txt.append((t.strip(),round(p[0]),round(p[1]),e.dxf.layer))
for t in txt:
    if re.search(r'(Р|P)[мm]|ригел|Ригел|Схема|Разрез|План|\+\d|-\d\.\d{3}',t[0]): print(t)
