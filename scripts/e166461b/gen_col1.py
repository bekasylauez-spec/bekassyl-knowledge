# Км-1 sheet 4.1 — phase A: elevation, rebuilt from the imported analog «Колонна Км-1.1» (Онкоцентр 4.1).
# Sheet-relative coords (frame origin X0,Y0). Analog column was at x 7787..8387, base y 20117 (-4.350).
import json, sys, math
import gx

X0, Y0 = 706779.0, 455939.0
R = json.load(open('w/k41_list.json'))
ops = []
def add(**k): ops.append(k); return k
def W(x, y): return [X0 + x, Y0 + y]

# ---- column data (Км-1) ----
B = 20117.0                       # -4.650
LEV = [(-4650, B), (-100, B + 4550), (3950, B + 8600)]
TOP = B + 8600                    # +3.950
FMB = B - 700                     # Фм bottom -5.350
CX0, CX1 = 7787.0, 8287.0         # 500 column
XC = [CX0 + 56, CX1 - 56]         # Ø32 corner bars (cover 40 + 16)
XM = (CX0 + CX1) / 2              # Ø20 mid bar
BAR0, BAR1 = FMB + 50, TOP - 20
BEAM_H = 550

keep = set()
def K(h): keep.add(h); return h

# ---- level marks: value + position ----
add(t='levelval', h=K('10B2B8'), old='-4,350', value='-4,650', tag='K41_LV0')
add(t='movegrp', h=[K('10B2B9')], d=[0, LEV[1][1] - 24387]); add(t='levelval', h='10B2B9', old='-0,080', value='-0,100', tag='K41_LV1')
add(t='movegrp', h=[K('10B2D6')], d=[0, LEV[2][1] - 28287]); add(t='levelval', h='10B2D6', old='+3,820', value='+3,950', tag='K41_LV2')

# ---- left dims ----
add(t='dimpts', h=K('10B2BB'), p1=W(6886, LEV[1][1]), p2=W(6886, B))
add(t='dimpts', h=K('10B2D7'), p1=W(6886, LEV[1][1]), p2=W(6886, TOP))
add(t='dimpts', h=K('10B2C8'), p1=W(6886, TOP), p2=W(6886, B))
add(t='dimpts', h=K('10B37C'), p1=W(6669, B), p2=W(6669, FMB))

# ---- bottom dims (bar positions) ----
add(t='dimpts', h=K('10B318'), p1=W(CX0, B), p2=W(CX0 + 40, B))
add(t='dimpts', h=K('10B329'), p1=W(CX1, B), p2=W(CX1 - 40, B))
add(t='dimpts', h=K('10B33A'), p1=W(CX0 + 40, B), p2=W(XM, B))
add(t='dimpts', h=K('10B349'), p1=W(CX1 - 40, B), p2=W(XM, B))

# ---- Фм (700) + подготовка ----
add(t='spmove', h=K('10B2B3'), items=[[2, X0 + 6669, Y0 + FMB], [3, X0 + 9669, Y0 + FMB]])   # pts: (9669,B)(6669,B)(6669,19317)(9669,19317)
add(t='spmove', h=K('10B2B5'), items=[[0, X0 + 6669, Y0 + FMB - 100], [1, X0 + 9669, Y0 + FMB - 100], [2, X0 + 9669, Y0 + FMB], [3, X0 + 6669, Y0 + FMB]])
add(t='hatch', pat='ANSI36', sc=30, ang=0, layer='Размеры', loops=[[W(6669, FMB), W(9669, FMB), W(9669, B), W(6669, B)]], tag='K41_HFM')
add(t='hatch', pat='AR-CONC', sc=1, ang=0, layer='Размеры', loops=[[W(6669, FMB - 100), W(9669, FMB - 100), W(9669, FMB), W(6669, FMB)]], tag='K41_HPD')
for h in ('10B2B6', '10B2B7'):
    x = 6669 if h == '10B2B6' else 9669
    add(t='spmove', h=K(h), items=[[0, X0 + x, Y0 + FMB - 100], [1, X0 + x, Y0 + (FMB - 100 + B) / 2], [2, X0 + x, Y0 + B], [3, X0 + x, Y0 + B]])

# ---- Б.О. axis ----
add(t='spmove', h=K('10B5D3'), items=[[0, X0 + XM, Y0 + TOP + 266]])

# ---- column outline, bars ----
add(t='pl', p=[W(CX0, B), W(CX1, B), W(CX1, TOP), W(CX0, TOP)], closed=True, layer='Размеры', tag='K41_COL')
for x in XC:
    add(t='lineset', h='10B43C', s=W(x, B), e=W(x, BAR1), layer='диам32', lw=40, tag='K41_B1_%d' % x)
    add(t='lineset', h='10B389', s=W(x, BAR0), e=W(x, B), tag='K41_B1f_%d' % x)
add(t='lineset', h='10B43C', s=W(XM, B), e=W(XM, BAR1), layer='диам20', tag='K41_B2')
add(t='lineset', h='10B389', s=W(XM, BAR0), e=W(XM, B), tag='K41_B2f')

# ---- hoops: X + 2X + X per storey, first/last 50 from the zone boundary ----
def hoops(a, b):
    H = b - a; X = round(H / 4 / 50) * 50
    z = [(a, a + X, 100), (a + X, b - X, 200), (b - X, b, 100)]
    pos = []
    for (u, v, s) in z:
        p = u + 50
        while p <= v - 50 + 1e-6: pos.append(p); p += s
    return pos, z
HP = []; ZONES = []
for i in range(2):
    p, z = hoops(LEV[i][1], LEV[i + 1][1]); HP += p; ZONES += z
