# dump per-sheet content: texts, proxy texts (levels, notes), dimensions, tables, axes
import ezdxf, re, sys, pickle
from ezdxf import bbox
f, pat = sys.argv[1], sys.argv[2]
doc = ezdxf.readfile(f + '.dxf'); ms = doc.modelspace()
rows = pickle.load(open(f + 'rows.pkl', 'rb'))
frames = [r for r in rows if r[1] == 'ACAD_PROXY_ENTITY' and r[5] - r[3] > 15000 and r[6].startswith('Формат')]
nums = [r for r in rows if r[1] in ('TEXT', 'MTEXT') and re.fullmatch(pat, r[6].strip())]
sheets = []
for n in nums:
    x, y = n[2], n[3]
    fr = sorted([q for q in frames if q[2] < x < q[4] and q[3] < y < q[5]], key=lambda q: (q[4]-q[2])*(q[5]-q[3]))[:1]
    if fr: sheets.append((n[6].strip(), fr[0]))
sheets.sort(key=lambda s: [int(v) for v in s[0].split('.')])
def clean(t):
    t = re.sub(r'\\[A-Za-z][^;]*;', '', t); t = t.replace('{', '').replace('}', '').replace('\\P', ' / ').replace('%%C', 'Ø').replace('%%c', 'Ø').replace('%%D', '°')
    return re.sub(r'\s+', ' ', t).strip()
out = open(f + '_dump.txt', 'w', encoding='utf-8')
def P(*a): print(*a, file=out)
items = []  # (x0,y0,x1,y1,kind,text,handle)
for e in ms:
    t = e.dxftype()
    try: b = bbox.extents([e], fast=True)
    except Exception: continue
    if not b.has_data: continue
    x0, y0, x1, y1 = b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y
    if t == 'TEXT': items.append((x0, y0, x1, y1, 'T', clean(e.dxf.text), e.dxf.handle, e.dxf.layer))
    elif t == 'MTEXT': items.append((x0, y0, x1, y1, 'M', clean(e.text), e.dxf.handle, e.dxf.layer))
    elif t == 'DIMENSION':
        try: m = e.get_measurement()
        except Exception: m = None
        if isinstance(m, (int, float)): mv = round(m)
        else: mv = m
        items.append((x0, y0, x1, y1, 'D', '%s txt=%r' % (mv, e.dxf.text), e.dxf.handle, e.dxf.layer))
    elif t == 'ACAD_PROXY_ENTITY':
        try:
            vs = list(e.virtual_entities())
        except Exception: vs = []
        txt = ' | '.join(clean(v.dxf.text if v.dxftype() == 'TEXT' else v.text) for v in vs if v.dxftype() in ('TEXT', 'MTEXT'))
        if txt and not txt.startswith('Формат'): items.append((x0, y0, x1, y1, 'X', txt, e.dxf.handle, e.dxf.layer))
    elif t == 'ACAD_TABLE':
        items.append((x0, y0, x1, y1, 'TB', 'TABLE', e.dxf.handle, e.dxf.layer))
    elif t == 'INSERT':
        at = ' '.join(clean(a.dxf.text) for a in e.attribs) if e.attribs else ''
        items.append((x0, y0, x1, y1, 'B', e.dxf.name + (' [' + at + ']' if at else ''), e.dxf.handle, e.dxf.layer))
for sn, fr in sheets:
    P('\n==== SHEET', sn, 'frame', [round(v) for v in fr[2:6]])
    ins = [i for i in items if i[0] >= fr[2] - 1 and i[2] <= fr[4] + 1 and i[1] >= fr[3] - 1 and i[3] <= fr[5] + 1]
    for i in sorted(ins, key=lambda i: (-round(i[3] / 500), i[0])):
        if i[4] == 'B' and not re.search(r'\[', i[5]): continue
        P('%s %s (%d,%d)-(%d,%d) %s' % (i[4], i[6], i[0], i[1], i[2], i[3], i[5][:300]))
out.close()
print('sheets', [s[0] for s in sheets])
