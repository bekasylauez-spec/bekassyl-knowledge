"""Beam sheet «Балка Бм-N» (A2 1:100, АБК 6.x manner): elevation of the typical line, section 1-1 (1:20), ведомость деталей, spec, steel.
python gen6x.py <mark> <sheet no> [run]"""
import sys, math, re
import ab, beamdata as BD, beams_ob as BO

MARK, SNO = sys.argv[1], sys.argv[2]
RUN = len(sys.argv) > 3
K_ = int(SNO.split('.')[1])
X35, Y0 = -750903.0, -1749172.0
X0 = -513303.0 + (K_ - 1) * 59400.0
DX = X0 - X35
sch = BD.schedule(MARK); A = sch['A']; b, h = sch['b'], sch['h']
LN = sch['lines'][0]; seg = sch['segs'][0]
alongX = seg[1] == seg[3]
lvl = 11400 if sch['lv'] == '+11.400' else 6200
slope = sch['lv'] == 'уклон'
T_DIM, T_NOTE, T_TTL = 'T35:37FB09', 'T35:37FB36', 'T35:37FB38'
LM6, LM11 = ('3D9F9B', (-1186028.0, -1730872.0)), ('3D9F95', (-1185327.9, -1725671.8))
AXT, AXP = '3E444F', ((-1091273.0, -1710322.0), (-1091273.0, -1728572.0))
SECT = '3E529E'
PRE = 'b%s_' % SNO

O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1},
     {'t': 'eraseregion', 'win': [X0 + 1, Y0 - 1999, X0 + 59399, Y0 + 39999], 'mode': 'intersect'},
     {'t': 'clonexf', 'hs': ['37FB3A', '37FC4A', '37FC4B', '37FC4D', '37FCCB', '37FCCC'], 'd': [DX, 0], 'pre': PRE},
     {'t': 'settext', 'h': PRE + '37FC4B', 's': 'Балка %s' % MARK}, {'t': 'settext', 'h': PRE + '37FC4D', 's': SNO}]
_n = [0]


def tag():
    _n[0] += 1; return 'g6_%s_%d' % (SNO.replace('.', ''), _n[0])


def W(x, y): return [round(X0 + x, 1), round(Y0 + y, 1)]


def pl(pts, layer='Размеры', lw=30, closed=False):
    O.append({'t': 'pl', 'p': pts, 'layer': layer, 'lw': lw, 'closed': closed, 'tag': tag()})


def dim(p1, p2, at, vertical=False, txt=None, tx=None, lfac=1.0):
    d = {'t': 'dim', 'h': T_DIM, 'p1': p1, 'p2': p2, 'rot': math.pi / 2 if vertical else 0, 'lfac': lfac, 'txt': txt or '',
         'dl': [at, p1[1]] if vertical else [p1[0], at]}
    if tx: d['tx'] = tx
    O.append(d)


