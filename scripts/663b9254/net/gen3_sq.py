# БДМ Блок 3 — square column sheet from Bekassyl's template «Колонна Км-1» (Шаблон для Кж.dwg, 1:50), adapted from ЖК Галакси gen_km.py.
# usage: python gen3.py <type.json> [--imp] [--run]
#   type.json: {"mark":"Км-1","sheet":"4.1","SX":294417,"SY":271898,"b":700,"nf":3,"D":28,"L0":-1.2,
#               "floors":[[-0.05,900],[7.0,900]],"qty":20}
import json, math, sys, os
import gx, colgeo3 as CG
import colsheet as C

TY = json.load(open(sys.argv[1], encoding='utf-8'))
MARK, SHEET, SX, SY = TY['mark'], TY['sheet'], float(TY['SX']), float(TY['SY'])
b, nf, D = float(TY['b']), int(TY['nf']), float(TY['D'])
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
n = 4 * (nf - 1)
facepos = [e + k * (b - 2 * e) / (nf - 1) for k in range(nf)]
step = (b - 2 * e) / (nf - 1)
NPIN = 0 if nf <= 3 else 2 * (nf - 2)
TPLFILE = r'R:\Шаблон для Кж.dwg'

if '--imp' in sys.argv:
    H = json.load(open('tpl_h.json'))['ins']
    print(gx.run([{'t': 'import', 'file': TPLFILE, 'h': H, 'base': [264717, 271898], 'to': [SX, SY], 'pre': PRE},
                  {'t': 'import', 'file': TPLFILE, 'h': ['19EC6'], 'base': [304063, 294024], 'to': [SX + 40000, SY], 'pre': PRE + 'PIN:'},
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
SPLV = [Y(z) for z, h in FL[:-1]]                       # splice above every floor except the roof
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
LZ = [y - L[0] for y in L]
P, segs, per = CG.chain(LZ, BEAMS)
for (p, z) in per:
    n1, nm, n3 = z
    if nm == 0: idx = range(len(p))
    else: idx = sorted({0, n1, n1 + 1, len(p) - n3 - 2, len(p) - n3 - 1, len(p) - 1})
    for i in idx:
        add(t='pl', p=[W(CX + 40, L[0] + p[i]), W(CR - 40, L[0] + p[i])], layer=HL_LAY)
DL = CR + 1446.0
short_k = 0
for (y1, y2, st, k) in segs:
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
# level marks: template marks at y 9700 / 11700 / 15500 / 19300 (values follow from the template zero)
marks = [('18C36', 9700.0), ('18C37', 11700.0), ('18C3A', 15500.0), ('18C39', 19300.0)]
use = [marks[0], marks[1]] + ([marks[2]] if len(L) == 4 else []) + [marks[3]]
def lvs(v): return ('+' if v > 0 else '-') + ('%.3f' % abs(v)).replace('.', ',')
for i, ((h_, y0), y) in enumerate(zip(use, L)):
    KR(h_); add(t='movegrp', h=[R_(h_)], d=[0, y - y0])
LVOPS = []                                             # applied after a regen: base mark 18C36 keeps '-2.000', the others show -2.000 + (y - L0)
for i, ((h_, y0), y) in enumerate(zip(use, L)):
    z = TY['L0'] if i == 0 else FL[i - 1][0]
    old = '-2.000' if i == 0 else lvs(-2.0 + (y - L[0]) / 1000.0)
    LVOPS.append(dict(t='levelval', h=R_(h_), old=old, value=lvs(z), tag=R_(h_)))
# section marks 1-1 (in the main storey) and 2-2 (above the top)
K('111913', '111911', '111910')
s1y = [SPLV[0] + 2450] + ([SPLV[1] + 2050] if len(SPLV) > 1 else [])
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
    ynote = [SPLV[0] + 3000, SPLV[0] + 3800]
    for (lab, xs, gi), yy in zip(POS, ynote):
        add(t='note', l1=lab, l2=DIA, origin=W(CX - 355, yy), targets=[W(x, yy) for x in xs], angle=math.pi, **NOTEo)
else:
    y1 = SPLV[0] + 2400; add(t='note', l1='1', l2=DIA, origin=W(CX - 355, y1), targets=[W(x, y1) for x in XF], angle=math.pi, **NOTEo)
    y2 = SPLV[1] + 2200; add(t='note', l1='2', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XC], angle=math.pi, **NOTEo)
    y3 = SPLV[1] + 3000; add(t='note', l1='3', l2=DIA, origin=W(CX - 355, y3), targets=[W(x, y3) for x in XO], angle=math.pi, **NOTEo)
NM = {20: 'Н5', 22: 'Н4', 25: 'Н3', 28: 'Н2', 32: 'Н1'}[int(D)]
for lv in SPLV:
    y = lv + 600
    add(t='note', l1=NM, l2=DIA, origin=W(CR + 420, y + 260), targets=[W(XC[1] + NW / 2, y), W(XO[-1] + NW / 2, y + 600)], **NOTEo)
p, (n1, nm, n3) = per[-1]
add(t='note', l1='Х1;Х2' if NPIN == 0 else 'Х1;Шп1', l2='', origin=W(CR + 420, L[0] + p[n1 + 1] + 350),
    targets=[W(CR - 40, L[0] + p[n1]), W(CR - 40, L[0] + p[n1 + 1])], **NOTEo)
NODE_LV = L[1]; NODE_BH = BEAMS[0]
c = W(XM, NODE_LV - NODE_BH / 2); add(t='mcset', h=T('1118C7'), set={'Center': c, 'Rack': [c[0] - 880 - (b - 400) / 2, c[1] - 150], 'Knot': 'Б', 'XRadius': 420 + (b - 400) / 2})
c = W(XC[1], SPL[0][0]); add(t='mcset', h=T('1118D0'), set={'Center': c, 'Rack': [c[0] + 345, c[1] - 369], 'Knot': 'А'})
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
    for p_ in facepos:
        for q in (facepos[0], facepos[-1]):
            pts.add((p_, q)); pts.add((q, p_))
    return sorted((ox + Kx * x, oy + Kx * y) for x, y in pts)
def common(ox, oy, oldcol, oldbars, barT, dims, axes, tag):
    add(t='spmove', h=T(oldcol), items=[[0, SX + ox + Kx * b, SY + oy], [1, SX + ox + Kx * b, SY + oy + Kx * b], [2, SX + ox, SY + oy + Kx * b], [3, SX + ox, SY + oy]])
    bx, by, bc = barT
    for i, (x, y) in enumerate(bars(ox, oy)): add(t='clone', h=T(bc), base=W(bx, by), to=W(x, y), tag=PRE + tag + 'B%d' % i)
    add(t='erase', h=[T(h_) for h_ in oldbars])
    (b40l, b210l, b210r, b40r, b250l, b250r, yb1, yb2), (l40b, l210b, l210t, l40t, l250b, l250t, xl1, xl2) = dims
    xs = [0, 40, b / 2, b - 40, b]
    for h_, i in ((b40l, 0), (b210l, 1), (b210r, 2), (b40r, 3)):
        add(t='dimpts', h=T(h_), p1=W(ox + Kx * xs[i], oy), p2=W(ox + Kx * xs[i + 1], oy), dl=W(ox + Kx * (xs[i] + xs[i + 1]) / 2, yb1))
    add(t='dimpts', h=T(b250l), p1=W(ox, oy), p2=W(ox + Kx * b / 2, oy), dl=W(ox + Kx * b / 4, yb2))
    add(t='dimpts', h=T(b250r), p1=W(ox + Kx * b / 2, oy), p2=W(ox + Kx * b, oy), dl=W(ox + Kx * 3 * b / 4, yb2))
    for h_, i in ((l40b, 0), (l210b, 1), (l210t, 2), (l40t, 3)):
        add(t='dimpts', h=T(h_), p1=W(ox, oy + Kx * xs[i]), p2=W(ox, oy + Kx * xs[i + 1]), dl=W(xl1, oy + Kx * (xs[i] + xs[i + 1]) / 2))
    add(t='dimpts', h=T(l250b), p1=W(ox, oy), p2=W(ox, oy + Kx * b / 2), dl=W(xl2, oy + Kx * b / 4))
    add(t='dimpts', h=T(l250t), p1=W(ox, oy + Kx * b / 2), p2=W(ox, oy + Kx * b), dl=W(xl2, oy + Kx * 3 * b / 4))
    add(t='dimtx', h=T(b40l), at=W(ox - 300, yb1)); add(t='dimtx', h=T(b40r), at=W(ox + Kx * b + 300, yb1))
    add(t='dimtx', h=T(l40b), at=W(xl1, oy - 300)); add(t='dimtx', h=T(l40t), at=W(xl1, oy + Kx * b + 300))
    for h_, yy in ((l250b, oy + Kx * b / 4), (l250t, oy + Kx * 3 * b / 4)): add(t='dimtx', h=T(h_), at=W(xl2 - 73, yy))
    av, ah = axes; cx, cy = ox + Kx * b / 2, oy + Kx * b / 2
    add(t='spmove', h=T(av), items=[[0, SX + cx, SY + oy + Kx * b + (900 if nf > 3 else 720)], [1, SX + cx, SY + oy - 1060]])
    add(t='spmove', h=T(ah), items=[[0, SX + ox + Kx * b + 720, SY + cy], [1, SX + ox - 1090, SY + cy]])

S1 = (9314.0, 17388.0 - (b - 400)); ox, oy = S1
common(ox, oy, '11130A', ['11130B', '111329', '111345', '111337', '11133E', '111322', '111330', '11134C'], (9422, 18267, '11130B'),
       (('111353', '1113E3', '1113F0', '111361', '11138B', '111398', oy - 518, oy - 1129), ('11137D', '1113FD', '11140A', '11136F', '1113B2', '1113A5', 8796, 8403)),
       ('111306', '111309'), 's1')
add(t='movegrp', h=[T('1113BF')], d=[(ox + 112) - 9421, (oy + 112) - 17699])
add(t='scalegrp', h=[T('1113BF')], s=776 / 584.0, base=W(ox + 112, oy + 112))
R2 = Kx * b - 128 - 96
add(t='dyn', h=T('1113BF'), prop='Расстояние1', value=R2); add(t='dyn', h=T('1113BF'), prop='Расстояние2', value=R2)
if NPIN == 0:
    add(t='movegrp', h=[T('1113D0')], d=[(ox + Kx * b / 2) - 9713, (oy + Kx * e) - 17698])
    add(t='scalegrp', h=[T('1113D0')], s=Kx * (b - 2 * e) / 584.0, base=W(ox + Kx * b / 2, oy + Kx * e))
else:
    add(t='erase', h=[T('1113D0')])
    span = Kx * (b - 2 * e)
    for k in range(1, nf - 1):
        q = Kx * facepos[k]
        for j, (ins, ang) in enumerate(((W(ox + Kx * e, oy + q), 0.0), (W(ox + q, oy + Kx * e), math.pi / 2))):
            tg = PRE + 'PIN%d_%d' % (k, j)
            add(t='clone', h=PRE + 'PIN:19EC6', base=[SX + 40000, SY], to=ins, tag=tg)
            if ang: add(t='xform', h=tg, base=ins, to=ins, ang=ang)
            add(t='dyn', h=tg, prop='Расстояние1', value=span + 1)
    add(t='erase', h=[PRE + 'PIN:19EC6'])
B = bars(ox, oy)
top = [p_ for p_ in B if abs(p_[1] - (oy + Kx * (b - e))) < 1]; bot = [p_ for p_ in B if abs(p_[1] - (oy + Kx * e)) < 1]
add(t='erase', h=[T('1113E1'), T('1113E2')])
lab = '1, 2' if len(SPLV) == 1 else '1 ... 3'
add(t='note', l1=lab, l2=DIA, origin=W(ox + Kx * b + 520, oy + Kx * b + 230), targets=[W(*p_) for p_ in sorted(top, reverse=True)], arrow='none', **NOTE)
add(t='note', l1=lab, l2=DIA, origin=W(ox + Kx * b + 520, oy - 230), targets=[W(*p_) for p_ in sorted(bot, reverse=True)], arrow='none', **NOTE)
t2 = W(ox + Kx * b * 0.75, oy + Kx * b * 0.75) if NPIN == 0 else W(ox + Kx * b * 0.75, oy + Kx * facepos[1])
add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * b / 2 + 120], [1, SX + ox + Kx * b - 64, SY + oy + Kx * b * 0.72], [2, t2[0], t2[1]]])
add(t='mcset', h=T('11190A'), set={'FirstLine': 'Х1;Х2' if NPIN == 0 else 'Х1;Шп1'})
if NPIN == 0: add(t='erase', h=[PRE + 'PIN:19EC6'])

