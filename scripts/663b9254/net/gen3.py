# БДМ Блок 3 — square column sheet from Bekassyl's template «Колонна Км-1» (Шаблон для Кж.dwg, 1:50), adapted from ЖК Галакси gen_km.py.
# usage: python gen3.py <type.json> [--imp] [--run]
#   type.json: {"mark":"Км-1","sheet":"4.1","SX":294417,"SY":271898,"b":700,"nf":3,"D":28,"L0":-1.2,
#               "floors":[[-0.05,900],[7.0,900]],"qty":20}
import json, math, sys, os
import gx, colgeo3 as CG
import colsheet as C

TY = json.load(open(sys.argv[1], encoding='utf-8'))
MARK, SHEET, SX, SY = TY['mark'], TY['sheet'], float(TY['SX']), float(TY['SY'])
b, D = float(TY['b']), float(TY['D'])
h = float(TY.get('h', b)); nb = int(TY.get('nb', TY.get('nf', 3))); nh = int(TY.get('nh', nb)); nf = nb   # b = x (elevation face), h = y
PRE = 'K%s:' % MARK.replace('Км-', '').replace('.', '_')
MP = json.load(open('tplmap.json'))
def T(h): return PRE + MP[h]          # Galaxy-mapped template object
def R_(h): return PRE + h             # raw template handle
def W(x, y): return [SX + x, SY + y]
ops = []
def add(**k): ops.append(k); return k
NOTE = dict(scale=50, ts=2.5, style='ГОСТ 2.304', layer='Размеры')
NOTEo = dict(NOTE, arrow='oblique')
LAY = 'диам%d' % D
HL_LAY = 'диам10'
e = 40 + D / 2
n = 2 * nb + 2 * (nh - 2)
fpb = [e + k * (b - 2 * e) / (nb - 1) for k in range(nb)]
fph = [e + k * (h - 2 * e) / (nh - 1) for k in range(nh)]
facepos = fpb
DIAMOND = (nb == 3 and nh == 3 and abs(b - h) < 1)
NPB, NPH = nb - 2, nh - 2                               # S-pins: vertical (span h) at inner b-face bars, horizontal (span b) at inner h-face bars
NPIN = 0 if DIAMOND else NPB + NPH
TPLFILE = r'R:\Шаблон для Кж.dwg'

if '--imp' in sys.argv:
    H = json.load(open('tpl_h.json'))['ins']
    print(gx.run([{'t': 'import', 'file': TPLFILE, 'h': H, 'base': [264717, 271898], 'to': [SX, SY], 'pre': PRE},
                  {'t': 'import', 'file': TPLFILE, 'h': ['19EC6'], 'base': [304063, 294024], 'to': [SX + 1000, SY - 6000], 'pre': PRE + 'PIN:'},
                  {'t': 'save'}], 'imp_' + PRE[:-1])[-300:])
    sys.exit()

R = C.listwin(SX, SY, 29700, 21000)
m = gx.tagmap()
def hh(tag): return m.get(tag, '').upper()

# ================= 1. elevation =================
Y = lambda z: 11700.0 + 1000.0 * z                     # template 0.000 at y 11700 (level marks compute from it)
CX = 4103.0; CR = CX + b; XM = CX + b / 2
XF = [CX + p for p in facepos]; XC = [XF[0], XF[-1]]; XO = XF[1:-1]
FL = TY['floors']                                       # [[z, beam h], ...] bottom -> top
L = [Y(TY['L0'])] + [Y(z) for z, h in FL]; BEAMS = [float(h) for z, h in FL]
TOP = L[-1] - 20
NAK, NW = 10 * D, 2 * D
SPLV = [Y(z) for z in TY.get('splice', [z for z, h in FL[:-1]])]   # splice above the main floors only
SPL = []
for lv in SPLV: SPL += [(lv + 600, XC), (lv + 1200, XO)]
keep = set()
def K(*hs):
    for h_ in hs: keep.add(hh(T(h_)))
def KR(*hs):
    for h_ in hs: keep.add(hh(R_(h_)))
add(t='pl', p=[W(CX, L[0]), W(CR, L[0]), W(CR, L[-1]), W(CX, L[-1])], closed=True, layer='Размеры')
def zz(x, y0, y1):
    ym = (y0 + y1) / 2
    return dict(t='pl', p=[W(x, y1), W(x, ym + 40), W(x - 60, ym + 15), W(x + 60, ym - 15), W(x, ym - 40), W(x, y0)], layer='Размеры')
for lv, bh in zip(L[1:], BEAMS):
    if bh <= 0: continue
    for x0, x1 in ((CX - 450, CX), (CR, CR + 450)):
        add(t='pl', p=[W(x0, lv), W(x1, lv)], layer='Размеры'); add(t='pl', p=[W(x0, lv - bh), W(x1, lv - bh)], layer='Размеры')
    add(**zz(CX - 450, lv - bh - 75, lv + 75)); add(**zz(CR + 450, lv - bh - 75, lv + 75))
HFM = 400.0; FX0, FX1 = CX - 411, CR + 469
add(t='pl', p=[W(FX0, L[0]), W(FX1, L[0]), W(FX1, L[0] - HFM), W(FX0, L[0] - HFM)], closed=True, layer='Размеры')
add(t='hatch', pat='ANSI36', sc=20, ang=0, layer='.', loops=[[W(FX0, L[0] - HFM), W(FX1, L[0] - HFM), W(FX1, L[0]), W(FX0, L[0])]])
add(**zz(FX0, L[0] - HFM - 75, L[0] + 75)); add(**zz(FX1, L[0] - HFM - 75, L[0] + 75))
# bars: выпуск from Фм (dashed, template proto 1111C5) up to the first splice, then storey bars splice to splice, last to TOP
segs_bar = []                                           # (x, y0, y1, pos)
for gi, xs in ((0, XC), (1, XO)):
    ys = [SPL[2 * i + gi][0] for i in range(len(SPLV))] + [TOP]
    for x in xs:
        add(t='clone', h=T('1111C5'), base=[0, 0], to=[0, 0], tag=PRE + 'V%d' % x)
        add(t='spmove', h=PRE + 'V%d' % x, items=[[0, SX + x, SY + ys[0]], [1, SX + x, SY + L[0] - HFM + 50]])
        for i in range(len(ys) - 1):
            add(t='pl', p=[W(x, ys[i]), W(x, ys[i + 1])], layer=LAY, lw=40)
            segs_bar.append((x, ys[i], ys[i + 1], gi, i))
