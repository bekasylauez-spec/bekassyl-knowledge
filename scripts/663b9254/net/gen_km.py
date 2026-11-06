# Column sheet from Bekassyl's template «Колонна Км-1» (Шаблон для Кж.dwg, 1:50) for any square column with nf bars per face.
# usage: python gen_km.py <mark> <sheet no> <SX> <SY> <b> <nf> <D> [--run]
import json, math, sys, os
import gx, colgeo as CG

MARK, SHEET, SX, SY, b, nf, D = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), float(sys.argv[7])
PRE = 'K%s:' % MARK.replace('Км-', '').replace('.', '_')
MP = json.load(open('tplmap.json'))                 # t41 handle -> template handle
def T(h): return PRE + MP[h]                         # template object in this sheet
def W(x, y): return [SX + x, SY + y]
ops = []
def add(**k): ops.append(k); return k
NOTE = dict(scale=50, ts=2.5, style='ГОСТ 2.304', layer='Размеры')
LAY = 'диам%d' % D
e = 40 + D / 2                                        # bar centre from the face
n = 4 * (nf - 1)                                      # bars
facepos = [e + k * (b - 2 * e) / (nf - 1) for k in range(nf)]
step = (b - 2 * e) / (nf - 1)
NPIN = 0 if nf <= 3 else 2 * (nf - 2)

# ================= 0. import the template sheet =================
TPL = json.load(open('st/tpl_h.json'))
if '--imp' in sys.argv:
    r = gx.run([{'t': 'import', 'file': gx.S + r'\st\tplcol.dwg', 'h': TPL['ins'] + TPL['bad'], 'base': [264717, 271898], 'to': [SX, SY], 'pre': PRE},
                {'t': 'import', 'file': gx.S + r'\st\tplcol.dwg', 'h': ['19EC6'], 'base': [304063, 294024], 'to': [SX + 40000, SY], 'pre': PRE + 'PIN:'}], 'imp_' + MARK)
    print(r[-200:])
    m = gx.tagmap(); new = set(v.upper() for k, v in m.items() if k.startswith(PRE) and 'PIN' not in k)
    gx.run([{'t': 'list', 'win': [SX - 1e6, SY - 1e6, SX + 1e6, SY + 1e6]}], 'l')
    out = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8'):
        if not l.startswith('L\t'): continue
        rr = l.split('\t')
        if rr[2].upper() not in new: continue
        ex = [float(v) for v in rr[4][1:].split(',')]
        if not (ex[0] >= SX - 10 and ex[2] <= SX + 29710 and ex[1] >= SY - 10 and ex[3] <= SY + 21010): out.append(rr[2])
    print('out', len(out), gx.run([{'t': 'erase', 'h': out}, {'t': 'save'}], 'eo')[-60:])
    sys.exit()

# list of the imported sheet (handles in this drawing) to erase the elevation leftovers
import colsheet as C
R = C.listwin(SX, SY, 29700, 21000)
m = gx.tagmap(); hmap = {v.upper(): k for k, v in m.items() if k.startswith(PRE)}

# ================= 1. elevation =================
CX = 4103.0; CR = CX + b; XM = CX + b / 2
XF = [CX + p for p in facepos]; XC = [XF[0], XF[-1]]; XO = XF[1:-1]
L = [9700.0, 14250.0, 18300.0]; BEAM = 550.0; HFM = 700.0; TOP = L[2] - 20
NAK, NW = 10 * D, 2 * D
SPL = [(L[0] + 600, XC), (L[0] + 1200, XO), (L[1] + 600, XC), (L[1] + 1200, XO)]
keep = set()
def K(*hs):
    for h in hs: keep.add(m.get(T(h), '').upper())
add(t='pl', p=[W(CX, L[0]), W(CR, L[0]), W(CR, L[2]), W(CX, L[2])], closed=True, layer='Размеры')
def zz(x, y0, y1):
    ym = (y0 + y1) / 2
    return dict(t='pl', p=[W(x, y1), W(x, ym + 40), W(x - 60, ym + 15), W(x + 60, ym - 15), W(x, ym - 40), W(x, y0)], layer='Размеры')
