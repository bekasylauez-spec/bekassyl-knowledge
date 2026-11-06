# БДМ Блок 3 rigels: parts (LIRA geometry + scheme columns) -> marks -> sheet JSON files for net/rb3.py
import json, collections, math
P = json.load(open('parts.json')); geo = json.load(open('schgeo.json'))
AXX = [(650, '23'), (5950, '24'), (11300, '25'), (17300, '26'), (23300, '27'), (29300, '28'), (35300, '29'), (41300, '30'),
       (47300, '31'), (53300, '32')]
AXY = [(0, 'А'), (9000, 'Б'), (13900, 'В'), (21000, 'Г'), (27500, 'Д'), (36000, 'Е'), (39000, 'Ж')]
LV = {4.5: '2.3', 7.0: '2.4'}
MAXL = 11700 - 250            # bar piece limit (stock 11.7 m)
SHEETL = 23400                # longest beam drawn on one A4x3 1:50 sheet

def supports(p):
    res = []
    for x0, y0, x1, y1 in geo[LV[p['z']]]['cols']:
        if p['dir'] == 'X' and y0 <= p['c'] <= y1 and x1 >= p['s'] - 1 and x0 <= p['e'] + 1: res.append(dict(k='c', a=x0, b=x1, h=0))
        if p['dir'] == 'Y' and x0 <= p['c'] <= x1 and y1 >= p['s'] - 1 and y0 <= p['e'] + 1: res.append(dict(k='c', a=y0, b=y1, h=0))
    L = p['e'] - p['s']
    for q in P:
        if q is p or q['z'] != p['z'] or q['dir'] == p['dir']: continue
        if not (q['s'] <= p['c'] <= q['e'] and p['s'] <= q['c'] <= p['e']): continue
        if q['sec'][1] > p['sec'][1] or (q['sec'][1] == p['sec'][1] and q['e'] - q['s'] > L):
            if not any(r['a'] <= q['c'] <= r['b'] for r in res):
                res.append(dict(k='b', a=q['c'] - q['sec'][0] // 2, b=q['c'] + q['sec'][0] // 2, h=q['sec'][1]))
    return sorted(res, key=lambda r: r['a'])

def perp_at(p, x):
    return any(q['z'] == p['z'] and q['dir'] != p['dir'] and q['s'] <= p['c'] <= q['e'] and abs(q['c'] - x) < 1 for q in P)

def beam(p):
    sup = supports(p)
    s, e = p['s'], p['e']
    first = [r for r in sup if r['a'] <= s <= r['b']]; last = [r for r in sup if r['a'] <= e <= r['b']]
    E0 = first[0]['a'] if first else s - (125 if perp_at(p, s) else 0)
    E1 = last[0]['b'] if last else e + (125 if perp_at(p, e) else 0)
    sup = [r for r in sup if r['b'] > E0 - 1 and r['a'] < E1 + 1]
    return E0, E1, sup

marks = collections.OrderedDict()
for p in sorted(P, key=lambda p: (p['z'], -p['sec'][1], -p['sec'][0], p['dir'], p['c'], p['s'])):
    E0, E1, sup = beam(p)
    sig = (p['z'], tuple(p['sec']), p['dir'], tuple((r['k'], r['a'] - E0, r['b'] - E0, r['h']) for r in sup), E1 - E0)
    marks.setdefault(sig, []).append(p)

def splices(E0, E1, cands):
    pos, out = E0, []
    while E1 - pos > MAXL:
        ok = [c for c in cands if pos + 1500 < c <= pos + MAXL - 250]
        if not ok: break
        c = max(ok); out.append(c); pos = c - 250
    return out

sheets = []; no = 0; SX0 = 172179.0
for mi, (sig, parts) in enumerate(marks.items(), 1):
    p = parts[0]; E0, E1, sup = beam(p)
    mark = 'Рм-%d' % mi
    axes = AXX if p['dir'] == 'X' else AXY
    cen = [(r['a'] + r['b']) / 2.0 for r in sup]
    # splices on the whole beam
    faces = [E0] + [c for r in sup for c in (r['a'], r['b'])] + [E1]
    spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
    free0 = not any(r['a'] <= p['s'] <= r['b'] for r in sup); free1 = not any(r['a'] <= p['e'] <= r['b'] for r in sup)
    inner = [q for i, q in enumerate(spans) if not ((i == 0 and free0) or (i == len(spans) - 1 and free1))]
    topc = splices(E0, E1, sorted((a + b) / 2.0 for a, b in inner if b - a > 1500))
    botc = splices(E0, E1, sorted(c + 1700 for c in cen[:-1]))
    # sheets: split at support faces so that every piece <= SHEETL
    cuts = [E0]
    while E1 - cuts[-1] > SHEETL + 1:
        ok = [r for r in sup if r['b'] - cuts[-1] <= SHEETL and r['a'] > cuts[-1] + 1000]
        r = max(ok, key=lambda r: r['b']); cuts.append(r['b'])
    cuts.append(E1)
    for si in range(len(cuts) - 1):
        a0, a1 = cuts[si], cuts[si + 1]
        ss = [r for r in sup if r['b'] > a0 + 1 and r['a'] < a1 - 1]
        if si > 0:                                   # the cut column is drawn on both sheets
            prev = [r for r in sup if abs(r['b'] - a0) < 1]
            ss = prev + ss; a0 = prev[0]['a']
        def cen_of(r):
            k = [x for x, _ in axes if r['a'] - 1 <= x <= r['b'] + 1]; return k[0] if k else (r['a'] + r['b']) / 2.0
        cs = [cen_of(r) for r in ss]
        fz = [a0] + [c for r in ss for c in (r['a'], r['b'])] + [a1]
        sp = [(fz[i], fz[i + 1]) for i in range(0, len(fz), 2) if fz[i + 1] - fz[i] > 1]
        # chain refs: support centre (or axis) left/right of each span, free end coordinate otherwise
        def refl(x):
            c = [q for q in cs if q <= x + 1]; return max(c) if c else a0
        def refr(x):
            c = [q for q in cs if q >= x - 1]; return min(c) if c else a1
        refs = [[refl(a), refr(b)] for a, b in sp]
        ax = [[x, v] for x, v in axes if a0 - 1 <= x <= a1 + 1]
        row2 = sorted(set([x for x, _ in ax] + [round(c) for c in cs]))
        if a0 not in row2 and not any(r['a'] <= a0 + 1 and r['b'] >= a0 - 1 for r in ss): row2 = [a0] + row2
        if a1 not in row2 and not any(r['a'] <= a1 + 1 and r['b'] >= a1 - 1 for r in ss): row2 = row2 + [a1]
        def near_ax(c):
            k = [x for x, _ in axes if abs(x - c) < 400]; return k[0] if k else c
        spT = [[c - 250, c + 250, near_ax(refl(c))] for c in topc if a0 < c < a1]
        spB = [[c - 250, c + 250, near_ax(refl(c - 1700))] for c in botc if a0 < c < a1]
        lng = max(sp, key=lambda q: q[1] - q[0])
        avoid = [c for gg in spT + spB for c in gg[:2]] + [x for x, _ in ax]
        cand = [a + (b - a) * f for a, b in sp if b - a > 1200 for f in (0.25, 0.4, 0.6, 0.75)] or [(lng[0] + lng[1]) / 2.0]
        secx = max(cand, key=lambda c: min([abs(c - q) for q in avoid] + [1e9]))
        no += 1
        B = dict(mark=mark, no='6.%d' % no, SX=SX0 + 31500 * (no - 1), P='R%d:' % no, E=[a0, a1], h=p['sec'][1], b=p['sec'][0],
                 level='+4.500' if p['z'] == 4.5 else '+7.000', hoopd=10,
                 sup=[[r['a'], r['b']] for r in ss], supk=[[r['k'], r['h']] for r in ss], axes=ax, row2=row2, refs=refs,
                 ends=['sk' if si == 0 else 'cut', 'sk' if si == len(cuts) - 2 else 'cut'],
                 spT=spT, spB=spB, dop=[], secs=[['1', round(secx)]],
                 secdefs=[dict(w='1', nT=4 if p['sec'][0] > 300 else 3, nB=4 if p['sec'][0] > 300 else 3)],
                 part=[si + 1, len(cuts) - 1], full=[E0, E1], beams=['%s%d' % (q['dir'], q['c']) for q in parts],
                 spans_full=spans, nspl=len(topc) + len(botc))
        sheets.append(B)
        json.dump(B, open('sh_%d.json' % no, 'w', encoding='utf-8'), ensure_ascii=False)
for B in sheets:
    print(B['no'], B['mark'], B['level'], '%dx%d' % (B['b'], B['h']), 'E', [round(v) for v in B['E']], 'part', B['part'], 'sup', len(B['sup']),
          'axes', [v for _, v in B['axes']], 'spT', len(B['spT']), 'spB', len(B['spB']), B['ends'], len(B['beams']))
print(len(marks), 'marks', len(sheets), 'sheets')
