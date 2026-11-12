# -*- coding: utf-8 -*-
import ezdxf, sys, re
from ezdxf.tools.text import plain_mtext
sys.stdout.reconfigure(encoding='utf-8')
doc = ezdxf.readfile(sys.argv[1])
msp = doc.modelspace()
Y0 = -300000.0
SLOT = {'2.1': 131100, '2.2': 160800, '3.3': 279600, '4.1': 339000, '4.2': 368700, '4.3': 398400}
BAD = ['уточняется', '?', 'Конаев', '01-2024-05', 'Tengri', '5(1)', '26600', '24000', 'Вторичный', 'Цех', 'Аэротенк']
out = {k: [] for k in SLOT}


def where(x, y):
    for k, x0 in SLOT.items():
        if x0 <= x <= x0 + 29700 and Y0 <= y <= Y0 + 21000: return k


for e in msp:
    t = e.dxftype(); s = None; p = None
    try:
        if t == 'TEXT': s = e.dxf.text; p = e.dxf.insert
        elif t == 'MTEXT': s = plain_mtext(e.text); p = e.dxf.insert
        elif t == 'DIMENSION': s = e.dxf.get('text', ''); p = e.dxf.get('defpoint')
        elif t == 'INSERT':
            p = e.dxf.insert
            k = where(p[0], p[1])
            if k:
                for a in e.attribs: out[k].append(('ATT', a.dxf.tag, a.dxf.text))
            continue
    except Exception:
        continue
    if s is None or p is None: continue
    k = where(p[0], p[1])
    if k and s not in ('', '<>'): out[k].append((t, e.dxf.layer, s))
for k, v in out.items():
    bad = [x for x in v if any(b in x[2] for b in BAD) or re.fullmatch(r'\s*L\s*', x[2]) or re.search(r'(^|\s)L(\s|$)', x[2])]
    print('==', k, 'texts', len(v), 'BAD', len(bad))
    for b in bad: print('   BAD', b)
    if '-v' in sys.argv:
        for x in v: print('   ', x)