S2 = (13824.0, 17441.0 - (b - 400)); ox, oy = S2
common(ox, oy, '1117EA', ['11188F', '11189D', '1118B9', '1118AB', '1118B2', '111896', '1118A4', '1118C0'], (13932, 18320, '11188F'),
       (('1117EB', '111857', '111864', '1117F9', '111823', '111830', oy - 518, oy - 1129), ('111815', '111871', '11187E', '111807', '11184A', '11183D', 13306, 12882)),
       ('1117E6', '1117E9'), 's2')
Pp = lambda x, y: W(ox + Kx * x, oy + Kx * y)
add(t='erase', h=[T('11188B'), T('11188C'), T('11188E'), T('11188D')])
add(t='pl', p=[Pp(e, e), Pp(b - e, b - e)], layer='диам16', lw=40); add(t='pl', p=[Pp(e, b - e), Pp(b - e, e)], layer='диам16', lw=40)
for k in range(1, nf - 1):
    q = facepos[k]
    add(t='pl', p=[Pp(q, e), Pp(q, b - e)], layer='диам16', lw=40); add(t='pl', p=[Pp(e, q), Pp(b - e, q)], layer='диам16', lw=40)
add(t='spmove', h=T('11190F'), items=[[0, SX + ox + Kx * b + 300, SY + oy - 120], [1, SX + ox + Kx * (b - e) - 40, SY + oy + Kx * (b - e) - 40],
                                      [2, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3], [3, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3], [4, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3]])

