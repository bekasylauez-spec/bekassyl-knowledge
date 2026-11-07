# concrete / reinforcement geometry check of every section type of every rigel (design data, the same layout rules as rsec.py)
import json, math, itertools, rsec
A = json.load(open('beams_auto.json', encoding='utf-8'))
bad = []
for mk, B in A.items():
    b, h = B['b'], B['h']; dh = B['hoop']['d']; nm = B['main']['top'][0]; dm = B['main']['top'][1]
    YBOT, YTOP = 55.0, h - 55.0
    for sc in B['secs']:
        t1 = [x for x in sc['top'] if x[3] == 1]; t2 = [x for x in sc['top'] if x[3] == 2]
        b1 = [x for x in sc['bot'] if x[3] == 1]; b2 = [x for x in sc['bot'] if x[3] == 2]
        def xs(n1):
            if nm == 3:
                st = (b - 110) / 2.0; return [55 + st * i for i in range(3)], []
            m_, d_, _ = rsec.bar_x(b, 4, n1); return m_, d_
        mT, dT = xs(sum(x[1] for x in t1)); mB, dB = xs(sum(x[1] for x in b1))
        bars = [(x, YTOP, dm, 'T1') for x in mT] + [(x, YBOT, dm, 'B1') for x in mB]
        i = 0
        for (pos, n, d_, row) in t1: bars += [(x, YTOP, d_, 'T1') for x in dT[i:i + n]]; i += n
        i = 0
        for (pos, n, d_, row) in b1: bars += [(x, YBOT, d_, 'B1') for x in dB[i:i + n]]; i += n
        def r2(n):
            if n >= nm: return list(mB)
            if n == 1: return [mB[len(mB) // 2]]
            if n == 2: return [mB[0], mB[-1]]
            return [mB[0], mB[1], mB[-1]]
        for (pos, n, d_, row) in t2: bars += [(x, YTOP - 98, d_, 'T2') for x in r2(n)]
        for (pos, n, d_, row) in b2: bars += [(x, YBOT + 98, d_, 'B2') for x in r2(n)]
        sr = rsec.side_rows(B)
        sy = [YBOT + (YTOP - YBOT) * (k + 1) / (len(sr) + 1.0) for k in range(len(sr))]
        for yy in sy: bars += [(mB[0], yy, B['side_d'], 'S'), (mB[-1], yy, B['side_d'], 'S')]
        tag = '%s sec %s' % (mk, sc['word'])
        for x, y, d, k in bars:
            c = min(x, b - x, y, h - y) - d / 2.0 - dh
            if c < 25 - 1e-6: bad.append((tag, 'cover %.0f < 25 at %s (%.0f,%.0f)' % (c, k, x, y)))
        for (x1, y1, d1, k1), (x2, y2, d2, k2) in itertools.combinations(bars, 2):
            cl = math.hypot(x1 - x2, y1 - y2) - (d1 + d2) / 2.0
            need = max(25, d1, d2) if abs(y1 - y2) < 1 else (70 if {k1[1:], k2[1:]} == {'1', '2'} and k1[0] == k2[0] else max(25, d1, d2))
            if cl < need - 1e-6: bad.append((tag, 'clear %.0f < %d between %s(%.0f,%.0f) and %s(%.0f,%.0f)' % (cl, need, k1, x1, y1, k2, x2, y2)))
        ys = sorted(set([YBOT, YTOP] + sy))
        if h >= 700 and max(q - p for p, q in zip(ys, ys[1:])) > 400 + 1e-6: bad.append((tag, 'side rows spacing > 400'))
    for d in B['dop']:
        if d['u1'] - d['u0'] > 11700: bad.append((mk, 'dop pos %s longer than 11.7 m' % d['pos']))
        if d['u0'] < B['END0'] or d['u1'] > B['END1']: bad.append((mk, 'dop pos %s outside the beam' % d['pos']))
print('checked', len(A), 'marks;', 'problems', len(bad))
for x in bad[:60]: print(x)