for lv in L[1:]:
    for x0, x1 in ((CX - 450, CX), (CR, CR + 450)):
        add(t='pl', p=[W(x0, lv), W(x1, lv)], layer='Размеры'); add(t='pl', p=[W(x0, lv - BEAM), W(x1, lv - BEAM)], layer='Размеры')
    add(**zz(CX - 450, lv - BEAM - 75, lv + 75)); add(**zz(CR + 450, lv - BEAM - 75, lv + 75))
FX0, FX1 = CX - 411, CR + 469
add(t='pl', p=[W(FX0, L[0]), W(FX1, L[0]), W(FX1, L[0] - HFM), W(FX0, L[0] - HFM)], closed=True, layer='Размеры')
add(t='hatch', pat='ANSI36', sc=20, ang=0, layer='.', loops=[[W(FX0, L[0] - HFM), W(FX1, L[0] - HFM), W(FX1, L[0]), W(FX0, L[0])]])
add(**zz(FX0, L[0] - HFM - 75, L[0] + 75)); add(**zz(FX1, L[0] - HFM - 75, L[0] + 75))
for xs, y0 in ((XC, SPL[0][0]), (XO, SPL[1][0])):
    for x in xs:
        add(t='pl', p=[W(x, y0), W(x, y0 + 4550)], layer=LAY, lw=40)
        add(t='clone', h=T('1111C5'), base=[0, 0], to=[0, 0], tag=PRE + 'V%d' % x)
        add(t='spmove', h=PRE + 'V%d' % x, items=[[0, SX + x, SY + y0], [1, SX + x, SY + L[0] - HFM + 50]])
for xs, y0 in ((XC, SPL[2][0]), (XO, SPL[3][0])):
    for x in xs: add(t='pl', p=[W(x, y0), W(x, TOP)], layer=LAY, lw=40)
for y, xs in SPL:
    for x in xs:
        add(t='pl', p=[W(x - NW / 2, y - NAK / 2), W(x + NW / 2, y - NAK / 2), W(x + NW / 2, y + NAK / 2), W(x - NW / 2, y + NAK / 2)], closed=True, layer=LAY)
LEG = {20: 200, 22: 220, 25: 250, 28: 280, 32: 320}[int(D)]
add(t='pl', p=[W(XC[0], TOP - LEG), W(XC[0], TOP), W(XC[1], TOP), W(XC[1], TOP - LEG)], layer='диам16', lw=40)
LZ = [y - L[0] for y in L]
P, segs = CG.chain(LZ, [BEAM, BEAM])
HL = {}
for i in range(2):
    p, (n1, nm, n3), s = CG.storey_hoops(LZ[i], LZ[i + 1] - BEAM)
    HL[i] = (p, n1, nm, n3)
    for y in sorted({p[0], p[n1], p[n1 + 1], p[-n3 - 2], p[-n3 - 1], p[-1]}):
        add(t='pl', p=[W(CX + 40, L[0] + y), W(CR - 40, L[0] + y)], layer='диам8')
DL = CR + 1246.0
for (y1, y2, st, k) in segs:
    o = dict(t='dim', h=T('111219'), p1=W(CR, L[0] + y1), p2=W(CR, L[0] + y2), dl=W(DL, L[0] + (y1 + y2) / 2), rot=math.pi / 2,
             txt=('%dх%d' % (st, k)) if k > 1 else '')
    if (y2 - y1) < 300: o['tx'] = W(DL + 362, L[0] + (y1 + y2) / 2)
    add(**o)