for y, xs in SPL:
    for x in xs:
        add(t='pl', p=[W(x - NW / 2, y - NAK / 2), W(x + NW / 2, y - NAK / 2), W(x + NW / 2, y + NAK / 2), W(x - NW / 2, y + NAK / 2)], closed=True, layer=LAY)
LEG = {20: 200, 22: 220, 25: 250, 28: 280, 32: 320}[int(D)]
add(t='pl', p=[W(XC[0], TOP - LEG), W(XC[0], TOP), W(XC[1], TOP), W(XC[1], TOP - LEG)], layer='диам16', lw=40)
# node zones (beam height, no hoops): overlapping zones of different beams are merged
ZON = []
for lv, bh in sorted(zip(L[1:], BEAMS), key=lambda q: q[0] - q[1]):
    lo_, hi_ = lv - bh, lv
    if ZON and lo_ <= ZON[-1][1] + 1e-6: ZON[-1] = (ZON[-1][0], max(ZON[-1][1], hi_))
    else: ZON.append((lo_, hi_))
LZ = [0.0] + [hi_ - L[0] for lo_, hi_ in ZON]
P, segs, per = CG.chain(LZ, [hi_ - lo_ for lo_, hi_ in ZON])
for (p, z) in per:
    n1, nm, n3 = z
    if nm == 0: idx = range(len(p))
    else: idx = sorted({0, n1, n1 + 1, len(p) - n3 - 2, len(p) - n3 - 1, len(p) - 1})
    for i in idx:
        add(t='pl', p=[W(CX + 40, L[0] + p[i]), W(CR - 40, L[0] + p[i])], layer=HL_LAY)
DL = CR + 1446.0
short_k = 0
for (y1, y2, st, k) in segs:
    if y2 - y1 < 1: continue
    o = dict(t='dim', h=T('111219'), p1=W(CR, L[0] + y1), p2=W(CR, L[0] + y2), dl=W(DL, L[0] + (y1 + y2) / 2), rot=math.pi / 2,
             txt=('%dх%d' % (round(st), k)) if k > 1 else '')
    if (y2 - y1) < 300 and y1 < 1e-6:                  # first short segment: text outside, below the chain start
        o['tx'] = W(DL, L[0] + y1 - 230)
    elif (y2 - y1) < 300:
        o['tx'] = W(DL + (362, 760)[short_k % 2], L[0] + (y1 + y2) / 2); short_k += 1
    else: short_k = 0
    add(**o)
# left chain: total, storeys
K('111174', '111182', '11118F', '1111A9', '1111B6', '1112B9', '1112C6')
add(t='dimpts', h=T('111174'), p1=W(2685, L[-1]), p2=W(3150, L[0]))
sto = [T('111182'), T('11118F')]
for i in range(len(L) - 1):
    if i < 2: add(t='dimpts', h=sto[i], p1=W(3150, L[i + 1]), p2=W(3150, L[i]))
    else: add(t='dim', h=T('11118F'), p1=W(3150, L[i + 1]), p2=W(3150, L[i]), dl=W(2743 + 203, (L[i] + L[i + 1]) / 2), rot=math.pi / 2, txt='')
if len(L) - 1 < 2: add(t='erase', h=[T('11118F')])
spl_d = [('1111A9', '1111B6'), ('1112B9', '1112C6')]
for i, lv in enumerate(SPLV):
    h1, h2 = spl_d[i]
    add(t='dimpts', h=T(h1), p1=W(4093, lv), p2=W(XC[0], lv + 600))
    add(t='dimpts', h=T(h2), p1=W(4093, lv + 600), p2=W(XO[0], lv + 1200))
for i in range(len(SPLV), 2): add(t='erase', h=[T(spl_d[i][0]), T(spl_d[i][1])])
# level marks: L0 -> base 18C36, top -> 18C39, intermediates -> 18C37, 18C3A, clones of 18C37; values by levelset after a regen
def lvs(v): return ('+' if v > 0 else '-') + ('%.3f' % abs(v)).replace('.', ',')
ZS = [TY['L0']] + [z for z, hh_ in FL]
mk = [(R_('18C36'), 9700.0)] + [None] * (len(L) - 2) + [(R_('18C39'), 19300.0)]
spare = [(R_('18C37'), 11700.0), (R_('18C3A'), 15500.0)]
for i in range(1, len(L) - 1):
    if spare: mk[i] = spare.pop(0)
    else:
        tg = PRE + 'LVC%d' % i
        add(t='clone', h=R_('18C37'), base=[0, 0], to=[0, 0], tag=tg); mk[i] = (tg, 11700.0)
for hh_, y0 in spare: add(t='erase', h=[hh_])
LVOPS = []
for i, ((h_, y0), y) in enumerate(zip(mk, L)):
    if h_.startswith(PRE) and h_[len(PRE):] in ('18C36', '18C37', '18C3A', '18C39'): KR(h_[len(PRE):])
    add(t='movegrp', h=[h_], d=[0, y - y0])
    LVOPS.append(dict(t='levelset', h=h_, value=lvs(ZS[i]), tag=h_))
