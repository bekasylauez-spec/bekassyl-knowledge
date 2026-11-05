# Км-1 sheet 4.1 from Bekassyl's template «Колонна Км-1» (Шаблон для Кж.dwg, sheet 1:50) — elevation.
import json, math, sys
import gx, colgeo as CG

X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
R = json.load(open('w/t41_list.json'))
ops = []
def add(**k): ops.append(k); return k
T = 'T41e_'

# ---- column data ----
CX = 4103.0; b = 500.0; CR = CX + b; XM = CX + b / 2
XC = [CX + 56, CX + b - 56]                 # Ø32 corners (cover 40 + 16)
L = [9700.0, 14250.0, 18300.0]              # -4.650, -0.100, +3.950
BEAM = 550.0
HFM = 700.0
SPL = [(L[0] + 600, XC), (L[0] + 1200, [XM]), (L[1] + 600, XC), (L[1] + 1200, [XM])]
TOP = L[2] - 20
NAK = 320.0; NW = 64.0                      # накладка Н1 for Ø32: 10d long

keep = set()
def K(*hs):
    for h in hs: keep.add(h)

# ---- column outline, beam stubs, Фм ----
add(t='pl', p=[W(CX, L[0]), W(CR, L[0]), W(CR, L[2]), W(CX, L[2])], closed=True, layer='Размеры', tag=T + 'COL')
for lv in L[1:]:
    for x0, x1 in ((CX - 450, CX), (CR, CR + 450)):
        add(t='pl', p=[W(x0, lv), W(x1, lv)], layer='Размеры'); add(t='pl', p=[W(x0, lv - BEAM), W(x1, lv - BEAM)], layer='Размеры')
FX0, FX1 = 3692.0, 5072.0
add(t='pl', p=[W(FX0, L[0]), W(FX1, L[0]), W(FX1, L[0] - HFM), W(FX0, L[0] - HFM)], closed=True, layer='Размеры', tag=T + 'FM')
add(t='hatch', pat='ANSI36', sc=20, ang=0, layer='.', loops=[[W(FX0, L[0] - HFM), W(FX1, L[0] - HFM), W(FX1, L[0]), W(FX0, L[0])]], tag=T + 'HFM')
# breaks: template pairs (+7.600 -> top beam, +3.800 -> -0.100 beam, -2.000 -> Фм)
for (hl, hr), (y0, y1) in ((('1111D1', '1111D0'), (L[2] - BEAM - 75, L[2] + 75)), (('1111CF', '1111CE'), (L[1] - BEAM - 75, L[1] + 75)), (('1111CD', '1111CC'), (L[0] - HFM - 75, L[0] + 75))):
    for h, x in ((hl, CX - 450 if y1 > L[0] + 100 else FX0), (hr, CR + 450 if y1 > L[0] + 100 else FX1)):
        K(h); add(t='spmove', h=h, items=[[0, X0 + x, Y0 + y0], [1, X0 + x, Y0 + (y0 + y1) / 2], [2, X0 + x, Y0 + y1], [3, X0 + x, Y0 + y1]])

# ---- bars: pos 1 (storey 1), pos 2 (corners, storey 2), pos 3 (mid, storey 2); выпуски dashed below the first splice ----
for xs, y0 in ((XC, SPL[0][0]), ([XM], SPL[1][0])):
    for x in xs:
        add(t='pl', p=[W(x, y0), W(x, y0 + 4550)], layer='диам32', lw=40)
        add(t='clone', h='1111C5', base=[0, 0], to=[0, 0], tag=T + 'V%d' % x)
        add(t='spmove', h=T + 'V%d' % x, items=[[0, X0 + x, Y0 + y0], [1, X0 + x, Y0 + L[0] - HFM + 50]])
for xs, y0 in ((XC, SPL[2][0]), ([XM], SPL[3][0])):
    for x in xs: add(t='pl', p=[W(x, y0), W(x, TOP)], layer='диам32', lw=40)
# накладки at every splice (both sides of the joint, drawn as the template's 2d x 10d rectangles)
for y, xs in SPL:
    for x in xs:
        add(t='pl', p=[W(x - NW / 2, y - NAK / 2), W(x + NW / 2, y - NAK / 2), W(x + NW / 2, y + NAK / 2), W(x - NW / 2, y + NAK / 2)], closed=True, layer='диам32')

# ---- hoops (zone-end lines) and the right chain ----
LZ = [y - L[0] for y in L]
P, segs = CG.chain(LZ, [BEAM, BEAM])
for i in range(2):
    p, (n1, nm, n3), s = CG.storey_hoops(LZ[i], LZ[i + 1] - BEAM)
    for y in sorted({p[0], p[n1], p[n1 + 1], p[-n3 - 2], p[-n3 - 1], p[-1]}):
        add(t='pl', p=[W(CX + 40, L[0] + y), W(CR - 40, L[0] + y)], layer='Размеры', tag=T + 'H%d' % y)
DL = 5849.0
for (y1, y2, st, n) in segs:
    o = dict(t='dim', h='111219', p1=W(CR, L[0] + y1), p2=W(CR, L[0] + y2), dl=W(DL, L[0] + (y1 + y2) / 2), rot=math.pi / 2,
             txt=('%dх%d' % (st, n)) if n > 1 else '', tag=T + 'D%d' % y1)
    if (y2 - y1) < 300: o['tx'] = W(DL + 362, L[0] + (y1 + y2) / 2)
    add(**o)