K('111174', '111182', '11118F', '1111A9', '1111B6', '1112B9', '1112C6')
add(t='dimpts', h=T('111174'), p1=W(2685, L[2]), p2=W(3150, L[0]))
add(t='dimpts', h=T('111182'), p1=W(3150, L[1]), p2=W(3150, L[0]))
add(t='dimpts', h=T('11118F'), p1=W(3150, L[2]), p2=W(3150, L[1]))
for h, a, c, xb in (('1111A9', L[0], L[0] + 600, XC[0]), ('1111B6', L[0] + 600, L[0] + 1200, XO[0]), ('1112B9', L[1], L[1] + 600, XC[0]), ('1112C6', L[1] + 600, L[1] + 1200, XO[0])):
    add(t='dimpts', h=T(h), p1=W(4093, a), p2=W(xb, c))
add(t='dim', h=T('111182'), p1=W(FX0, L[0]), p2=W(FX0, L[0] - HFM), dl=W(3150, L[0] - HFM / 2), rot=math.pi / 2, txt='')
K('11116F', '111173', '111172', '111171')
add(t='movegrp', h=[T('111173')], d=[0, L[1] - 15500]); add(t='movegrp', h=[T('111172')], d=[0, L[2] - 19300])
K('111913', '111911', '111910')
add(t='movegrp', h=[T('111913')], d=[0, L[0] + 2450 - 13418]); add(t='movegrp', h=[T('111911')], d=[0, L[1] + 2050 - 17535])
add(t='movegrp', h=[T('111910')], d=[0, L[2] + 685 - 19535])
K('111912', '1118C7', '1118D0', '11116E')
add(t='spmove', h=T('111912'), items=[[1, SX + XM, SY + TOP], [0, SX + XM + 200, SY + L[2] + 340]])
DIA = '(%%%%C%d)' % D
NOTEo = dict(NOTE, arrow='oblique')
y1 = L[0] + 2400; add(t='note', l1='1', l2=DIA, origin=W(CX - 355, y1 + 0), targets=[W(x, y1) for x in XF], angle=math.pi, **NOTEo)
y2 = L[1] + 2200; add(t='note', l1='2', l2=DIA, origin=W(CX - 355, y2), targets=[W(x, y2) for x in XC], angle=math.pi, **NOTEo)
y3 = L[1] + 3000; add(t='note', l1='3', l2=DIA, origin=W(CX - 355, y3), targets=[W(x, y3) for x in XO], angle=math.pi, **NOTEo)
NM = {20: 'Н5', 22: 'Н4', 25: 'Н3', 28: 'Н2', 32: 'Н1'}[int(D)]
for y in (SPL[0][0], SPL[2][0]):
    add(t='note', l1=NM, l2=DIA, origin=W(CR + 420, y + 300 if y > L[1] else y + 260), targets=[W(XC[1] + NW / 2, y), W(XO[-1] + NW / 2, y + 600)], **NOTEo)
p, n1, nm, n3 = HL[1]
add(t='note', l1='Х1;Х2' if NPIN == 0 else 'Х1;Шп1', l2='', origin=W(CR + 420, L[0] + (p[n1 + nm] + p[n1 + nm + 1]) / 2 - 350),
    targets=[W(CR - 40, L[0] + p[n1 + nm]), W(CR - 40, L[0] + p[n1 + nm + 1])], **NOTEo)
