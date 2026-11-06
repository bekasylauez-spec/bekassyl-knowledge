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


# ---------------- elevation: Фм (part, with breaks), подготовка, column, beam stubs, console
z1 = col['z1']; zl_top = z1 or top
PADH = 1000
fm = [E(-PADH, -1500), E(PADH, -1500), E(PADH, -500), E(-PADH, -500)]
pl('3E8793', [E(-PADH, -500), E(PADH, -500)]); pl('3E8793', [E(-PADH, -1500), E(PADH, -1500)])
for s_ in (-1, 1):
    b = s_ * PADH
    ln([E(b, -400), E(b, -930), E(b - s_ * 60, -1000), E(b + s_ * 60, -1040), E(b, -1100), E(b, -1700)], 'Размеры', 5)
th = clone('3E8792'); add(t='hatchset', h=th, loops=[fm])
pl('3E8793', [E(-PADH, -1600), E(PADH, -1600)])
pl('3E8749', [E(-C.BY / 2, -500), E(C.BY / 2, -500), E(C.BY / 2, zl_top), E(-C.BY / 2, zl_top)], closed=True)
if z1:
    pl('3E8749', [E(-C.UB / 2, z1), E(C.UB / 2, z1), E(C.UB / 2, top), E(-C.UB / 2, top)], closed=True)
for zs, hb, sides in col['nodes']:
    if sides is None: continue
    for s_ in ((-1, 1) if sides == 0 else (sides,)):
        a = s_ * C.BY / 2; b = s_ * (C.BY / 2 + 700)
        pl('3E8749', [E(a, zs - hb), E(b, zs - hb)]); pl('3E8749', [E(a, zs), E(b, zs)])
        zz = [E(b, zs + 150), E(b, zs - hb / 2 + 60), E(b - s_ * 60, zs - hb / 2), E(b + s_ * 60, zs - hb / 2 - 40), E(b, zs - hb / 2 - 100), E(b, zs - hb - 150)]
        ln(zz, 'Размеры', 5)
        if zs < 8000: pl('3E8749', [E(a, zs - 200), E(b, zs - 200)])          # slab underside
CONS = col.get('cons')
if CONS:
    cl, ch_ = C.CONS['l'], C.CONS['h']
    pl('3E8749', [E(C.BY / 2, z1 - ch_), E(C.BY / 2 + cl, z1 - ch_ + 250), E(C.BY / 2 + cl, z1), E(C.BY / 2, z1)])

# ---------------- elevation bars
zb = sch['zend']
joints = sch['joints']
for y in C.YS:
    corner = y in (C.YS[0], C.YS[-1])
    js = [j + (600 if corner else 1200) for j in joints]
    for i_, zj in enumerate(js):
        z_to = js[i_ + 1] if i_ + 1 < len(js) else zb
        pl('3E879A', [E(y, zj), E(y, z_to)], layer='диам28')
        for s_ in (-1, 1):
            x0 = y + s_ * 14; x1 = y + s_ * 42
            pl('3E878C', [E(x0, zj - 140), E(x1, zj - 140), E(x1, zj + 140), E(x0, zj + 140)], closed=True, layer='диам28')
    pl('3E878D', [E(y, -1440), E(y, js[0])])                     # dowel Вп (dashed, see sheet 3.6)
if z1:
    for y in (-C.UO, C.UO):
        pl('3E879A', [E(y, z1 - C.ANCH), E(y, top - 20)], layer='диам28')
    pl('3E879A', [E(0, z1 + 50), E(0, top - 20)], layer='диам28')
HX = C.YS[-1] + C.OFF
UX = C.UO + C.OFF
st = C.storeys(col)
zone_marks = []
for lo, hi, hb in st:
    upper = bool(z1) and lo >= z1
    p, (n1, n2, n3), stp = C.colgeo.storey_hoops(lo, hi - hb)
    hx = UX if upper else HX
    for k in range(len(p)):                        # every hoop drawn
        ln([E(-hx, p[k]), E(hx, p[k])], 'диам10', 30)
    zone_marks.append(p)
    if hb:
        for zm in range(int(hi - hb + 50), int(hi - 49), 100):
            ln([E(-C.BY / 2 + 20, zm), E(C.BY / 2 - 20, zm)], 'диам10', 30)