# ---- left dims: overall, storeys, splice offsets ----
K('111174', '111182', '11118F', '1111A9', '1111B6', '1112B9', '1112C6')
add(t='dimpts', h='111174', p1=W(2685, L[2]), p2=W(3150, L[0]))
add(t='dimpts', h='111182', p1=W(3150, L[1]), p2=W(3150, L[0]))
add(t='dimpts', h='11118F', p1=W(3150, L[2]), p2=W(3150, L[1]))
for h, a, c, xb in (('1111A9', L[0], L[0] + 600, XC[0]), ('1111B6', L[0] + 600, L[0] + 1200, XM), ('1112B9', L[1], L[1] + 600, XC[0]), ('1112C6', L[1] + 600, L[1] + 1200, XM)):
    add(t='dimpts', h=h, p1=W(4093, a), p2=W(xb, c))
# Фм thickness dim on the left (clone of a storey dim)
add(t='dim', h='111182', p1=W(FX0, L[0]), p2=W(FX0, L[0] - HFM), dl=W(3150, L[0] - HFM / 2), rot=math.pi / 2, txt='', tag=T + 'DFM')

# ---- level marks: move, then shift the stored zero to -0.100 + 100 ----
K('11116F', '111173', '111172', '111171')
add(t='movegrp', h=['111173'], d=[0, L[1] - 15500]); add(t='movegrp', h=['111172'], d=[0, L[2] - 19300])
for h, tg in (('11116F', 'T41e_LV0'), ('111173', 'T41e_LV1'), ('111172', 'T41e_LV2')):
    add(t='levbase', h=h, old=Y0 + 11700, new=Y0 + L[1] + 100, tag=tg)

# ---- section marks: 1-1 in each storey (middle of the 200 zone), 2-2 above the top ----
K('111913', '111911', '111910')
add(t='movegrp', h=['111913'], d=[0, L[0] + 2400 - 13418 - 250]); add(t='movegrp', h=['111911'], d=[0, L[1] + 2300 - 17535 - 250])
add(t='movegrp', h=['111910'], d=[0, L[2] + 235 - 19535])

# ---- callouts ----
K('111909', '111907', '111908', '111912', '1118C7', '1118D0', '11116E')
y1 = L[0] + 2400
add(t='spmove', h='111909', items=[[0, X0 + 3748, Y0 + y1], [1, X0 + XC[1], Y0 + y1], [2, X0 + XC[0], Y0 + y1], [3, X0 + XM, Y0 + y1]])
add(t='mcset', h='111909', set={'SecondLine': '(%%C32)'})
y2 = L[1] + 2200
add(t='spmove', h='111907', items=[[0, X0 + 3748, Y0 + y2], [1, X0 + XC[1], Y0 + y2], [2, X0 + XC[0], Y0 + y2]])
add(t='mcset', h='111907', set={'SecondLine': '(%%C32)'})
y3 = L[1] + 3000
add(t='spmove', h='111908', items=[[0, X0 + 3899, Y0 + y3], [1, X0 + XM, Y0 + y3], [2, X0 + XM, Y0 + y3], [3, X0 + XM, Y0 + y3]])
add(t='mcset', h='111908', set={'SecondLine': '(%%C32)'})
add(t='spmove', h='111912', items=[[1, X0 + XM, Y0 + TOP], [0, X0 + XM + 200, Y0 + L[2] + 236]])
NOTE = dict(scale=50, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')
for y, xs in ((SPL[0][0], XC), (SPL[2][0], XC)):
    add(t='note', l1='Н1', l2='(%%C32)', origin=W(CR + 420, y + 260), targets=[W(xs[1] + NW / 2, y), W(XM + NW / 2, y + 600)], **NOTE)
p, (n1, nm, n3), s = CG.storey_hoops(LZ[1], LZ[2] - BEAM)
add(t='note', l1='Х1;Х2', l2='', origin=W(CR + 420, L[0] + p[n1 + 3] + 100), targets=[W(CR - 40, L[0] + p[n1 + 1]), W(CR - 40, L[0] + p[n1 + nm])], **NOTE)
# knots: node at -0.100 (meshes), splice detail «А»
c = W(XM, L[1] - BEAM / 2); add(t='mcset', h='1118C7', set={'Center': c, 'Rack': [c[0] - 880, c[1] - 825], 'Knot': 'Б'})
c = W(XC[1], SPL[0][0]); add(t='mcset', h='1118D0', set={'Center': c, 'Rack': [c[0] + 345, c[1] - 369], 'Knot': 'А'})

# ---- erase the rest of the template elevation ----
OLD = [r['h'] for r in R if r['x1'] < 8200 and r['y0'] > 8000 and r['h'] not in keep]
TPL = {'1111C5', '111219', '111182'}
add(t='erase', h=[h for h in OLD if h not in TPL])
add(t='erase', h=[h for h in TPL if h not in keep])
add(t='save')
json.dump(ops, open('ops/t41a.json', 'w'), ensure_ascii=False)
print(len(ops), 'ops, erase', len(OLD))
if '--run' in sys.argv: print(gx.run(ops, 't41a')[-2500:])
