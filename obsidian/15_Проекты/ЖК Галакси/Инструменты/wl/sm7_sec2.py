# См-7 sheet 5.29 stage 2: our dots / hoops (Х1;Х2 only at the free-end edge zones, as in the spec 5.28) / bottom chains /
# axis dims / note texts from sm7_vert.json (D, LABELS) and sm7_hor.json (POS, CKS, HD). 1-1 basement (group 0), 2-2 floors (group 1).
import sys, json; sys.path.insert(0, 'wl'); from common import *
X, Y = 2149800.0, 455939.0; A0 = 8000.0
PX = lambda x: X + A0 + 2 * x
wx = lambda xa: (xa - A0) / 2
V = json.load(open('wl/sm7_vert.json', encoding='utf-8')); H = json.load(open('wl/sm7_hor.json', encoding='utf-8'))
D = V['D']; LAB = V['LABELS']; HD = H['HD']; HCK = {int(k): v for k, v in H['CKS'].items()}
R = json.load(open('w/r7r2.json')); N = json.load(open('w/n7r2.json'))
PCS = {0: [(0, -125, 22875)], 1: [(0, -125, 3175), (1, 5750, 17100), (2, 20375, 22875)]}
HPOS = {0: {0: 12}, 1: {0: 13, 1: 14, 2: 15}}
CKP = {0: [-125, 22875], 1: [-125, 3175, 5750, 17100, 20375]}           # Ск ends shown on 5.27
PLANS = [(38000, 0), (26696, 1)]
near = lambda r, wl: abs((r['y0'] + r['y1']) / 2 - wl) < 2600
ops = []; er = []
tdot = next(r for r in R if r['t'] == 'INSERT' and r['x1'] - r['x0'] < 60 and r['lay'].startswith('диам'))
thoop = next(r for r in R if r['t'] == 'INSERT' and r['lay'] == '0' and 350 < r['x1'] - r['x0'] < 430 and near(r, 26696))
tnh = next(n for n in N if n['l1'] == 'Х1;Х2')
tsk = next(n for n in N if n['l1'].startswith('Ск') and abs(n['pts'][0][1] - 26696) < 2600)
ops += [dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S7D'), dict(t='clone', h=thoop['h'], base=[0, 0], to=[0, -300000], tag='S7H')]
dcx, dcy = (tdot['x0'] + tdot['x1']) / 2, (tdot['y0'] + tdot['y1']) / 2; hcx, hcy = (thoop['x0'] + thoop['x1']) / 2, (thoop['y0'] + thoop['y1']) / 2
for wl, gi in PLANS:
    PIE = PCS[gi]
    def piece_of(x):
        for i, a, b in PIE:
            if a - 200 <= x <= b + 200: return i
    er += [r['h'] for r in R if r['t'] == 'INSERT' and near(r, wl) and (r['x1'] - r['x0'] < 60 and r['lay'].startswith('диам') or r['lay'] == '0' and 300 < r['x1'] - r['x0'] < 500)]
    er += [n['h'] for n in N if abs(n['pts'][0][1] - wl) < 2600 and n['l1'].startswith('Х')]
    for i, a, b in PIE:
        for z in D[i][gi]:
            for xb in z[5]: ops.append(dict(t='clone', h='S7D', base=[0, 0], to=[PX(xb) - X - dcx, wl - dcy + 300000], layer='диам%d' % z[3]))
            if gi and z[0] in ('L', 'R'):                     # hoops Х1;Х2 in the free-end edge zone (two, ш.200 in height)
                hx = [z[1] + 100, z[1] + 300]
                for x in hx: ops.append(dict(t='clone', h='S7H', base=[0, 0], to=[PX(x) - X - hcx, wl - hcy + 300000]))
                tg = 'S7n%d' % len(ops); ox = PX(z[1] + (450 if z[0] == 'L' else -650))
                ops.append(dict(t='clone', h=tnh['h'], base=[0, 0], to=[0, 0], tag=tg))
                ops.append(dict(t='spmove', h=tg, items=[[0, ox, Y + wl + 1501]] + [[k + 1, PX(x), Y + wl + 180] for k, x in enumerate(hx[:len(tnh['pts']) - 1])]))
    seen = set(); notes_ck = set()
    for n in N:
        if abs(n['pts'][0][1] - wl) > 2600 or n['h'] in er: continue
        tg_ = [wx(p[0]) for p in n['pts'][1:]]; mx = sum(tg_) / len(tg_); i = piece_of(mx); below = n['pts'][0][1] < wl
        if i is None: er.append(n['h']); continue
        if below:
            zs = D[i][gi]; z = min(zs, key=lambda z: abs((z[1] + z[2]) / 2 - mx))
            if (i, z[0]) in seen: er.append(n['h']); continue
            seen.add((i, z[0]))
            ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': LAB['%d|%d|%s' % (i, gi, z[0])], 'SecondLine': 'ш.%d' % z[4]}))
            ops.append(dict(t='spmove', h=n['h'], items=[[k, PX((z[1] + z[2]) / 2 + (k - 1) * min(150, (z[2] - z[1]) / 3)), Y + wl] for k in range(1, len(n['pts']))]))
        elif n['l1'].startswith('Ск'):
            e = min(CKP[gi], key=lambda e: abs(e - mx))
            if abs(e - mx) > 400 or e in notes_ck: er.append(n['h']); continue
            notes_ck.add(e); d = HD[0 if gi == 0 else 1][0]
            ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': 'Ск%d' % HCK[d], 'SecondLine': '(%%%%C%d)' % d}))
        elif n['l1'][:1].isdigit():
            st = HD[0 if gi == 0 else 1][1]
            ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(HPOS[gi][i]), 'SecondLine': 'ш.%d' % st}))
    for e in CKP[gi]:                                      # Ск ends without a note: clone one
        if e in notes_ck: continue
        d = HD[0 if gi == 0 else 1][0]; tg = 'S7k%d' % len(ops); xe = e + (20 if e in (-125, 22875) else (50 if e in (3175, 5750, 17100, 20375) else 0)) * (1 if e < 11000 else -1)
        ops.append(dict(t='clone', h=tsk['h'], base=[0, 0], to=[0, 0], tag=tg))
        ops.append(dict(t='spmove', h=tg, items=[[0, PX(xe) - (900 if e > 11000 else -300), Y + wl + 528], [1, PX(xe), Y + wl]]))
        ops.append(dict(t='mcset', h=tg, set={'FirstLine': 'Ск%d' % HCK[d], 'SecondLine': '(%%%%C%d)' % d}))
    for i, a, b in PIE:
        for z in D[i][gi]:
            if (i, z[0]) in seen: continue
            src = next(n for n in N if abs(n['pts'][0][1] - wl) < 2600 and n['pts'][0][1] < wl and n['h'] not in er)
            tg = 'S7z%d' % len(ops); xc = (z[1] + z[2]) / 2
            ops.append(dict(t='clone', h=src['h'], base=[0, 0], to=[0, 0], tag=tg))
            ops.append(dict(t='spmove', h=tg, items=[[0, PX(xc) + 300, src['pts'][0][1] + Y]] + [[k, PX(xc), Y + wl] for k in range(1, len(src['pts']))]))
            ops.append(dict(t='mcset', h=tg, set={'FirstLine': LAB['%d|%d|%s' % (i, gi, z[0])], 'SecondLine': 'ш.%d' % z[4]}))
    # bottom chain
    CH = [r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and abs(r['sp'][0][1] - (wl - 250)) < 30 and -3300 < r['sp'][2][1] - wl < -2700]
    er += [r['h'] for r in CH]
    y1, ydl = wl - 250, wl - 3085
    ops.append(dict(t='clone', h=CH[0]['h'], base=[0, 0], to=[0, 0], tag='S7C%d' % gi))
    for i, a, b in PIE:
        zs = D[i][gi]; lo = zs[0][1] - 50; hi = zs[-1][2] + 50
        segs = [(lo, lo + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(hi - 50, hi, 50, 1)]
        for k, (s0, s1, st, n_) in enumerate(segs):
            kw = dict(t='dim', h='S7C%d' % gi, p1=[PX(s0), Y + y1], p2=[PX(s1), Y + y1], dl=[PX((s0 + s1) / 2), Y + ydl], rot=0, txt=('%dх%d' % (st, n_)) if n_ > 1 else '')
            if 2 * (s1 - s0) < 650: kw['tx'] = [PX((s0 + s1) / 2), Y + ydl - 330 - (330 if k % 2 else 0)]
            ops.append(kw)
    ops.append(dict(t='erase', h=['S7C%d' % gi]))
    # axis dims
    AD = sorted([r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and abs(r['sp'][0][1] - wl) < 3500 and -3100 < r['sp'][0][1] - wl < -2600], key=lambda r: abs(r['sp'][1][0] - r['sp'][0][0]))
    if AD:
        tot = AD[-1]; ch = AD[:-1]; ya = ch[0]['sp'][0][1] if ch else tot['sp'][0][1]; ych = ch[0]['sp'][2][1] if ch else tot['sp'][2][1] + 700
        ops.append(dict(t='dimpts', h=tot['h'], p1=[PX(0), Y + tot['sp'][0][1]], p2=[PX(22750), Y + tot['sp'][0][1]], dl=[PX(11375), Y + tot['sp'][2][1]])); ops.append(dict(t='dimdef', h=[tot['h']]))
        for r, (a, b) in zip(ch, ((0, 5000), (5000, 14750), (14750, 22750))):
            ops.append(dict(t='dimpts', h=r['h'], p1=[PX(a), Y + ya], p2=[PX(b), Y + ya], dl=[PX((a + b) / 2), Y + ych])); ops.append(dict(t='dimdef', h=[r['h']]))
        er += [r['h'] for r in ch[3:]]
ops += [dict(t='erase', h=sorted(set(er))), dict(t='erase', h=['S7D', 'S7H']), dict(t='save')]
print('ops', len(ops), 'erase', len(set(er)))
if '--run' in sys.argv:
    out = gx.run(ops, 's72'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
