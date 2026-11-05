# См-9 sheet 5.37 «Разрез 1-1 (Армирование) М1:50» (analog 4.31, already stretched by sm9_elev): basement group 0.
# Dots / hoops Х1 only in the free-end edge zones / zone notes with polyline fans / Ск + straight-bar notes / bottom chains.
import sys, json; sys.path.insert(0, 'wl'); from common import *
X, Y = 2543100.0, 455939.0; BX = 41455.0
PX = lambda x: X + BX + 2 * (x - 14750)                        # wall x -> absolute section x (1:50)
V = json.load(open('wl/sm9_vert.json', encoding='utf-8')); H = json.load(open('wl/sm9_hor.json', encoding='utf-8'))
D = V['D']; LAB = V['LABELS']; HD = H['HD']; HP = {tuple(int(v) for v in k.split('_')): p for k, p in H['POS'].items()}; HCK = {int(k): v for k, v in H['CKS'].items()}
R = json.load(open('w/r9s.json')); N = {n['h']: n for n in json.load(open('w/n9s.json'))}
WL = 32452.0; YT = 32308.0; YS = 31291.0                       # wall centre line, dot tops, shelf line of the zone notes
gi = 0; d0, st0 = HD[0]; LEG = {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}[d0]
ops = []; er = []
# dots
dots = [r for r in R if r['t'] == 'INSERT' and r['lay'].startswith('диам')]
er += [r['h'] for r in dots]; td = dots[0]; dcx, dcy = (td['x0'] + td['x1']) / 2, (td['y0'] + td['y1']) / 2
ops.append(dict(t='clone', h=td['h'], base=[0, 0], to=[0, -300000], tag='S9D'))
for i in range(2):
    for z in D[i][gi]:
        for xb in z[5]: ops.append(dict(t='clone', h='S9D', base=[0, 0], to=[PX(xb) - X - dcx, WL - dcy + 300000], layer='диам%d' % z[3]))
# hoops: right-end ones (at the cross walls) and their «Х1;Х2» notes away; left (free end) two hoops over the edge zone bars
er += ['278302', '2782F1', '278354', '278349', '278379', '27837C']
HOOPS = {0: ['2782C7', '2782E6'], 1: ['27832B', '27833E']}
Rh = {r['h']: r for r in R}
for i, hs in HOOPS.items():
    z = D[i][gi][0]; assert z[0] == 'L'
    for h, xc in zip(hs, (z[1] + 100, z[1] + 300)):
        r = Rh[h]; cx = (r['x0'] + r['x1']) / 2
        ops.append(dict(t='move', h=[h], d=[PX(xc) - X - cx, 0]))
ops.append(dict(t='spmove', h='278377', items=[[1, PX(D[0][gi][0][1] + 180), Y + 32633], [2, PX(D[0][gi][0][1] + 380), Y + 32633]]))
ops.append(dict(t='spmove', h='27837A', items=[[1, PX(D[1][gi][0][1] + 180), Y + 32633], [2, PX(D[1][gi][0][1] + 380), Y + 32633]]))
# horizontal bars: U (Ск) only at the free left end, leg = lap; top bar straight into the cross wall
for h, x0 in (('278293', 15225 + 20), ('278295', 20375 + 20)):
    ops.append(dict(t='spmove', h=h, items=[[0, PX(x0) + 2 * LEG, Y + 32623]]))
for h, xe in (('278294', 18005), ('278296', 22855)):
    ops.append(dict(t='spmove', h=h, items=[[k, PX(xe), Y + 32662] for k in (2, 3, 4, 5)]))
# straight-bar note: «11 (Ø10)» at the left end -> Ск; new note right of each piece for the straight bars
for h, i, (a, b) in (('27837D', 0, (15225, 18025)), ('27837E', 1, (20375, 22875))):
    ops.append(dict(t='mcset', h=h, set={'FirstLine': 'Ск%d' % HCK[d0], 'SecondLine': '(%%%%C%d)' % d0}))
    fa = a + 50; fb = b - 20; p = HP[(d0, int(round(fb - fa, -1)))]
    tg = 'S9h%d' % i
    ops.append(dict(t='clone', h=h, base=[0, 0], to=[0, 0], tag=tg))
    ops.append(dict(t='spmove', h=tg, items=[[0, PX(b) + 600, Y + 33150], [1, PX(fb) - 300, Y + 32662]]))
    ops.append(dict(t='mcset', h=tg, set={'FirstLine': str(p), 'SecondLine': '(%%%%C%d)' % d0}))
# vertical zone notes: one per zone, polyline fan dots -> shelf (analog 1 ш.100)
er += ['27837F', '278381']
for i, nh in ((0, '278380'), (1, '278382')):
    zL, zM = D[i][gi]
    cx = zL[1] + 300                                              # edge zone: fan converges right of the zone centre, shelf to the left
    ops.append(dict(t='pl', p=[[PX(zL[1]), Y + YT], [PX(cx), Y + YS], [PX(cx) - 1500, Y + YS]], layer='Размеры'))
    ops.append(dict(t='pl', p=[[PX(zL[2]), Y + YT], [PX(cx), Y + YS]], layer='Размеры'))
    tg = 'S9z%d' % i
    ops.append(dict(t='clone', h=nh, base=[0, 0], to=[0, 0], tag=tg))
    ops.append(dict(t='spmove', h=tg, items=[[0, PX(cx) - 1500, Y + YS]]))
    ops.append(dict(t='mcset', h=tg, set={'FirstLine': LAB['%d|%d|L' % (i, gi)], 'SecondLine': 'ш.%d' % zL[4]}))
    m0, m1 = PX(zM[1]) + 500, PX(zM[2]) - 400
    ops.append(dict(t='pl', p=[[PX(zM[1]), Y + YT], [m0, Y + YS], [m1, Y + YS], [PX(zM[2]), Y + YT]], layer='Размеры'))
    ops.append(dict(t='spmove', h=nh, items=[[0, m0, Y + YS]]))
    ops.append(dict(t='mcset', h=nh, set={'FirstLine': LAB['%d|%d|M' % (i, gi)], 'SecondLine': 'ш.%d' % zM[4]}))
# bottom chains 50 | zone segments | 50
CH = [r for r in R if r['t'] == 'DIMENSION' and r['lay'] == '0_ANNOT_Dimensions' and abs(r['sp'][0][1] - 32202) < 5]
er += [r['h'] for r in CH]
ops.append(dict(t='clone', h=CH[0]['h'], base=[0, 0], to=[0, 0], tag='S9C'))
for i in range(2):
    zs = D[i][gi]; lo = zs[0][1] - 50; hi = zs[-1][2] + 50
    segs = [(lo, lo + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(hi - 50, hi, 50, 1)]
    segs = [s for s in segs if s[1] > s[0]]
    for k, (s0, s1, st, n_) in enumerate(segs):
        kw = dict(t='dim', h='S9C', p1=[PX(s0), Y + 32202], p2=[PX(s1), Y + 32202], dl=[PX((s0 + s1) / 2), Y + 30100], rot=0, txt=('%dх%d' % (st, n_)) if n_ > 1 else '')
        if 2 * (s1 - s0) < 650: kw['tx'] = [PX((s0 + s1) / 2), Y + 30100 - 330]
        ops.append(kw)
ops += [dict(t='erase', h=sorted(set(er))), dict(t='erase', h=['S9D', 'S9C']), dict(t='save')]
print('ops', len(ops), 'erase', len(set(er)))
if '--run' in sys.argv:
    out = gx.run(ops, 's92'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
