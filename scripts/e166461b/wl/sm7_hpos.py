# 5.27 positions of the straight bars by (Ø, L) — one position per piece as in the analog (32/33/34); basement bar 22.96 m
# is ordered as 3 bars with 2 laps (stock ≤ 11.7 m). Relabels the existing pos notes and rewrites wl/sm7_hor.json BARS.
import sys, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
from rowsplit import rows as ROWS
SX, SY, AX1 = 2078100.0, 455939.0, 15030.0
L = [27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320]; SLAB = 250.0
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))
J = json.load(open('wl/sm7_hor.json', encoding='utf-8')); HD = J['HD']
vj = json.load(open('wl/sm7_vert.json', encoding='utf-8')); P0 = max(vj['POS'].values())
POS = {}; BARS = [b for b in J['BARS'] if str(b['pos']).startswith('Ск')]
def pos_of(k):
    if k not in POS: POS[k] = P0 + len(POS) + 1
    return POS[k]
LAB = {}
for s in range(7):
    d, st = HD[s]; pos, segs = ROWS(L[s], L[s + 1], st, SLAB); rows = len(pos)
    pcs = [(-105, 22855)] if s == 0 else [(-105, 3125), (5800, 17050), (20425, 22855)]
    for k, (fa, fb) in enumerate(pcs):
        Lb = int(round(fb - fa, -1))
        if Lb > 11700:
            nb = math.ceil((Lb - LAP(d)) / (11700.0 - LAP(d))); Lb = int(math.ceil((Lb + (nb - 1) * LAP(d)) / nb / 10.0) * 10)
        else: nb = 1
        p = pos_of((d, Lb)); LAB[(s, k)] = p
        BARS.append(dict(pos=p, d=d, L=Lb, n=2 * rows * nb, storey=s))
N = notes(SX, SY, 42000, 59400); ops = []
for n in N:
    if not n['l2'].startswith('ш.') or n['pts'][0][1] < L[0]: continue
    x = n['pts'][0][0] - AX1; y = n['pts'][0][1]
    s = next(i for i in range(7) if L[i] <= y < L[i + 1])
    k = 0 if s == 0 else (0 if x < 4000 else (1 if x < 19000 else 2))
    ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(LAB[(s, k)])}))
ops.append(dict(t='save'))
J['BARS'] = BARS; J['POS'] = {'%d_%d' % k: v for k, v in POS.items()}
json.dump(J, open('wl/sm7_hor.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(POS, len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'h7p'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l])