c = W(XM, L[1] - BEAM / 2); add(t='mcset', h=T('1118C7'), set={'Center': c, 'Rack': [c[0] - 880 - (b - 400) / 2, c[1] - 825], 'Knot': 'Б', 'XRadius': 420 + (b - 400) / 2})
c = W(XC[1], SPL[0][0]); add(t='mcset', h=T('1118D0'), set={'Center': c, 'Rack': [c[0] + 345, c[1] - 369], 'Knot': 'А'})
add(t='settext', h=T('11116E'), s='{\\L' + 'Колонна ' + MARK + '}')
OLD = [r['h'] for r in R if r['x1'] < 8200 and r['y0'] > 8000 and r['h'].upper() not in keep]
OLD += [r['h'] for r in R if r['t'] == 'INSERT' and r['x1'] < 8200 and 7500 < r['y0'] < 8500]
TPLH = {m[T(h)].upper() for h in ('1111C5', '111219', '111182')}
add(t='erase', h=[h for h in OLD if h.upper() not in TPLH])
add(t='erase', h=[h for h in TPLH if h not in keep])
# level values: the marks compute from the template zero (0.000 at y 11700)
add(t='levelval', h=T('11116F'), old='-2.000', value='-4,650')
add(t='levelval', h=T('111173'), old='+2,550', value='-0,100')
add(t='levelval', h=T('111172'), old='+6,600', value='+3,950')

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
    add(t='erase', h=[T(h) for h in oldbars])
    (b40l, b210l, b210r, b40r, b250l, b250r, yb1, yb2), (l40b, l210b, l210t, l40t, l250b, l250t, xl1, xl2) = dims
    xs = [0, 40, b / 2, b - 40, b]
    for h, i in ((b40l, 0), (b210l, 1), (b210r, 2), (b40r, 3)):
        add(t='dimpts', h=T(h), p1=W(ox + Kx * xs[i], oy), p2=W(ox + Kx * xs[i + 1], oy), dl=W(ox + Kx * (xs[i] + xs[i + 1]) / 2, yb1))
    add(t='dimpts', h=T(b250l), p1=W(ox, oy), p2=W(ox + Kx * b / 2, oy), dl=W(ox + Kx * b / 4, yb2))
    add(t='dimpts', h=T(b250r), p1=W(ox + Kx * b / 2, oy), p2=W(ox + Kx * b, oy), dl=W(ox + Kx * 3 * b / 4, yb2))
    for h, i in ((l40b, 0), (l210b, 1), (l210t, 2), (l40t, 3)):
        add(t='dimpts', h=T(h), p1=W(ox, oy + Kx * xs[i]), p2=W(ox, oy + Kx * xs[i + 1]), dl=W(xl1, oy + Kx * (xs[i] + xs[i + 1]) / 2))
    add(t='dimpts', h=T(l250b), p1=W(ox, oy), p2=W(ox, oy + Kx * b / 2), dl=W(xl2, oy + Kx * b / 4))
    add(t='dimpts', h=T(l250t), p1=W(ox, oy + Kx * b / 2), p2=W(ox, oy + Kx * b), dl=W(xl2, oy + Kx * 3 * b / 4))
    add(t='dimtx', h=T(b40l), at=W(ox - 300, yb1)); add(t='dimtx', h=T(b40r), at=W(ox + Kx * b + 300, yb1))
    add(t='dimtx', h=T(l40b), at=W(xl1, oy - 300)); add(t='dimtx', h=T(l40t), at=W(xl1, oy + Kx * b + 300))
    for h, yy in ((l250b, oy + Kx * b / 4), (l250t, oy + Kx * 3 * b / 4)): add(t='dimtx', h=T(h), at=W(xl2 - 73, yy))
    if nf > 3:      # bar spacing on the top face
        add(t='dim', h=T(b210l), p1=W(ox + Kx * facepos[0], oy + Kx * b), p2=W(ox + Kx * facepos[-1], oy + Kx * b), dl=W(ox + Kx * b / 2, oy + Kx * b + 230),
            rot=0, txt='%dх%d=%d' % (round(step), nf - 1, round(step * (nf - 1))))
    av, ah = axes; cx, cy = ox + Kx * b / 2, oy + Kx * b / 2
    add(t='spmove', h=T(av), items=[[0, SX + cx, SY + oy + Kx * b + (900 if nf > 3 else 720)], [1, SX + cx, SY + oy - 1060]])
    add(t='spmove', h=T(ah), items=[[0, SX + ox + Kx * b + 720, SY + cy], [1, SX + ox - 1090, SY + cy]])

