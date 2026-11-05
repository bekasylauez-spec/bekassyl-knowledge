# Column elevation at 1:50 on a 1:100 sheet (geometry x2, dims dimlfac 0.5, annotations at sheet size).
# Rebuilds the Км-1 elevation of sheet 4.1 from the objects already there (reuses level marks, knots, sections, dims).
import json, math, sys
import gx, colhoops as CH

X0, Y0 = 706779.0, 455939.0
S = 2.0
BX, BY = 7787.0, 20500.0                 # column left face / -4.650 on the sheet
b = 500.0; H = 8600.0; HFM = 700.0; HPD = 100.0; BEAM = 550.0
LEVZ = [0.0, 4550.0, 8600.0]               # from -4.650
LEVV = ['-4,650', '-0,100', '+3,950']
XC = [56.0, b - 56.0]; XM = b / 2
LF = 1.0 / S
def g(x, z): return [X0 + BX + S * x, Y0 + BY + S * z]          # model mm -> world
def W(x, y): return [X0 + x, Y0 + y]                             # sheet rel -> world
TOPY = BY + S * H

R = json.load(open('w/k41_list2.json'))
m = gx.tagmap(); inv = {v.upper(): k for k, v in m.items()}
REUSE = {'10B2BB', '10B2C8', '10B2D7', '10B37C', '10B318', '10B329', '10B33A', '10B349', '10B2B6', '10B2B7', '10B5D3',
         '10CD04', '10D1E3', '10D1E4', '10BD84', '10BD85', '10C8DE', '10C8E3', '10C8E8', '10BC3F', '10B2BA', '10CE3F', '10CE40'}
OLD = [r['h'] for r in R if r['x1'] < 13300 and r['y0'] > 16400 and r['h'].upper() not in REUSE]
ops = []
def add(**k): ops.append(k); return k
T = 'K41v_'

# ---- column, Фм, hatches ----
add(t='pl', p=[g(0, 0), g(b, 0), g(b, H), g(0, H)], closed=True, layer='Размеры', tag=T + 'COL')
FX0, FX1 = -600.0, b + 600.0
add(t='pl', p=[g(FX1, 0), g(FX0, 0), g(FX0, -HFM), g(FX1, -HFM)], closed=False, layer='Размеры', tag=T + 'FM')
add(t='pl', p=[g(FX0, -HFM), g(FX1, -HFM), g(FX1, -HFM - HPD), g(FX0, -HFM - HPD)], closed=False, layer='Размеры', tag=T + 'PD')
add(t='hatch', pat='ANSI36', sc=20, ang=0, layer='Размеры', loops=[[g(FX0, -HFM), g(FX1, -HFM), g(FX1, 0), g(FX0, 0)]], tag=T + 'HFM')
add(t='hatch', pat='AR-CONC', sc=1, ang=0, layer='Размеры', loops=[[g(FX0, -HFM - HPD), g(FX1, -HFM - HPD), g(FX1, -HFM), g(FX0, -HFM)]], tag=T + 'HPD')
for h, x in (('10B2B6', FX0), ('10B2B7', FX1)):
    p0, p1 = g(x, -HFM - HPD), g(x, 0)
    add(t='spmove', h=h, items=[[0, p0[0], p0[1]], [1, p0[0], (p0[1] + p1[1]) / 2], [2, p1[0], p1[1]], [3, p1[0], p1[1]]])

# ---- bars ----
z0, z1 = -HFM + 50, H - 20
for x in XC:
    add(t='lineset', h='K41_B1_7843', s=g(x, 0), e=g(x, z1), tag=T + 'B1_%d' % x)
    add(t='lineset', h='K41_B1f_7843', s=g(x, z0), e=g(x, 0), tag=T + 'B1f_%d' % x)
add(t='lineset', h='K41_B2', s=g(XM, 0), e=g(XM, z1), tag=T + 'B2')
add(t='lineset', h='K41_B1f_7843', s=g(XM, z0), e=g(XM, 0), tag=T + 'B2f')

# ---- hoops (zone ends) + right chain ----
for a, c in zip(LEVZ, LEVZ[1:]):
    p, (n1, n2, n3) = CH.storey(a, c)
    for z in sorted({p[0], p[n1], p[n1 + 1], p[n1 + n2], p[n1 + n2 + 1], p[-1]}):
        add(t='lineset', h='K41_H_20167', s=g(20, z), e=g(b - 20, z), tag=T + 'H_%d' % z)
P, segs = CH.chain(LEVZ)
DL = BX + S * b + 2415
col = 1
for (y1, y2, st, n) in segs:
    o = dict(t='dim', h='K41_HD_20167', p1=g(b, y1), p2=g(b, y2), dl=W(DL, BY + S * (y1 + y2) / 2), rot=math.pi / 2, lfac=LF,
             txt=('%dх%d' % (st, n)) if n > 1 else '', tag=T + 'HD_%d' % y1)
    fits = S * (y2 - y1) >= (len(o['txt'] or str(st)) * 0.85 * 250 + 300)
    if not fits:
        o['tx'] = W(DL + (500 if col == 1 else 880), BY + S * (y1 + y2) / 2 + (S * 25 if y1 == 0 else 0))
        col = 2 if col == 1 else 1
    else:
        col = 1
    add(**o)

