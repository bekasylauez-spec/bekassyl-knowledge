"""Section 1-1 redrawn with a break between axes 2 and 5 (A3), section 2-2 -> new sheet 2.6. Level marks are kept and moved."""
import sys, math
import ab, pl_ob, pl2
from pl_ob import AX, AY

Y0 = -1731000.0; XA = -1188000.0
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
IMP = ['39A08B', '39A081', '37F114', '39A1CF', '39A1DC']
T_OUT, T_LIN, T_CUT, T_NOTE, T_DIM = ['T25b:' + h for h in IMP]
CUT0, CUT1, SH = 4500, 15500, 9500           # removed zone (local x) and shift of the right part
BRK = (CUT0 + CUT1 - SH) / 2                 # break line x (drawn)


def m(x):
    return x if x <= CUT0 else x - SH


si = pl_ob.sheetinfo([-1196403, -1749172, -1107303, -1707172])
keep_t = ('SPDSLEVELMARK', 'SPDSCONSTRUCTIONLINE', 'SPDSFORMAT', 'INSERT')
ERASE = [e['h'] for e in si['E'] if e['t'] not in keep_t and e['h'] not in ('3A3F94', '3A38E6', '37EFDB', '37EFDD')
         and (e['ext'][0] + e['ext'][2]) / 2 > XA - 2000 and (e['ext'][0] + e['ext'][2]) / 2 < -1146500]
