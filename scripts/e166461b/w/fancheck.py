# fancheck: «Разрез (Армирование)» sheets — rule 05.11 (Bekassyl: «былықпай»). For every wall line (horizontal SPDS axis) of a sheet:
#  1) fan polylines (dot top -> shelf) do not cross each other and stay within one wall piece (+-600)
#  2) hoop inserts (layer 0, 300..500 wide) only within 700 of a piece end
#  3) exactly one horizontal axis line per wall line, 4) a stamp (logo / stamp block insert in the stamp box)
# usage: python w/fancheck.py X W H [X W H ...]      -> prints problems, TOTAL n
import sys, itertools; sys.path.insert(0, r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad\wl')
from common import *
from lwin import lw
from shapely.geometry import LineString
Y = 455939.0; tot = 0
a = [float(v) for v in sys.argv[1:]]
for X, W, H in zip(a[::3], a[1::3], a[2::3]):
    R = [r for r in lw(X - 5, Y - 900, X + W + 5, Y + H + 5) if r['ext']]
    bad = []
    HX = [r for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and abs(r['sp'][0][1] - r['sp'][1][1]) < 1]
    wls = sorted(set(round(r['sp'][0][1]) for r in HX))
    for wl in wls:
        n = sum(1 for r in HX if abs(r['sp'][0][1] - wl) < 2)
        if n != 1: bad.append('axis lines at y %d: %d' % (wl - Y, n))
        # wall pieces: outlines 250x2 thick (1:50) on the line
        pcs0 = sorted((r['ext'][0], r['ext'][2]) for r in R if r['t'] in ('LWPOLYLINE', 'LINE') and abs((r['ext'][1] + r['ext'][3]) / 2 - wl) < 30 and 480 < r['ext'][3] - r['ext'][1] < 520)
        pcs0 += sorted((r['ext'][0], r['ext'][2]) for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['ext'][3] - r['ext'][1] < 2 and abs(abs(r['ext'][1] - wl) - 250) < 3 and r['ext'][2] - r['ext'][0] > 400)
        pcs = []
        for a_, b_ in sorted(pcs0):                                   # wall face lines / outlines merged into pieces
            if pcs and a_ <= pcs[-1][1] + 5: pcs[-1] = (pcs[-1][0], max(pcs[-1][1], b_))
            else: pcs.append((a_, b_))
        fans = [r for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) >= 2 and any(abs(p[1] - (wl - 144)) < 3 for p in r['sp']) and any(-1700 < p[1] - wl < -500 for p in r['sp'])]
        for r in fans:
            xs = [p[0] for p in r['sp'] if abs(p[1] - (wl - 144)) < 3]
            if pcs and not any(a_ - 600 <= min(xs) and max(xs) <= b_ + 600 for a_, b_ in pcs): bad.append('fan %s leaves its piece' % r['h'])
        for r1, r2 in itertools.combinations(fans, 2):
            if LineString(r1['sp']).crosses(LineString(r2['sp'])): bad.append('fans %s x %s cross' % (r1['h'], r2['h']))
        hoops = [r for r in R if r['t'] == 'INSERT' and r['lay'] == '0' and 300 < r['ext'][2] - r['ext'][0] < 500 and abs((r['ext'][1] + r['ext'][3]) / 2 - wl) < 30]
        ends = [e for ab in pcs for e in ab]
        for r in hoops:
            cx = (r['ext'][0] + r['ext'][2]) / 2
            if ends and min(abs(cx - e) for e in ends) > 1700: bad.append('hoop %s in the middle (x %d)' % (r['h'], cx - X))
    stamp = [r for r in R if r['t'] == 'INSERT' and r['ext'][0] > X + W - 21000 and r['ext'][3] < Y + 6500 and (r['lay'] == '0' or r['lay'] == 'Размеры') and r['ext'][2] - r['ext'][0] > 3000]
    slines = [r for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['ext'][0] > X + W - 21000 and r['ext'][3] < Y + 6500]
    if not stamp and len(slines) < 20: bad.append('no stamp (logo / block / lines)')
    print('== %d  wall lines %d  problems %d' % (X, len(wls), len(bad)))
    for b in bad[:15]: print('  ', b)
    tot += len(bad)
print('TOTAL', tot)
