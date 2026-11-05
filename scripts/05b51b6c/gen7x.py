"""Slab sheets (АБК 7.x manner, A2 1:100): plan base copied from 2.2 / 2.3, representative bars + bar-step chains, section 1-1 (1:20), spec/steel.
python gen7x.py <Пм-1|Пм-2> <sheet no> [run]"""
import sys, os, math, ezdxf
import ab, slabdata as SD, beams_ob as BO

MARK, SNO = sys.argv[1], sys.argv[2]
RUN = len(sys.argv) > 3
K_ = int(SNO.split('.')[1])
Y0 = -1749172.0
X35 = -750903.0
SLOT = 496497.0 + (K_ - 1) * 59400.0
SRC = {'Пм-1': -1463703.0, 'Пм-2': -1374603.0}[MARK]
DXP, DYP = 8305.0, 12300.0                    # A3 sheet content -> A2 sheet (as on 3.1)
DX = SLOT - SRC + DXP
sch = SD.pm1() if MARK == 'Пм-1' else SD.pm2()
T_DIM, T_NOTE, T_TTL = 'T35:37FB09', 'T35:37FB36', 'T35:37FB38'
PRE = 's%s_' % SNO

ab.run([{'t': 'list', 'win': [SRC, Y0, SRC + 42000, Y0 + 29700]}], 'si')
E = []
for l in open(os.path.join(os.environ['TEMP'], 'ob_log.txt'), encoding='utf-8-sig'):
    f = l.rstrip('\n').split('\t')
    if f[0] == 'L' and len(f) >= 5:
        E.append(dict(t=f[1], h=f[2], lay=f[3], e=list(map(float, f[4][1:].split(','))), pts=[tuple(map(float, q.split(',')[:2])) for q in f[5:] if ',' in q]))
ab.dxf(); D = ezdxf.readfile('w/live.dxf')
AXL = [e for e in E if e['t'] == 'SPDSCONSTRUCTIONLINE']
V = sorted([e for e in AXL if abs(e['pts'][0][0] - e['pts'][1][0]) < 1], key=lambda e: e['pts'][0][0])
H = sorted([e for e in AXL if abs(e['pts'][0][1] - e['pts'][1][1]) < 1], key=lambda e: e['pts'][0][1])
XA, YA = V[0]['pts'][0][0] + DX, H[0]['pts'][0][1] + DYP
KEEPM = {3250, 4500, 6000, 12000, 32000}
base = [e['h'] for e in AXL]
base += [e['h'] for e in E if e['t'] == 'DIMENSION' and round(D.entitydb.get(e['h']).get_measurement()) in KEEPM]
stamp_y = Y0 + 6500
base += [e['h'] for e in E if e['t'] in ('LWPOLYLINE', 'HATCH') and e['e'][1] > stamp_y - 4000 and not (e['e'][0] > SRC + 23000 and e['e'][3] < Y0 + 6000)]

O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1},
     {'t': 'eraseregion', 'win': [SLOT + 1, Y0 + 1, SLOT + 59399, Y0 + 41999], 'mode': 'intersect'},
     {'t': 'clonexf', 'hs': ['a2_31_3E425D', 'a2_31_3E425E', 'a2_31_3E425F', 'a2_31_3E4261'], 'd': [SLOT - (-1107303.0), 0], 'pre': 'fr%s_' % SNO},
     {'t': 'clonexf', 'hs': base, 'd': [DX, DYP], 'pre': 'b%s_' % SNO},
     {'t': 'clonexf', 'hs': ['37FCCB', '37FCCC'], 'd': [SLOT - X35, 2000], 'pre': PRE}]
m = ab.tagmap()
TITLE = {'Пм-1': 'Плита по грунту Пм-1 на отм. 0.000. Армирование', 'Пм-2': 'Плита Пм-2 на отм. +6.200. Армирование'}[MARK]
O += [{'t': 'settext', 'h': 'fr%s_' % SNO + m['a2_31_3E4261'], 's': TITLE}, {'t': 'settext', 'h': 'fr%s_' % SNO + m['a2_31_3E425F'], 's': SNO}]
_n = [0]