def note(l1, l2, tgt, org, arrow='Oblique'):
    t = tag(); O.append({'t': 'clone', 'h': T_NOTE, 'tag': t})
    O.append({'t': 'moveto', 'h': t, 'idx': 1, 'to': tgt})
    O.append({'t': 'mcset', 'h': t, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': org, 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow}})


def mtext(at, s, hgt=250, att=5, w=None, rot=None):
    d = {'t': 'mtext', 'at': at, 'h': hgt, 'layer': 'Размеры', 's': s, 'att': att}
    if w: d['w'] = w
    if rot is not None: d['rot'] = rot
    O.append(d)


def dot(c, r, layer):
    O.append({'t': 'circle', 'c': c, 'r': r, 'layer': layer})
    O.append({'t': 'hatch', 'pat': 'SOLID', 'layer': layer, 'loops': [[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]]})


fmt = lambda v: ('+' if v > 0 else '-') + ('%.3f' % abs(v / 1000)).replace('.', ',')


def level(x, y, z):
    src, ap = (LM11 if len(fmt(z)) == 7 else LM6)
    t = tag(); O.append({'t': 'clone', 'h': src, 'tag': t})
    O.append({'t': 'move', 'h': [t], 'd': [x - ap[0], y - ap[1]]})
    old = '+11,400' if src == LM11[0] else '+6,200'
    if fmt(z) != old: O.append({'t': 'levelval', 'h': t, 'old': old, 'value': fmt(z)})


# ---------------- elevation (1:100): s = coordinate along the beam, z = level
XS0, YT, KE = 8000.0, 24500.0, 2.0
e0, e1 = LN['e0'], LN['e1']
def ztop(s):
    if slope and alongX and s > 20000: return lvl - (s - 20000) / 12000 * 500
    return lvl
def P(s, z): return W(XS0 + KE * (s - e0), YT + KE * (z - lvl))
top0, top1 = ztop(e0), ztop(e1)
pl([P(e0, top0), P(e1, top1), P(e1, top1 - h), P(e0, top0 - h)], closed=True)
for (sp, w, kind) in LN['S']:
    zt = ztop(sp)
    if kind == 'col':
        for s_ in (-1, 1):
            pl([P(sp + s_ * w / 2, zt + 700), P(sp + s_ * w / 2, zt - h - 250)], lw=5)
        for zz in (zt + 700,):
            pl([P(sp - w / 2 - 100, zz), P(sp - 60, zz), P(sp - 20, zz + 80), P(sp + 20, zz - 80), P(sp + 60, zz), P(sp + w / 2 + 100, zz)], lw=5)
    elif kind != 'end':
        hb = BO.B62.get(kind, BO.B114.get(kind, (300, 400)))[1]
        pl([P(sp - w / 2, zt), P(sp + w / 2, zt), P(sp + w / 2, zt - hb), P(sp - w / 2, zt - hb)], lw=5, closed=True)
# bars
cov = 50
pl([P(e0 + 30, top0 - h + cov), P(e1 - 30, top1 - h + cov)], 'диам%d' % A['d'], 40)
pl([P(e0 + 30, top0 - cov), P(e1 - 30, top1 - cov)], 'диам%d' % A['d'], 40)
for k in range(A['side']):
    zz = (k + 1) / (A['side'] + 1)
    pl([P(e0 + 30, top0 - h + h * zz), P(e1 - 30, top1 - h + h * zz)], 'диам12', 40)
leg = sch['leg']
for e, s_ in ((e0 + 55, 1), (e1 - 55, -1)):
    zt = ztop(e)
    pl([P(e + s_ * leg, zt - cov - 25), P(e, zt - cov - 25), P(e, zt - h + cov + 25), P(e + s_ * leg, zt - h + cov + 25)], 'диам16', 40)
# hoops (zone ends) + chain under the beam
yb_ch = YT - h - 900 - 600
runs_all = []
for (a, c), hz in zip(LN['spans'], LN['hz']):
    if c - a < 1: continue
    pts = [a] + hz + [c]
    dd = [round(q - p) for p, q in zip(pts, pts[1:])]
    k = 0
    while k < len(dd):
        m_ = k
        while m_ + 1 < len(dd) and dd[m_ + 1] == dd[k]: m_ += 1
        runs_all.append((pts[k], pts[m_ + 1], dd[k], m_ - k + 1)); k = m_ + 1
    for z_ in hz:
        zt = ztop(z_)
        pl([P(z_, zt - 30), P(z_, zt - h + 30)], 'диам10', 30)
lowest = min(top0, top1) - h
ych = YT + KE * (lowest - lvl) - 1500
span_ends = set()
for a_, c_ in LN['spans']: span_ends.add(round(a_)); span_ends.add(round(c_))
for (p, q, st, n) in runs_all:
    txt = ('%dх%d' % (st, n)) if n > 1 else None
    tx = None
    if q - p < 450:
        xm = X0 + XS0 + KE * ((p + q) / 2 - e0)
        if round(p) in span_ends: tx = [X0 + XS0 + KE * (q - e0) + 330, Y0 + ych - 300]
        elif round(q) in span_ends: tx = [X0 + XS0 + KE * (p - e0) - 330, Y0 + ych - 300]
        else: tx = [xm - 600, Y0 + ych - 300]
    dim(P(p, lowest), P(q, lowest), Y0 + ych, False, txt, tx, 1 / KE)
# axes chain + overall + SPDS axes
axpos = [(sp, kind) for sp, w, kind in LN['S']]
names = ['1', '2', '3', '4', '5', '6', '7', '8'] if alongX else ['А', 'Б', 'В']
grid = BO.AX if alongX else BO.AY
ya1, ya2 = ych - 800, ych - 1600
pts_ax = [sp for sp, kind in axpos]
for p, q in zip(pts_ax, pts_ax[1:]):
    dim(P(p, lowest), P(q, lowest), Y0 + ya1, lfac=1 / KE)
axx = [P(sp_, 0)[0] for sp_, w_, k_ in LN['S']]
cxx = P((e0 + e1) / 2, 0)[0]
for kk in [0] + [s_ * j * 700 for j in range(1, 15) for s_ in (1, -1)]:
    if all(abs(cxx + kk - a_) > 1300 for a_ in axx): cxx += kk; break
dim(P(e0, lowest), P(e1, lowest), Y0 + ya2, lfac=1 / KE, tx=[cxx, Y0 + ya2 + 170])
for sp, kind in axpos:
    if any(abs(sp - g) < 1 for g in grid):
        nm = names[[abs(sp - g) < 1 for g in grid].index(True)]
        t = tag(); O.append({'t': 'clone', 'h': AXT, 'tag': t})
        O.append({'t': 'axis', 'h': t, 's': P(sp, ztop(sp) + 900), 'e': [P(sp, 0)[0], Y0 + ych - 1600 - 1700], 'val': nm})
# level marks, notes, section mark, title
level(X0 + XS0 - 300, Y0 + YT + KE * (top0 - lvl), top0)
if slope and abs(top1 - top0) > 1: level(X0 + XS0 + KE * (e1 - e0) + 700 + 3900, Y0 + YT + KE * (top1 - lvl), top1)
(sa, sc_) = LN['spans'][0] if LN['spans'][0][1] - LN['spans'][0][0] > 1 else LN['spans'][1]
sp2 = [q for q in LN['spans'] if q[1] - q[0] > 1]
spL = sp2[-1]
bnd = sorted(set([spL[0], spL[1]] + [r[0] for r in runs_all if spL[0] <= r[0] <= spL[1]] + [r[1] for r in runs_all if spL[0] <= r[1] <= spL[1]]))
gaps = [(q_ - p_, (p_ + q_) / 2) for p_, q_ in zip(bnd, bnd[1:])]
if len(sp2) == 1: gaps = [g for g in gaps if spL[0] + (spL[1] - spL[0]) * 0.75 < g[1] < spL[0] + (spL[1] - spL[0]) * 0.9] or gaps
sm = max(gaps)[1]
sp2 = [q for q in LN['spans'] if q[1] - q[0] > 1]
s2a, s2c = sp2[1] if len(sp2) > 2 else sp2[0]
hz2 = LN['hz'][LN['spans'].index((s2a, s2c))]
note('1(%%%%C%d)' % A['d'], '%d шт.' % A['n'], P(e0 + 150, ztop(e0) - h + cov), [X0 + XS0 - 900, Y0 + YT + KE * (ztop(e0) - lvl - h) - 500])
note('2(%%%%C%d)' % A['d'], '%d шт.' % A['n'], P(sa + (sc_ - sa) * 0.25, ztop(sa) - cov), [P(sa + (sc_ - sa) * 0.25, 0)[0] + 700, Y0 + YT + KE * (ztop(sa) - lvl) + 1800])
hxx = hz2[len(hz2) // 3] if len(sp2) > 2 else hz2[int(len(hz2) * 0.6)]
note('Х1(%%C10)', 'см. цепочку', P(hxx, ztop(s2a) - h / 2), [max(P(hxx, 0)[0] + 700, P(sa + (sc_ - sa) * 0.25, 0)[0] + 700 + 2600) if len(sp2) > 1 else P(sa + (sc_ - sa) * 0.25, 0)[0] + 700 + 1900, Y0 + YT + KE * (ztop(s2a) - lvl) + 1800])
note('Ск1(%%C16)', '', P(e1 - 55, ztop(e1) - h / 2), [P(e1, 0)[0] + 900, Y0 + YT + KE * (ztop(e1) - lvl) + 1500])
t = tag(); O.append({'t': 'clone', 'h': SECT, 'tag': t})
O.append({'t': 'spmove', 'h': t, 'items': [[0] + [P(sm, 0)[0], P(sm, ztop(sm) - h)[1] - 750], [1] + [P(sm, 0)[0], P(sm, ztop(sm))[1] + 750]]})
O.append({'t': 'secset', 'h': t, 'word': '1'})
t = tag(); O.append({'t': 'clone', 'h': T_TTL, 'tag': t})
ttl = 'Балка %s (%s)' % (MARK, ', '.join('%s шт.' % len(sch['segs']) for _ in [0]))
O.append({'t': 'settext', 'h': t, 's': '{\\L%s}' % ttl})
O.append({'t': 'moveto', 'h': t, 'idx': 0, 'to': W(XS0 + KE * (e1 - e0) / 2 - len(ttl) * 120, YT + KE * (max(top0, top1) - lvl) + 3600)})

# ---------------- section 1-1 (1:20 = x5)
KS = 5.0
SX, SY = 11000.0, 8500.0
def Q(x, z): return W(SX + KS * x, SY + KS * z)
pl([Q(-b / 2, 0), Q(b / 2, 0), Q(b / 2, h), Q(-b / 2, h)], closed=True)
xs = [-b / 2 + cov + k * (b - 2 * cov) / (A['n'] - 1) for k in range(A['n'])]
for x in xs:
    dot(Q(x, cov), KS * A['d'] / 2, 'диам%d' % A['d']); dot(Q(x, h - cov), KS * A['d'] / 2, 'диам%d' % A['d'])
for k in range(A['side']):
    z = h * (k + 1) / (A['side'] + 1)
    for x in (xs[0], xs[-1]): dot(Q(x, z), KS * 6, 'диам12')
hw = A['d'] / 2 + 5
if A['hoops'] == 1:
    hs = [(xs[0] - hw, xs[-1] + hw)]
else:
    hs = [(xs[0] - hw, xs[2] + hw), (xs[-3] - hw, xs[-1] + hw)]
for k, (a, c) in enumerate(hs):
    o_ = 0 if k == 0 else 10
    pl([Q(a, cov - hw - o_ / 2), Q(c, cov - hw - o_ / 2), Q(c, h - cov + hw + o_ / 2), Q(a, h - cov + hw + o_ / 2)], 'диам10', 30, True)
    pl([Q(a, h - cov + hw), Q(a + 40, h - cov + hw - 40)], 'диам10', 30)
dim(Q(-b / 2, 0), Q(b / 2, 0), Y0 + SY - 1200, lfac=1 / KS)
dim(Q(-b / 2, 0), Q(xs[0], 0), Y0 + SY - 600, lfac=1 / KS, tx=Q(-b / 2 - 90, -150))
dim(Q(xs[-1], 0), Q(b / 2, 0), Y0 + SY - 600, lfac=1 / KS, tx=Q(b / 2 + 90, -150))
pass
dim(Q(-b / 2, 0), Q(-b / 2, h), X0 + SX - KS * b / 2 - 600, True, lfac=1 / KS)
ox = b / 2 + 120
note('2(%%%%C%d)' % A['d'], '%d шт.' % A['n'], Q(xs[-1], h - cov), Q(ox, h + 60), 'None')
note('1(%%%%C%d)' % A['d'], '%d шт.' % A['n'], Q(xs[-1], cov), Q(ox, -60), 'None')
if A['side']: note('3(%%C12)', '', Q(xs[-1], h / (A['side'] + 1)), Q(ox, h * 0.35), 'None')
note('Х1(%%C10)', '%d шт. в сеч.' % A['hoops'], Q(hs[-1][1], h * 0.6), Q(ox, h * 0.7))
for k in range(A['side']):
    z = h * (k + 1) / (A['side'] + 1)
    pl([Q(xs[0] + 30, z + 30), Q(xs[0] - 12, z), Q(xs[-1] + 12, z), Q(xs[-1] - 30, z - 30)], 'диам10', 30)
if A['side']: note('Шп1(%%C10)', 'на каждом хомуте', Q(0, h / (A['side'] + 1)), Q(-b / 2 - 250, h * 0.5 if A['side'] > 1 else h * 0.75))
level(X0 + SX - KS * b / 2 - 1300, Y0 + SY + KS * h, ztop(sm))
t = tag(); O.append({'t': 'clone', 'h': T_TTL, 'tag': t})
O.append({'t': 'settext', 'h': t, 's': '{\\LРазрез 1 - 1}'})
O.append({'t': 'moveto', 'h': t, 'idx': 0, 'to': Q(-b / 2 - 150, h + 300)})

# ---------------- ведомость деталей
TX0, TY1, CW0, CW, RH = X0 + 20500, Y0 + 14500, 1300, 5000, 2000
DET = [('Х1', sch['hx1']), ('Ск1', None)] + ([('Шп1', None)] if A['side'] else [])
TY0 = TY1 - 800 - RH * len(DET)
mtext([TX0 + (CW0 + CW) / 2, TY1 + 450], 'Ведомость деталей')
pl([[TX0, TY0], [TX0 + CW0 + CW, TY0], [TX0 + CW0 + CW, TY1], [TX0, TY1]], '0', 30, True)
pl([[TX0 + CW0, TY0], [TX0 + CW0, TY1]], '0', 30); pl([[TX0, TY1 - 800], [TX0 + CW0 + CW, TY1 - 800]], '0', 30)
mtext([TX0 + CW0 / 2, TY1 - 400], 'Поз.'); mtext([TX0 + CW0 + CW / 2, TY1 - 400], 'Эскиз')
PD = {p[0]: p for p in sch['pos']}
for k, (pos, g) in enumerate(DET):
    yt = TY1 - 800 - RH * k; yb = yt - RH
    if k: pl([[TX0, yt], [TX0 + CW0 + CW, yt]], '0', 30)
    mtext([TX0 + CW0 / 2, (yt + yb) / 2], pos)
    _, d, L, n, _ = PD[pos]
    mtext([TX0 + CW0 + CW / 2, yb + 260], '%%%%C%d A500С  L=%d' % (d, L))
    sx, sy = TX0 + CW0 + 900, yb + 650
    if pos == 'Х1':
        a, c = g; hh = 950; w = hh * a / c
        pl([[sx, sy], [sx + w, sy], [sx + w, sy + hh], [sx, sy + hh]], 'диам10', 30, True)
        pl([[sx, sy + hh], [sx + 90, sy + hh - 90]], 'диам10', 30)
        mtext([sx + w / 2, sy + hh + 170], '%d' % a); mtext([sx - 180, sy + hh / 2], '%d' % c, rot=math.pi / 2)
        mtext([sx + w + 400, sy + hh / 2], 'крюки 2х100', att=4)
    elif pos == 'Шп1':
        w = 2600
        pl([[sx + 300, sy + 750], [sx + 50, sy + 500], [sx + w, sy + 500], [sx + w - 250, sy + 250]], 'диам10', 30)
        mtext([sx + w / 2, sy + 680], '%d' % (b - 2 * cov + 12)); mtext([sx + w / 2, sy + 80], 'крюки 135° 2х100')
    else:
        web = h - 2 * cov; hh = 950; w = 2000
        pl([[sx + w, sy + hh], [sx, sy + hh], [sx, sy], [sx + w, sy]], 'диам16', 40)
        mtext([sx + w / 2, sy + hh + 170], '%d' % leg); mtext([sx - 180, sy + hh / 2], '%d' % web, rot=math.pi / 2)

# ---------------- notes
segtxt = '; '.join('%s %d…%d' % (('ось ' + (['А', 'Б', 'В'][BO.AY.index(s_[1])] if s_[1] in BO.AY else str(s_[1]))) if s_[1] == s_[3] else
                                  ('ось ' + (str(BO.AX.index(s_[0]) + 1) if s_[0] in BO.AX else str(s_[0]))), min(s_[0], s_[1]) if False else (s_[0] if s_[1] == s_[3] else s_[1]),
                                  s_[2] if s_[1] == s_[3] else s_[3]) for s_ in sch['segs'])
mtext([X0 + 2300, Y0 + 3800], '1. Балка %s %dх%d, верх %s, бетон С20/25 (B25). Участки: %s. На листе показан участок %d…%d, остальные - аналогично (длины по схемам 2.3, 2.4).\\P'
      '2. Продольная арматура непрерывная, стыки - накладками Н (ГОСТ 14098-2014, С21-Рн), вразбежку, верх - в пролете, низ - над опорами.\\P'
      '3. Хомуты Х1 - по цепочке; в зоне опирания на колонну хомуты колонны (сетки С1). Защитный слой - 40 мм.'
      % (MARK, b, h, sch['lv'], segtxt, e0, e1), att=1, w=30000)

# ---------------- tables (cloned from 3.5): spec / steel
SP, ST = PRE + '37FCCB', PRE + '37FCCC'
POS = sch['pos']; Np = len(POS)
O.append({'t': 'trows', 'h': SP, 'mode': 'del', 'at': 3 + Np, 'n': 11 - Np})
O.append({'t': 'trows', 'h': SP, 'mode': 'del', 'at': 3 + Np + 2, 'n': 1})                # подготовка row
O.append({'t': 'theight', 'h': SP, 'rows': [[3 + Np, 800], [3 + Np + 1, 1100], [3 + Np + 2, 800]]})
cells = [[2, 2, 'Балка %s' % MARK]]; form = []
for r, p in zip(range(3, 3 + Np), POS):
    pos, d, L, n, _ = p
    unit = BD.KG[d] if L is None else round(L / 1000 * BD.KG[d], 2)
    cells += [[r, 0, pos + ('*' if pos in ('Х1', 'Ск1', 'Шп1') else '')], [r, 3, str(d)], [r, 5, '500С'], [r, 9, 'пог.м.' if L is None else str(int(L))],
              [r, 10, ('%.1f' % n) if L is None else str(n)], [r, 11, '%.2f' % unit]]
    form.append([r, 12, 'K%d*L%d' % (r + 1, r + 1)])
form.append([2, 12, 'Sum(M4:M%d)' % (3 + Np)])
cells.append([3 + Np + 1, 12, '%.2f' % sch['conc']])
O += [{'t': 'tset', 'h': SP, 'cells': cells}, {'t': 'tformula', 'h': SP, 'cells': form, 'fmt': '%lu2%pr2'}]
by = {}
for p in POS:
    unit = BD.KG[p[1]] if p[2] is None else round(p[2] / 1000 * BD.KG[p[1]], 2)
    by[p[1]] = by.get(p[1], 0) + unit * p[3]
big = 25 if A['d'] == 25 else 20
sc = [[5, 1, '%%C10'], [5, 2, '%%C12'], [5, 3, '%%C16'], [5, 4, '%%C20'], [5, 5, '%%C28'], [6, 0, 'Балка %s' % MARK]]
for c, d in zip(range(1, 6), (10, 12, 16, 20, 28)): sc.append([6, c, '%.2f' % by.get(d, 0)])
O += [{'t': 'tset', 'h': ST, 'cells': sc}, {'t': 'tformula', 'h': ST, 'cells': [[6, 6, 'Sum(B7:F7)'], [6, 7, 'G7']], 'fmt': '%lu2%pr2'},
      {'t': 'move', 'h': [ST], 'd': [-16950, 16640]}]
O.append({'t': 'vpset2', 'layout': SNO, 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [X0, Y0 - 2000, X0 + 59400, Y0 + 40000], 'scale': 100})
O.append({'t': 'save'})
print(MARK, SNO, len(O), 'ops; total kg %.1f' % sum(by.values()))
if RUN:
    out = ab.run(O, 'g6', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l)[-1500:])
