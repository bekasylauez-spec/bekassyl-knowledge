# БДМ Блок 4 «униф»: rigel runs from LIRA lines -> supports from the scheme columns / crossing beams -> marks (identical
# geometry + section = one mark, As envelope) -> reinforcement (Ø25 main, As(drawing) >= As(LIRA) everywhere).
import json, pickle, math, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.join(HERE, '..', 'sch', 'rects.json')
L = pickle.load(open(os.path.join(HERE, 'blines.pkl'), 'rb'))
AS = json.load(open(os.path.join(HERE, 'as_lines.json'), encoding='utf-8'))
R = json.load(open(SCH))
SHEET = {-0.05: '2.2', 4.5: '2.3', 7.0: '2.4'}
LEVEL = {-0.05: '-0.050', 4.5: '+4.500', 7.0: '+7.000'}
AXX = {0: '32', 650: '33', 6650: '34', 12650: '35', 18650: '36', 24850: '37', 31850: '38', 38850: '39', 44850: '40'}
AXY = {0: 'А', 9000: 'Б', 13900: 'В', 21000: 'Г', 27500: 'Д', 36000: 'Е', 39000: 'Ж'}
A25 = 4.909
SLAB = {-0.05: 200, 4.5: 200, 7.0: 200}


def cols(z):
    out = []
    for r in R[SHEET[z]]:
        if r['c'] != 0: continue
        if r['x1'] - r['x0'] > 3000 or r['y1'] - r['y0'] > 3000: continue
        out.append((r['x0'], r['y0'], r['x1'], r['y1']))
    return out


def sec_of(k):
    b, h = k[3].split('x'); return int(b) * 10, int(h) * 10


def merge(rs):
    rs = sorted((a, b) for a, b, _ in rs); out = [[rs[0][0], rs[0][1]]]
    for a, b in rs[1:]:
        if a <= out[-1][1] + 1: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def runs():
    res = []
    for k, segs in L.items():
        d, z, c, sec = k
        if d not in 'XY': continue
        b, h = sec_of(k)
        for a, e in merge(segs):
            res.append(dict(dir=d, z=round(z, 2), c=c, b=b, h=h, a=a, e=e, key=str(k)))
    return res


def supports(r, allruns):
    """supports along the run: columns crossing the beam line, else crossing beams not lower than this one"""
    d, c = r['dir'], r['c']
    sup = []
    for (x0, y0, x1, y1) in cols(r['z']):
        lo, hi, p0, p1 = (y0, y1, x0, x1) if d == 'X' else (x0, x1, y0, y1)
        if lo - 1 <= c <= hi + 1 and p1 >= r['a'] - 1 and p0 <= r['e'] + 1:
            sup.append((p0, p1, 'col'))
    for o in allruns:
        if o['z'] != r['z'] or o['dir'] == d: continue
        if not (o['a'] - 1 <= c <= o['e'] + 1): continue
        if not (r['a'] - 1 <= o['c'] <= r['e'] + 1): continue
        if any(p0 - 1 <= o['c'] <= p1 + 1 for p0, p1, _ in sup): continue
        if o['h'] >= r['h']:
            sup.append((o['c'] - o['b'] / 2, o['c'] + o['b'] / 2, 'beam'))
    return sorted(set(sup))


def profile(r):
    pts = [p for p in AS[r['key']] if r['a'] - 1 <= p[0] <= r['e'] + 1]
    return pts                                  # (pos, bot, top, asw)


def build():
    rr = runs()
    out = []
    for r in rr:
        sp = supports(r, rr)
        # beam ends: outer face of the end support (column / beam) if it is at the run end, else free end
        E0, E1 = r['a'], r['e']
        if sp and sp[0][0] <= r['a'] + 1 <= sp[0][1] + 2: E0 = sp[0][0]
        if sp and sp[-1][0] - 2 <= r['e'] - 1 <= sp[-1][1]: E1 = sp[-1][1]
        r.update(E0=E0, E1=E1, sups=sp, prof=profile(r))
        out.append(r)
    return out


def sig(r):
    """geometry signature relative to E0"""
    return (r['z'], r['b'], r['h'], round(r['E1'] - r['E0']), tuple((round(a - r['E0']), round(b - r['E0']), k) for a, b, k in r['sups']))


if __name__ == '__main__':
    rr = build()
    g = collections.OrderedDict()
    for r in sorted(rr, key=lambda r: (-r['z'] if r['z'] < 0 else r['z'], r['dir'], r['h'], r['c'], r['a'])):
        s = sig(r); m = None
        for k in g:
            if k == s: m = k
        g.setdefault(s, []).append(r)
    print(len(rr), 'runs', len(g), 'geometry groups')
    for s, rs in g.items():
        r = rs[0]
        lab = ', '.join('%s%s %s-%s' % ('ось ' if True else '', (AXY if x['dir'] == 'X' else AXX).get(x['c'], x['c']), x['a'], x['e']) for x in rs)
        print(LEVEL[r['z']], r['dir'], '%dx%d' % (r['b'], r['h']), 'L=%d' % (r['E1'] - r['E0']), 'sup', len(r['sups']), [k for _, _, k in r['sups']].count('beam'), 'beam |', lab)
    pickle.dump((rr, list(g.items())), open(os.path.join(HERE, 'groups.pkl'), 'wb'))