# П elements: top of the lower part (Ск1/Ск2) and of the upper part (Ск3)
pl('3E879A', [E(C.YS[0] - 22, zb - C.LAP_N), E(C.YS[0] - 22, zb - 8), E(C.YS[-1] + 22, zb - 8), E(C.YS[-1] + 22, zb - C.LAP_N)], layer='диам16')
if z1:
    zt = top - 20
    pl('3E879A', [E(-C.UO - 22, zt - C.LAP_N), E(-C.UO - 22, zt - 8), E(C.UO + 22, zt - 8), E(C.UO + 22, zt - C.LAP_N)], layer='диам16')
if CONS:
    zk = z1 - 60
    ln([E(C.YS[0] + 30, zk - 400), E(C.YS[0] + 30, zk), E(C.BY / 2 + cl - 30, zk), E(C.BY / 2 + cl - 30, zk - 600)], 'диам28', 40)
    for yk in range(int(C.BY / 2 + 60), int(C.BY / 2 + cl - 29), 100):
        zbk = z1 - ch_ + 250 * (yk - C.BY / 2) / cl + 40
        ln([E(yk, zbk), E(yk, z1 - 40)], 'диам10', 30)

# ---------------- elevation dims: left level chain + overall, right hoop chain
LV = sorted(set([-1500, bot] + [zs - hb for zs, hb, _ in col['nodes']] + [zs for zs, hb, _ in col['nodes']] + [top] + ([z1] if z1 else [])))
XL1, XL2 = FL - 1100, FL - 1500
for a, b in zip(LV, LV[1:]):
    dim('3E874A', E(-C.BY / 2, a), E(-C.BY / 2, b), W(XL1, 0), True)
dim('3E874A', E(-C.BY / 2, bot), E(-C.BY / 2, top), W(XL2, 0), True)
P, segs = C.colgeo.chain([bot] + [s[1] for s in st], [s[2] for s in st])
XR = FR + (650 + C.CONS['l'] + 500 if CONS else 650)
colx = 0
for (y1, y2, stp, n) in segs:
    if y2 - y1 < 1: continue
    txt = ('%dх%d' % (stp, n)) if n > 1 else None
    small = (y2 - y1) < 450
    tx = None
    if small:
        tx = W(XR + (260 if colx == 0 else 520), YB + (y1 + y2) / 2); colx = 1 - colx
    else:
        colx = 0
    fx = C.UB / 2 if (z1 and y1 >= z1) else C.BY / 2
    dim('3E8855', E(fx, y1), E(fx, y2), W(XR, 0), True, txt, tx)

# ---------------- level marks: first = template «-2.000» (fixed text), the rest clones of 3E8738 (stored zero fixed by levbase)
add(t='move', h=[T('3E8739')], d=[0, YB - 11700 - 500])
fmt = lambda v: ('+' if v > 0 else '-') + ('%.3f' % abs(v / 1000)).replace('.', ',')
ORIG = {LV[0]: '3E8737', LV[1]: '3E8738', LV[-2]: '3E873B', LV[-1]: '3E873A'}
CUR = {'3E8737': 9700, '3E8738': 11700, '3E873B': 15500, '3E873A': 19300}
done_tag = {}
for z, h in ORIG.items():
    add(t='move', h=[T(h)], d=[FL - 4103, YB + z - CUR[h]])
    if h == '3E8737':
        add(t='levelval', h=T(h), old='-2.000', value=('%.3f' % (z / 1000)).replace('.', ',')); done_tag[z] = T(h)
        continue
    tg = 'lv_%s_%s' % (MARK, h)
    add(t='levbase', h=T(h), old=Y0 + YB + 500, new=Y0 + YB, tol=3, tag=tg)
    tg2 = tg + 'v'
    add(t='levelval', h=tg, old=fmt(z - 500), value=fmt(z), tag=tg2); done_tag[z] = tg2