# draw first and last hoop of every zone (analog draws the zone ends)
for (u, v, s) in ZONES:
    inz = [p for p in HP if u <= p <= v]
    for p in (inz[0], inz[-1]):
        add(t='lineset', h='10B43C', s=W(CX0 + 20, p), e=W(CX1 - 20, p), layer='диам8', tag='K41_H_%d' % p)
# chain on the right: base→first, runs of equal steps, last→level
pts = []
for i in range(2):
    a, b = LEV[i][1], LEV[i + 1][1]
    ps = [p for p in HP if a < p < b]
    pts.append([a] + ps + [b])
DL = 10702
for seq in pts:
    d = [seq[k + 1] - seq[k] for k in range(len(seq) - 1)]
    segs = [(0, 1)]
    k = 1
    while k < len(d) - 1:
        m = k
        while m + 1 < len(d) - 1 and abs(d[m + 1] - d[k]) < 1e-6: m += 1
        segs.append((k, m + 1)); k = m + 1
    segs.append((len(d) - 1, len(d)))
    for (i0, i1) in segs:
        y1, y2, n = seq[i0], seq[i1], i1 - i0
        o = dict(t='dim', h='10B3AC', p1=W(CX1, y1), p2=W(CX1, y2), dl=W(DL, (y1 + y2) / 2), rot=math.pi / 2, tag='K41_HD_%d' % y1)
        o['txt'] = ('%dх%d' % (round(d[i0]), n)) if n > 1 else ''
        add(**o)

# ---- beam stubs at the node levels (rectangle + break line) ----
for lv in (LEV[1][1], LEV[2][1]):
    add(t='pl', p=[W(CX1, lv), W(CX1 + 600, lv), W(CX1 + 600, lv - BEAM_H), W(CX1, lv - BEAM_H)], closed=False, layer='Размеры', tag='K41_BM_%d' % lv)
    add(t='clone', h='10B30F', base=W(8987, 24387), to=W(CX1 + 600, lv), tag='K41_BK_%d' % lv)
    add(t='spmove', h='K41_BK_%d' % lv, items=[[0, X0 + CX1 + 600, Y0 + lv - BEAM_H - 75], [1, X0 + CX1 + 600, Y0 + lv - BEAM_H / 2], [2, X0 + CX1 + 600, Y0 + lv + 75], [3, X0 + CX1 + 600, Y0 + lv + 75]])

# ---- top П elements (Ск1 over Ø32, legs 320) + welds + callout ----
add(t='pl', p=[W(XC[0], BAR1 - 320), W(XC[0], BAR1), W(XC[1], BAR1), W(XC[1], BAR1 - 320)], layer='диам16', tag='K41_SK')
add(t='clone', h=K('10B486'), base=W(7807, 38267), to=W(XC[0] - 21, BAR1 - 320), tag='K41_W1'); add(t='spmove', h='K41_W1', items=[[0, X0 + XC[0] - 21, Y0 + BAR1 - 320], [1, X0 + XC[0] - 21, Y0 + BAR1 - 1]])
add(t='clone', h=K('10B487'), base=W(8267, 38267), to=W(XC[1] + 21, BAR1 - 320), tag='K41_W2'); add(t='spmove', h='K41_W2', items=[[0, X0 + XC[1] + 21, Y0 + BAR1 - 320], [1, X0 + XC[1] + 21, Y0 + BAR1 - 1]])
add(t='movegrp', h=[K('10C8DE')], d=[XM - 8096 + 0, BAR1 - 38467]); add(t='mcset', h='10C8DE', set={'FirstLine': 'Ск1;Ск2'})

# ---- bar callouts ----
add(t='note', l1='1', l2='∅32', origin=W(8800, 21800), targets=[W(x, 21800) for x in XC], scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры', tag='K41_N1')
add(t='note', l1='2', l2='∅20', origin=W(8800, 26300), targets=[W(XM, 26300)], scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры', tag='K41_N2')

# ---- node knots (mesh С1) ----
add(t='movegrp', h=[K('10BD84')], d=[XM - 8207, LEV[1][1] - BEAM_H / 2 - 24325]); add(t='mcset', h='10BD84', set={'Knot': 'А'})
add(t='movegrp', h=[K('10BD85')], d=[XM - 8047, LEV[2][1] - BEAM_H / 2 - 31971]); add(t='mcset', h='10BD85', set={'Knot': 'А'})

# ---- section marks: 1-1 in storey 1, 2-2 above the top ----
add(t='movegrp', h=[K('10C8E3')], d=[0, 22900 - 22453 - 0])
add(t='movegrp', h=[K('10C8E8')], d=[0, TOP + 500 - 38883]); add(t='secset', h='10C8E8', word='2')

# ---- title ----
add(t='settext', h=K('10BC3F'), s='{\\LКолонна Км-1}')
add(t='movegrp', h=['10BC3F'], d=[0, TOP + 1700 - 39702])

# ---- erase the rest of the analog elevation ----
er = []
for r in R:
    if r['x1'] < 12700 and r['y0'] > 16400 and r['h'] not in keep and r['t'] not in ('SPDSRELATIONMARK',):
        if r['t'] == 'SPDSCONSTRUCTIONLINE': continue
        er.append(r['h'])
TPL={'10B43C','10B389','10B30F','10B3AC'}
ops.insert(0, dict(t='erase', h=[h for h in er if h not in TPL]))
ops.append(dict(t='erase', h=sorted(TPL)))
ops.append(dict(t='save'))
for h in ('10B2E4', '10B2F2', '10B300'): pass
json.dump(ops, open('ops/k41a.json', 'w'), ensure_ascii=False)
print(len(ops), 'ops, erase', len(er), 'hoops', len(HP))
for s in pts: print(s)
if '--run' in sys.argv: print(gx.run(ops, 'k41a')[-2500:])
