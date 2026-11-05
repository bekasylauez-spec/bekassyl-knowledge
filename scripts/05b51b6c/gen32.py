"""Лист 3.2 «Фундамент Фм-1. Армирование» (A2, изображения 1:25 = x4 в модели, размеры dimlfac 0.25), рамка аналога АБК 3.5."""
import sys, math
import ab, pl_ob, pl2, fm_data as FD

X0, Y0 = -750903.0, -1749172.0
WIN = [X0, Y0, X0 + 59400, Y0 + 42000]
K = 4.0
T_BAR, T_THIN, T_NOTE, T_DIM, T_LM, T_TTL = '37FC02', '37FCBB', '37FB36', '37FB09', '37FB07', '37FB38'
SPEC, STEEL = '37FCCB', '37FCCC'
TPL = [T_BAR, T_THIN, T_NOTE, T_DIM, T_LM, T_TTL]
FIRST = len(sys.argv) > 2 and sys.argv[2] == 'first'

si = pl_ob.sheetinfo(WIN)
o = pl2.Ops('g32_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
PARK = [h for h in TPL if any(e['h'] == h for e in si['E'])]
if PARK: o.add({'t': 'move', 'h': PARK, 'd': [0, -30000]})
o.add({'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + TPL})


class View:
    def __init__(s, ox, oy): s.ox, s.oy = X0 + ox, Y0 + oy
    def P(s, x, y): return [round(s.ox + K * x, 1), round(s.oy + K * y, 1)]


def pl(v, pts, tmpl=T_THIN, closed=False):
    t = o.tag(); o.add({'t': 'clone', 'h': tmpl, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': [v.P(*p) for p in pts], 'closed': closed})


def rect(v, x0, y0, x1, y1, tmpl=T_THIN):
    pl(v, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], tmpl, True)


def dot(v, x, y, d):
    c = v.P(x, y)
    o.add({'t': 'circle', 'c': c, 'r': K * d / 2, 'layer': 'Размеры'})
    o.add({'t': 'hatch', 'pat': 'SOLID', 'layer': 'Размеры', 'loops': [[[c[0] + K * d / 2 * math.cos(a / 8 * math.pi), c[1] + K * d / 2 * math.sin(a / 8 * math.pi)] for a in range(16)]]})


def dim(v, p1, p2, at, vertical=False, txt=None, tx=None):
    a, b = v.P(*p1), v.P(*p2)
    if vertical:
        d = {'t': 'dim', 'h': T_DIM, 'p1': a, 'p2': b, 'dl': [v.ox + K * at, a[1]], 'rot': math.pi / 2, 'lfac': 1 / K}
    else:
        d = {'t': 'dim', 'h': T_DIM, 'p1': a, 'p2': b, 'dl': [a[0], v.oy + K * at], 'rot': 0, 'lfac': 1 / K}
    if txt: d['txt'] = txt
    if tx: d['tx'] = v.P(*tx)
    o.add(d)


def chain(v, pts, at, vertical=False, texts=None, origin=None, small=None):
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        txt = texts[k] if texts and texts[k] else None
        tx = small.get(k) if small else None
        if vertical: dim(v, (origin if origin is not None else at, a), (origin if origin is not None else at, b), at, True, txt, tx)
        else: dim(v, (a, origin if origin is not None else at), (b, origin if origin is not None else at), at, False, txt, tx)


def note(v, l1, l2, tgt, org, arrow='oblique'):
    h = o.tag(); o.add({'t': 'clone', 'h': T_NOTE, 'tag': h})
    o.add({'t': 'moveto', 'h': h, 'idx': 1, 'to': v.P(*tgt)})
    o.add({'t': 'mcset', 'h': h, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': v.P(*org), 'Angle': 0.0 if org[0] > tgt[0] else math.pi,
                                          'Arrow': 'Oblique' if arrow == 'oblique' else 'None'}})


def title(v, text, xa, xb, y):
    x = (xa + xb) / 2 - len(text) * 240 / 2 / K
    h = o.tag(); o.add({'t': 'clone', 'h': T_TTL, 'tag': h})
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + text + '}'})
    o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': v.P(x, y)})


def stubs_plan(v):
    for x0, y0, x1, y1 in ((825, 3000, 1175, 3300), (825, -300, 1175, 0), (-300, 1325, 0, 1675), (2000, 1325, 2300, 1675)):
        pl(v, [(x0, y0), (x0, y1)] if y1 - y0 == 300 else [(x0, y0), (x1, y0)])
        pl(v, [(x1, y0), (x1, y1)] if y1 - y0 == 300 else [(x0, y1), (x1, y1)])


PX, PY = FD.PX, FD.PY
# ---------------- plan: bottom mesh
v1 = View(5500, 22500)
rect(v1, 0, 0, PX, PY); stubs_plan(v1)
for x in FD.B1: pl(v1, [(x, 50), (x, PY - 50)], T_BAR)
for y in FD.B2: pl(v1, [(50, y), (PX - 50, y)], T_BAR)
chain(v1, [0, 50, FD.B1[-2], FD.B1[-1], PX], -700, texts=[None, '150х%d=%d' % (len(FD.B1) - 2, FD.B1[-2] - 50), None, None], origin=0,
      small={0: (-250, -560), 2: (PX - 100, -560), 3: (PX + 220, -560)})
dim(v1, (0, 0), (PX, 0), -1150)
chain(v1, [0, 50, FD.B2[-2], FD.B2[-1], PY], -700, True, texts=[None, '150х%d=%d' % (len(FD.B2) - 2, FD.B2[-2] - 50), None, None], origin=0,
      small={0: (-560, -250), 2: (-560, PY - 100), 3: (-560, PY + 220)})
dim(v1, (0, 0), (0, PY), -1150, True)
note(v1, '1(%%C20)', 'ш.150', (FD.B1[-4], 2650), (PX + 450, PY - 150))
note(v1, '2(%%C20)', 'ш.150', (1700, FD.B2[4]), (PX + 450, FD.B2[4] - 450))
title(v1, 'Подушка Фм-1. Нижняя сетка', 0, PX, PY + 450)

# ---------------- plan: top mesh + column dowels
v2 = View(20500, 22500)
rect(v2, 0, 0, PX, PY); stubs_plan(v2)
rect(v2, 650, 1050, 1350, 1950)
for x in FD.T3: pl(v2, [(x, 50), (x, PY - 50)], T_BAR)
for y in FD.T4: pl(v2, [(50, y), (PX - 50, y)], T_BAR)
for dx, dy in FD.DOW: dot(v2, 1000 + dx, 1500 + dy, 28)
rect(v2, 1000 - FD.X1_A / 2 - 20, 1500 - FD.X1_B / 2 - 20, 1000 + FD.X1_A / 2 + 20, 1500 + FD.X1_B / 2 + 20, T_BAR)
chain(v2, [0, 50, FD.T3[-2], FD.T3[-1], PX], -700, texts=[None, '200х%d=%d' % (len(FD.T3) - 2, FD.T3[-2] - 50), None, None], origin=0,
      small={0: (-250, -560), 2: (PX - 100, -560), 3: (PX + 220, -560)})
chain(v2, [0, 50, FD.T4[-2], FD.T4[-1], PY], -700, True, texts=[None, '200х%d=%d' % (len(FD.T4) - 2, FD.T4[-2] - 50), None, None], origin=0,
      small={0: (-560, -250), 2: (-560, PY - 100), 3: (-560, PY + 220)})
note(v2, '3(%%C16)', 'ш.200', (FD.T3[-4], 2650), (PX + 450, PY - 150))
note(v2, '4(%%C16)', 'ш.200', (1800, FD.T4[2]), (PX + 450, FD.T4[2] - 450))
note(v2, 'Вп1(%%C28)', '14 шт.', (1000 + FD.COLX[-1], 1500 + FD.COLY[2]), (PX + 450, 1500 + 300), 'none')
note(v2, 'Х1(%%C8)', 'ш.200', (1000 + FD.X1_A / 2 + 20, 1500 - 250), (PX + 450, 1500 - 700))
title(v2, 'Подушка Фм-1. Верхняя сетка', 0, PX, PY + 450)

# ---------------- section 3-3 (beam 350x600)
v3 = View(35000, 22000)
rect(v3, 0, 0, 350, 600)
rect(v3, 40, 30, 310, 570, T_BAR)
for x in (60, 175, 290):
    dot(v3, x, 60, 20); dot(v3, x, 540, 20)
for x in (60, 290): dot(v3, x, 300, 12)
dim(v3, (0, 0), (350, 0), -400)
chain(v3, [0, 600], -350, True, origin=0)
note(v3, '5(%%C20)', '3+3', (290, 540), (750, 1000), 'none')
note(v3, '6(%%C12)', '', (290, 300), (750, 150), 'none')
note(v3, 'Х2(%%C10)', 'ш.150', (310, 420), (750, 620))
title(v3, 'Разрез 3 - 3', 0, 350, 1300)


def section(v, L, along_y):
    """1-1 (along Y, L=3000) / 2-2 (along X, L=2000): pad, подготовка, beam stubs, column stub, bars"""
    rect(v, 0, 0, L, 1000)
    rect(v, -100, -100, L + 100, 0)
    for a, b in ((-300, 0), (L, L + 300)):
        rect(v, a, 400, b, 1000)
    rect(v, L / 2 - (450 if along_y else 350), 1000, L / 2 + (450 if along_y else 350), 2900)
    lo, hi = (FD.B2, FD.B1) if along_y else (FD.B1, FD.B2)          # lower-layer dots, upper-layer line
    pl(v, [(50, 80), (L - 50, 80)], T_BAR)
    for p in lo: dot(v, p, 60, 20)
    tl, td = (FD.T4, FD.T3) if along_y else (FD.T3, FD.T4)
    pl(v, [(50, 942), (L - 50, 942)], T_BAR)
    for p in tl: dot(v, p, 926, 16)
    for e in (40, L - 40):                                          # Ск1 П-скобы
        s = 1 if e < L / 2 else -1
        pl(v, [(e + s * 1000, 40), (e, 40), (e, 960), (e + s * 1000, 960)], T_BAR)
    off = FD.COLY if along_y else FD.COLX
    for d in off:                                                   # dowels Вп1 (visible behind the cut)
        x = L / 2 + d; s = 1 if d > 0 else -1
        pl(v, [(x + s * 200, 100), (x, 100), (x, 1000 + FD.LAP28)], T_BAR)
    w = (FD.X1_B if along_y else FD.X1_A) / 2 + 20
    for z in (150, 350, 550, 750, 900):
        pl(v, [(L / 2 - w, z), (L / 2 + w, z)], T_BAR)
    for a, b in ((-300, 300), (L - 300, L + 300)):
        pl(v, [(a, 460), (b, 460)], T_BAR); pl(v, [(a, 900), (b, 900)], T_BAR)
    chain(v, [0, L / 2, L], -500, origin=-100)
    dim(v, (0, -100), (L, -100), -900)
    chain(v, [-100, 0, 1000, 1000 + FD.LAP28], L + 600, True, origin=L, small={0: (L + 1060, -300)})
    note(v, '1(%%C20)' if along_y else '2(%%C20)', '', (L * 0.15, 80), (-700, 330))
    note(v, '2(%%C20)' if along_y else '1(%%C20)', '', (lo[2], 60), (-700, -230), 'none')
    note(v, 'Ск1(%%C16)', 'ш.200', (40, 700), (-600, 1500))
    note(v, 'Вп1(%%C28)', '', (L / 2 + off[-1], 1500), (L / 2 + off[-1] + 500, 2300))
    note(v, 'Х1(%%C8)', 'ш.200', (L / 2 + w, 550), (L / 2 + w + 500, 1300))
    note(v, '3(%%C16)' if along_y else '4(%%C16)', '', (L * 0.8, 942), (L * 0.8 + 400, 1500))


v4 = View(6500, 3500); section(v4, PY, True); title(v4, 'Разрез 1 - 1', 0, PY, 3150)
v5 = View(28000, 3500); section(v5, PX, False); title(v5, 'Разрез 2 - 2', 0, PX, 3150)


# ---------------- Ведомость деталей (lines lw 0.30 + mtext 2.5 mm)
TX0, TY1, CW0, CW, RH = X0 + 33900, Y0 + 38200, 1300, 5000, 2200
DET = [('Ск1', 'sk'), ('Вп1', 'vp'), ('Х1', 'x1'), ('Х2', 'x2')]
TY0 = TY1 - 800 - RH * len(DET)


def ln(pts, lw=30, closed=False):
    t = o.tag(); o.add({'t': 'pl', 'p': [[round(a, 1), round(b, 1)] for a, b in pts], 'layer': '0', 'lw': lw, 'closed': closed, 'tag': t})


def tx(x, y, s, att=5, rot=None):
    d = {'t': 'mtext', 'at': [round(x, 1), round(y, 1)], 'h': 250, 'layer': 'Размеры', 's': s, 'att': att}
    if rot is not None: d['rot'] = rot
    o.add(d)


tx(TX0 + (CW0 + CW) / 2, TY1 + 450, 'Ведомость деталей')
ln([(TX0, TY0), (TX0 + CW0 + CW, TY0), (TX0 + CW0 + CW, TY1), (TX0, TY1)], closed=True)
ln([(TX0 + CW0, TY0), (TX0 + CW0, TY1)])
ln([(TX0, TY1 - 800), (TX0 + CW0 + CW, TY1 - 800)])
tx(TX0 + CW0 / 2, TY1 - 400, 'Поз.'); tx(TX0 + CW0 + CW / 2, TY1 - 400, 'Эскиз')
P = {p[0]: p for p in FD.POS}
for k, (pos, kind) in enumerate(DET):
    yt = TY1 - 800 - RH * k; yb = yt - RH
    if k: ln([(TX0, yt), (TX0 + CW0 + CW, yt)])
    tx(TX0 + CW0 / 2, (yt + yb) / 2, pos)
    _, _, d, cls, L, n, _ = P[pos]
    sx = TX0 + CW0 + 900; sy = yb + 650
    tx(TX0 + CW0 + CW / 2, yb + 280, '%%%%C%d A%s  L=%d' % (d, cls, L))
    B = lambda pts: pl(View(0, 0), [((a - X0) / K, (b - Y0) / K) for a, b in pts], T_BAR)
    if kind == 'sk':
        w, h = 2800, 1150
        B([(sx + w, sy + h), (sx, sy + h), (sx, sy), (sx + w, sy)])
        tx(sx + w / 2, sy + h + 180, '1000'); tx(sx - 200, sy + h / 2, '%d' % (FD.PH - 80), rot=math.pi / 2)
    elif kind == 'vp':
        w, h = 3400, 350
        B([(sx, sy + h + 350), (sx + w, sy + h + 350), (sx + w, sy + 350)])
        tx(sx + w / 2, sy + h + 530, '%d' % (L - 200)); tx(sx + w + 200, sy + h / 2 + 350, '200', rot=math.pi / 2)
    else:
        a, b = (FD.X1_A, FD.X1_B) if kind == 'x1' else (280, 530)
        h = 1150; w = h * a / b
        cx = sx + 900
        B([(cx + 180, sy + h - 180), (cx, sy + h), (cx + w, sy + h), (cx + w, sy), (cx, sy), (cx, sy + h), (cx + 180 + 40, sy + h - 180 + 40)])
        tx(cx + w / 2, sy + h + 180, '%d' % a); tx(cx - 200, sy + h / 2, '%d' % b, rot=math.pi / 2)
        tx(cx + w + 1000, sy + h / 2, 'крюки 2х100')

o.add({'t': 'settext', 'h': '37FC4B', 's': 'Фундамент Фм-1. Армирование'})
o.add({'t': 'settext', 'h': '37FC4D', 's': '3.2'})
o.add({'t': 'vpset2', 'layout': '3.5', 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [X0, Y0 - 2000, X0 + 59400, Y0 + 40000], 'scale': 100})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g32', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'no prop' in l)[-1500:])
