"""Column sheet (A2, 1:50) from the template sheet «Колонна Км-1» (Шаблон для Кж.dwg) imported with prefix PRE.
Elevation 1:50 (real size), sections 1:25 (x2, dims «СПДС М2» show real values). Run: python gen4x.py <mark> <x0> <y0> <PRE> <sheet no> [run]"""
import sys, json, math
import ab, coldata as C

MARK, X0, Y0, PRE, SNO = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
RUN = len(sys.argv) > 6 and sys.argv[6] == 'run'
col = C.COLS[MARK]; sch = C.schedule(MARK)
R = json.load(open('w/k41_list.json', encoding='utf-8'))
N2O = {r['h'].upper(): r['old'] for r in R}


def T(newh):                              # template object (handles of the 4.1 import) -> tag of this sheet's copy
    return PRE + N2O[newh.upper()]


O = []
_n = [0]


def add(**k):
    O.append(k); return k


def tag():
    _n[0] += 1; return '%s%s_%d' % ('g4_', MARK.replace('-', ''), _n[0])


def W(x, y): return [round(X0 + x, 1), round(Y0 + y, 1)]


# ---------------- layout of the elevation
bot, top = col['bot'], col['top']
CX = 4600.0; FL, FR = CX - C.BY / 2, CX + C.BY / 2
z_lo, z_hi = -1600, top + 1700
YB = 10600 - (z_lo + z_hi) / 2
def E(y, z): return W(CX + y, YB + z)          # y = along the column width (Y of the building), z = level (mm)


# ---------------- erase template content that is redrawn
ERASE_NEW = [r['h'] for r in R if (r['e'][2] < 7000 and r['e'][1] > 7700 and r['t'] != 'SPDSFORMAT')
             or (7300 < r['e'][0] and r['e'][2] < 15700 and r['e'][1] > 15500 and r['e'][3] < 20500)
             or (16500 < r['e'][0] < 20000 and r['e'][1] > 15700 and r['e'][3] < 20700 and r['t'] != 'ACAD_TABLE')
             or r['h'] in ('3E8EA8',) or r['old'] == '18E05']
REUSE = ('3E8739', '3E8737', '3E8738', '3E873B', '3E873A', '3E8EA3', '3E8E9A', '3E8E99', '3E8736', '3E8E9D')
ERASE_NEW = [PRE + N2O[h.upper()] for h in ERASE_NEW if h not in REUSE and N2O.get(h.upper())]
KEEP_TPL = ['3E8749', '3E879A', '3E878D', '3E878C', '3E879D', '3E8793', '3E8792', '3E874A', '3E8855', '3E8882', '3E8E9D',
            '3E8737', '3E8738', '3E873B', '3E873A', '3E8739', '3E8EA3', '3E8E9A', '3E8E99', '3E8736', '18CB9', '18CF8', '18CB6', '18E05']
NEWH = {r['old']: r['h'] for r in R}


def tpl(h):    # template handle given as new handle of 4.1 or old handle of the template file
    return T(h) if h.upper() in N2O else PRE + h