o = pl2.Ops('g25b_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
o.add({'t': 'erase', 'h': ERASE})
o.add({'t': 'import', 'file': ABK, 'h': IMP, 'base': [0, 0], 'to': [0, 0], 'pre': 'T25b:'})


def R(x0, z0, x1, z1, cut=False, thin=False):
    """rectangle in section coords; split by the break"""
    parts = []
    if x1 <= CUT0 or x0 >= CUT1:
        parts = [(m(x0), m(x1))]
    else:
        if x0 < CUT0: parts.append((x0, CUT0))
        if x1 > CUT1: parts.append((m(CUT1), m(x1)))
    for a, b in parts:
        pts = [[XA + a, Y0 + z0], [XA + b, Y0 + z0], [XA + b, Y0 + z1], [XA + a, Y0 + z1]]
        t = o.tag(); o.add({'t': 'clone', 'h': T_LIN if thin else T_OUT, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': pts, 'closed': True})
        if cut:
            th = o.tag(); o.add({'t': 'clone', 'h': T_CUT, 'tag': th}); o.add({'t': 'hatchset', 'h': th, 'loops': [pts]})


def PL(pts, thin=True, closed=False):
    p = [[XA + m(x), Y0 + z] for x, z in pts]
    t = o.tag(); o.add({'t': 'clone', 'h': T_LIN if thin else T_OUT, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': p, 'closed': closed})


top = {6: 5950, 7: 5700}
for i, x in enumerate(AX):
    if CUT0 < x < CUT1: continue
    R(x - 1000, -1500, x + 1000, -500, cut=True)
    if i <= 5:
        R(x - 350, -500, x + 350, 11400, thin=True); R(x - 300, 11400, x + 300, 13700, thin=True)
    else:
        R(x - 350, -500, x + 350, top[i] - 200, thin=True)
for a, b in zip(AX, AX[1:]):
    R(a + 1000, -1100, b - 1000, -500, thin=True)
R(-350, -120, 32350, 0, cut=True)                                             # Пм-1
R(-350, 6000, 20000, 6200, cut=True)                                          # Пм-2 (flat part)
th = o.tag(); o.add({'t': 'clone', 'h': T_OUT, 'tag': th})
P2 = [[XA + m(20000), Y0 + 6000], [XA + m(32350), Y0 + 5486], [XA + m(32350), Y0 + 5686], [XA + m(20000), Y0 + 6200]]
o.add({'t': 'plset', 'h': th, 'p': P2, 'closed': True})
th2 = o.tag(); o.add({'t': 'clone', 'h': T_CUT, 'tag': th2}); o.add({'t': 'hatchset', 'h': th2, 'loops': [P2]})
for x, h, w in ((0, 700, 500), (3250, 700, 600), (16750, 800, 700), (20000, 700, 450)):
    R(x - w / 2, 6200 - h, x + w / 2, 6000, cut=True)
for x in (26000, 32000):
    zt = 6200 - (x - 20000) / 12000 * 500
    R(x - 225, zt - 700, x + 225, zt - 200, cut=True)
for a, b in zip(AX[:6], AX[1:6]):
    R(a + 350, 5600, b - 350, 6000, thin=True); R(a + 350, 10800, b - 350, 11400, thin=True)
PL([(20350, 5500), (31650, 5000)])
for x in (3250, 16750):
    R(x - 350, 10550, x + 350, 11400, thin=True)
R(-200, 11400, 20200, 11710, thin=True)
R(-450, 13700, 20450, 14200, thin=True)
PL([(-4000, -300), (-1100, -300)]); PL([(33100, -300), (36000, -300)])
# break line (zigzag) through the whole section
zz = [(BRK, -1900), (BRK, 6400), (BRK - 150, 6600), (BRK + 150, 6900), (BRK, 7100), (BRK, 14700)]
t = o.tag(); o.add({'t': 'clone', 'h': T_LIN, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': [[XA + x, Y0 + z] for x, z in zz], 'closed': False})
# axes: 1,2,5..8 moved, 3,4 erased
V = sorted([e for e in si['E'] if e['t'] == 'SPDSCONSTRUCTIONLINE' and (e['ext'][0] + e['ext'][2]) / 2 < -1146500], key=lambda e: e['ext'][0])
for k, e in enumerate(V):
    if k in (2, 3): o.add({'t': 'erase', 'h': [e['h']]}); continue
    o.add({'t': 'axis', 'h': e['h'], 's': [XA + m(AX[k]), Y0 + 14200], 'e': [XA + m(AX[k]), Y0 - 2900], 'val': str(k + 1)})
# dims: axes chain with the merged middle span, overall, level chain on the right
xs = [m(v) for v in AX if not (CUT0 < v < CUT1)]
for a, b in zip(xs, xs[1:]):
    txt = '4500х3=13500' if (a, b) == (3250, m(16750)) else None
    o.dim2(T_DIM, (XA + a, Y0 - 2900), (XA + b, Y0 - 2900), Y0 - 2300, txt=txt)
o.dim2(T_DIM, (XA, Y0 - 2900), (XA + m(32000), Y0 - 2900), Y0 - 3000, txt='32000')
o.chain2(T_DIM, [Y0 + z for z in (-1500, -500, 0, 6200, 11400, 13700)], XA + m(32000) + 2600, vertical=True, origin=XA + m(32350), out=1)
for it in (('Фм-1', (1000, -1000), 1, -1), ('Пм-1', (26000, -60), -1, 1), ('Пм-2', (2000, 6200), 1, 1), ('Бм-1', (1600, 5600), 1, -1),
           ('Бм-3', (26000, 5150), -1, -1), ('Бм-15', (1600, 10800), 1, -1), ('КН-1', (16400, 10550), -1, -1), ('Км-5', (350, 3000), 1, 1),
           ('Км-4', (3600, 3000), 1, 1), ('Км-2', (25650, 3000), -1, 1), ('Км-3', (31650, 3000), -1, 1)):
    o.mark(T_NOTE, it[0], (XA + m(it[1][0]), Y0 + it[1][1]), it[2], it[3], 600)
o.mark(T_NOTE, 'ПБ-1', (XA + m(18500), Y0 + 11710), 1, 1, 600, 'см. КМ')
o.mark(T_NOTE, 'Покрытие', (XA + m(19000), Y0 + 14200), 1, 1, 600, 'см. КМ')
o.add({'t': 'erase', 'h': IMP and ['T25b:' + h for h in IMP]})
o.add({'t': 'save'})
print(len(o.O), 'ops, erase', len(ERASE))
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g25b', 1500)
    print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or 'no prop' in l)[-1500:])
