# См-8 elevations from the analog См-9 (4.33 op / 4.34 vert / 4.34 hor): drop the extension left of A and the axes A/2, Б/1,
# remap the pieces (analog rel. A -> ours rel. А/1), axes А/1 0, А 5000, Б 14750, В 22750, slab hatches refitted.
import sys; sys.path.insert(0, 'wl'); from common import *
from notes import notes
Y = 455939.0
A_ = [(-3125, -125), (-125, -125), (2775, 2775), (6175, 6175), (7875, 7425), (8125, 7675), (10225, 15225), (12475, 17775),
      (12725, 18025), (15875, 20575), (17625, 22625), (17875, 22875)]
def run(X, A, YL, YH, W, H, go=True):
    R = listwin(X, Y, W, H, None)
    er = []
    for r in R:
        if r['y0'] < YL - 400 or r['y1'] > YH or r['x1'] > A + 20000: continue
        if r['t'] in ('SPDSLEVELMARK', 'SPDSSECTION', 'SPDSCONSTRUCTIONLINE'): continue
        if r['x0'] >= A - 3135 and r['x1'] <= A - 120 and r['y0'] > YL - 5: er.append(r['h'])
    for n in notes(X, Y, W, H):
        xs = [p[0] for p in n['pts']]
        if all(A - 3400 < x < A - 120 for x in xs) and n['pts'][0][1] > YL: er.append(n['h'])
    ax = sorted([r for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and r['y1'] - r['y0'] > 5000 and A - 500 < (r['x0'] + r['x1']) / 2 < A + 19000], key=lambda r: r['sp'][0][0])
    print('axes', [(r['h'], round(r['sp'][0][0] - A)) for r in ax])
    hA, hA1, hA2, hB, hB1, hV = [r['h'] for r in ax]
    sp = {r['h']: r['sp'] for r in ax}
    ops = [dict(t='erase', h=er + [hA2, hB1]), dict(t='pmap', win=[X + 1000, Y + YL - 400, X + A + 20000, Y + YH], pairs=[[X + A + a, X + A + b] for a, b in A_])]
    for h, x, v in ((hA, 0, 'А/1'), (hA1, 5000, 'А'), (hB, 14750, 'Б'), (hV, 22750, 'В')):
        (sx, sy), (ex, ey) = sp[h][0], sp[h][1]
        ops.append(dict(t='axis', h=h, s=[X + A + x, Y + sy], e=[X + A + x, Y + ey], val=v))
    ops.append(dict(t='save'))
    print('erase', len(er))
    if go:
        out = gx.run(ops, 'sm8e'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-3:])
    # slab / foundation hatches do not follow the remap: refit each to the polyline band it sits on
    R = listwin(X, Y, W, H, None)
    PL = [r for r in R if r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and r['y1'] - r['y0'] < 800 and r['x1'] - r['x0'] > 1500 and r['y0'] > YL - 900]
    ops = []
    for h in [r for r in R if r['t'] == 'HATCH' and r['y0'] > YL - 900 and r['x0'] < A + 20000]:
        b = [p for p in PL if abs(p['y0'] - h['y0']) < 3 and abs(p['y1'] - h['y1']) < 3]
        if not b: print('no band for hatch', h['h'], round(h['y0'])); continue
        b = max(b, key=lambda p: p['x1'] - p['x0'])
        ops.append(dict(t='hatchfit', h=h['h'], loops=[[[X + b['x0'], Y + b['y0']], [X + b['x1'], Y + b['y0']], [X + b['x1'], Y + b['y1']], [X + b['x0'], Y + b['y1']]]]))
    ops.append(dict(t='save'))
    if go:
        out = gx.run(ops, 'sm8e2'); print('hatchfit', len(ops) - 1, [l for l in out.splitlines() if 'ERR' in l or 'done' in l][-3:])
if __name__ == '__main__':
    a = [float(v) for v in sys.argv[1:7]]
    run(a[0], a[1], a[2], a[3], a[4], a[5])
