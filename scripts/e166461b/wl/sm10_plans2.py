# См-10 plan sheet 5.40 after sm10_plans: per plan (our geometry, x rel. our А/1 = A0) the analog dims are replaced by ours
# (piece chain at -1467, axis chain 5000|9750|8000 at -2506, total 22750 at -3206; 3-3 only Б-В), axes А/1 А Б В + wall axis «3»,
# cut outlines + hatches per piece, cross-wall stubs at the junctions, 3-3 cropped to the piece 15225..22875, titles, stamp.
import sys, json; sys.path.insert(0, 'wl'); from common import *
from lwin import lw
NX, Y = 2691600.0, 455939.0
W = lambda x, y: [x, Y + y]
PLANS = [  # (wall y on the sheet, A0 abs x, pieces, junction stub x (below), name, axes)
    (25300, NX + 6600, [(-125, 7675), (15225, 22875)], [0, 7550, 15350, 22750], '1', [0, 5000, 14750, 22750]),
    (16500, NX + 6600, [(-125, 2775), (6175, 7675), (15225, 22875)], [0, 7550, 15350, 22750], '2', [0, 5000, 14750, 22750]),
    (7400, NX - 7100, [(15225, 22875)], [15350, 22750], '3', [14750, 22750])]
VAL = {0: 'А/1', 5000: 'А', 14750: 'Б', 22750: 'В'}
STUBS_UP = {0, 7550, 22750}                                     # stubs above the wall too (cross walls both sides); См-4 (15350) one side
ops = []; er = []; pre = []
for yw, A0, P, ST, nm, AXS in PLANS:
    R = lw(A0 - 9000, Y + yw - 4800, A0 + 25000, Y + yw + 4200)
    R = [r for r in R if r['ext'] and r['t'] != 'SPDSFORMAT']
    rel = lambda x: x - A0
    # templates
    dims = [r for r in R if r['t'] == 'DIMENSION']
    tlong = next(r['h'] for r in dims if r['lay'] == '0_ANNOT_Dimensions')
    taxis = next(r['h'] for r in dims if r['lay'] == '0')
    tshort = next(r['h'] for r in dims if r['lay'] == 'Размеры')
    hat = next(r['h'] for r in R if r['t'] == 'HATCH')
    outl = next(r['h'] for r in R if r['t'] == 'LWPOLYLINE' and r['lay'] == '0' and abs(r['ext'][3] - r['ext'][1] - 250) < 3)
    stub = next(r for r in R if r['t'] == 'INSERT' and r['lay'] == 'Размеры' and abs(r['ext'][3] - r['ext'][1] - 728) < 5)
    stub_dn = (stub['ext'][3] - Y - yw) < 0
    tg = 'P10_%s_' % nm
    for k, h in (('L', tlong), ('A', taxis), ('S', tshort), ('H', hat), ('O', outl)):
        pre.append(dict(t='clone', h=h, base=[0, 0], to=[0, 0], tag=tg + k))
    pre.append(dict(t='clone', h=stub['h'], base=[0, 0], to=[0, 0], tag=tg + 'T'))
    scx = (stub['ext'][0] + stub['ext'][2]) / 2; scy = stub['ext'][1] if stub_dn else stub['ext'][1]
    # erase analog dims, hatches, outlines, stubs (rebuilt below); vertical axes not wanted
    er += [r['h'] for r in dims]
    er += [r['h'] for r in R if r['t'] == 'HATCH' or (r['t'] == 'LWPOLYLINE' and r['lay'] == '0' and abs(r['ext'][3] - r['ext'][1] - 250) < 3)]
    er += [r['h'] for r in R if r['t'] == 'INSERT' and r['lay'] == 'Размеры' and abs(r['ext'][3] - r['ext'][1] - 728) < 5]
    vax = [r for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and abs(r['sp'][0][0] - r['sp'][1][0]) < 1]
    hax = [r for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and abs(r['sp'][0][1] - r['sp'][1][1]) < 1]
    for r in hax: ops.append(dict(t='axis', h=r['h'], s=[A0 + 22750, Y + yw], e=[A0 + (AXS[0] - 2029 if nm == '3' else -2029), Y + yw], val='3'))
    vax = sorted(vax, key=lambda r: r['sp'][0][0]); used = []
    for x in AXS:
        r = min([q for q in vax if q['h'] not in used], key=lambda q: abs(rel(q['sp'][0][0]) - x), default=None)
        if r is None: break
        used.append(r['h']); (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
        ops.append(dict(t='axis', h=r['h'], s=[A0 + x, sy], e=[A0 + x, ey], val=VAL[x]))
    er += [r['h'] for r in vax if r['h'] not in used]
    if len(used) < len(AXS):                                      # missing axis (analog 1-1 had no A): clone the first one
        src = next(r for r in vax if r['h'] in used)
        for x in AXS[len(used):] if False else [x for x in AXS if x not in [round(rel(q['sp'][0][0])) for q in vax if q['h'] in used]][:len(AXS) - len(used)]:
            t2 = tg + 'X%d' % x; (sx, sy), (ex, ey) = src['sp'][0], src['sp'][1]
            ops.append(dict(t='clone', h=src['h'], base=[0, 0], to=[0, 0], tag=t2))
            ops.append(dict(t='axis', h=t2, s=[A0 + x, sy], e=[A0 + x, ey], val=VAL[x]))
    # outlines + hatches
    for i, (a, b) in enumerate(P):
        lp = [W(A0 + a, yw - 125), W(A0 + b, yw - 125), W(A0 + b, yw + 125), W(A0 + a, yw + 125)]
        ops.append(dict(t='clone', h=tg + 'O', base=[0, 0], to=[0, 0], tag=tg + 'o%d' % i))
        ops.append(dict(t='spmove', h=tg + 'o%d' % i, items=[[k, p[0], p[1]] for k, p in enumerate(lp)]))
        ops.append(dict(t='clone', h=tg + 'H', base=[0, 0], to=[0, 0], tag=tg + 'h%d' % i))
        ops.append(dict(t='hatchfit', h=tg + 'h%d' % i, loops=[lp]))
    # stubs
    for x in ST:
        for up in ((False, True) if x in STUBS_UP else (False,)):
            dy_ = (yw + 125) - (stub['ext'][1] - Y) if up else (yw - 125 - 728) - (stub['ext'][1] - Y)
            o = dict(t='clone', h=tg + 'T', base=[scx, 0], to=[A0 + x, dy_])
            ops.append(o)
    # dims: piece chain (faces / bands / gaps), axis chain, total
    pts = sorted(set([p for ab in P for p in ab] + [x for x in ST if x != 15350 and P[0][0] - 1 <= x <= P[-1][1] + 1] +
                     [x - 125 for x in ST if x not in (15350,)] + [x + 125 for x in ST if x not in (15350,)] + ([15475] if 15350 in ST else [])))
    pts = [p for p in pts if P[0][0] - 1 <= p <= P[-1][1] + 1]
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        d = dict(t='dim', h=tg + ('L' if b - a >= 450 else 'S'), p1=W(A0 + a, yw - 125), p2=W(A0 + b, yw - 125), dl=W(A0 + (a + b) / 2, yw - 1467), rot=0, txt='')
        if b - a < 450: d['tx'] = W(A0 + (a + b) / 2 + (-260 if (k % 2 == 0) else 260), yw - 1467 - 330)
        ops.append(d)
    ach = [(AXS[k], AXS[k + 1]) for k in range(len(AXS) - 1)]
    for a, b in ach: ops.append(dict(t='dim', h=tg + 'A', p1=W(A0 + a, yw - 1600), p2=W(A0 + b, yw - 1600), dl=W(A0 + (a + b) / 2, yw - 2506), rot=0, txt=''))
    if len(AXS) > 2: ops.append(dict(t='dim', h=tg + 'A', p1=W(A0 + AXS[0], yw - 1600), p2=W(A0 + AXS[-1], yw - 1600), dl=W(A0 + 11375, yw - 3206), rot=0, txt=''))
    # 3-3: everything left of the piece away
    if nm == '3':
        er += [r['h'] for r in R if r['t'] not in ('MTEXT', 'SPDSCONSTRUCTIONLINE') and r['ext'][2] < A0 + 14000]
    ops.append(dict(t='erase', h=[tg + k for k in 'LASHOT']))
ops = pre + [dict(t='erase', h=sorted(set(er)))] + ops
m = gx.tagmap()
ops += [dict(t='settext', h='2A7723', s='{\LРазрез 2 - 2 (Опалубка) М1:100}'), dict(t='settext', h='2A75D6', s='{\LРазрез 3 - 3 (Опалубка) М1:100}'),
        dict(t='move', h=['2A75D6'], d=[10400, -800]),
        dict(t='settext', h=m['P10F_234804'], s='Разрезы 1-1, 2-2, 3-3 (Опалубка) стены См-10'), dict(t='settext', h=m['P10F_234807'], s='5.40')]
# titles and stamp
ops += [dict(t='save')]
print('erase', len(set(er)), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'p102'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