def tag():
    _n[0] += 1; return 'g7_%s_%d' % (SNO.replace('.', ''), _n[0])


def P(x, y): return [round(XA + x, 1), round(YA + y, 1)]
def W(x, y): return [round(SLOT + x, 1), round(Y0 + y, 1)]


def pl(pts, layer='Размеры', lw=30, closed=False, ltype=None):
    d = {'t': 'pl', 'p': pts, 'layer': layer, 'lw': lw, 'closed': closed, 'tag': tag()}
    if ltype: d['ltype'] = ltype
    O.append(d)


def dim(p1, p2, at, vertical=False, txt=None, tx=None, lfac=1.0):
    d = {'t': 'dim', 'h': T_DIM, 'p1': p1, 'p2': p2, 'rot': math.pi / 2 if vertical else 0, 'lfac': lfac, 'txt': txt or '',
         'dl': [at, p1[1]] if vertical else [p1[0], at]}
    if tx: d['tx'] = tx
    O.append(d)


def note(l1, l2, tgt, org, arrow='Oblique'):
    t = tag(); O.append({'t': 'clone', 'h': T_NOTE, 'tag': t})
    O.append({'t': 'moveto', 'h': t, 'idx': 1, 'to': tgt})
    O.append({'t': 'mcset', 'h': t, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': org, 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow}})


def mtext(at, s, hgt=250, att=5, w=None):
    d = {'t': 'mtext', 'at': at, 'h': hgt, 'layer': 'Размеры', 's': s, 'att': att}
    if w: d['w'] = w
    O.append(d)


def dot(c, r, layer):
    O.append({'t': 'circle', 'c': c, 'r': r, 'layer': layer})
    O.append({'t': 'hatch', 'pat': 'SOLID', 'layer': layer, 'loops': [[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]]})


x0, y0, x1, y1 = SD.SL
d = 12 if MARK == 'Пм-1' else 14
lay = 'диам%d' % d
# representative bars: along X at y = Б+1050 (bay Б-В, clear of beams), along Y at x mid of bay 4-5
yr = BO.AY[1] + 1050; xr = (BO.AX[3] + BO.AX[4]) / 2 + 100
ops = [] if MARK == 'Пм-1' else list(BO.OPEN62.values())
for p, q in SD.intervals(x0 + 30, x1 - 30, [(o[0], o[2]) for o in ops if o[1] - 30 <= yr <= o[3] + 30]):
    pl([P(p, yr), P(q, yr)], lay, 40)
for p, q in SD.intervals(y0 + 30, y1 - 30, [(o[1], o[3]) for o in ops if o[0] - 30 <= xr <= o[2] + 30]):
    pl([P(xr, p), P(xr, q)], lay, 40)
if MARK == 'Пм-2':
    yr2, xr2 = yr + 100, xr + 100
    for p, q in SD.intervals(x0 + 30, x1 - 30, [(o[0], o[2]) for o in ops if o[1] - 30 <= yr2 <= o[3] + 30]):
        pl([P(p, yr2), P(q, yr2)], lay, 40, ltype='DASHED')
    for p, q in SD.intervals(y0 + 30, y1 - 30, [(o[1], o[3]) for o in ops if o[0] - 30 <= xr2 <= o[2] + 30]):
        pl([P(xr2, p), P(xr2, q)], lay, 40, ltype='DASHED')
    o = BO.OPEN62['О-2']
    for yy in (o[1] - 100, o[3] + 100):
        pl([P(o[0] - 600, yy), P(o[2] + 600, yy)], lay, 40)
    note('3(%%C14)', '2 шт. у каждой грани', P(o[0] + 2500, o[3] + 100), P(o[0] + 3500, o[3] + 1300))
    note('1(%%C14) низ', 'ш.200', P(x0 + 2000, yr), P(x0 + 2600, yr - 1200))
    note('2(%%C14) верх', 'ш.200', P(x0 + 4000, yr2), P(x0 + 4600, yr2 + 1300))
else:
    note('1(%%C12)', 'ш.200, 2 сетки', P(x0 + 2000, yr), P(x0 + 2600, yr - 1200))
# bar-step chains: top edge (bars along Y), right edge (bars along X)
nyb = int((x1 - x0 - 2 * SD.C0) // SD.STEP); nxb = int((y1 - y0 - 2 * SD.C0) // SD.STEP)
xs = [x0, x0 + SD.C0, x0 + SD.C0 + SD.STEP * nyb, x1]
ys = [y0, y0 + SD.C0, y0 + SD.C0 + SD.STEP * nxb, y1]
yt = y1 + 1500
for k, (p, q) in enumerate(zip(xs, xs[1:])):
    txt = '200х%d=%d' % (nyb, SD.STEP * nyb) if k == 1 else None
    tx = None if k == 1 else (P(p - 450, yt + 170) if k == 0 else P(q + 450, yt + 170))
    dim(P(p, y1), P(q, y1), YA + yt, False, txt, tx)
xt = x1 + 1600
for k, (p, q) in enumerate(zip(ys, ys[1:])):
    txt = '200х%d=%d' % (nxb, SD.STEP * nxb) if k == 1 else None
    tx = None if k == 1 else (P(xt - 170, p - 450) if k == 0 else P(xt - 170, q + 450))
    dim(P(x1, p), P(x1, q), XA + xt, True, txt, tx)
O.append({'t': 'mtext', 'at': P(16000, 12000 + 1500 + 2800 + 1000), 'h': 300, 'att': 2, 'style': 'ISOCPEUR.', 'layer': 'Размеры', 's': '{\\L%s}' % TITLE})

# ---------------- section 1-1 (1:20)
KS = 5.0
SX, SY = 9000.0, 9000.0
def Q(x, z): return W(SX + KS * x, SY + KS * z)
t = sch['t']
if MARK == 'Пм-1':
    pl([Q(-1000, 0), Q(1000, 0), Q(1000, t), Q(-1000, t)], closed=True)
    pl([Q(-1000, -100), Q(1000, -100), Q(1000, 0), Q(-1000, 0)], lw=5, closed=True)
    for z in (30, t - 30):
        pl([Q(-1000, z), Q(1000, z)], lay, 40)
        for k in range(10): dot(Q(-900 + 200 * k, z + (12 if z < t / 2 else -12)), KS * 6, lay)
    dim(Q(1000, 0), Q(1000, t), W(SX + KS * 1000 + 600, 0)[0], True, lfac=1 / KS)
    note('1(%%C12)', 'ш.200', Q(-500, t - 30), Q(-1300, t + 250))
else:
    bb, hb = 450, 600
    pl([Q(-1000, 0), Q(1000, 0), Q(1000, t), Q(-1000, t)], closed=True)
    pl([Q(-bb / 2, 0), Q(-bb / 2, -hb + t), Q(bb / 2, -hb + t), Q(bb / 2, 0)])
    for z, k_ in ((30, '1'), (t - 30, '2')):
        pl([Q(-1000, z), Q(1000, z)], lay, 40)
        for k in range(10):
            xx = -900 + 200 * k
            if -bb / 2 + 50 <= xx <= bb / 2 - 50: continue
            dot(Q(xx, z + (14 if z < t / 2 else -14)), KS * 7, lay)
    dim(Q(1000, 0), Q(1000, t), W(SX + KS * 1000 + 600, 0)[0], True, lfac=1 / KS)
    note('2(%%C14)', 'ш.200', Q(-500, t - 30), Q(-1300, t + 250))
    note('1(%%C14)', 'ш.200', Q(-700, 30), Q(-1300, -300))
tt = tag(); O.append({'t': 'clone', 'h': T_TTL, 'tag': tt})
O.append({'t': 'settext', 'h': tt, 's': '{\\LРазрез 1 - 1}'})
O.append({'t': 'moveto', 'h': tt, 'idx': 0, 'to': Q(-1000, t + 600)})
mtext([SLOT + 2300, Y0 + 5600], ('1. Плита по грунту Пм-1 t=120, бетон С20/25 (B25), по уплотненному основанию. Армирование - 2 сетки %%C12 А500С ш.200 в обоих направлениях, защитный слой 30.\\P'
       '2. Стыки стержней внахлест 730, вразбежку. На плане показаны характерные стержни, остальные - с тем же шагом по всей плите.' if MARK == 'Пм-1' else
       '1. Плита Пм-2 t=200 на отм. +6.200 (от оси 6 к оси 8 - уклон до +5.700), бетон С20/25 (B25). Нижняя (поз. 1) и верхняя (поз. 2) арматура %%C14 А500С ш.200 в обоих направлениях, защитный слой 30.\\P'
       '2. Стержни плиты, параллельные балкам, начинать в 50 мм от грани балки; перпендикулярные - проходят над балками без разрыва. Стыки внахлест 860, вразбежку.\\P'
       '3. У проёмов О-1...О-3 - доп. стержни поз. 3: по 2%%C14 у каждой грани сверху и снизу, с заведением 600 за проём. Проёмы - см. лист 2.3.'), att=1, w=30000)

# ---------------- tables (cloned from 3.5)
SP, ST = PRE + '37FCCB', PRE + '37FCCC'
POS = sch['pos']; Np = len(POS)
O.append({'t': 'trows', 'h': SP, 'mode': 'del', 'at': 3 + Np, 'n': 11 - Np})
O.append({'t': 'trows', 'h': SP, 'mode': 'del', 'at': 3 + Np + 2, 'n': 1})
cells = [[2, 2, 'Плита %s' % MARK]]; form = []
for r, p in zip(range(3, 3 + Np), POS):
    pos, dd, L, n, _ = p
    cells += [[r, 0, pos], [r, 3, str(dd)], [r, 5, '500С'], [r, 9, 'пог.м.'], [r, 10, '%.1f' % n], [r, 11, '%.3f' % SD.KG[dd]]]
    form.append([r, 12, 'K%d*L%d' % (r + 1, r + 1)])
form.append([2, 12, 'Sum(M4:M%d)' % (3 + Np)])
cells.append([3 + Np + 1, 12, '%.2f' % sch['conc']])
O += [{'t': 'tset', 'h': SP, 'cells': cells}, {'t': 'tformula', 'h': SP, 'cells': form, 'fmt': '%lu2%pr2'}]
by = {}
for p in POS: by[p[1]] = by.get(p[1], 0) + SD.KG[p[1]] * p[3]
sc = [[5, 1, '%%C12'], [5, 2, '%%C14'], [5, 3, '-'], [5, 4, '-'], [5, 5, '-'], [6, 0, 'Плита %s' % MARK],
      [6, 1, '%.2f' % by.get(12, 0)], [6, 2, '%.2f' % by.get(14, 0)], [6, 3, '0.00'], [6, 4, '0.00'], [6, 5, '0.00']]
O += [{'t': 'tset', 'h': ST, 'cells': sc}, {'t': 'tformula', 'h': ST, 'cells': [[6, 6, 'Sum(B7:F7)'], [6, 7, 'G7']], 'fmt': '%lu2%pr2'},
      {'t': 'move', 'h': [ST], 'd': [0, 400 * (11 - Np + 1) + 1000]}]
O.append({'t': 'vpset2', 'layout': SNO, 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [SLOT, Y0, SLOT + 59400, Y0 + 42000], 'scale': 100})
O.append({'t': 'save'})
print(MARK, SNO, len(O), 'ops; kg %.1f' % sum(by.values()), 'base', len(base))
if RUN:
    out = ab.run(O, 'g7', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l)[-1500:])
