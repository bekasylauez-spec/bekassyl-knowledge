# «Ведомость деталей» on the A3 spec sheet (exploded analog block, one column of 2000-high cells):
# Шп1 cell gets a П sketch (copy of cell 25); texts of the П cells set to our Ск / U-bars
import sys, json; sys.path.insert(0, 'wl'); from common import *
import ezdxf
X0, Y0 = 1071200.0, 455939.0
doc = ezdxf.readfile(gx.S + r'\w\k55.dxf'); msp = doc.modelspace()
R = json.load(open('wl/f55.json', encoding='utf-8'))
CEN = {'Шп1': 36799, 'Х1': 34799, 'Х2': 32799, 'Х3': 30799, '25': 28799, 'Ск1': 26799, 'Ск2': 24799, 'Ск3': 22799, 'Ск4': 20799, '23': 18799, '24': 16799}
inband = lambda r, c: r['x0'] > 1990 and r['x1'] < 8350 and r['y0'] > c - 1150 and r['y1'] < c + 1150 and not (r['t'] == 'INSERT' and r['x1'] - r['x0'] > 5000)
texts = {}
for e in msp.query('TEXT MTEXT'):
    p = e.dxf.insert; x, y = p.x - X0, p.y - Y0
    if 2000 < x < 9000 and 15700 < y < 38000:
        texts[e.dxf.handle] = (x, y, e.plain_text() if e.dxftype() == 'MTEXT' else e.dxf.text)
ops = []
# 1) Шп1 cell -> П sketch: erase its content, copy the content of cell 25 (+8000)
ops.append(dict(t='erase', h=[r['h'] for r in R if inband(r, CEN['Шп1'])]))
k = 0
for r in R:
    if inband(r, CEN['25']):
        ops.append(dict(t='clone', h=r['h'], base=[0, 0], to=[0, 8000], tag='VD%d_%s' % (k, r['h']))); k += 1
# 2) texts per П cell: (cell, name, top, bottom, label, L)
PLAN = [('Шп1', 'Ск1', 980, 980, 'по н.г.', 2130), ('25', 'Ск2', 1530, 1530, 'по н.г.', 3230),
        ('Ск1', '14', 1310, 860, 'по н.г.', 2340), ('Ск2', '15', 1810, 860, 'по н.г.', 2840),
        ('Ск3', '16', 1310, 980, 'по н.г.', 2460), ('Ск4', '17', 1810, 980, 'по н.г.', 2960),
        ('23', '18', 1310, 730, 'по н.г.', 2220), ('24', '19', 1810, 730, 'по н.г.', 2720)]
def cell_texts(cname, src='25'):
    c = CEN[cname]; out = {}
    for h, (x, y, t) in texts.items():
        if c - 1000 < y < c + 1000 and 1990 < x < 8350: out[h] = (x, y, t)
    return out
for cname, name, top, bot, lab, L in PLAN:
    if cname == 'Шп1':
        src = cell_texts('25'); dy = 8000
        for h, (x, y, t) in src.items():
            tag = next((o['tag'] for o in ops if o.get('t') == 'clone' and o['h'] == h), None)
            if tag is None: print('no clone for', h, x, y, t); continue
            new = name if t.strip() == '25' else str(top) if abs(y - (CEN['25'] + 600)) < 200 and t.strip().isdigit() and t.strip() != '170' else \
                  str(bot) if abs(y - (CEN['25'] - 480)) < 200 and t.strip().isdigit() else str(L) if t.strip().isdigit() and x > 7300 else lab if t.startswith('по') else None
            if new is not None: ops.append(dict(t='settext', h=tag, s=new))
        continue
    src = cell_texts(cname); c = CEN[cname]
    for h, (x, y, t) in src.items():
        s = t.strip()
        if s == cname: new = name
        elif s.startswith('по'): new = lab
        elif s.isdigit() and x > 7300: new = str(L)
        elif s.isdigit() and s != '170' and y > c + 300: new = str(top)
        elif s.isdigit() and s != '170' and y < c - 300: new = str(bot)
        else: new = None
        if new is not None: ops.append(dict(t='settext', h=h, s=new))
ops.append(dict(t='save'))
print(len(ops))
for o in ops:
    if o['t'] == 'settext': print(o['h'], o['s'])
if '--run' in sys.argv:
    out = gx.run(ops, 'sm1ved'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
