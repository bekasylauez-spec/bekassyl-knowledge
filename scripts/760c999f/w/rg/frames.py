import ezdxf, re, sys, pickle
from ezdxf import bbox
f, pat = sys.argv[1], sys.argv[2]
doc = ezdxf.readfile(f + '.dxf'); ms = doc.modelspace()
rows = []
for e in ms:
    try: b = bbox.extents([e], fast=True)
    except Exception: continue
    if not b.has_data: continue
    t = e.dxftype(); txt = ''
    if t == 'TEXT': txt = e.dxf.text
    elif t == 'MTEXT': txt = e.text
    elif t == 'ACAD_PROXY_ENTITY':
        try: txt = '|'.join((v.dxf.text if v.dxftype() == 'TEXT' else v.text) for v in e.virtual_entities() if v.dxftype() in ('TEXT', 'MTEXT'))
        except Exception: txt = '?'
    elif t == 'ACAD_TABLE': txt = 'TABLE'
    elif t == 'INSERT': txt = 'BLK:' + e.dxf.name
    rows.append((e.dxf.handle, t, b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y, txt, e.dxf.layer))
pickle.dump(rows, open(f + 'rows.pkl', 'wb'))
frames = [r for r in rows if r[1] == 'ACAD_PROXY_ENTITY' and r[5] - r[3] > 15000 and r[6].startswith('Формат')]
for r in rows:
    if r[1] == 'TEXT' and r[7] == 'Нумерация' and re.fullmatch(pat, r[6]):
        x, y = r[2], r[3]
        fr = sorted([q for q in frames if q[2] < x < q[4] and q[3] < y < q[5]], key=lambda q: (q[4]-q[2])*(q[5]-q[3]))[:1]
        print('SHEET', r[6], r[0], [tuple(round(v) for v in q[2:6]) for q in fr])
