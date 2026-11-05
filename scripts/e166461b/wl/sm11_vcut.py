# См-11: vertical bars cut by the openings (Obsidian rule: no extra side bars; bars inside the opening width stop 30 from its faces).
# The bars of wall_vert (A/B staggered, same geometry as wall_vert) inside each opening width are split into pieces -> new positions
# appended to wl/sm11_vert.json (BARS/POS, original counts reduced). On 5.47: the extreme cut bars drawn as pieces + one note per group.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
import importlib
C = importlib.import_module('cfg_sm11').VERT
SX, SY, AX1, L = C['SX'], 455939.0, C['AX1'], C['L']
G = C.get('G', [(0, 1), (1, 3), (3, 5), (5, len(L) - 1)])
OPN = C['OPENINGS']                                       # (storey, a, b, z0, z1)
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))
GAP = lambda lap: int(round(0.3 * lap, -1))
V = json.load(open(C['OUT'], encoding='utf-8')); D = V['D']
POS = {tuple(int(v) for v in k.split('|')): p for k, p in V['POS'].items()}
if any(b.get('cut') for b in V['BARS']): sys.exit('already cut: re-run wall_vert first')
nxt = [max(POS.values())]
def pos_of(d, Ln):
    if (d, Ln) not in POS: nxt[0] += 1; POS[(d, Ln)] = nxt[0]
    return POS[(d, Ln)]
def zd(i, g, kind):                                      # as wall_vert zone(): the kind, else the largest Ø (basement: piece 1)
    zs = D[i][g] or D[0][g]
    z = next((z for z in zs if z[0] == kind), None) or max(zs, key=lambda z: z[3])
    return z[3]
i = 1                                                     # piece 2 holds the openings
adds = []; minus = {}; draw = []
for gi, (g0, g1) in enumerate(G):
    DX = 20 * (gi % 2)
    ops_open = [(a, b, L[s] + z0 - 30, L[s] + z1 + 30, s) for s, a, b, z0, z1 in OPN if g0 <= s < g1]
    if not ops_open: continue
    for z in D[i][gi]:
        kind, x0, x1, d, st = z[:5]; xs = z[5]
        lpd = LAP(max(zd(i, gi - 1, kind), zd(i, gi, kind))) if gi > 0 else LAP(d)
        bA = L[g0]; bB = L[g0] + lpd + GAP(lpd)
        if gi < 3: lp = LAP(max(zd(i, gi, kind), zd(i, gi + 1, kind))); tA = L[g1] + lp; tB = L[g1] + 2 * lp + GAP(lp)
        else: tA = tB = L[g1] - 30
        for k, x in enumerate(xs):
            hits = [o for o in ops_open if o[0] < x < o[1]]
            if not hits: continue
            b, t = (bA, tA) if k % 2 == 0 else (bB, tB)
            Lo = int(round(t - b, -1)); po = POS[(d, Lo)]
            minus[po] = minus.get(po, 0) + 2
            segs = [(b, t)]
            for a_, b_, y0, y1, s in hits:
                segs = [p for (u, w) in segs for p in ((u, min(w, y0)), (max(u, y1), w)) if p[1] - p[0] > 0]
            for u, w in segs:
                Ln = int(round(w - u, -1))
                if Ln < 200: continue
                p = pos_of(d, Ln); adds.append(dict(pos=p, d=d, L=Ln, n=2, cut=True))
                draw.append((gi, x + DX, u, w, d, p, st))
# reduce the originals, append the pieces
for b in V['BARS']:
    if b['pos'] in minus and not str(b['pos']).startswith('Ск'):
        take = min(b['n'], minus[b['pos']]); b['n'] -= take; minus[b['pos']] -= take
V['BARS'] = [b for b in V['BARS'] if b['n'] > 0] + adds
V['POS'] = {'%d|%d' % k: v for k, v in POS.items()}
json.dump(V, open(C['OUT'], 'w', encoding='utf-8'), ensure_ascii=False)
print('new positions', sorted(set(a['pos'] for a in adds)), 'pieces', len(adds))
# drawing: per group the two extreme cut bars of each opening column as pieces + one note (positions, step) beside the opening
ops = []; notes_ = {}
for gi in set(g for g, *_ in draw):
    for a_, b_ in set((a, b) for s, a, b, z0, z1 in OPN if G[gi][0] <= s < G[gi][1]):
        ds = [r for r in draw if r[0] == gi and a_ < r[1] - 20 * (gi % 2) < b_]
        if not ds: continue
        xs = sorted(set(r[1] for r in ds)); ext = (xs[0], xs[-1])
        for g_, x, u, w, d, p, st in ds:
            if x in ext: ops.append(dict(t='pl', p=[[SX + AX1 + x, SY + u], [SX + AX1 + x, SY + w]], layer='диам%d' % d, lw=40))
        labs = sorted(set(r[5] for r in ds)); st = ds[0][6]
        s0 = min(s for s, a, b, z0, z1 in OPN if a == a_ and G[gi][0] <= s < G[gi][1]); z0 = next(z0 for s, a, b, z0, z1 in OPN if a == a_ and s == s0)
        y = L[s0] + max(250, z0 / 2) if z0 > 300 else L[s0] + 2200 + 350        # window: in the sill zone; opening from the floor: in the lintel
        notes_[(gi, a_)] = (';'.join(str(v) for v in labs), 'ш.%d' % st, ext, y, b_)
json.dump({'%d|%d' % k: v for k, v in notes_.items()}, open('wl/sm11_vcut_notes.json', 'w', encoding='utf-8'), ensure_ascii=False)
for k, (l1, l2, ext, y, b_) in notes_.items():
    t = 'VC11_%d_%d' % k
    ops += [dict(t='clone', h='345FB1', base=[0, 0], to=[0, 0], tag=t),
            dict(t='spmove', h=t, items=[[0, SX + AX1 + b_ + 350, SY + y], [1, SX + AX1 + ext[0], SY + y], [2, SX + AX1 + ext[1], SY + y]]),
            dict(t='mcset', h=t, set={'FirstLine': l1, 'SecondLine': l2})]
print(notes_)
if '--run' in sys.argv:
    out = gx.run(ops + [dict(t='save')], 'vc11'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