S1 = (9314.0, 17388.0 - (b - 400)); ox, oy = S1
common(ox, oy, '11130A', ['11130B', '111329', '111345', '111337', '11133E', '111322', '111330', '11134C'], (9422, 18267, '11130B'),
       (('111353', '1113E3', '1113F0', '111361', '11138B', '111398', oy - 518, oy - 1129), ('11137D', '1113FD', '11140A', '11136F', '1113B2', '1113A5', 8796, 8403)),
       ('111306', '111309'), 's1')
# square hoop (template dynamic block): corner at 64 from the faces, size by Расстояние1/2 (= outer - 96)
add(t='movegrp', h=[T('1113BF')], d=[(ox + 112) - 9421, (oy + 112) - 17699])
add(t='scalegrp', h=[T('1113BF')], s=776 / 584.0, base=W(ox + 112, oy + 112))
R_ = Kx * b - 128 - 96
add(t='dyn', h=T('1113BF'), prop='Расстояние1', value=R_); add(t='dyn', h=T('1113BF'), prop='Расстояние2', value=R_)
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
B = bars(ox, oy)
top = [p_ for p_ in B if abs(p_[1] - (oy + Kx * (b - e))) < 1]; bot = [p_ for p_ in B if abs(p_[1] - (oy + Kx * e)) < 1]
add(t='erase', h=[T('1113E1'), T('1113E2')])
add(t='note', l1='1 ... 3', l2=DIA, origin=W(ox + Kx * b + 520, oy + Kx * b + 230), targets=[W(*p_) for p_ in sorted(top, reverse=True)], arrow='none', **NOTE)
add(t='note', l1='1 ... 3', l2=DIA, origin=W(ox + Kx * b + 520, oy - 230), targets=[W(*p_) for p_ in sorted(bot, reverse=True)], arrow='none', **NOTE)
t2 = W(ox + Kx * b * 0.75, oy + Kx * b * 0.75) if NPIN == 0 else W(ox + Kx * b * 0.75, oy + Kx * facepos[1])
add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * b / 2 + 120], [1, SX + ox + Kx * b - 64, SY + oy + Kx * b * 0.72], [2, t2[0], t2[1]]])
add(t='mcset', h=T('11190A'), set={'FirstLine': 'Х1;Х2' if NPIN == 0 else 'Х1;Шп1'})

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
                                      [2, SX + ox + Kx * facepos[-2] if nf > 2 else 0, SY + oy + Kx * b * 0.3], [3, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3], [4, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3]])
for h, y in (('111307', 0),): pass

# ================= 3. node + mesh С1 =================
for h, s_ in (('111534', '550'), ('111583', '50'), ('111563', '100х4'), ('111572', '100'), ('111514', '%d' % (b / 2)), ('111523', '%d' % (b / 2)), ('111546', '%d' % b)):
    add(t='dimtext', h=T(h), s=s_)
add(t='dimtx', h=T('111583'), at=W(9120, 12520)); add(t='dimtx', h=T('111546'), at=W(10100, 10380))
add(t='movegrp', h=[T('11150C'), T('111533')], d=[-450, 0]); add(t='spmove', h=T('11150D'), items=[[1, SX + 7899, SY + 12728]])
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
add(t='note', l1='4', l2='ш.100', origin=W(12980, 11792), targets=[W(x, 11792) for x in rx], arrow='oblique', **NOTE)
add(t='spmove', h=T('11190C'), items=[[1, SX + 14144, SY + yc]]); add(t='mcset', h=T('11190C'), set={'FirstLine': '4'})
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
add(t='note', l1='4', l2='ш.100', origin=W(18186, 10698), targets=[W(18186, y) for y in ry], arrow='oblique', **NOTE)
add(t='spmove', h=T('11190E'), items=[[1, SX + xr, SY + 11686]]); add(t='mcset', h=T('11190E'), set={'FirstLine': '4'})
add(t='spmove', h=T('1114FD'), items=[[1, SX + xr, SY + ry[0]]])

