# См-8 sheet 5.33 stage 2: dots / bottom chain / axis dims / note texts from our zones (wl/sm8_vert.json D, LABELS; sm8_hor POS, CKS)
# 1-1 basement (group 0), 2-2 floors (group 1, storey -0.100...+3.950), 3-3 top storey (group 3, piece 3 only, cropped to Б-В).
import sys, json, math; sys.path.insert(0, 'wl'); from common import *
X, Y = 2394600.0, 455939.0; A0 = 8000.0
PX = lambda x: X + A0 + 2 * x                                   # wall x -> absolute plan x (1:50)
wx = lambda xa: (xa - A0) / 2                                   # sheet-relative plan x -> wall x
V = json.load(open('wl/sm8_vert.json', encoding='utf-8')); H = json.load(open('wl/sm8_hor.json', encoding='utf-8'))
D = V['D']; LAB = V['LABELS']; HP = {tuple(int(v) for v in k.split('_')): p for k, p in H['POS'].items()}; HCK = {int(k): v for k, v in H['CKS'].items()}
HD = H['HD']
R = json.load(open('w/r8r2.json')); N = json.load(open('w/n8r2.json'))
PCS = {0: [(0, -125, 7675), (2, 15225, 18025), (3, 20575, 22875)], 1: [(0, -125, 2775), (1, 6175, 7675), (2, 15225, 18025), (3, 20575, 22875)], 3: [(2, 15225, 18025)]}
FACE = {(-125): 125, 7675: 7425, 18025: 17775, 22875: 22625}      # inner faces of the cross walls
HSTO = {0: 0, 1: 1, 3: 7}                                       # storey of the horizontal bars shown in each plan
PLANS = [(37446, 0), (25937, 1), (13291, 3)]
ops = []; er = []
tdot = next(r for r in R if r['t'] == 'INSERT' and r['x1'] - r['x0'] < 60 and r['lay'].startswith('диам'))
tx0 = (tdot['x0'] + tdot['x1']) / 2; ty0 = (tdot['y0'] + tdot['y1']) / 2
ops.append(dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S8D'))
def hpos(gi, i):                                                 # horizontal straight-bar position of piece i in that plan's storey
    s = HSTO[gi]; d, st = HD[s]
    a, b = next((a, b) for i_, a, b in PCS[gi] if i_ == i)
    fa = a + (20 if a in FACE else 50); fb = b - (20 if b in FACE else 50); Lb = int(round(fb - fa, -1))
    if Lb > 11700:
        nb = math.ceil((Lb - 980) / (11700.0 - 980)); Lb = int(math.ceil((Lb + (nb - 1) * {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100}[d]) / nb / 10.0) * 10)
    return HP.get((d, Lb)), d
for wl, gi in PLANS:
    near = lambda r: abs((r['y0'] + r['y1']) / 2 - wl) < 3200
    PIE = PCS[gi]
    def piece_of(x):
        for i, a, b in PIE:
            if a - 200 <= x <= b + 200: return i
    # dots
    er += [r['h'] for r in R if r['t'] == 'INSERT' and r['x1'] - r['x0'] < 60 and r['lay'].startswith('диам') and near(r)]
    for i, a, b in PIE:
        for z in D[i][gi]:
            for xb in z[5]: ops.append(dict(t='clone', h='S8D', base=[0, 0], to=[PX(xb) - X - tx0, wl - ty0 + 300000], layer='диам%d' % z[3]))
    # 3-3: only piece 3 between axes Б-В: everything of the other pieces / axes А/1, А away
    if gi == 3:
        for r in R:
            if not near(r) or r['t'] in ('SPDSFORMAT', 'MTEXT'): continue
            cx = wx((r['x0'] + r['x1']) / 2)
            if r['t'] == 'SPDSCONSTRUCTIONLINE':
                if abs(r['sp'][0][0] - r['sp'][1][0]) < 1 and wx(r['sp'][0][0]) < 14000: er.append(r['h'])
                continue
            if r['t'] == 'DIMENSION': continue
            if cx < 14000 or cx > 19000: er.append(r['h'])
    # notes
    seen = set()
    for n in N:
        if abs(n['pts'][0][1] - wl) > 2600: continue
        tg = [wx(p[0]) for p in n['pts'][1:]]; mx = sum(tg) / len(tg); i = piece_of(mx); below = n['pts'][0][1] < wl
        if i is None or (gi == 3 and i != 2): er.append(n['h']); continue
        if below:                                                 # vertical zone note -> nearest zone of the piece
            zs = D[i][gi]; z = min(zs, key=lambda z: abs((z[1] + z[2]) / 2 - mx))
            if (i, z[0]) in seen: er.append(n['h']); continue
            seen.add((i, z[0]))
            ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': LAB['%d|%d|%s' % (i, gi, z[0])], 'SecondLine': 'ш.%d' % z[4]}))
            ops.append(dict(t='spmove', h=n['h'], items=[[k, PX((z[1] + z[2]) / 2 + (k - 1) * min(150, (z[2] - z[1]) / 3)), Y + wl] for k in range(1, len(n['pts']))]))
        elif n['l1'].startswith('Ск'):
            if mx > (dict((i_, (a + b) / 2) for i_, a, b in PIE)[i]): er.append(n['h']); continue      # our Ск only at the left (free / A/1) end
            d = HD[HSTO[gi]][0]; ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': 'Ск%d' % HCK[d], 'SecondLine': '(%%%%C%d)' % d}))
        elif n['l1'][:1].isdigit():                               # horizontal straight bar of the piece
            if mx < -110 and gi in (0, 1) and n['pts'][0][1] - wl > 1000: er.append(n['h']); continue    # analog extension piece «22»
            p, d = hpos(gi, i)
            ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(p), 'SecondLine': '(%%%%C%d)' % d}))
    for i, a, b in PIE:                                           # zones without a note: clone a zone note under the zone
        for z in D[i][gi]:
            if (i, z[0]) in seen: continue
            src = next(n for n in N if abs(n['pts'][0][1] - wl) < 2600 and n['pts'][0][1] < wl and n['h'] not in er)
            tg_ = 'S8n%d' % len(ops); xc = (z[1] + z[2]) / 2
            ops.append(dict(t='clone', h=src['h'], base=[0, 0], to=[0, 0], tag=tg_))
            ops.append(dict(t='spmove', h=tg_, items=[[0, PX(xc) + 300, src['pts'][0][1] + Y]] + [[k, PX(xc), Y + wl] for k in range(1, len(src['pts']))]))
            ops.append(dict(t='mcset', h=tg_, set={'FirstLine': LAB['%d|%d|%s' % (i, gi, z[0])], 'SecondLine': 'ш.%d' % z[4]}))
    # bottom chain: 50 | zone segments | 50 per piece
    CH = [r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and near(r) and -3100 < r['sp'][2][1] - wl < -2800]
    er += [r['h'] for r in CH]
    tdim = CH[0]; y1 = tdim['sp'][0][1]; ydl = wl - 2991
    ops.append(dict(t='clone', h=tdim['h'], base=[0, 0], to=[0, 0], tag='S8C%d' % gi))
    for i, a, b in PIE:
        zs = D[i][gi]; lo = zs[0][1] - 50; hi = zs[-1][2] + 50
        segs = [(lo, lo + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(hi - 50, hi, 50, 1)]
        for k, (s0, s1, st, n_) in enumerate(segs):
            kw = dict(t='dim', h='S8C%d' % gi, p1=[PX(s0), Y + y1], p2=[PX(s1), Y + y1], dl=[PX((s0 + s1) / 2), Y + ydl], rot=0, txt=('%dх%d' % (st, n_)) if n_ > 1 else '')
            if 2 * (s1 - s0) < 650: kw['tx'] = [PX(s0) - 260 if k == 0 else PX(s1) + 260, Y + ydl + 60]
            ops.append(kw)
    ops.append(dict(t='erase', h=['S8C%d' % gi]))
    # axis dims: chain 5000 | 9750 | 8000 (3-3: Б-В 8000 only), total 22750
    AXD = [r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and near(r) and abs(r['sp'][2][1] - (wl - 4374)) < 60]
    TOT = [r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and near(r) and abs(r['sp'][2][1] - (wl - 5023)) < 60]
    ya = AXD[0]['sp'][0][1] if AXD else wl - 2562
    segs = [(14750, 22750)] if gi == 3 else [(0, 5000), (5000, 14750), (14750, 22750)]
    for r, (a, b) in zip(AXD, segs):
        ops.append(dict(t='dimpts', h=r['h'], p1=[PX(a), Y + ya], p2=[PX(b), Y + ya], dl=[PX((a + b) / 2), Y + wl - 4374])); ops.append(dict(t='dimdef', h=[r['h']]))
    er += [r['h'] for r in AXD[len(segs):]]
    for r in TOT:
        if gi == 3: er.append(r['h']); continue
        ops.append(dict(t='dimpts', h=r['h'], p1=[PX(0), Y + r['sp'][0][1]], p2=[PX(22750), Y + r['sp'][0][1]], dl=[PX(11375), Y + wl - 5023])); ops.append(dict(t='dimdef', h=[r['h']]))
ops += [dict(t='erase', h=sorted(set(er))), dict(t='erase', h=['S8D']), dict(t='save')]
print('ops', len(ops), 'erase', len(set(er)))
if '--run' in sys.argv:
    out = gx.run(ops, 's82'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
