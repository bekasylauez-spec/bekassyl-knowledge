# Км-1: main bars 8Ø22 (max total As 27.32 cm2 / 8 = 3.42 -> Ø22 3.80), накладки Н4 (Ø22, L220), Ск legs 220.
import json, sys, gx
X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
ops = []
def add(**k): ops.append(k)
D = 22.0; e = 40 + D / 2                      # bar centre from the face
CX, b = 4103.0, 500.0
XC = [CX + e, CX + b - e]; XM = CX + b / 2
L = [9700.0, 14250.0, 18300.0]; TOP = L[2] - 20; HFM = 700.0
NAK, NW = 10 * D, 2 * D
SPL = [(L[0] + 600, XC), (L[0] + 1200, [XM]), (L[1] + 600, XC), (L[1] + 1200, [XM])]
# ---- elevation: bars, выпуски, накладки, П on top ----
add(t='erase', h=['11222B', '11222D', '11222F', '112231', '112232', '112233', '112234', '112235', '112236', '112237', '112238', '112239'])
for xs, y0 in ((XC, SPL[0][0]), ([XM], SPL[1][0])):
    for x in xs:
        add(t='pl', p=[W(x, y0), W(x, y0 + 4550)], layer='диам22', lw=40)
        add(t='clone', h='T41e_V4159', base=[0, 0], to=[0, 0], tag='T41d_V%d' % x)
        add(t='spmove', h='T41d_V%d' % x, items=[[0, X0 + x, Y0 + y0], [1, X0 + x, Y0 + L[0] - HFM + 50]])
for xs, y0 in ((XC, SPL[2][0]), ([XM], SPL[3][0])):
    for x in xs: add(t='pl', p=[W(x, y0), W(x, TOP)], layer='диам22', lw=40)
for y, xs in SPL:
    for x in xs:
        add(t='pl', p=[W(x - NW / 2, y - NAK / 2), W(x + NW / 2, y - NAK / 2), W(x + NW / 2, y + NAK / 2), W(x - NW / 2, y + NAK / 2)], closed=True, layer='диам22')
add(t='pl', p=[W(XC[0], TOP - 220), W(XC[0], TOP), W(XC[1], TOP), W(XC[1], TOP - 220)], layer='диам16', lw=40, tag='T41d_SK')
add(t='erase', h=['T41e_V4159', 'T41e_V4547', 'T41e_V4353'])
# callouts
for h in ('111909', '111907', '111908'): add(t='mcset', h=h, set={'SecondLine': '(%%C22)'})
y1 = L[0] + 2400; add(t='spmove', h='111909', items=[[1, X0 + XC[1], Y0 + y1], [2, X0 + XC[0], Y0 + y1], [3, X0 + XM, Y0 + y1]])
y2 = L[1] + 2200; add(t='spmove', h='111907', items=[[1, X0 + XC[1], Y0 + y2], [2, X0 + XC[0], Y0 + y2]])
for h, y in (('112360', SPL[0][0]), ('112361', SPL[2][0])):
    add(t='mcset', h=h, set={'FirstLine': 'Н4', 'SecondLine': '(%%C22)'})
    add(t='spmove', h=h, items=[[1, X0 + XC[1] + NW / 2, Y0 + y], [2, X0 + XM + NW / 2, Y0 + y + 600]])
add(t='mcset', h='1118D0', set={'Center': W(XC[1], SPL[0][0])})
# ---- sections: bars to 51 mm from the faces (x2), diamond hoop through the mid bars ----
K = 2.0
for tag, ox, oy in (('T41s1_', 9314.0, 17588.0), ('T41s2_', 13824.0, 17641.0)):
    v_old = [56.0, 250.0, 444.0]; v_new = [e, 250.0, b - e]
    pts = [(i, j) for i in range(3) for j in range(3) if not (i == 1 and j == 1)]
    for k, (i, j) in enumerate(pts):
        dx = K * (v_new[i] - v_old[i]); dy = K * (v_new[j] - v_old[j])
        if dx or dy: add(t='movegrp', h=[tag + 'B%d' % k], d=[dx, dy])
ox, oy = 9314.0, 17588.0
add(t='movegrp', h=['1113D0'], d=[0, K * (e - 56)])
add(t='scalegrp', h=['1113D0'], s=(b - 2 * e) / (b - 112.0), base=W(ox + K * 250, oy + K * e))
# 2-2: П lines between the new bar centres
ox, oy = 13824.0, 17641.0
P = lambda x, y: W(ox + K * x, oy + K * y)
add(t='erase', h=['T41s2_K0', 'T41s2_K1', 'T41s2_K2', 'T41s2_K3'])
for i, (a, c) in enumerate((((e, e), (b - e, b - e)), ((e, b - e), (b - e, e)), ((b / 2, b - e), (b - e, b / 2)), ((e, b / 2), (b / 2, e)))):
    add(t='pl', p=[P(*a), P(*c)], layer='диам16', lw=40, tag='T41s2_K%d' % i)
# ---- tables ----
m = gx.tagmap(); SP, ST = '113BFB', '113D32'
add(t='tset', h=SP, cells=[[5, 3, '22'], [6, 3, '22'], [7, 3, '22'], [9, 0, 'Н4'], [9, 3, '22'], [9, 9, '220'], [3, 9, '720'], [4, 9, '1000']])
add(t='tset', h=ST, cells=[[5, 6, '%%C22']])
for h, s in (('11172F', '220'), ('111732', '220'), ('111737', '720'), ('111745', '220'), ('111744', '560'), ('111748', '220'), ('11174D', '1000')):
    add(t='settext', h=h, s=s)
add(t='tdump', h=SP); add(t='tdump', h=ST); add(t='save')
json.dump(ops, open('ops/t41d.json', 'w'), ensure_ascii=False)
if '--run' in sys.argv:
    print(gx.run(ops, 't41d')[-300:])
    import os
    print('\n'.join(l[-120:] for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines() if l.startswith('R')))
