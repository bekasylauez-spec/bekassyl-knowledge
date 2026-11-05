"""Лист 2.5 «Разрезы 1-1, 2-2» — Помещение обезвоживания."""
import sys
import ab, pl_ob
from pl_ob import AX, AY

WIN = [-1196403, -1749172, -1107303, -1707172]
Y0 = -1731000.0                    # level 0.000 of both sections
XA = -1188000.0                    # section 1-1: axis 1
XB = -1138000.0                    # section 2-2: axis А
T_OUT, T_LIN, T_CUT, T_FILL, T_NOTE, T_DIM, T_DIMV = '39A08B', '39A081', '37F114', '39A143', '39A1CF', '39A1DC', '39A08F'
AX11 = ['39B50B', '39B50C', '39B50D', '39B50E', '39B50F', '39B510', '39B511', '39B512', '39B513', '39B514', '39B6B0']
AX22 = ['39A146', '39A147', '39A193']
LM22 = ['39A0B7', '3A3236', '3A3237', '3A3238']; Z22 = -1718980.0
LM11 = ['39B722', '3A3233', '3A3234', '3A3235']; Z11 = -1735672.0
TT22, TT11 = '3A38E6', '3A3F94'
KEEP = ['37EFDA', '37EFDB', '37EFDD', '37F014', T_OUT, T_LIN, T_CUT, T_FILL, T_NOTE, T_DIM, T_DIMV] + AX11 + AX22 + LM22 + LM11 + [TT22, TT11]