# section marks 1-1 (in the main storey) and 2-2 (above the top)
K('111913', '111911', '111910')
def zone_mid(lo_y, hi_y=1e9):
    best = None
    tops = [L[0]] + [hi_ for lo_, hi_ in ZON]; bots = [lo_ for lo_, hi_ in ZON]
    for i in range(len(bots)):
        a_ = max(tops[i], lo_y); b2 = min(bots[i], hi_y)
        if b2 - a_ > (best[1] - best[0] if best else 0): best = (a_, b2)
    return best
ZN = []
for k_, sp in enumerate(SPLV):
    nxt = SPLV[k_ + 1] if k_ + 1 < len(SPLV) else 1e9
    ZN.append(zone_mid(sp + 1200, nxt))
s1y = [(a_ + b2) / 2 for a_, b2 in ZN]
CHP = sorted({L[0] + y for a_, b2, st_, k_ in segs for y in (a_, b2)})       # chain points (extension lines run there)
def clear_y(y):
    for _ in range(20):
        if all(abs(y - q) > 160 for q in CHP): return y
        y += 100
    return y
s1y = [clear_y(y) for y in s1y]
add(t='movegrp', h=[T('111913')], d=[0, s1y[0] - 13418])
if len(s1y) > 1: add(t='movegrp', h=[T('111911')], d=[0, s1y[1] - 17535])
else: add(t='erase', h=[T('111911')])
add(t='movegrp', h=[T('111910')], d=[0, L[-1] + 685 - 19535])
# section strokes keep the template's offsets from the column / dim chain (template: chain 5949, right point 6560; 2-2 right 5841 = CR+1338)
DLc = CR + 1446.0
add(t='spmove', h=T('111913'), items=[[1, SX + DLc + 611, SY + s1y[0]]])
if len(s1y) > 1: add(t='spmove', h=T('111911'), items=[[1, SX + DLc + 611, SY + s1y[1]]])
add(t='spmove', h=T('111910'), items=[[0, SX + CX - 1162, SY + L[-1] + 685], [1, SX + CR + 1338, SY + L[-1] + 685]])
K('111912', '1118C7', '1118D0', '11116E')
add(t='spmove', h=T('111912'), items=[[1, SX + XM, SY + TOP], [0, SX + XM + 200, SY + L[-1] + 340]])
DIA = '(%%%%C%d)' % D
if len(SPLV) == 1:
    POS = [('1', XC, 0), ('2', XO, 1)]
    ynote = [s1y[0] - 700, s1y[0] + 700]
    for (lab, xs, gi), yy in zip(POS, ynote):
        add(t='note', l1=lab, l2=DIA, origin=W(CX - 355, yy), targets=[W(x, yy) for x in xs], angle=math.pi, **NOTEo)
else:
    y1 = s1y[0] - 700; add(t='note', l1='1', l2=DIA, origin=W(CX - 355, y1), targets=[W(x, y1) for x in XF], angle=math.pi, **NOTEo)
    room = (L[-1] - BEAMS[-1]) - (SPLV[1] + 1200)
    if room >= 1100:
        y2 = SPLV[1] + 1200 + room * 0.3; add(t='note', l1='2', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XC], angle=math.pi, **NOTEo)
        y3 = SPLV[1] + 1200 + room * 0.75; add(t='note', l1='3', l2=DIA, origin=W(CX - 355, y3), targets=[W(x, y3) for x in XO], angle=math.pi, **NOTEo)
    else:
        y2 = SPLV[1] + 1200 + max(room, 300) / 2; add(t='note', l1='2, 3', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XF], angle=math.pi, **NOTEo)
NM = {20: 'Н5', 22: 'Н4', 25: 'Н3', 28: 'Н2', 32: 'Н1'}[int(D)]
for lv in SPLV:
    y = lv + 600
    add(t='note', l1=NM, l2=DIA, origin=W(CR + 420, y + 260), targets=[W(XC[1] + NW / 2, y), W(XO[-1] + NW / 2, y + 600)], **NOTEo)
p, (n1, nm, n3) = max(per, key=lambda q: q[0][-1] - q[0][0])
HLAB = 'Х1;Х2' if NPIN == 0 else ('Х1;Шп1;Шп2' if (NPB and NPH and abs(b - h) > 1) else 'Х1;Шп1')
add(t='note', l1=HLAB, l2='', origin=W(CR + (420 if len(HLAB) <= 6 else 250), L[0] + p[n1 + 1] + 350),
    targets=[W(CR - 40, L[0] + p[n1]), W(CR - 40, L[0] + p[n1 + 1])], **NOTEo)
_cand = [(lv, bh) for lv, bh in zip(L[1:], BEAMS) if bh > 0]
_below = [(lv, bh) for lv, bh in _cand if lv <= SPLV[0] + 1]                  # node at/below the splice floor (knot clear of detail А)
_far = [(lv, bh) for lv, bh in _cand if lv - bh > SPLV[0] + 2100 and lv < L[-1] - 1]
NODE_LV, NODE_BH = (_below or _far or _cand)[0]
c = W(XM, NODE_LV - NODE_BH / 2); add(t='mcset', h=T('1118C7'), set={'Center': c, 'Rack': [c[0] - 880 - (b - 400) / 2, c[1] - 150], 'Knot': 'Б', 'XRadius': 420 + (b - 400) / 2})
c = W(XC[1], SPL[0][0]); add(t='mcset', h=T('1118D0'), set={'Center': c, 'Rack': [SX + CR + 291 + 240, c[1] - 369], 'Knot': 'А'})
add(t='settext', h=T('11116E'), s='{\\L' + 'Колонна ' + MARK + '}')
OLD = [r['h'] for r in R if r['x1'] < 8200 and r['y0'] > 8000 and r['h'].upper() not in keep]
OLD += [r['h'] for r in R if r['t'] == 'INSERT' and r['x1'] < 8200 and 7500 < r['y0'] < 8500]
TPLH = {hh(T(h_)) for h_ in ('1111C5', '111219')}
add(t='erase', h=[h_ for h_ in OLD if h_.upper() not in TPLH])
add(t='erase', h=[h_ for h_ in TPLH if h_ not in keep])