# ================= 3. node + mesh С1 =================
NMESH = int(round((NODE_BH - 100) / 100)) + 1          # 50 inside the beam faces, step 100
for h_, s_ in (('111534', '%d' % NODE_BH), ('111583', '50'), ('111563', '100х%d' % (NMESH - 1)), ('111572', '50'), ('111514', '%d' % (b / 2)), ('111523', '%d' % (b / 2)), ('111546', '%d' % b)):
    add(t='dimtext', h=T(h_), s=s_)
LM = 2 * (b - 40); rods = [35 + 100 * i for i in range(int((b - 40 - 35 - 100) // 100) + 1)]
x0, y0 = 13769.0, 11403.0
rx = [x0 + 2 * v for v in rods]
for x in rx: add(t='lineset', h=T('111466'), s=W(x, y0), e=W(x, y0 + LM))
yc = y0 + LM - 70
add(t='lineset', h=T('111467'), s=W(x0, yc), e=W(x0 + LM, yc))
add(t='erase', h=[T('111466'), T('111478'), T('111479'), T('111467')])
add(t='dimpts', h=T('111417'), p1=W(rx[0], y0), p2=W(x0, y0))
add(t='dimpts', h=T('11147A'), p1=W(rx[0], y0), p2=W(rx[-1], y0)); add(t='dimtext', h=T('11147A'), s='100х%d' % (len(rods) - 1))
add(t='dimtx', h=T('11147A'), at=W((rx[0] + rx[-1]) / 2, 11150))
add(t='dimpts', h=T('111468'), p1=W(rx[-1], y0), p2=W(x0 + LM, yc))
add(t='dimpts', h=T('111428'), p1=W(x0 + LM, yc), p2=W(x0, yc))
add(t='dimpts', h=T('111437'), p1=W(x0 + LM, yc), p2=W(rx[-1], y0 + LM))
add(t='dimpts', h=T('111448'), p1=W(x0 + LM, yc), p2=W(rx[-1], y0))
add(t='dimpts', h=T('111457'), p1=W(rx[-1], y0 + LM), p2=W(rx[-1], y0))
add(t='erase', h=[T('11190B')])
add(t='note', l1='10', l2='ш.100', origin=W(12980, 11792), targets=[W(x, 11792) for x in rx], arrow='oblique', **NOTE)
add(t='spmove', h=T('11190C'), items=[[1, SX + 14144, SY + yc]]); add(t='mcset', h=T('11190C'), set={'FirstLine': '10'})
xa, yb = 17797.0, 11121.0
ry = [yb + 2 * v for v in rods]
for y in ry: add(t='lineset', h=T('1114DA'), s=W(xa, y), e=W(xa + LM, y))
xr = xa + LM - 70
add(t='lineset', h=T('1114DB'), s=W(xr, yb), e=W(xr, yb + LM))
add(t='erase', h=[T('1114DA'), T('1114EC'), T('1114ED'), T('1114DB')])
add(t='dimpts', h=T('11148B'), p1=W(xa, ry[0]), p2=W(xa, yb))
add(t='dimpts', h=T('1114EE'), p1=W(xa, ry[0]), p2=W(xa, ry[-1])); add(t='dimtext', h=T('1114EE'), s='100х%d' % (len(rods) - 1))
add(t='dimtx', h=T('1114EE'), at=W(17420, (ry[0] + ry[-1]) / 2))
add(t='dimpts', h=T('1114DC'), p1=W(xa, ry[-1]), p2=W(xr, yb + LM))
add(t='dimpts', h=T('11149C'), p1=W(xr, yb), p2=W(xr, yb + LM))
add(t='dimpts', h=T('1114AB'), p1=W(xr, yb + LM), p2=W(xa + LM, ry[-1]))
add(t='dimpts', h=T('1114BC'), p1=W(xr, yb + LM), p2=W(xa, ry[-1]))
add(t='dimpts', h=T('1114CB'), p1=W(xa + LM, ry[-1]), p2=W(xa, ry[-1]))
add(t='erase', h=[T('11190D')])
add(t='note', l1='10', l2='ш.100', origin=W(18186, 10698), targets=[W(18186, y) for y in ry], arrow='oblique', **NOTE)
add(t='spmove', h=T('11190E'), items=[[1, SX + xr, SY + 11686]]); add(t='mcset', h=T('11190E'), set={'FirstLine': '10'})
add(t='spmove', h=T('1114FD'), items=[[1, SX + xr, SY + ry[0]]])

# ================= 4. tables, ведомость деталей, notes, stamp =================
HD = 10                                                  # hoops / pins Ø10 (Bekassyl 06.11)
env = b - 80; dia = round(env / math.sqrt(2) / 10) * 10
X1L = 4 * env + 200; X2L = 4 * dia + 200; PINL = (b - 2 * e) + 200
SK1W = round((b - 2 * e) / 10) * 10; SK2W = round((b - 2 * e) * math.sqrt(2) / 10) * 10
NHOOP = len(P)
NODES = len(L) - 1                                       # mesh nodes: every floor
nrods = 2 * (len(rods) + 1)
V = {'1117B8': env + 100, '1117B0': env, '1117B2': env + 100, '1117AF': env, '1117BE': X1L,
     '1117D3': dia + 100, '1117CB': dia, '1117CD': dia + 100, '1117CA': dia, '1117D9': X2L if NPIN == 0 else PINL,
     '11172F': LEG, '11172E': SK1W, '111732': LEG, '111737': 2 * LEG + SK1W,
     '111745': LEG, '111744': SK2W, '111748': LEG, '11174D': 2 * LEG + SK2W}
for h_, v in V.items(): add(t='settext', h=T(h_), s='%d' % v)
SPM = PRE + '18D93'; STM = PRE + '18DCA'
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
cells = [[0, 2, 'Колонна ' + MARK], [1, 3, '%d' % HD], [1, 9, '%d' % X1L], [1, 10, '%d' % NHOOP],
         [2, 0, 'Х2' if NPIN == 0 else 'Шп1'], [2, 3, '%d' % HD], [2, 9, '%d' % (X2L if NPIN == 0 else PINL)], [2, 10, '%d' % (NHOOP if NPIN == 0 else NHOOP * NPIN)],
         [3, 9, '%d' % (2 * LEG + SK1W)], [3, 10, '%d' % (2 * (nf - 2) if nf > 2 else 2)], [4, 9, '%d' % (2 * LEG + SK2W)], [4, 10, '2']]
for k, (lab, ls, q) in enumerate(pos_rows):
    cells += [[5 + k, 0, lab], [5 + k, 3, '%d' % D], [5 + k, 9, '%d' % list(ls)[0]], [5 + k, 10, '%d' % q]]
if len(pos_rows) == 2: cells += [[7, c_, ''] for c_ in (0, 1, 2, 3, 4, 5, 8, 9)]
cells += [[9, 0, NM], [9, 3, '%d' % D], [9, 9, '%d' % (10 * D)], [9, 10, '%d' % (2 * n * len(SPLV))], [10, 10, '%d' % (2 * NODES * 0 + NMESH * NODES)],
          [12, 12, '%.2f' % (b * b / 1e6 * Ltot)], [14, 9, '%d' % (b - 40)], [14, 10, '%d' % nrods]]
add(t='tset', h=SPM, cells=cells)
if len(pos_rows) == 2: add(t='tformula', h=SPM, cells=[[7, 10, 'TEXT:'], [7, 11, 'TEXT:'], [7, 12, 'TEXT:']])
SPMh = m[SPM]
add(t='tformula', h=STM, cells=[[6, 2, '0'], [6, 4, 'Table({T:%s}).Evaluate(Sum(M2:M3))+Table({T:%s}).M11' % (SPMh, SPMh)]])
add(t='tset', h=STM, cells=[[5, 6, '%%%%C%d' % D], [6, 0, 'Колонна ' + MARK]])
import tfix
add(t='tformula', h=SPM, cells=tfix.spec_formulas(tuple([1, 2, 3, 4] + [5 + k for k in range(len(pos_rows))] + [9, 14])))
add(t='evalf')
if NPIN:
    add(t='settext', h=T('1117D3'), s=''); add(t='settext', h=T('1117CD'), s=''); add(t='settext', h=T('1117CA'), s='')
add(t='settext', h=T('1118CE'), s=SHEET)
add(t='settext', h=T('1112D8'), s='Колонна ' + MARK)
add(t='settext', h=T('111304'), s='{\\C0;1. Схему расположения монолитных колонн см. лист 4.0.\\P2. Бетонирование колонн в местах примыкания ригелей и монолитной плиты вести после установки рабочей \\Pарматуры ригеля, плиты и сеток косвенного армирования.\\P3. Сварные соединения выполнять ручной электродуговой сваркой, электроды типа Э-42A по ГОСТ 9467-75.\\P4. Защитный слой бетона принят по наружной грани продольной арматуры.\\P5. Стыковку продольной арматуры выполнять по ГОСТ 14098-91, тип соединения С21-Рн.\\P6. Сетки С-1 составляются из двух взаимно перпендикулярных элементов.\\P7. Выпуски из фундамента см. лист фундамента.}')
add(t='regen')
ops += LVOPS
add(t='save')
json.dump(ops, open(os.path.join(gx.S, 'ops', 'k3_%s.json' % PRE[:-1]), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(ops), 'ops', 'n=%d D=%d pins=%d hoops=%d rods=%s pos=%s' % (n, D, NPIN, NHOOP, rods, [(a, list(b_)[0], q) for a, b_, q in pos_rows]))
print('chain', [(round(a), round(b_), round(s), k) for a, b_, s, k in segs])
if '--run' in sys.argv: print(gx.run(ops, 'k3_' + PRE[:-1])[-2500:])
