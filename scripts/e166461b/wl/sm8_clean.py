# См-8 elevation cleanup after sm8_elev + generators: analog leftovers left of А/1, storey dims (dim line at the analog column),
# foundation rectangle + its hatches, axis dims 5000|9750|8000 + 22750, «+21,450» mark, section marks (1 basement, 2 floors, 3 top storey).
import sys, json; sys.path.insert(0, 'wl'); from common import *
Y = 455939.0
def run(X, A, L, W=42000, H=59400, go=True):
    YL = L[0]
    R = listwin(X, Y, W, H, None)
    ops = []; er = []
    near = lambda v, lst: any(abs(v - q) < 6 for q in lst)
    dl_x = None
    for r in R:
        if r['t'] != 'DIMENSION' or len(r['sp']) < 3: continue
        (x1, y1), (x2, y2), (x3, y3) = r['sp'][:3]
        if max(x1, x2) > A + 100 or max(y1, y2) < YL - 3200: continue
        lo, hi = min(y1, y2), max(y1, y2)
        if hi - lo > 20000: continue                                         # total height
        if near(lo, L) and near(hi, L) and hi - lo > 1500:                   # storey dim: line in the analog column
            dl_x = A - 3378                                                    # analog storey-dim column
            ops.append(dict(t='dimpts', h=r['h'], p1=[X + A - 125, Y + lo], p2=[X + A - 125, Y + hi], dl=[X + dl_x, Y + (lo + hi) / 2]))
            ops.append(dict(t='dimdef', h=[r['h']])); continue
        if abs(hi - YL) < 3 and abs(lo - (YL - 700)) < 3:                   # foundation 700
            ops.append(dict(t='dimpts', h=r['h'], p1=[X + A - 325, Y + YL], p2=[X + A - 325, Y + YL - 700], dl=[X + (dl_x or A - 3378), Y + YL - 350]))
            ops.append(dict(t='dimdef', h=[r['h']])); continue
        er.append(r['h'])
    er += [r['h'] for r in R if r['t'] == 'LINE' and r['lay'] == 'Размеры' and r['x1'] < A + 100 and YL - 5 < r['y0'] < L[1] and r['y1'] - r['y0'] < 1500]
    # foundation: rectangle A-325 .. A+23075 (700), preparation A-425 .. A+23175 (100); hatches refitted
    FP = [r for r in R if r['t'] == 'LWPOLYLINE' and r['y1'] <= YL + 3 and r['y0'] >= YL - 810 and r['x1'] - r['x0'] > 15000]
    for r in FP:
        y0, y1 = r['y0'], r['y1']; x0, x1 = (A - 325, A + 23075) if y1 - y0 > 300 else (A - 425, A + 23175)
        ops.append(dict(t='spmove', h=r['h'], items=[[i, X + (x1 if p[0] > (r['x0'] + r['x1']) / 2 else x0), Y + p[1]] for i, p in enumerate(r['sp'][:4])]))
        for h in [q for q in R if q['t'] == 'HATCH' and abs(q['y0'] - y0) < 3 and abs(q['y1'] - y1) < 3]:
            ops.append(dict(t='hatchfit', h=h['h'], loops=[[[X + x0, Y + y0], [X + x1, Y + y0], [X + x1, Y + y1], [X + x0, Y + y1]]]))
    # axis dims
    AD = [r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and YL - 6500 < r['sp'][2][1] < YL - 2000 and abs(r['sp'][0][1] - r['sp'][1][1]) < 700 and min(r['sp'][0][0], r['sp'][1][0]) > A - 100]
    if AD:
        tot = max(AD, key=lambda r: abs(r['sp'][1][0] - r['sp'][0][0])); ytot = tot['sp'][2][1]
        ch = [r for r in AD if r is not tot]
        ych = ch[0]['sp'][2][1] if ch else ytot + 700; yx = max(r['sp'][0][1] for r in AD)
        ops.append(dict(t='dimpts', h=tot['h'], p1=[X + A, Y + yx], p2=[X + A + 22750, Y + yx], dl=[X + A + 11375, Y + ytot])); ops.append(dict(t='dimdef', h=[tot['h']]))
        keep = ch[:3]; er += [r['h'] for r in ch[3:]]
        for r, (a, b) in zip(keep, ((0, 5000), (5000, 14750), (14750, 22750))):
            ops.append(dict(t='dimpts', h=r['h'], p1=[X + A + a, Y + yx], p2=[X + A + b, Y + yx], dl=[X + A + (a + b) / 2, Y + ych])); ops.append(dict(t='dimdef', h=[r['h']]))
        ops.append(dict(t='eprops', src=keep[0]['h'] if keep else tot['h'], h=[tot['h']]))
    # +21,450 mark to the top piece; sections
    for r in R:
        if r['t'] == 'SPDSLEVELMARK' and abs(r['sp'][0][1] - L[-1]) < 3:
            ops.append(dict(t='spmove', h=r['h'], items=[[0, X + A + 15225, Y + L[-1]]]))
    SEC = sorted([r for r in R if r['t'] == 'SPDSSECTION'], key=lambda r: r['sp'][0][1])
    if len(SEC) == 3:
        s3 = SEC[2]; yy = (L[-2] + L[-1]) / 2 - 0
        ops.append(dict(t='spmove', h=s3['h'], items=[[0, X + A - 6670, Y + yy], [1, X + s3['sp'][1][0], Y + yy]]))
    ops.append(dict(t='erase', h=sorted(set(er))))
    ops.append(dict(t='save'))
    print('erase', len(er), 'ops', len(ops))
    if go:
        out = gx.run(ops, 'cl8'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-5:])
if __name__ == '__main__':
    X, A = float(sys.argv[1]), float(sys.argv[2]); y0 = float(sys.argv[3])
    d = [0, 4550, 8600, 11750, 14900, 18050, 21200, 24350, 26100]
    run(X, A, [y0 + v for v in d], float(sys.argv[4]) if len(sys.argv) > 4 else 42000, float(sys.argv[5]) if len(sys.argv) > 5 else 59400)