# ================= 2. sections (x2) =================
Kx = 2.0
def bars(ox, oy):
    pts = set()
    for p_ in fpb: pts.add((p_, fph[0])); pts.add((p_, fph[-1]))
    for q in fph: pts.add((fpb[0], q)); pts.add((fpb[-1], q))
    return sorted((ox + Kx * x, oy + Kx * y) for x, y in pts)
def common(ox, oy, oldcol, oldbars, barT, dims, axes, tag):
    add(t='spmove', h=T(oldcol), items=[[0, SX + ox + Kx * b, SY + oy], [1, SX + ox + Kx * b, SY + oy + Kx * h], [2, SX + ox, SY + oy + Kx * h], [3, SX + ox, SY + oy]])
    bx, by, bc = barT
    for i, (x, y) in enumerate(bars(ox, oy)): add(t='clone', h=T(bc), base=W(bx, by), to=W(x, y), tag=PRE + tag + 'B%d' % i)
    add(t='erase', h=[T(h_) for h_ in oldbars])
    (b40l, b210l, b210r, b40r, b250l, b250r, yb1, yb2), (l40b, l210b, l210t, l40t, l250b, l250t, xl1, xl2) = dims
    xs = [0, 40, b / 2, b - 40, b]; ys = [0, 40, h / 2, h - 40, h]
    for h_, i in ((b40l, 0), (b210l, 1), (b210r, 2), (b40r, 3)):
        add(t='dimpts', h=T(h_), p1=W(ox + Kx * xs[i], oy), p2=W(ox + Kx * xs[i + 1], oy), dl=W(ox + Kx * (xs[i] + xs[i + 1]) / 2, yb1))
    add(t='dimpts', h=T(b250l), p1=W(ox, oy), p2=W(ox + Kx * b / 2, oy), dl=W(ox + Kx * b / 4, yb2))
    add(t='dimpts', h=T(b250r), p1=W(ox + Kx * b / 2, oy), p2=W(ox + Kx * b, oy), dl=W(ox + Kx * 3 * b / 4, yb2))
    for h_, i in ((l40b, 0), (l210b, 1), (l210t, 2), (l40t, 3)):
        add(t='dimpts', h=T(h_), p1=W(ox, oy + Kx * ys[i]), p2=W(ox, oy + Kx * ys[i + 1]), dl=W(xl1, oy + Kx * (ys[i] + ys[i + 1]) / 2))
    add(t='dimpts', h=T(l250b), p1=W(ox, oy), p2=W(ox, oy + Kx * h / 2), dl=W(xl2, oy + Kx * h / 4))
    add(t='dimpts', h=T(l250t), p1=W(ox, oy + Kx * h / 2), p2=W(ox, oy + Kx * h), dl=W(xl2, oy + Kx * 3 * h / 4))
    add(t='dimtx', h=T(b40l), at=W(ox - 300, yb1)); add(t='dimtx', h=T(b40r), at=W(ox + Kx * b + 300, yb1))
    add(t='dimtx', h=T(l40b), at=W(xl1, oy - 300)); add(t='dimtx', h=T(l40t), at=W(xl1, oy + Kx * h + 300))
    for h_, yy in ((l250b, oy + Kx * h / 4), (l250t, oy + Kx * 3 * h / 4)): add(t='dimtx', h=T(h_), at=W(xl2 - 73, yy))
    av, ah = axes; cx, cy = ox + Kx * b / 2, oy + Kx * h / 2
    add(t='spmove', h=T(av), items=[[0, SX + cx, SY + oy + Kx * h + (900 if nb > 3 else 720)], [1, SX + cx, SY + oy - 1060]])
    add(t='spmove', h=T(ah), items=[[0, SX + ox + Kx * b + 720, SY + cy], [1, SX + ox - 1090, SY + cy]])

S1 = (9314.0, 17388.0 - (h - 400)); ox, oy = S1
common(ox, oy, '11130A', ['11130B', '111329', '111345', '111337', '11133E', '111322', '111330', '11134C'], (9422, 18267, '11130B'),
       (('111353', '1113E3', '1113F0', '111361', '11138B', '111398', oy - 518, oy - 1129), ('11137D', '1113FD', '11140A', '11136F', '1113B2', '1113A5', 8796, 8403)),
       ('111306', '111309'), 's1')
add(t='movegrp', h=[T('1113BF')], d=[(ox + 112) - 9421, (oy + 112) - 17699])
add(t='scalegrp', h=[T('1113BF')], s=776 / 584.0, base=W(ox + 112, oy + 112))
add(t='dyn', h=T('1113BF'), prop='Расстояние1', value=Kx * b - 224); add(t='dyn', h=T('1113BF'), prop='Расстояние2', value=Kx * h - 224)
if NPIN == 0:
    add(t='movegrp', h=[T('1113D0')], d=[(ox + Kx * b / 2) - 9713, (oy + Kx * e) - 17698])
    add(t='scalegrp', h=[T('1113D0')], s=Kx * (b - 2 * e) / 584.0, base=W(ox + Kx * b / 2, oy + Kx * e))
else:
    add(t='erase', h=[T('1113D0')])
    PINS = [(W(ox + Kx * fpb[k], oy + Kx * e), math.pi / 2, Kx * (h - 2 * e), 'v%d' % k) for k in range(1, nb - 1)]
    PINS += [(W(ox + Kx * e, oy + Kx * fph[k]), 0.0, Kx * (b - 2 * e), 'h%d' % k) for k in range(1, nh - 1)]
    for ins, ang, span, nm_ in PINS:
        tg = PRE + 'PIN' + nm_
        add(t='clone', h=PRE + 'PIN:19EC6', base=[SX + 1000, SY - 6000], to=ins, tag=tg)
        if ang: add(t='xform', h=tg, base=ins, to=ins, ang=ang)
        add(t='dyn', h=tg, prop='Расстояние1', value=span + 1)