for z in LV:
    if z in ORIG: continue
    src_z = min((zz for zz in ORIG if zz != LV[0] and len(fmt(zz)) == len(fmt(z))), key=lambda zz: abs(zz - z))
    h0 = tag(); add(t='clone', h=done_tag[src_z], tag=h0)
    add(t='move', h=[h0], d=[0, z - src_z])
    add(t='levelval', h=h0, old=fmt(src_z), value=fmt(z))


# ---------------- callouts on the elevation (left, shelf away from the column)
OX = FL - 230
lows = [s for s in st if not (z1 and s[0] >= z1)]
for i_, (lo, hi, hb) in enumerate(lows):
    za, zb_ = lo + 2050, lo + 2600
    note(str(2 * i_ + 1), '(%%C28)', E(C.YS[0], za - 300), W(OX, YB + za), 'Oblique')
    note(str(2 * i_ + 2), '(%%C28)', E(C.YS[1], zb_ - 300), W(OX, YB + zb_), 'Oblique')
    note('С1', '%d шт.' % (int((hb - 100) // 100) + 1), E(-C.BY / 2 + 20, hi - hb / 2), W(OX, YB + hi - hb - (1050 if i_ == 0 else 400)), 'Oblique')
hz = zone_marks[0]
zx = min(hz, key=lambda q: abs(q - (bot + 1400)))
zx2 = min(hz, key=lambda q: abs(q - (bot + 2700))); zx3 = min(hz, key=lambda q: abs(q - (bot + 3350)))
note('Х1', '(%%C10)', E(-HX, zx), W(OX, YB + bot + 1500), 'Oblique')
note('Н2', '(%%C28)', E(C.YS[0] - 42, bot + 600), W(OX, YB + bot + 950), 'Oblique')
note('Вп1', 'см. лист 3.6', E(C.YS[-1], -1000), W(FR + 1000, YB - 1100), 'Oblique')
note('Вп2', 'см. лист 3.6', E(C.YS[-2], -1700), W(FR + 1000, YB - 1800), 'Oblique')
if z1:
    up = [s for s in st if s[0] >= z1][0]
    zc_ = (up[0] + up[1]) / 2
    hzu = zone_marks[-1]
    note('Ск1', '(%%C16)', E(C.YS[0] - 22, zb - 150), W(OX, YB + z1 + 400), 'Oblique')
    zh4 = min(hzu, key=lambda q: abs(q - z1 - 1400)); zh5 = min(hzu, key=lambda q: abs(q - z1 - 1900))
    note('Х4', '(%%C10)', E((1 if CONS else -1) * UX, zh4), W(CX + 1300, YB + z1 + 1900) if CONS else W(OX, YB + z1 + 1450), 'Oblique')
    note(str(len(joints) * 2 + 1), '(%%C28)', E(-C.UO, z1 + 1850), W(OX, YB + z1 + 1950), 'Oblique')
    add(t='moveto', h=T('3E8E9D'), idx=1, to=E(C.UO + 22, top - 140))
    add(t='mcset', h=T('3E8E9D'), set={'FirstLine': 'Ск3', 'SecondLine': '(%%C16)', 'Origin': W(CX + 800, YB + top + 500), 'Angle': 0.0, 'Arrow': 'Oblique'})
else:
    add(t='moveto', h=T('3E8E9D'), idx=1, to=E(C.YS[-1] + 22, zb - 120))
    add(t='mcset', h=T('3E8E9D'), set={'FirstLine': 'Ск1', 'SecondLine': '(%%C16)', 'Origin': W(FR + 900, YB + top + 950), 'Angle': 0.0, 'Arrow': 'Oblique'})
if CONS:
    note('К1', '(%%C28)', E(C.BY / 2 + cl - 30, zk - 450), W(CX + 1300, YB + z1 + 330), 'Oblique')
    note('Хк', '(%%C10)', E(C.BY / 2 + 560, z1 - ch_ + 250 * 0.6 + 120), W(CX + 1300, YB + z1 + 1150), 'Oblique')

# ---------------- section marks, knot, title
lo0, hi0, hb0_ = st[0]
p0_, (n1_, n2_, n3_), _s = C.colgeo.storey_hoops(lo0, hi0 - hb0_)
zc = p0_[n1_ + n2_] - 490
add(t='spmove', h=T('3E8EA3'), items=[[0] + E(-C.BY / 2 - 450, zc), [1] + E(C.BY / 2 + 450, zc)])
add(t='secset', h=T('3E8EA3'), word='1')
if z1:
    zc2 = z1 + 800
    s2 = clone('3E8EA3')
    add(t='spmove', h=s2, items=[[0] + E(-C.UB / 2 - 450, zc2), [1] + E(C.UB / 2 + 450, zc2)])
    add(t='secset', h=s2, word='2')
    add(t='spmove', h=T('3E8E9A'), items=[[0] + E(-C.UB / 2 - 450, top + 900), [1] + E(C.UB / 2 + 450, top + 900)])
    add(t='secset', h=T('3E8E9A'), word='3')
else:
    add(t='spmove', h=T('3E8E9A'), items=[[0] + E(-C.BY / 2 - 450, top + 450), [1] + E(C.BY / 2 + 450, top + 450)])
    add(t='secset', h=T('3E8E9A'), word='2')
zs0, hb0 = col['nodes'][0][:2]
kc = E(0, zs0 - hb0 / 2)
add(t='mcset', h=T('3E8E99'), set={'Center': kc, 'Rack': [kc[0] - 1150, kc[1] - 1150], 'XRadius': 650.0, 'YRadius': 650.0, 'Knot': 'Б'})
add(t='settext', h=T('3E8736'), s='{\\LКолонна %s (%s шт.)}' % (MARK, col['n']))
add(t='moveto', h=T('3E8736'), idx=0, to=W(CX - 700, YB + top + 1900))

# ---------------- sections 1:25 (x2)
K = 2.0


def section(cx, cy, title, kind):
    """kind: 'low' (700x900 hoops), 'lowtop' (П at the top of the lower part), 'up' (600x600 hoops), 'uptop' (П at the top)"""
    S = lambda x, y: W(cx + K * x, cy + K * y)
    bx, by = (C.BX, C.BY) if kind.startswith('low') else (C.UB, C.UB)
    bars = C.BARS if kind.startswith('low') else C.UBARS
    pl('18CB9', [S(-bx / 2, -by / 2), S(bx / 2, -by / 2), S(bx / 2, by / 2), S(-bx / 2, by / 2)], closed=True)
    for x, y in bars: dot(S(x, y), K * C.D / 2)
    ox = bx / 2 + 250
    if kind in ('low', 'up'):
        if kind == 'low':
            for k, (a, b) in enumerate((C.X1, C.X2, C.X3)):
                if k == 1: b -= 24
                if k == 2: a -= 24
                ln([S(-a / 2, -b / 2), S(a / 2, -b / 2), S(a / 2, b / 2), S(-a / 2, b / 2)], 'диам10', 30, closed=True)
                ln([S(-a / 2, b / 2), S(-a / 2 + 55, b / 2 - 55)], 'диам10', 30)
            xs = [-bx / 2] + C.XS + [bx / 2]; ys = [-by / 2] + C.YS + [by / 2]
        else:
            a = C.X4[0]
            ln([S(-a / 2, -a / 2), S(a / 2, -a / 2), S(a / 2, a / 2), S(-a / 2, a / 2)], 'диам10', 30, closed=True)
            ln([S(-a / 2, a / 2), S(-a / 2 + 55, a / 2 - 55)], 'диам10', 30)
            r = C.X5R - 12
            ln([S(0, -r), S(r, 0), S(0, r), S(-r, 0)], 'диам10', 30, closed=True)
            xs = [-bx / 2, -C.UO, 0, C.UO, bx / 2]; ys = xs[:]
        yb_ = -by / 2
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            tx = S(a - 130, yb_ - 330) if k == 0 else (S(b + 130, yb_ - 330) if k == len(xs) - 2 else None)
            dim('18CF8', S(a, yb_), S(b, yb_), S(0, yb_ - 230), False, None, tx)
        dim('18CF8', S(-bx / 2, yb_), S(bx / 2, yb_), S(0, yb_ - 430), False)
        xl = -bx / 2
        for k, (a, b) in enumerate(zip(ys, ys[1:])):
            tx = S(xl - 330, a - 130) if k == 0 else (S(xl - 330, b + 130) if k == len(ys) - 2 else None)
            dim('18CF8', S(xl, a), S(xl, b), S(xl - 230, 0), True, None, tx)
        dim('18CF8', S(xl, -by / 2), S(xl, by / 2), S(xl - 430, 0), True)
        if kind == 'low':
            nb = lambda i: str(2 * i + 1)
            note('1', '(%%C28)', S(C.XS[-1], C.YS[-1]), S(ox, 520), 'None')
            note('2', '(%%C28)', S(C.XS[-1], C.YS[3]), S(ox, 260), 'None')
            note('Х3', '(%%C10)', S(C.X3[0] / 2 - 12, -60), S(ox, 0), 'Oblique')
            note('Х1', '(%%C10)', S(C.X1[0] / 2, -300), S(ox, -260), 'Oblique')
            note('Х2', '(%%C10)', S(C.X2[0] / 2, -C.YS[-1] + 120), S(ox, -520), 'Oblique')
        else:
            note(str(2 * len(sch['joints']) + 1), '(%%C28)', S(C.UO, C.UO), S(ox, 330), 'None')
            note('Х4', '(%%C10)', S(C.X4[0] / 2, -150), S(ox, 0), 'Oblique')
            note('Х5', '(%%C10)', S(C.X5R / 2, -C.X5R / 2), S(ox, -330), 'Oblique')
    elif kind == 'lowtop':
        for x in C.XS: ln([S(x, C.YS[0]), S(x, C.YS[-1])], 'диам16', 40)
        for y in C.YS[1:-1]: ln([S(C.XS[0], y), S(C.XS[-1], y)], 'диам16', 40)
        note('Ск1', '(%%C16)', S(C.XS[2], C.YS[3] + 80), S(ox, by / 2 + 200), 'Oblique')
        note('Ск2', '(%%C16)', S(C.XS[-1] - 120, C.YS[1]), S(ox, C.YS[1] - 200), 'Oblique')
    else:
        for x in (-C.UO, 0, C.UO): ln([S(x, -C.UO), S(x, C.UO)], 'диам16', 40)
        ln([S(-C.UO, 0), S(C.UO, 0)], 'диам16', 40)
        note('Ск3', '(%%C16)', S(C.UO / 2, C.UO / 2), S(ox, by / 2 + 200), 'Oblique')
    h = clone('18CB6'); add(t='settext', h=h, s='{\\L%s}' % title)
    add(t='moveto', h=h, idx=0, to=S(-bx / 2, by / 2 + 300))


section(9300, 17200, 'Разрез 1 - 1', 'low')
if col['z1']:
    section(13900, 17400, 'Разрез 2 - 2', 'up')
    section(9700, 12700, 'Разрез 3 - 3', 'uptop')
else:
    section(13900, 17200, 'Разрез 2 - 2', 'lowtop')

# ---------------- ведомость деталей (own lines, text 2.5 mm = 125)
PD = {p[0]: p for p in sch['pos']}
DET = [(p, g) for p, g in (('Х1', C.X1), ('Х2', C.X2), ('Х3', C.X3), ('Х4', C.X4), ('Х5', None), ('Ск1', C.SK1), ('Ск2', C.SK2),
                           ('Ск3', C.SK3), ('К1', None), ('Хк', (C.BX - 60, C.CONS['h'] - 60))) if p in PD]
RH = 960 if len(DET) <= 6 else 760
TX0, TY1, CW0, CW = X0 + 16600, Y0 + 20250, 600, 2900
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
for k, (pos, g) in enumerate(DET):
    yt = TY1 - 400 - RH * k; yb = yt - RH
    if k: ln([[TX0, yt], [TX0 + CW0 + CW, yt]], '0', 30)
    tx(TX0 + CW0 / 2, (yt + yb) / 2, pos)
    _, d, L, n, _ = PD[pos]
    tx(TX0 + CW0 + CW / 2, yb + 110, '%%%%C%d A500С  L=%d' % (d, L))
    sx, sy = TX0 + CW0 + 700, yb + 250
    hh = RH - 480
    if pos == 'Х5':
        r = hh / 2; cx_, cy_ = sx + 300, sy + r
        ln([[cx_, cy_ - r], [cx_ + r, cy_], [cx_, cy_ + r], [cx_ - r, cy_]], 'диам10', 30, closed=True)
        tx(cx_ + r + 150, cy_, 'ромб %dх%d' % (round(C.X5R * 2), round(C.X5R * 2)), att=4)
    elif pos == 'К1':
        ln([[sx, sy + hh * 0.4], [sx, sy + hh], [sx + 1500, sy + hh], [sx + 1500, sy]], 'диам28', 40)
        tx(sx + 750, sy + hh + 90, '%d' % ((C.CONS['l'] - 30) + (C.BY - 60))); tx(sx - 90, sy + hh * 0.7, '400', rot=math.pi / 2)
        tx(sx + 1590, sy + hh / 2, '600', rot=math.pi / 2)
    elif pos.startswith('Х'):
        a, b = g
        if a < b: h_ = hh; w = max(150, h_ * a / b)
        else: w = min(420, hh * a / b); h_ = w * b / a
        ln([[sx, sy], [sx + w, sy], [sx + w, sy + h_], [sx, sy + h_]], 'диам10', 30, closed=True)
        ln([[sx + 60, sy + h_ - 60], [sx, sy + h_]], 'диам10', 30)
        tx(sx + w / 2 + 60, sy + h_ + 110, '%d' % a); tx(sx - 120, sy + h_ / 2 - 40, '%d' % b, rot=math.pi / 2)
        tx(sx + w + 150, sy + h_ / 2, 'крюки 135° 2х100', att=4)
    else:
        web, leg = g; w = 1300; h_ = hh * 0.8
        ln([[sx, sy], [sx, sy + h_], [sx + w, sy + h_], [sx + w, sy]], 'диам16', 40)
        tx(sx + w / 2, sy + h_ + 90, '%d' % web); tx(sx - 90, sy + h_ / 2, '%d' % leg, rot=math.pi / 2)

# ---------------- node «Б» (1:50) and mesh С1 (1:25), own drawing instead of the template ones
ERASE_NEW += [PRE + r['old'] for r in R if 8300 < r['e'][0] and r['e'][2] < 20600 and 9800 < r['e'][1] and r['e'][3] < 13600
              and r['old'] not in ('18D64',) and not (15300 < r['e'][0] and r['e'][2] < 18600 and r['e'][3] < 7000)]
NX, NY = 10200, 9000                      # node: column centre x, beam bottom y
zs0, hb0 = col['nodes'][0][:2]
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
    tx_ = None if k == 1 else W(NX + C.BY / 2 + 1110, NY + (a + b) / 2 - (zs0 - hb0) + (-60 if k == 0 else 60))
    dim('3E8855', Nd(C.BY / 2, a), Nd(C.BY / 2, b), W(NX + C.BY / 2 + 900, 0), True, t_, tx_)
dim('3E874A', Nd(-C.BY / 2, zs0 - hb0), Nd(-C.BY / 2, zs0), W(NX - C.BY / 2 - 900, 0), True)
for a, b in ((-C.BY / 2, -C.BY / 2 + 20), (-C.BY / 2 + 20, C.BY / 2 - 20), (C.BY / 2 - 20, C.BY / 2)):
    tx_ = W(NX + a - 260, NY - 800) if b - a < 100 and a < 0 else (W(NX + b + 260, NY - 800) if b - a < 100 else None)
    dim('3E8855', Nd(a, zs0 - hb0 - 500), Nd(b, zs0 - hb0 - 500), W(0, NY - 800), False, None, tx_)
note('С1', '%d шт.' % len(mz), Nd(-C.BY / 2 + 20, mz[2]), W(NX - C.BY / 2 - 800, NY - 350), 'Oblique')
ERASE_NEW += [PRE + '18D72', PRE + '18D73']
add(t='moveto', h=PRE + '18D64', idx=0, to=W(NX - 1500, NY + hb0 + 700))
add(t='settext', h=PRE + '18D64', s='%%UУзел Б. Расположение сеток С1')
# mesh С1 plan 1:25
MX, MY = 14200, 11500
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
        None if k == 1 else (M(a_ + 200, a + 150) if k == 0 else M(a_ + 200, b + 70)))
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