# ---- left dims (reuse), bottom dims (reuse) ----
add(t='dimpts', h='10B2BB', p1=W(6886, BY + S * LEVZ[1]), p2=W(6886, BY), dl=W(5699, BY))
add(t='dimpts', h='10B2D7', p1=W(6886, BY + S * LEVZ[1]), p2=W(6886, TOPY), dl=W(5699, TOPY))
add(t='dimpts', h='10B2C8', p1=W(6886, TOPY), p2=W(6886, BY), dl=W(5013, BY))
add(t='dimpts', h='10B37C', p1=g(FX0, 0), p2=g(FX0, -HFM), dl=W(5699, BY))
DLB1 = BY - S * (HFM + HPD) - 600; DLB2 = DLB1 - 420
add(t='dimpts', h='10B318', p1=g(0, 0), p2=g(40, 0), dl=W(BX, DLB1))
add(t='dimpts', h='10B329', p1=g(b, 0), p2=g(b - 40, 0), dl=W(BX, DLB1))
add(t='dimpts', h='10B33A', p1=g(40, 0), p2=g(XM, 0), dl=W(BX, DLB2))
add(t='dimpts', h='10B349', p1=g(b - 40, 0), p2=g(XM, 0), dl=W(BX, DLB2))
add(t='dimset', h=['10B2BB', '10B2D7', '10B2C8', '10B37C', '10B318', '10B329', '10B33A', '10B349'], lfac=LF)
add(t='dimtx', h='10B318', at=W(BX - 330, DLB1 + 0))
add(t='dimtx', h='10B329', at=W(BX + S * b + 330, DLB1))
add(t='dimtx', h='10B33A', at=W(BX + S * 40 - 420, DLB2))
add(t='dimtx', h='10B349', at=W(BX + S * (b - 40) + 420, DLB2))

# ---- Б.О. axis ----
add(t='spmove', h='10B5D3', items=[[0, X0 + BX + S * XM, Y0 + TOPY + 266], [1, X0 + BX + S * XM, Y0 + DLB2 - 500]])

# ---- beam stubs at node levels ----
for zl in LEVZ[1:]:
    add(t='pl', p=[g(b, zl), g(b + 300, zl), g(b + 300, zl - BEAM), g(b, zl - BEAM)], closed=False, layer='Размеры', tag=T + 'BM_%d' % zl)
    add(t='clone', h='10B2B7', base=W(BX + S * FX1, BY - S * (HFM + HPD) / 2), to=g(b + 300, zl - BEAM / 2), tag=T + 'BK_%d' % zl)

# ---- П elements at the top, welds, callout ----
add(t='pl', p=[g(XC[0], z1 - 320), g(XC[0], z1), g(XC[1], z1), g(XC[1], z1 - 320)], layer='диам16', tag=T + 'SK')
for h, x, dx in (('10CE3F', XC[0], -21), ('10CE40', XC[1], 21)):
    a, c = g(x, z1 - 320), g(x, z1)
    add(t='spmove', h=h, items=[[0, a[0] + dx, a[1]], [1, c[0] + dx, c[1] - 1]])
tg = g(XM, z1); add(t='spmove', h='10C8DE', items=[[1, tg[0] - 80, tg[1]], [0, tg[0] + 300, tg[1] + 900]])

# ---- bar callouts (СПДС, oblique ticks on the bars) ----
for txt, l2, xs, z in (('1', '∅32', XC, 1600), ('2', '∅20', [XM], 6400)):
    add(t='note', l1=txt, l2=l2, origin=g(b + 560, z), targets=[g(x, z) for x in xs], scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')

# ---- node knots (mesh С1): centre on the node, ring around column + beam ----
for h, zl in (('10BD84', LEVZ[1]), ('10BD85', LEVZ[2])):
    c = g(XM, zl - BEAM / 2)
    add(t='mcset', h=h, set={'Center': [c[0], c[1]], 'Rack': [c[0] - 1100, c[1] - 1100], 'XRadius': 820, 'YRadius': 820, 'Knot': 'А'})

# ---- level marks: move to their levels (values fixed afterwards) ----
for h, zl, y0 in (('10CD04', 0, 20117), ('10D1E3', LEVZ[1], 24667), ('10D1E4', LEVZ[2], 28717)):
    add(t='movegrp', h=[h], d=[0, BY + S * zl - y0])
add(t='movegrp', h=['10B2BA'], d=[0, BY - 20117])

# ---- section marks: strokes close to the column, not across any dim chain ----
add(t='secset', h='10C8E3', pts=[W(BX - 1100, BY + S * 2300), W(BX + S * b + 1100, BY + S * 2300)], word='1')
add(t='secset', h='10C8E8', pts=[W(BX - 1100, TOPY + 900), W(BX + S * b + 1100, TOPY + 900)], word='2')

# ---- title ----
add(t='movegrp', h=['10BC3F'], d=[0, TOPY + 1900 - 30417])

add(t='erase', h=OLD)
add(t='save')
json.dump(ops, open('ops/k41v.json', 'w'), ensure_ascii=False)
print(len(ops), 'ops; erase', len(OLD))
if '--run' in sys.argv: print(gx.run(ops, 'k41v')[-3000:])