B = bars(ox, oy)
top = [p_ for p_ in B if abs(p_[1] - (oy + Kx * (h - e))) < 1]; bot = [p_ for p_ in B if abs(p_[1] - (oy + Kx * e)) < 1]
add(t='erase', h=[T('1113E1'), T('1113E2')])
lab = '1, 2' if len(SPLV) == 1 else '1 ... 3'
add(t='note', l1=lab, l2=DIA, origin=W(ox + Kx * b + 520, oy + Kx * h + 230), targets=[W(*p_) for p_ in sorted(top, reverse=True)], arrow='none', **NOTE)
add(t='note', l1=lab, l2=DIA, origin=W(ox + Kx * b + 520, oy - 230), targets=[W(*p_) for p_ in sorted(bot, reverse=True)], arrow='none', **NOTE)
t2 = W(ox + Kx * b * 0.75, oy + Kx * h * 0.75) if NPIN == 0 else (W(ox + Kx * b * 0.75, oy + Kx * fph[1]) if NPH else W(ox + Kx * fpb[1], oy + Kx * h * 0.3))
TWO_PINS = bool(NPB and NPH and abs(b - h) > 1)
HLAB = 'Х1;Х2' if NPIN == 0 else ('Х1;Шп1;Шп2' if TWO_PINS else 'Х1;Шп1')
add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * h * 0.72 + 150], [1, SX + ox + Kx * b - 64, SY + oy + Kx * h * 0.72], [2, t2[0], t2[1]]])
add(t='mcset', h=T('11190A'), set={'FirstLine': HLAB})

S2 = (13824.0, 17441.0 - (h - 400)); ox, oy = S2
common(ox, oy, '1117EA', ['11188F', '11189D', '1118B9', '1118AB', '1118B2', '111896', '1118A4', '1118C0'], (13932, 18320, '11188F'),
       (('1117EB', '111857', '111864', '1117F9', '111823', '111830', oy - 518, oy - 1129), ('111815', '111871', '11187E', '111807', '11184A', '11183D', 13306, 12882)),
       ('1117E6', '1117E9'), 's2')
Pp = lambda x, y: W(ox + Kx * x, oy + Kx * y)
add(t='erase', h=[T('11188B'), T('11188C'), T('11188E'), T('11188D')])
add(t='pl', p=[Pp(e, e), Pp(b - e, h - e)], layer='диам16', lw=40); add(t='pl', p=[Pp(e, h - e), Pp(b - e, e)], layer='диам16', lw=40)
for q in fpb[1:-1]: add(t='pl', p=[Pp(q, e), Pp(q, h - e)], layer='диам16', lw=40)
for q in fph[1:-1]: add(t='pl', p=[Pp(e, q), Pp(b - e, q)], layer='диам16', lw=40)
add(t='spmove', h=T('11190F'), items=[[0, SX + ox + Kx * b + 300, SY + oy - 120], [1, SX + ox + Kx * (b - e) - 40, SY + oy + Kx * (h - e) - 40 * h / b],
                                      [2, SX + ox + Kx * fpb[-2], SY + oy + Kx * h * 0.3], [3, SX + ox + Kx * fpb[-2], SY + oy + Kx * h * 0.3], [4, SX + ox + Kx * fpb[-2], SY + oy + Kx * h * 0.3]])

# ================= 3. node + mesh С1 =================
NMESH = int(round((NODE_BH - 100) / 100)) + 1          # 50 inside the beam faces, step 100
for h_, s_ in (('111534', '%d' % NODE_BH), ('111583', '50'), ('111563', '100х%d' % (NMESH - 1)), ('111572', '50'), ('111514', '%d' % (b / 2)), ('111523', '%d' % (b / 2)), ('111546', '%d' % b)):
    add(t='dimtext', h=T(h_), s=s_)