O.append({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
O.append({'t': 'eraseregion', 'win': [X0 - 1, Y0 - 1, X0 + 29701, Y0 + 21001]})
O.append({'t': 'import', 'file': r'D:\РАБОЧКА\Шаблон для Кж.dwg', 'wins': [[264700, 271880, 294430, 292910]], 'base': [264717, 271898], 'to': [X0, Y0], 'pre': PRE})
# detail A / ГОСТ block right, накладки table up, junk insert away
add(t='move', h=[tpl('18C89')], d=[4300, 0])
TBLN = [PRE + r['old'] for r in R if 15300 < r['e'][0] and r['e'][2] < 18600 and 3990 < r['e'][1] and r['e'][3] < 7000]
add(t='move', h=TBLN, d=[0, 3500])


def clone(h, layer=None, lw=None):
    t = tag(); d = dict(t='clone', h=tpl(h), tag=t)
    if layer: d['layer'] = layer
    if lw is not None: d['lw'] = lw
    add(**d); return t


def pl(h, pts, closed=False, layer=None, lw=None):
    t = clone(h, layer, lw); add(t='plset', h=t, p=pts, closed=closed); return t


def ln(pts, layer, lw, closed=False):
    t = tag(); add(t='pl', p=pts, layer=layer, lw=lw, closed=closed, tag=t); return t


def dot(c, r, layer='диам28'):
    add(t='circle', c=c, r=r, layer=layer)
    add(t='hatch', pat='SOLID', layer=layer, loops=[[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]])


def dim(h, p1, p2, dl, vertical=False, txt=None, tx=None):
    d = dict(t='dim', h=tpl(h), p1=p1, p2=p2, dl=dl, rot=math.pi / 2 if vertical else 0)
    d['txt'] = txt or ''
    if tx: d['tx'] = tx
    add(**d)


def note(l1, l2, tgt, org, arrow='Oblique'):
    h = clone('3E8E9D')
    add(t='moveto', h=h, idx=1, to=tgt)
    add(t='mcset', h=h, set={'FirstLine': l1, 'SecondLine': l2, 'Origin': org, 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow})


# ---------------- elevation: Фм, подготовка, column, beam stubs
PADH = 1500
fm = [E(-PADH, -1500), E(PADH, -1500), E(PADH, -500), E(-PADH, -500)]
pl('3E8793', fm, closed=True)
th = clone('3E8792'); add(t='hatchset', h=th, loops=[fm])
pl('3E8793', [E(-PADH - 100, -1600), E(PADH + 100, -1600), E(PADH + 100, -1500), E(-PADH - 100, -1500)], closed=True)
pl('3E8749', [E(-C.BY / 2, -500), E(C.BY / 2, -500), E(C.BY / 2, top), E(-C.BY / 2, top)], closed=True)
for zs, hb in col['nodes']:
    for s in (-1, 1):
        a = s * C.BY / 2; b = s * (C.BY / 2 + 700)
        pl('3E8749', [E(a, zs - hb), E(b, zs - hb)]); pl('3E8749', [E(a, zs), E(b, zs)])
        zz = [E(b, zs + 150), E(b, zs - hb / 2 + 60), E(b - s * 60, zs - hb / 2), E(b + s * 60, zs - hb / 2 - 40), E(b, zs - hb / 2 - 100), E(b, zs - hb - 150)]
        ln(zz, 'Размеры', 5)
        pl('3E8749', [E(a, zs - 200), E(b, zs - 200)])          # slab underside

# ---------------- elevation bars
YV = C.YS                                       # visible bar lines (corner, mids, corner)
zb = top - 20
for y in YV:
    corner = y in (C.YS[0], C.YS[-1])
    zj = bot + (600 if corner else 1200)
    clone_bar = pl('3E879A', [E(y, zj), E(y, zb)], layer='диам28')
    pl('3E878D', [E(y, -1440), E(y, zj)])                   # dowel Вп (dashed, see sheet 3.2)
    for s in (-1, 1):                                       # накладки Н2
        x0 = y + s * 14; x1 = y + s * 42
        pl('3E878C', [E(x0, zj - 140), E(x1, zj - 140), E(x1, zj + 140), E(x0, zj + 140)], closed=True, layer='диам28')
# hoops: zone ends of every storey; meshes С1 in the node
HX = C.YS[-1] + C.OFF
lo = bot
zone_marks = []
for zs, hb in col['nodes']:
    p, (n1, n2, n3), st = C.colgeo.storey_hoops(lo, zs - hb)
    for k in sorted({0, n1, n1 + n2, len(p) - 1}):
        ln([E(-HX, p[k]), E(HX, p[k])], 'диам10', 30)
    zone_marks.append(p)
    for zm in range(int(zs - hb + 50), int(zs - 49), 100):
        ln([E(-C.BY / 2 + 20, zm), E(C.BY / 2 - 20, zm)], 'диам10', 30)
    lo = zs
# П elements at the top
pl('3E879A', [E(C.YS[0] - 22, zb - C.LAP_N), E(C.YS[0] - 22, zb - 8), E(C.YS[-1] + 22, zb - 8), E(C.YS[-1] + 22, zb - C.LAP_N)], layer='диам16')

# ---------------- elevation dims: left level chain + overall, right hoop chain
LV = sorted(set([-1500, bot] + [zs - hb for zs, hb in col['nodes']] + [zs for zs, hb in col['nodes']] + [top]))
XL1, XL2 = FL - 1100, FL - 1500
for a, b in zip(LV, LV[1:]):
    dim('3E874A', E(-C.BY / 2, a), E(-C.BY / 2, b), W(XL1, 0), True)
dim('3E874A', E(-C.BY / 2, bot), E(-C.BY / 2, top), W(XL2, 0), True)
P, segs = C.colgeo.chain([bot] + [zs for zs, hb in col['nodes']], [hb for zs, hb in col['nodes']])
XR = FR + 650
colx = 0
for (y1, y2, stp, n) in segs:
    txt = ('%dх%d' % (stp, n)) if n > 1 else None
    small = (y2 - y1) < 450
    tx = None
    if small:
        tx = W(XR + (260 if colx == 0 else 520), YB + (y1 + y2) / 2); colx = 1 - colx
    dim('3E8855', E(C.BY / 2, y1), E(C.BY / 2, y2), W(XR, 0), True, txt, tx)

# ---------------- level marks (values follow the relation mark)
add(t='move', h=[T('3E8739')], d=[0, YB - 11700 - 500])
for h, z in (('3E8737', -1500), ('3E8738', bot), ('3E873B', LV[2] if len(LV) > 3 else top), ('3E873A', top)):
    cur = {'3E8737': 9700, '3E8738': 11700, '3E873B': 15500, '3E873A': 19300}[h]
    add(t='move', h=[T(h)], d=[FL - 4103, YB + z - cur])
    fmt = lambda v: ('+' if v > 0 else '-') + ('%.3f' % abs(v / 1000)).replace('.', ',')
    if h == '3E8737':
        add(t='levelval', h=T(h), old='-2.000', value=('%.3f' % (z / 1000)).replace('.', ','))
    else:
        tg = 'lv_%s_%s' % (MARK, h)
        add(t='levbase', h=T(h), old=Y0 + YB + 500, new=Y0 + YB, tol=3, tag=tg)
        add(t='levelval', h=tg, old=fmt(z - 500), value=fmt(z))

# ---------------- callouts on the elevation (left, shelf away from the column)
OX = FL - 230
note('1', '(%%C28)', E(C.YS[0], 2400), W(OX, YB + 2700), 'Oblique')
note('2', '(%%C28)', E(C.YS[1], 3600), W(OX, YB + 3900), 'Oblique')
hz = zone_marks[0]
note('Х1...Х3', '(%%C10)', E(-HX, hz[len(hz) // 4]), W(OX, YB + hz[len(hz) // 4] + 300), 'Oblique')
note('Н2', '(%%C28)', E(C.YS[0] - 42, bot + 600), W(OX, YB + bot + 950), 'Oblique')
note('Вп1, Вп2', 'см. лист 3.2', E(C.YS[0], -1000), W(OX - 700, YB - 650), 'Oblique')
zs0, hb0 = col['nodes'][0]
note('С1', '', E(-C.BY / 2 + 20, zs0 - 350), W(OX, YB + zs0 - 700), 'Oblique')
add(t='moveto', h=T('3E8E9D'), idx=1, to=E(C.YS[-1] + 22, zb - 120))
add(t='mcset', h=T('3E8E9D'), set={'FirstLine': 'Ск1, Ск2', 'SecondLine': '(%%C16)', 'Origin': W(FR + 900, YB + top + 950), 'Angle': 0.0, 'Arrow': 'Oblique'})

# ---------------- section marks, knot, title
zc = (bot + zs0 - hb0) / 2
add(t='spmove', h=T('3E8EA3'), items=[[0] + E(-C.BY / 2 - 450, zc), [1] + E(C.BY / 2 + 450, zc)])
add(t='secset', h=T('3E8EA3'), word='1')
add(t='spmove', h=T('3E8E9A'), items=[[0] + E(-C.BY / 2 - 450, top + 450), [1] + E(C.BY / 2 + 450, top + 450)])
add(t='secset', h=T('3E8E9A'), word='2')
kc = E(0, zs0 - hb0 / 2)
add(t='mcset', h=T('3E8E99'), set={'Center': kc, 'Rack': [kc[0] - 1150, kc[1] - 1150], 'XRadius': 650.0, 'YRadius': 650.0, 'Knot': 'Б'})
add(t='settext', h=T('3E8736'), s='{\\LКолонна %s (%s шт.)}' % (MARK, col['n']))
add(t='moveto', h=T('3E8736'), idx=0, to=W(CX - 700, YB + top + 1900))

# ---------------- sections 1:25 (x2)
K = 2.0


def section(cx, cy, title, pi):
    S = lambda x, y: W(cx + K * x, cy + K * y)
    pl('18CB9', [S(-C.BX / 2, -C.BY / 2), S(C.BX / 2, -C.BY / 2), S(C.BX / 2, C.BY / 2), S(-C.BX / 2, C.BY / 2)], closed=True)
    for x, y in C.BARS: dot(S(x, y), K * C.D / 2)
    if pi:
        for k, (a, b) in enumerate((C.X1, C.X2, C.X3)):
            if k == 1: b -= 24
            if k == 2: a -= 24
            ln([S(-a / 2, -b / 2), S(a / 2, -b / 2), S(a / 2, b / 2), S(-a / 2, b / 2)], 'диам10', 30, closed=True)
            ln([S(-a / 2, b / 2), S(-a / 2 + 55, b / 2 - 55)], 'диам10', 30)
        # dims: bottom (cover/bar steps), left
        yb_ = -C.BY / 2
        xs = [-C.BX / 2] + C.XS + [C.BX / 2]
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            tx = None
            if k == 0: tx = S(a - 130, yb_ - 330)
            if k == len(xs) - 2: tx = S(b + 130, yb_ - 330)
            dim('18CF8', S(a, yb_), S(b, yb_), S(0, yb_ - 230), False, None, tx)
        for a, b in ((-C.BX / 2, 0), (0, C.BX / 2)):
            dim('18CF8', S(a, yb_), S(b, yb_), S(0, yb_ - 430), False)
        ys = [-C.BY / 2] + C.YS + [C.BY / 2]
        xl = -C.BX / 2
        for k, (a, b) in enumerate(zip(ys, ys[1:])):
            tx = None
            if k == 0: tx = S(xl - 330, a - 130)
            if k == len(ys) - 2: tx = S(xl - 330, b + 130)
            dim('18CF8', S(xl, a), S(xl, b), S(xl - 230, 0), True, None, tx)
        for a, b in ((-C.BY / 2, 0), (0, C.BY / 2)):
            dim('18CF8', S(xl, a), S(xl, b), S(xl - 430, 0), True)
        ox = C.BX / 2 + 250
        note('1', '(%%C28)', S(C.XS[-1], C.YS[-1]), S(ox, 520), 'None')
        note('2', '(%%C28)', S(C.XS[-1], C.YS[3]), S(ox, 260), 'None')
        note('Х3', '(%%C10)', S(C.X3[0] / 2 - 12, -60), S(ox, 0), 'Oblique')
        note('Х1', '(%%C10)', S(C.X1[0] / 2, -300), S(ox, -260), 'Oblique')
        note('Х2', '(%%C10)', S(C.X2[0] / 2, -C.YS[-1] + 120), S(ox, -520), 'Oblique')
    else:
        for x in C.XS:
            ln([S(x, C.YS[0]), S(x, C.YS[-1])], 'диам16', 40)
        for y in C.YS[1:-1]:
            ln([S(C.XS[0], y), S(C.XS[-1], y)], 'диам16', 40)
        note('Ск1', '(%%C16)', S(C.XS[2], C.YS[3] + 80), S(C.BX / 2 + 220, C.BY / 2 + 200), 'Oblique')
        note('Ск2', '(%%C16)', S(C.XS[-1] - 120, C.YS[1]), S(C.BX / 2 + 220, C.YS[1] - 200), 'Oblique')
    h = clone('18CB6'); add(t='settext', h=h, s='{\\L%s}' % title)
    add(t='moveto', h=h, idx=0, to=S(-C.BX / 2, C.BY / 2 + 300))


section(9300, 17200, 'Разрез 1 - 1', True)
section(13900, 17200, 'Разрез 2 - 2', False)

# ---------------- ведомость деталей (own lines, text 2.5 mm = 125)
TX0, TY1, CW0, CW, RH = X0 + 16600, Y0 + 20250, 600, 2900, 960
DET = [('Х1', C.X1), ('Х2', C.X2), ('Х3', C.X3), ('Ск1', C.SK1), ('Ск2', C.SK2)]
TY0 = TY1 - 400 - RH * len(DET)


def tx(x, y, s, att=5, rot=None):
    d = dict(t='mtext', at=[round(x, 1), round(y, 1)], h=125, layer='Размеры', s=s, att=att)
    if rot is not None: d['rot'] = rot
    add(**d)


tx(TX0 + (CW0 + CW) / 2, TY1 + 230, 'Ведомость деталей')
ln([[TX0, TY0], [TX0 + CW0 + CW, TY0], [TX0 + CW0 + CW, TY1], [TX0, TY1]], '0', 30, closed=True)
ln([[TX0 + CW0, TY0], [TX0 + CW0, TY1]], '0', 30)
ln([[TX0, TY1 - 400], [TX0 + CW0 + CW, TY1 - 400]], '0', 30)
tx(TX0 + CW0 / 2, TY1 - 200, 'Поз.'); tx(TX0 + CW0 + CW / 2, TY1 - 200, 'Эскиз')
PD = {p[0]: p for p in sch['pos']}
for k, (pos, g) in enumerate(DET):
    yt = TY1 - 400 - RH * k; yb = yt - RH
    if k: ln([[TX0, yt], [TX0 + CW0 + CW, yt]], '0', 30)
    tx(TX0 + CW0 / 2, (yt + yb) / 2, pos)
    _, d, L, n, _ = PD[pos]
    tx(TX0 + CW0 + CW / 2, yb + 110, '%%%%C%d A500С  L=%d' % (d, L))
    sx, sy = TX0 + CW0 + 700, yb + 270
    if pos.startswith('Х'):
        a, b = g
        if a < b: h = 470; w = max(150, h * a / b)
        else: w = 700; h = w * b / a
        ln([[sx, sy], [sx + w, sy], [sx + w, sy + h], [sx, sy + h]], 'диам10', 30, closed=True)
        ln([[sx + 60, sy + h - 60], [sx, sy + h]], 'диам10', 30)
        tx(sx + w / 2, sy + h + 80, '%d' % a); tx(sx - 90, sy + h / 2, '%d' % b, rot=math.pi / 2)
        tx(sx + w + 150, sy + h / 2, 'крюки 135°, 2х100', att=4)
    else:
        web, leg = g; w = 1300; h = 380
        ln([[sx, sy], [sx, sy + h], [sx + w, sy + h], [sx + w, sy]], 'диам16', 40)
        tx(sx + w / 2, sy + h + 80, '%d' % web); tx(sx - 90, sy + h / 2, '%d' % leg, rot=math.pi / 2)

# ---------------- node «Б» (1:50) and mesh С1 (1:25), own drawing instead of the template ones
ERASE_NEW += [PRE + r['old'] for r in R if 8300 < r['e'][0] and r['e'][2] < 20600 and 9800 < r['e'][1] and r['e'][3] < 13600
              and r['old'] not in ('18D64',) and not (15300 < r['e'][0] and r['e'][2] < 18600 and r['e'][3] < 7000)]
NX, NY = 10200, 10500                      # node: column centre x, beam bottom y
zs0, hb0 = col['nodes'][0]
def Nd(y, z): return W(NX + y, NY + z - (zs0 - hb0))
pl('3E8749', [Nd(-C.BY / 2, zs0 - hb0 - 500), Nd(-C.BY / 2, zs0 - hb0)]); pl('3E8749', [Nd(C.BY / 2, zs0 - hb0 - 500), Nd(C.BY / 2, zs0 - hb0)])
for s_ in (-1, 1):
    a = s_ * C.BY / 2; b = s_ * (C.BY / 2 + 500)
    pl('3E8749', [Nd(a, zs0 - hb0), Nd(b, zs0 - hb0)]); pl('3E8749', [Nd(a, zs0 + 0), Nd(b, zs0)])
    ln([Nd(b, zs0 + 120), Nd(b, zs0 - hb0 / 2 + 50), Nd(b - s_ * 50, zs0 - hb0 / 2), Nd(b + s_ * 50, zs0 - hb0 / 2 - 30), Nd(b, zs0 - hb0 / 2 - 80), Nd(b, zs0 - hb0 - 120)], 'Размеры', 5)
ln([Nd(-C.BY / 2 - 500, zs0), Nd(C.BY / 2 + 500, zs0)], 'Размеры', 5)
for y in C.YS: pl('3E879A', [Nd(y, zs0 - hb0 - 500), Nd(y, zs0 - 20)], layer='диам28')
mz = list(range(int(zs0 - hb0 + 50), int(zs0 - 49), 100))
for z in mz: ln([Nd(-C.BY / 2 + 20, z), Nd(C.BY / 2 - 20, z)], 'диам10', 30)
ch = [zs0 - hb0, mz[0], mz[-1], zs0]
for k, (a, b) in enumerate(zip(ch, ch[1:])):
    t_ = '100х%d' % (len(mz) - 1) if k == 1 else None
    tx_ = None if k == 1 else W(NX + C.BY / 2 + 860, NY + (a + b) / 2 - (zs0 - hb0) + (-60 if k == 0 else 60))
    dim('3E8855', Nd(C.BY / 2, a), Nd(C.BY / 2, b), W(NX + C.BY / 2 + 650, 0), True, t_, tx_)
dim('3E874A', Nd(-C.BY / 2, zs0 - hb0), Nd(-C.BY / 2, zs0), W(NX - C.BY / 2 - 900, 0), True)
for a, b in ((-C.BY / 2, -C.BY / 2 + 20), (-C.BY / 2 + 20, C.BY / 2 - 20), (C.BY / 2 - 20, C.BY / 2)):
    tx_ = W(NX + a - 150, NY - 900) if b - a < 100 and a < 0 else (W(NX + b + 150, NY - 900) if b - a < 100 else None)
    dim('3E8855', Nd(a, zs0 - hb0 - 500), Nd(b, zs0 - hb0 - 500), W(0, NY - 800), False, None, tx_)
note('С1', '%d шт.' % len(mz), Nd(-C.BY / 2 + 20, mz[2]), W(NX - C.BY / 2 - 300, NY + 300), 'Oblique')
ERASE_NEW += [PRE + '18D72', PRE + '18D73']
add(t='moveto', h=PRE + '18D64', idx=0, to=W(NX - 1500, NY + hb0 + 700))
add(t='settext', h=PRE + '18D64', s='%%UУзел Б. Расположение сеток С1')
# mesh С1 plan 1:25
MX, MY = 15000, 11400
def M(x, y): return W(MX + 2 * x, MY + 2 * y)
a_, b_ = C.MESH
xb = list(range(30, a_ - 29, 100)); yb_ = list(range(30, b_ - 29, 100))
for y in yb_: ln([M(0, y), M(a_, y)], 'диам10', 30)
for x in xb: ln([M(x, 0), M(x, b_)], 'диам10', 30)
dim('18CF8', M(0, 0), M(a_, 0), M(0, -260), False)
for k, (a, b) in enumerate(zip([0, xb[0], xb[-1]], [xb[0], xb[-1], a_])):
    dim('18CF8', M(a, 0), M(b, 0), M(0, -120), False, '100х%d' % (len(xb) - 1) if k == 1 else None,
        None if k == 1 else (M(a - 70, -200) if k == 0 else M(b + 70, -200)))
dim('18CF8', M(a_, 0), M(a_, b_), M(a_ + 260, 0), True)
for k, (a, b) in enumerate(zip([0, yb_[0], yb_[-1]], [yb_[0], yb_[-1], b_])):
    dim('18CF8', M(a_, a), M(a_, b), M(a_ + 120, 0), True, '100х%d' % (len(yb_) - 1) if k == 1 else None,
        None if k == 1 else (M(a_ + 200, a - 70) if k == 0 else M(a_ + 200, b + 70)))
note('10', '(%%C10) ш.100', M(xb[2], yb_[-2]), M(-160, b_ + 120), 'Oblique')
note('11', '(%%C10) ш.100', M(xb[-2], yb_[3]), M(-160, yb_[3] - 300), 'Oblique')
h = clone('18CB6'); add(t='settext', h=h, s='{\LСетка С1}')
add(t='moveto', h=h, idx=0, to=M(0, b_ + 330))

add(t='erase', h=ERASE_NEW)
add(t='vpset2', layout=SNO, media='ISO_full_bleed_A2_(594.00_x_420.00_MM)', win=[X0, Y0, X0 + 29700, Y0 + 21000], scale=50)
add(t='save')
json.dump(O, open('ops/g4_%s.json' % MARK, 'w', encoding='utf-8'), ensure_ascii=False)
print(len(O), 'ops, erase', len(ERASE_NEW))
if RUN:
    out = ab.run(O, 'g4', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'no prop' in l or 'xception' in l)[-2500:])
