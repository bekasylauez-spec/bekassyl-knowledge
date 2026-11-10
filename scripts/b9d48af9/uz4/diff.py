import sys, ezdxf, collections
from ezdxf import bbox
old = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\uz3\uz.dxf"
new = r"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\uz4\uz.dxf"

def load(p):
    d = ezdxf.readfile(p); msp = d.modelspace()
    st = [e for e in msp.query('INSERT') if 'Штамп' in e.dxf.name]
    sig = collections.Counter()
    ents = []
    for e in msp:
        try:
            if e.dxftype() in ('LINE',):
                a, b = e.dxf.start, e.dxf.end; ents.append(((a.x + b.x) / 2, (a.y + b.y) / 2, ('L', round(a.x), round(a.y), round(b.x), round(b.y))))
            elif e.dxftype() in ('LWPOLYLINE',):
                pts = [tuple(map(round, p[:2])) for p in e.get_points()]; x = sum(p[0] for p in pts) / len(pts); y = sum(p[1] for p in pts) / len(pts); ents.append((x, y, ('P', tuple(pts))))
            elif e.dxftype() in ('INSERT', 'CIRCLE', 'TEXT', 'MTEXT', 'DIMENSION'):
                p = e.dxf.insert if e.dxf.hasattr('insert') else (e.dxf.center if e.dxf.hasattr('center') else e.dxf.defpoint)
                t = e.dxf.name if e.dxftype() == 'INSERT' else (e.plain_text() if e.dxftype() == 'MTEXT' else (e.dxf.text if e.dxftype() == 'TEXT' else ''))
                ents.append((p.x, p.y, (e.dxftype()[0], round(p.x), round(p.y), t)))
        except Exception:
            pass
    return st, ents

so, eo = load(old); sn, en = load(new)
print('stamps old', len(so), 'new', len(sn))
def frames(st):
    out = []
    for s in st:
        bb = bbox.extents([s])
        out.append((round(s.dxf.insert.x), round(s.dxf.insert.y), bb.extmin.x, bb.extmin.y, bb.extmax.x, bb.extmax.y))
    return sorted(out)
fo = frames(so); fn = frames(sn)
for f in fn: print('frame', f[0], f[1], 'bb', round(f[2]), round(f[3]), round(f[4]), round(f[5]))
def per(fr, ents):
    m = collections.defaultdict(set)
    for x, y, k in ents:
        for f in fr:
            if f[2] - 1 <= x <= f[4] + 1 and f[3] - 1 <= y <= f[5] + 1: m[(f[0], f[1])].add(k); break
        else: m['outside'].add(k)
    return m
po = per(fn, eo); pn = per(fn, en)
for k in sorted(set(po) | set(pn), key=str):
    a, b = po.get(k, set()), pn.get(k, set())
    if a != b: print('CHANGED', k, 'removed', len(a - b), 'added', len(b - a), [t for t in list(b - a) if t[0] in ('T', 'M')][:12])