LMb, LMh = 2 * (b - 40), 2 * (h - 40)
rodsf = lambda w: [35 + 100 * i for i in range(int((w - 40 - 35 - 100) // 100) + 1)]
rods, rodsh = rodsf(b), rodsf(h)
DYM = LMh - LMb                                         # rectangular: meshes taller, top kept -> bottom dims/notes go down
x0, y0 = 13769.0, 11403.0 - DYM
if DYM > 1: add(t='movegrp', h=[T(x) for x in ('111417', '11147A', '111468', '111428', '11148B', '11190E')], d=[0, -DYM])
rx = [x0 + 2 * v for v in rods]
for x in rx: add(t='lineset', h=T('111466'), s=W(x, y0), e=W(x, y0 + LMh))
yc = y0 + LMh - 70
add(t='lineset', h=T('111467'), s=W(x0, yc), e=W(x0 + LMb, yc))
add(t='erase', h=[T('111466'), T('111478'), T('111479'), T('111467')])
add(t='dimpts', h=T('111417'), p1=W(rx[0], y0), p2=W(x0, y0))
add(t='dimpts', h=T('11147A'), p1=W(rx[0], y0), p2=W(rx[-1], y0)); add(t='dimtext', h=T('11147A'), s='100х%d' % (len(rods) - 1))
add(t='dimtx', h=T('11147A'), at=W((rx[0] + rx[-1]) / 2, 11150 - DYM))
add(t='dimpts', h=T('111468'), p1=W(rx[-1], y0), p2=W(x0 + LMb, yc))
add(t='dimpts', h=T('111428'), p1=W(x0 + LMb, yc), p2=W(x0, yc))
add(t='dimpts', h=T('111437'), p1=W(x0 + LMb, yc), p2=W(rx[-1], y0 + LMh))
add(t='dimpts', h=T('111448'), p1=W(x0 + LMb, yc), p2=W(rx[-1], y0))
add(t='dimpts', h=T('111457'), p1=W(rx[-1], y0 + LMh), p2=W(rx[-1], y0))
add(t='erase', h=[T('11190B')])
ya = y0 + 389 + (LMh - LMb) * 0.5
add(t='note', l1='10', l2='ш.100', origin=W(rx[0] - 600, ya), targets=[W(x, ya) for x in rx], arrow='oblique', angle=math.pi, **NOTE)
add(t='spmove', h=T('11190C'), items=[[1, SX + 14144, SY + yc]]); add(t='mcset', h=T('11190C'), set={'FirstLine': '10'})
xa, yb = 17797.0, 11121.0 - (LMh - LMb)
ry = [yb + 2 * v for v in rodsh]
for y in ry: add(t='lineset', h=T('1114DA'), s=W(xa, y), e=W(xa + LMb, y))
xr = xa + LMb - 70
add(t='lineset', h=T('1114DB'), s=W(xr, yb), e=W(xr, yb + LMh))
add(t='erase', h=[T('1114DA'), T('1114EC'), T('1114ED'), T('1114DB')])
add(t='dimpts', h=T('11148B'), p1=W(xa, ry[0]), p2=W(xa, yb))
add(t='dimpts', h=T('1114EE'), p1=W(xa, ry[0]), p2=W(xa, ry[-1])); add(t='dimtext', h=T('1114EE'), s='100х%d' % (len(rodsh) - 1))
add(t='dimtx', h=T('1114EE'), at=W(17420, (ry[0] + ry[-1]) / 2))
add(t='dimpts', h=T('1114DC'), p1=W(xa, ry[-1]), p2=W(xr, yb + LMh))
add(t='dimpts', h=T('11149C'), p1=W(xr, yb), p2=W(xr, yb + LMh))
add(t='dimpts', h=T('1114AB'), p1=W(xr, yb + LMh), p2=W(xa + LMb, ry[-1]))
add(t='dimpts', h=T('1114BC'), p1=W(xr, yb + LMh), p2=W(xa, ry[-1]))
add(t='dimpts', h=T('1114CB'), p1=W(xa + LMb, ry[-1]), p2=W(xa, ry[-1]))
add(t='erase', h=[T('11190D')])
add(t='note', l1='10', l2='ш.100', origin=W(18186, 10698 - (LMh - LMb)), targets=[W(18186, y) for y in ry], arrow='oblique', angle=math.pi, **NOTE)
add(t='spmove', h=T('11190E'), items=[[1, SX + xr, SY + 11686 - (LMh - LMb)]]); add(t='mcset', h=T('11190E'), set={'FirstLine': '10'})
add(t='spmove', h=T('1114FD'), items=[[1, SX + xr, SY + ry[0]]])

# ================= 4. tables, ведомость деталей, notes, stamp =================
HD = 10                                                  # hoops / pins Ø10 (Bekassyl 06.11)
envb, envh = b - 80, h - 80; dia = round(envb / math.sqrt(2) / 10) * 10
X1L = 2 * (envb + envh) + 200; X2L = 4 * dia + 200
PINLv = (h - 2 * e) + 200; PINLh = (b - 2 * e) + 200    # vertical pins span h, horizontal span b
SKV = round((h - 2 * e) / 10) * 10; SKH = round((b - 2 * e) / 10) * 10
SKD = round(math.hypot(b - 2 * e, h - 2 * e) / 10) * 10
NHOOP = len(P)
NODES = len(L) - 1                                       # mesh nodes: every floor
SQ = abs(b - h) < 1

SPM = PRE + '18D93'; STM = PRE + '18DCA'
SPMh = m[SPM]
Ltot = (L[-1] - L[0]) / 1000.0
lens = {}
for x, y0_, y1_, gi, i in segs_bar:
    lens.setdefault((gi, i), set()).add(round(y1_ - y0_))
if len(SPLV) == 1:
    pos_rows = [('1', lens[(0, 0)], 4), ('2', lens[(1, 0)], n - 4)]
else:
    a0 = lens[(0, 0)] | lens[(1, 0)]
    pos_rows = [('1', a0, n), ('2', lens[(0, 1)], 4), ('3', lens[(1, 1)], n - 4)]
for r_ in pos_rows: assert len(r_[1]) == 1, r_
# hoop / pin rows
hoop_rows = [('Х1', X1L, NHOOP)]
if NPIN == 0: hoop_rows.append(('Х2', X2L, NHOOP))
elif SQ: hoop_rows.append(('Шп1', PINLv, NHOOP * NPIN))
else:
    if NPB: hoop_rows.append(('Шп1', PINLv, NHOOP * NPB))
    if NPH: hoop_rows.append(('Шп2' if NPB else 'Шп1', PINLh, NHOOP * NPH))
# П-elements on top (NП = n/2): straight across h (inner b-face bars), straight across b (inner h-face bars), 2 diagonals
sk_rows = []
if SQ:
    if NPB: sk_rows.append(('Ск1', 2 * LEG + SKV, NPB + NPH))
else:
    if NPB: sk_rows.append(('Ск1', 2 * LEG + SKV, NPB))
    if NPH: sk_rows.append(('Ск%d' % (len(sk_rows) + 1), 2 * LEG + SKH, NPH))
sk_rows.append(('Ск%d' % (len(sk_rows) + 1), 2 * LEG + SKD, 2))
mesh_rows = [('10', b - 40, len(rods) + 1 + (0 if SQ else len(rodsh) + 1) * 0 + (len(rodsh) + 1 if SQ else 0))] if SQ else \
            [('10', h - 40, len(rods) + 1), ('11', b - 40, len(rodsh) + 1)]
# template rows: 1-2 hoops, 3-4 Ск, 5-7 positions, 8 blank, 9 Н, 10 С1, 11 Материалы, 12 concrete, 13 'Сетка С1', 14 mesh rod, 15 footnote
nh_extra = len(hoop_rows) - 2; nsk_extra = len(sk_rows) - 2; nm_extra = len(mesh_rows) - 1; npos_extra = len(pos_rows) - 3
assert nh_extra >= -1 and nsk_extra >= -1
if nm_extra > 0: add(t='trows', h=SPM, mode='ins', at=15, n=nm_extra, **{'from': 14})
if npos_extra > 0: add(t='trows', h=SPM, mode='ins', at=8, n=npos_extra, **{'from': 7})
if nsk_extra > 0: add(t='trows', h=SPM, mode='ins', at=5, n=nsk_extra, **{'from': 4})
if nh_extra > 0: add(t='trows', h=SPM, mode='ins', at=3, n=nh_extra, **{'from': 2})
oh = max(nh_extra, 0); osk = oh + max(nsk_extra, 0); opos = osk + max(npos_extra, 0); om = opos
r_h = [1 + i for i in range(max(len(hoop_rows), 2))]
r_sk = [3 + oh + i for i in range(max(len(sk_rows), 2))]
r_pos = [5 + osk + i for i in range(max(len(pos_rows), 3))]
r_N = 9 + opos; r_C1 = 10 + opos; r_conc = 12 + opos; r_mesh = [14 + om + i for i in range(len(mesh_rows))]
cells = [[0, 2, 'Колонна ' + MARK]]
blank_rows = []
def fill(rows_idx, data, d_):
    for k, r in enumerate(rows_idx):
        if k < len(data):
            lab, Lr, q = data[k]
            cells.extend([[r, 0, lab], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, '%d' % d_], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='], [r, 9, '%d' % Lr], [r, 10, '%d' % q]])
        else:
            cells.extend([[r, c_, ''] for c_ in (0, 1, 2, 3, 4, 5, 8, 9)]); blank_rows.append(r)
fill(r_h, hoop_rows, HD)
fill(r_sk, sk_rows, 16)
fill(r_pos, [(lab, list(ls)[0], q) for lab, ls, q in pos_rows], D)
fill([r_N], [(NM, 10 * D, 2 * n * len(SPLV))], D)
NMESH_TOT = sum(int(round((hi_ - lo_ - 100) / 100)) + 1 for lo_, hi_ in ZON if hi_ - lo_ > 0)
cells += [[r_C1, 10, '%d' % NMESH_TOT], [r_conc, 12, '%.2f' % (b * h / 1e6 * Ltot)]]
fill(r_mesh, mesh_rows, 10)
add(t='tset', h=SPM, cells=cells)
if blank_rows: add(t='tformula', h=SPM, cells=sum([[[r, 10, 'TEXT:'], [r, 11, 'TEXT:'], [r, 12, 'TEXT:']] for r in blank_rows], []))
F = []
for r in [x for x in r_h + r_sk + r_pos + [r_N] + r_mesh if x not in blank_rows]:
    Rr = r + 1
    F += [[r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (Rr, Rr, Rr)], [r, 12, 'L%d*K%d' % (Rr, Rr)]]
F += [[r_C1, 11, '+'.join('M%d' % (r + 1) for r in r_mesh)], [r_C1, 12, 'L%d*K%d' % (r_C1 + 1, r_C1 + 1)], [0, 12, 'Sum(M2:M%d)' % (r_C1 + 1)]]
add(t='tformula', h=SPM, cells=F)
TT = 'Table({T:%s})' % SPMh
add(t='tformula', h=STM, cells=[[6, 2, '0'],
                                [6, 4, '%s.Evaluate(Sum(M%d:M%d))+%s.M%d' % (TT, r_h[0] + 1, r_h[-1] + 1, TT, r_C1 + 1)],
                                [6, 5, '%s.Evaluate(Sum(M%d:M%d))' % (TT, r_sk[0] + 1, r_sk[-1] + 1)],
                                [6, 6, '%s.Evaluate(Sum(M%d:M%d))' % (TT, r_pos[0] + 1, r_N + 1)]])
add(t='tset', h=STM, cells=[[5, 6, '%%%%C%d' % D], [6, 0, 'Колонна ' + MARK]])
NEXTRA = max(nh_extra, 0) + max(nsk_extra, 0) + max(npos_extra, 0) + max(nm_extra, 0)
if NEXTRA: add(t='movegrp', h=[STM], d=[0, -400.0 * NEXTRA])
add(t='evalf')

# ---- Ведомость деталей ----
ROWC = {  # template rows: label, texts (top, left, right, bottom), sketch pline, 'по в.г.', 'L=', L value  (raw template handles)
    'X1': dict(lab='18DCB', top='18DD6', left='18DCE', right='18DD0', bot='18DCD', pl='18DE5', L='18DDC', rest=['18DE6', '18DCF']),
    'X2': dict(lab='18DCC', top='18DF1', left='18DE9', right='18DEB', bot='18DE8', pl='18E00', L='18DF7', rest=['18E01', '18DEA']),
    'S1': dict(lab='18DAF', top='18D9F', left='18D9E', bot='18DA2', pl='18DB0', ml='18DB3', L='18DA7', rest=['18DA1', '18DB1']),
    'S2': dict(lab='18DC5', top='18DB5', left='18DB4', bot='18DB8', pl='18DC6', ml='18DC9', L='18DBD', rest=['18DB7', '18DC7']),
}
def rowobjs(r): return [v for k, v in r.items() if k != 'rest'] + r['rest']
hx = max(len(hoop_rows) - 2, 0); skx = max(len(sk_rows) - 2, 0)
VX = 16550.0; VW = 3150.0
# 1) Ск rows move down by the extra hoop rows (before exploding the cell grid)
if hx: add(t='movegrp', h=[R_(x) for x in rowobjs(ROWC['S1']) + rowobjs(ROWC['S2'])], d=[0, -1000.0 * hx])
# 2) extra cells: explode the grid block, clone the last cell downwards
if hx + skx:
    add(t='explode', h=R_('18D95'), pre=PRE + 'VD')
    for k in range(1, hx + skx + 1):
        add(t='clone', h=PRE + 'VD15', base=[0, 0], to=[0, -1000.0 * k])
# 3) row content: hoop rows 0..len-1 (row 1 template = X2 content), Ск rows after them
def clone_row(src, dy, tagp):
    out = {}
    for k, v in src.items():
        if k == 'rest':
            out['rest'] = []
            for j, x in enumerate(v):
                add(t='clone', h=R_(x), base=[0, 0], to=[0, dy], tag=tagp + 'r%d' % j); out['rest'].append(tagp + 'r%d' % j)
        else:
            add(t='clone', h=R_(v), base=[0, 0], to=[0, dy], tag=tagp + k); out[k] = tagp + k
    return out
def raw(r): return {k: ([R_(x) for x in v] if k == 'rest' else R_(v)) for k, v in r.items()}
rows_h = [raw(ROWC['X1']), raw(ROWC['X2'])]
for k in range(2, len(hoop_rows)): rows_h.append(clone_row(ROWC['X2'], -1000.0 * (k - 1), PRE + 'VH%d' % k))
rows_s = [raw(ROWC['S1']), raw(ROWC['S2'])]
for k in range(2, len(sk_rows)):
    src = {kk: (vv if kk != 'rest' else vv) for kk, vv in ROWC['S2'].items()}
    rows_s.append(clone_row(src, -1000.0 * (k - 1), PRE + 'VS%d' % k))   # S2 content is already moved down by hx
def st(hd, v): add(t='settext', h=hd, s=v)
# hoop rows
lab0 = rows_h[0]
st(lab0['top'], '%d' % (envb + 100)); st(lab0['bot'], '%d' % envb); st(lab0['left'], '%d' % envh); st(lab0['right'], '%d' % (envh + 100)); st(lab0['L'], 'L=%d' % X1L if False else '%d' % X1L)
for k, (labr, Lr, q) in enumerate(hoop_rows[1:], start=1):
    r = rows_h[k]
    st(r['lab'], labr)
    st(r['L'], '%d' % Lr)
    if labr == 'Х2':
        st(r['top'], '%d' % (dia + 100)); st(r['left'], '%d' % dia); st(r['right'], '%d' % (dia + 100)); st(r['bot'], '%d' % dia)
    else:   # S-pin: the template pin block (as in the sections) replaces the hoop sketch
        span = Lr - 200
        for kk in ('left', 'right', 'bot'): st(r[kk], '')
        st(r['top'], '%d' % span)
        yc = 18327.0 - 1000.0 * (k - 1)
        add(t='erase', h=[r['pl']])
        tg = PRE + 'VPIN%d' % k
        add(t='clone', h=PRE + 'PIN:19EC6', base=[SX + 1000, SY - 6000], to=W(17998, yc), tag=tg)
        add(t='dyn', h=tg, prop='Расстояние1', value=700)
for k in range(len(hoop_rows), 2): pass
# Ск rows (П-elements Ø16): width text + legs + L
for k, (labr, Lr, q) in enumerate(sk_rows):
    r = rows_s[k]
    st(r['lab'], labr); st(r['top'], '%d' % LEG); st(r['bot'], '%d' % LEG); st(r['left'], '%d' % (Lr - 2 * LEG)); st(r['L'], '%d' % Lr)
SKLAB = ';'.join(x[0] for x in sk_rows) if len(sk_rows) <= 2 else '%s...%s' % (sk_rows[0][0], sk_rows[-1][0])
add(t='mcset', h=T('111912'), set={'FirstLine': SKLAB}); add(t='mcset', h=T('11190F'), set={'FirstLine': SKLAB})
TAB = dict(hoop=hoop_rows, sk=sk_rows, pos=[(a_, list(b2)[0], q) for a_, b2, q in pos_rows], mesh=mesh_rows, N=(NM, 10 * D, 2 * n * len(SPLV)), C1=NMESH_TOT)
add(t='settext', h=T('1118CE'), s=SHEET)
add(t='settext', h=T('1112D8'), s='Колонна ' + MARK)
add(t='settext', h=T('111304'), s='{\\C0;1. Схему расположения монолитных колонн см. лист 4.1.\\P2. Бетонирование колонн в местах примыкания ригелей и монолитной плиты вести после установки рабочей \\Pарматуры ригеля, плиты и сеток косвенного армирования.\\P3. Сварные соединения выполнять ручной электродуговой сваркой, электроды типа Э-42A по ГОСТ 9467-75.\\P4. Защитный слой бетона принят по наружной грани продольной арматуры.\\P5. Стыковку продольной арматуры выполнять по ГОСТ 14098-91, тип соединения С21-Рн.\\P6. Сетки С-1 составляются из двух взаимно перпендикулярных элементов.\\P7. Выпуски из фундамента см. лист фундамента.}')
add(t='erase', h=[PRE + 'PIN:19EC6'])
add(t='regen')
ops += LVOPS
add(t='save')
json.dump(ops, open(os.path.join(gx.S, 'ops', 'k3_%s.json' % PRE[:-1]), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(ops), 'ops', 'n=%d D=%d pins=%d hoops=%d' % (n, D, NPIN, NHOOP), json.dumps(TAB, ensure_ascii=False))
print('chain', [(round(a), round(b_), round(s), k) for a, b_, s, k in segs])
if '--run' in sys.argv: print(gx.run(ops, 'k3_' + PRE[:-1])[-2500:])
