import ezdxf, sys, re, io, collections
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
out = io.open(sys.argv[2], 'w', encoding='utf-8')
Y0, Y1 = float(sys.argv[3]), float(sys.argv[4])
def dec(s): return re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda g: chr(int(g.group(1), 16)), s)
rows = []
for e in m:
    t = None; p = None
    if e.dxftype() == 'TEXT': t, p = e.dxf.text, e.dxf.insert
    elif e.dxftype() == 'MTEXT': t, p = e.plain_text(), e.dxf.insert
    elif e.dxftype() == 'DIMENSION':
        try: t = e.dxf.text if e.dxf.text not in ('', '<>') else '%.0f' % e.get_measurement(); p = e.dxf.text_midpoint
        except Exception: continue
    elif e.dxftype() == 'INSERT' and e.attribs:
        t = ' / '.join(a.dxf.text for a in e.attribs); p = e.dxf.insert
    if t and p is not None and Y0 <= p.y <= Y1:
        rows.append((round(p.x), round(p.y), e.dxftype()[:3], dec(t).replace('\n', ' | ')[:160]))
rows.sort(key=lambda r: (r[0] // 50000, -r[1], r[0]))
for r in rows: out.write('%9d %9d %s %s\n' % r)
print(len(rows))
