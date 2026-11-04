# positions: 1 = base Ø16 (пог.м., analog), Ск1 Ø16 980+620+980, Ф1 Ø12 300/620/300/620/300 (analog), dop 2.. in sheet order 3.3..3.6
import json, math
F = json.load(open('arm/fm_final.json'))
import sys; sys.path.insert(0, '.'); import model as M
FX0, FY0, FX1, FY1 = M.FM; COV = 50
def clip(key): return (FX0 + COV, FX1 - COV) if key.split('_')[1] == 'x' else (FY0 + COV, FY1 - COV)
LAP = lambda d: int(math.ceil(71 * d / 50.0) * 50)
for key in list(F):
    nz = []
    lo, hi = clip(key)
    for z in F[key]:
        L = z['s1'] - z['s0']; Lr = math.ceil(L / 500.0) * 500
        s0 = z['s0'] - (Lr - L) / 2; s1 = s0 + Lr
        if s0 < lo: s1 += lo - s0; s0 = lo
        if s1 > hi: s0 -= s1 - hi; s1 = hi
        s0 = max(s0, lo); z['s0'], z['s1'] = s0, s1
        if s1 - s0 > 11700:                                   # stock 11.7 m: two bars lapped 71d (analog note)
            lap = LAP(z['d']); half = (s1 - s0 + lap) / 2; half = math.ceil(half / 500.0) * 500
            a = dict(z, s1=s0 + half); b = dict(z, s0=s1 - half, lap=True)
            nz += [a, b]
        else: nz.append(z)
    F[key] = nz
KG = {8: .395, 10: .617, 12: .888, 14: 1.21, 16: 1.58, 18: 2.0, 20: 2.47, 22: 2.98, 25: 3.85, 28: 4.83, 32: 6.31}
pos = {}; order = []
for key in ('bot_x', 'top_x', 'bot_y', 'top_y', 'bot_y_3'):
    for z in sorted(F.get(key, []), key=lambda z: (z['p0'], z['s0'])):
        L = int(z['s1'] - z['s0']); k = (z['d'], L)
        if k not in pos: pos[k] = str(len(pos) + 2); order.append(k)
        z['pos'] = pos[k]; z['L'] = L
json.dump(F, open('arm/fm_final.json', 'w'), indent=1)
cnt = {}
for key, zs in F.items():
    for z in zs: cnt[z['pos']] = cnt.get(z['pos'], 0) + z['n']
rows = []
for k in order:
    p = pos[k]; rows.append((p, k[0], k[1], cnt[p], round(KG[k[0]] * k[1] / 1000, 2)))
json.dump(rows, open('arm/fm_rows.json', 'w'))
print(len(rows), 'positions'); tot = sum(r[3] * r[4] for r in rows); print('dop kg', round(tot))
for r in rows: print(r)