# ================= 4. tables, ведомость деталей, notes, stamp =================
env = b - 80; dia = round(env / math.sqrt(2) / 10) * 10
X1L = 4 * env + 200; X2L = 4 * dia + 200; PINL = (b - 2 * e) + 200
SK1W = round((b - 2 * e) / 10) * 10; SK2W = round((b - 2 * e) * math.sqrt(2) / 10) * 10
NHOOP = len(HL[0][0]) + len(HL[1][0])
nrods = 2 * (len(rods) + 1)
V = {'1117B8': env + 100, '1117B0': env, '1117B2': env + 100, '1117AF': env, '1117BE': X1L,
     '1117D3': dia + 100, '1117CB': dia, '1117CD': dia + 100, '1117CA': dia, '1117D9': X2L if NPIN == 0 else PINL,
     '11172F': LEG, '11172E': SK1W, '111732': LEG, '111737': 2 * LEG + SK1W,
     '111745': LEG, '111744': SK2W, '111748': LEG, '11174D': 2 * LEG + SK2W}
for h, v in V.items(): add(t='settext', h=T(h), s='%d' % v)
SPM = '%s:%s' % (PRE[:-1], '18D93'); STM = '%s:%s' % (PRE[:-1], '18DCA')
cells = [[0, 2, 'Колонна ' + MARK], [1, 9, '%d' % X1L], [1, 10, '%d' % NHOOP],
         [2, 0, 'Х2' if NPIN == 0 else 'Шп1'], [2, 9, '%d' % (X2L if NPIN == 0 else PINL)], [2, 10, '%d' % (NHOOP if NPIN == 0 else NHOOP * NPIN)],
         [3, 9, '%d' % (2 * LEG + SK1W)], [3, 10, '%d' % (2 * (nf - 2))], [4, 9, '%d' % (2 * LEG + SK2W)], [4, 10, '2'],
         [5, 3, '%d' % D], [5, 9, '4550'], [5, 10, '%d' % n], [6, 3, '%d' % D], [6, 9, '3430'], [6, 10, '4'], [7, 3, '%d' % D], [7, 9, '2830'], [7, 10, '%d' % (n - 4)],
         [9, 0, NM], [9, 3, '%d' % D], [9, 9, '%d' % (10 * D)], [9, 10, '%d' % (4 * n)], [10, 10, '10'],
         [12, 12, '%.2f' % (b * b / 1e6 * 8.6)], [14, 0, '4'], [14, 9, '%d' % (b - 40)], [14, 10, '%d' % nrods]]
add(t='tset', h=SPM, cells=cells)
add(t='tset', h=STM, cells=[[5, 6, '%%%%C%d' % D], [6, 0, 'Колонна ' + MARK]])
if NPIN:
    add(t='settext', h=T('1117D3'), s=''); add(t='settext', h=T('1117CD'), s=''); add(t='settext', h=T('1117CA'), s='')
add(t='settext', h=T('1118CE'), s=SHEET)
add(t='settext', h=T('1112D8'), s='Колонна ' + MARK)
add(t='settext', h=T('111304'), s='{\\C0;1. Схему расположения монолитных колонн см. листы КЖ-2.1 ... 2.7.\\P2. Бетонирование колонн в местах примыкания ригелей и монолитной плиты вести после установки рабочей \\Pарматуры ригеля, плиты и сеток косвенного армирования.\\P3. Сварные соединения выполнять ручной электродуговой сваркой, электроды типа Э-42A по ГОСТ 9467-75.\\P4. Защитный слой бетона принят по наружной грани продольной арматуры.\\P5. Стыковку продольной арматуры выполнять по ГОСТ 14098-91, тип соединения С21-Рн.\\P6. Сетки С-1 составляются из двух взаимно перпендикулярных элементов.}')
add(t='save')
json.dump(ops, open('ops/km_%s.json' % PRE[:-1], 'w'), ensure_ascii=False)
print(len(ops), 'ops', 'n=%d D=%d pins=%d hoops=%d rods=%s' % (n, D, NPIN, NHOOP, rods))
if '--run' in sys.argv: print(gx.run(ops, 'km_' + PRE[:-1])[-1500:])