o = pl_ob.Ops('f25_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
o.add({'t': 'eraseregion', 'win': WIN, 'keep': KEEP})


def R(x0, z0, x1, z1, cut=False, thin=False, base=XA):
    pts = [[base + x0, Y0 + z0], [base + x1, Y0 + z0], [base + x1, Y0 + z1], [base + x0, Y0 + z1]]
    t = o.tag(); o.add({'t': 'clone', 'h': T_LIN if thin else T_OUT, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': pts, 'closed': True})
    if cut:
        th = o.tag(); o.add({'t': 'clone', 'h': T_CUT, 'tag': th}); o.add({'t': 'hatchset', 'h': th, 'loops': [pts]})


def PL(pts, thin=True, closed=False, base=XA, cut=False):
    p = [[base + x, Y0 + z] for x, z in pts]
    t = o.tag(); o.add({'t': 'clone', 'h': T_LIN if thin else T_OUT, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': p, 'closed': closed})
    if cut:
        th = o.tag(); o.add({'t': 'clone', 'h': T_CUT, 'tag': th}); o.add({'t': 'hatchset', 'h': th, 'loops': [p]})


def N(text, tgt, org, base=XA, t2=None):
    o.note(T_NOTE, text, (base + tgt[0], Y0 + tgt[1]), (base + org[0], Y0 + org[1]), t2)


# ======================= section 1-1: along row В (cut plane y = 10900, looking to В)
top = {0: 13700, 1: 13700, 2: 13700, 3: 13700, 4: 13700, 5: 13700, 6: 5950, 7: 5700}
for i, x in enumerate(AX):
    R(x - 1000, -1500, x + 1000, -500, cut=True)                       # pads (cut)
    if i <= 5:
        R(x - 350, -500, x + 350, 11400, thin=True)                    # lower column (behind)
        R(x - 300, 11400, x + 300, 13700, thin=True)                   # upper column
    else:
        R(x - 350, -500, x + 350, top[i] - 200, thin=True)
for a, b in zip(AX, AX[1:]):                                            # foundation beams Фб (behind)
    R(a + 1000, -1100, b - 1000, -500, thin=True)
R(-350, -120, 32350, 0, cut=True)                                       # slab on grade Пм-1
PL([(-350, 6000), (20000, 6000), (32350, 5486), (32350, 5686), (20000, 6200), (-350, 6200)], thin=False, closed=True, cut=True)   # Пм-2 (cut)
for x, h, w in ((0, 700, 500), (3250, 700, 600), (7750, 800, 600), (12250, 800, 700), (16750, 800, 700), (20000, 700, 450)):
    R(x - w / 2, 6200 - h, x + w / 2, 6000, cut=True)                   # Y-beams Бм-9…Бм-13 cut
for x, w in ((26000, 450), (32000, 450)):
    zt = 6200 - (x - 20000) / 12000 * 500
    R(x - w / 2, zt - 700, x + w / 2, zt - 200, cut=True)
for a, b in zip(AX[:6], AX[1:6]):                                       # Бм-1 (row В) and Бм-15 behind
    R(a + 350, 5600, b - 350, 6000, thin=True)
    R(a + 350, 10800, b - 350, 11400, thin=True)
PL([(20350, 5500), (31650, 5000)], thin=True)                           # Бм-3 bottom (sloped)
for x in (3250, 7750, 12250, 16750):                                    # consoles КН-1
    R(x - 350, 10550, x + 350, 11400, thin=True)
R(-200, 11400, 20200, 11710, thin=True)                                 # crane runway ПБ-1 (see КМ)
PL([(-450, 13700), (20450, 13700), (20450, 14200), (-450, 14200), (-450, 13700)], thin=True)   # rafters/roof line (see КМ)
PL([(-4000, -300), (-1100, -300)]); PL([(33100, -300), (36000, -300)])
for k, h in enumerate(AX11):
    if k < 8: o.add({'t': 'axis', 'h': h, 's': [XA + AX[k], Y0 + 14200], 'e': [XA + AX[k], Y0 - 2900], 'val': str(k + 1)})
    else: o.add({'t': 'erase', 'h': [h]})
o.chain(T_DIM, [XA + x for x in AX], Y0 - 2300)
o.dim(T_DIM, (XA, Y0 - 2300), (XA + 32000, Y0 - 2300), (XA, Y0 - 3000))
o.chain(T_DIM, [Y0 + z for z in (-1500, -500, 0, 6200, 11400, 13700)], XA - 2600, vertical=True)
for it in (('Фм-1', (1000, -1000), (-1000 + 1500, -2000 + 0)), ('Пм-1', (24000, -60), (24500, 900)), ('Пм-2', (10000, 6100), (10500, 7100)),
                  ('Бм-1', (5500, 5800), (6000, 4800)), ('Бм-3', (26000, 5150), (26500, 4300)), ('Бм-15', (5500, 11100), (6000, 9900)),
                  ('КН-1', (7400, 10900), (8300, 9700)), ('ПБ-1', (14500, 11555), (15000, 12500), 'см. КМ'), ('Км-4', (3600, 3000), (4300, 3800)),
                  ('Км-5', (350, 3000), (1000, 3800)), ('Км-2', (26350, 3000), (27000, 3800)), ('Км-3', (31650, 3000), (30300, 3800)),
                  ('Покрытие', (10000, 14200), (10500, 15200), 'см. КМ')):
    N(it[0], it[1], it[2], t2=(it[3] if len(it) > 3 else None))

# ======================= section 2-2: between axes 3 and 4 (x = 10000, looking to axis 3)
B2 = XB
for y in AY:
    R(y - 175, -1100, y + 175, -500, cut=True, base=B2)                # Фб-2 cut
    R(y - 1500, -1500, y + 1500, -500, thin=True, base=B2)              # pads of axis 3 (behind)
for y, ztop in ((0, 13700), (12000, 13700)):
    R(y - 450, -500, y + 450, 11400, thin=True, base=B2); R(y - 300, 11400, y + 300, 13700, thin=True, base=B2)
R(6000 - 450, -500, 6000 + 450, 6000, thin=True, base=B2)
R(-450, -120, 12450, 0, cut=True, base=B2)
R(-450, 6000, 7975, 6200, cut=True, base=B2); R(10225, 6000, 12450, 6200, cut=True, base=B2)
for y, w, h in ((0, 450, 600), (3000, 400, 600), (6000, 400, 600), (7775, 400, 500), (10425, 400, 500), (12000, 450, 600)):
    R(y - w / 2, 6200 - h, y + w / 2, 6000, cut=True, base=B2)
for y in (0, 12000):
    R(y - 225, 10800, y + 225, 11400, cut=True, base=B2)                 # Бм-15 cut
for y, s in ((0, 1), (12000, -1)):
    a, b = y + s * 450, y + s * 1050
    R(min(a, b), 10550, max(a, b), 11400, thin=True, base=B2)          # consoles (behind)
for yc in (800, 11200):
    R(yc - 125, 11400, yc + 125, 11710, thin=True, base=B2)            # ПБ-1 (see КМ)
PL([(-450, 13700), (6000, 14300), (12450, 13700), (12450, 14200), (6000, 14800), (-450, 14200), (-450, 13700)], thin=True, base=B2)
PL([(-4500, -300), (-1600, -300)], base=B2); PL([(13600, -300), (16500, -300)], base=B2)
for k, h in enumerate(AX22):
    o.add({'t': 'axis', 'h': h, 's': [B2 + AY[k], Y0 + 14800], 'e': [B2 + AY[k], Y0 - 2900], 'val': 'АБВ'[k]})
o.chain(T_DIM, [B2 + y for y in AY], Y0 - 2300)
o.dim(T_DIM, (B2, Y0 - 2300), (B2 + 12000, Y0 - 2300), (B2, Y0 - 3000))
o.chain(T_DIM, [Y0 + z for z in (-1500, -500, 0, 6200, 11400, 13700, 14300)], B2 + 12000 + 3000, vertical=True)
for it in (('Фб-2', (175, -800), (900, -2000)), ('Пм-2', (2000, 6100), (2500, 7100)), ('О-2', (9100, 6100), (8500, 7300)),
                  ('Бм-1', (-225, 5800), (-1700, 4900)), ('Бм-4', (3200, 5800), (3700, 4900)), ('Бм-2', (6200, 5800), (6900, 4900)),
                  ('Бм-7', (10625, 5900), (11000, 4900)), ('Бм-15', (12225, 11100), (13000, 10000)), ('КН-1', (1050, 10900), (1900, 9800)),
                  ('ПБ-1', (925, 11555), (2000, 12500), 'см. КМ'), ('Км-4', (450, 3000), (1200, 3800)), ('Км-1', (6450, 3000), (7200, 3800)),
                  ('Стропильная балка', (6000, 14550), (7000, 15600), 'см. КМ')):
    N(it[0], it[1], it[2], base=B2, t2=(it[3] if len(it) > 3 else None))

# ======================= level marks: rebase to the new 0.000 and move
def LM(h, zold, x_tip, x_shelf, z, up):
    o.add({'t': 'levbase', 'h': h, 'old': zold, 'new': Y0, 'tag': 'lm_' + h})
    o.add({'t': 'spmove', 'h': 'lm_' + h, 'items': [[0, x_tip, Y0 + z], [1, x_shelf, Y0 + z + (500 if up else -500)]]})


L11 = [(0, True), (-1500, False), (6200, True), (11400, True)]
L22 = [(0, True), (-1500, False), (6200, True), (13700, True)]
for h, (z, up) in zip(LM11, L11):
    LM(h, Z11, XA - 1200, XA - 5700, z, up)
for h, (z, up) in zip(LM22, L22):
    LM(h, Z22, B2 - 1700, B2 - 6200, z, up)
for h, txt, x in ((TT11, 'Разрез 1 - 1', XA + 14000), (TT22, 'Разрез 2 - 2', B2 + 4500)):
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + txt + '}'})
    o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': [x, Y0 + 16800]})
o.add({'t': 'erase', 'h': [T_OUT, T_LIN, T_CUT, T_FILL, T_NOTE, T_DIM, T_DIMV]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g25', 1500)
    print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or l.startswith('levbase')))
