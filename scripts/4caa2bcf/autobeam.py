# Build beam definitions (beams.py format) for every mark: geometry from the scheme rectangles,
# supports from LIRA, reinforcement from LIRA As/Asw (main Ø25 fully covering As, dop / 2nd row where needed).
import json, math, os, gx
S = gx.S
MK = json.load(open(S + r'\b2\marks.json', encoding='utf-8'))
RECTS = json.load(open(S + r'\b2\rects.json'))
LEV = {-0.05: '-0.050', 4.5: '+4.500', 7.0: '+7.000'}
AXX = {'13': 0, '14': 1300, '15': 4975, '16': 11075, '17': 17075, '18': 23075, '19': 29075, '20': 35075, '21': 41075, '22': 47450, '23': 48750}
AXY = {'А': 0, 'Б': 9000, 'В': 13900, 'Г': 21000, 'Д': 27500, 'Е': 36000, 'Ж': 39000}
LX = [74.05, 78.05, 84.15, 90.15, 96.15, 102.15, 108.15, 114.15, 120.85]
SXa = [1125, 4975, 11075, 17075, 23075, 29075, 35075, 41075, 47625]
AR = lambda d: math.pi * d * d / 400.0
SLAB = {'-0.050': 0, '+4.500': 200, '+7.000': 200}


def mapx(x):
    if x <= LX[0]: return SXa[0] + (x - LX[0]) * 1000
    if x >= LX[-1]: return SXa[-1] + (x - LX[-1]) * 1000
    for i in range(len(LX) - 1):
        if LX[i] <= x <= LX[i + 1]:
            return SXa[i] + (x - LX[i]) / (LX[i + 1] - LX[i]) * (SXa[i + 1] - SXa[i])


def along(d, v): return mapx(v) if d == 'X' else v * 1000.0
def perp(d, c): return c * 1000.0 if d == 'X' else mapx(c)


def rects_on(lev, d, cs, tol=1):
    out = []
    for r in RECTS[lev]:
        a0, a1, p0, p1 = (r[0], r[2], r[1], r[3]) if d == 'X' else (r[1], r[3], r[0], r[2])
        if p0 - tol <= cs <= p1 + tol: out.append((a0, a1, p0, p1))
    return out


def axes_for(d):
    return AXX if d == 'X' else AXY


def build(m):
    d, lev = m['d'], LEV[m['z']]
    b, h = [int(v) * 10 for v in m['s'].split('x')]
    c0 = None
    li = 0
    c = m['lines'][li]; x0 = m['x0s'][li]
    cs = perp(d, c)
    s0, s1 = along(d, x0), along(d, x0 + m['L'])
    rs = rects_on(lev, d, cs)
    sup = []
    AX = axes_for(d)
    for sp in m['sup']:
        u = along(d, x0 + sp)
        col = [r for r in rs if r[0] - 1 <= u <= r[1] + 1 and (r[1] - r[0]) <= 1600 and (r[3] - r[2]) <= 1600]
        if col:
            a_, b_ = min(r[0] for r in col), max(r[1] for r in col)
            kind = 'col' if not m['onbeam'] else 'beam'
        else:
            a_, b_ = u - 250, u + 250; kind = 'beam'
        ax = [(v, k) for k, v in AX.items() if a_ - 1 <= v <= b_ + 1]
        e = dict(a=round(a_), b=round(b_), kind=kind)
        if ax: e['ax'], e['axn'] = ax[0][0], ax[0][1]
        sup.append(e)
    # beam ends: scheme beam rectangles of this width on the line, else supports / LIRA
    bm = [r for r in rs if abs((r[3] - r[2]) - b) <= 60 and r[1] >= s0 - 1500 and r[0] <= s1 + 1500]
    E0 = min([r[0] for r in bm] + [sup[0]['a'] if sup else s0])
    E1 = max([r[1] for r in bm] + [sup[-1]['b'] if sup else s1])
    E0 = max(E0, s0 - 600); E1 = min(E1, s1 + 600)
    return dict(levels=[lev], b=b, h=h, END0=round(E0), END1=round(E1), slab=SLAB[lev], sup=sup,
                line=d, cs=cs, x0s=m['x0s'], lines=m['lines'], qty=len(m['lines']))


def need_profile(m, B):
    """LIRA envelope over all lines of the mark, mapped to scheme u: list (u, bot, top, asw)"""
    d = m['d']; out = []
    for li, pts in enumerate(m['pts']):
        x0 = m['x0s'][li]
        for q in pts: out.append((along(d, x0 + q[0]), q[1], q[2], q[3]))
    return sorted(out)


def design(m, B):
    b, h = B['b'], B['h']
    nm = 3 if b <= 300 else 4
    dm = 28                     # Bekassyl 06.11: «арматурасын тексермей барлығын 28-дік қоя сал»
    B['main'] = dict(top=(nm, dm), bot=(nm, dm))
    prof = need_profile(m, B)
    legs = 2 if b <= 300 else 4
    amax = max(q[3] for q in prof)
    for dh in (8, 10, 12, 14, 16, 18, 20):
        if legs * AR(dh) * 10 >= amax: break
    # middle spacing 200 allowed where Asw <= capacity at 200
    cols = [sp for sp in B['sup']]
    mid_ok = True
    for i in range(len(cols) - 1):
        a, bb = cols[i]['b'], cols[i + 1]['a']; L = bb - a
        for q in prof:
            if a + L / 4 <= q[0] <= bb - L / 4 and q[3] > legs * AR(dh) * 5: mid_ok = False
    B['hoop'] = dict(d=dh, s_end=100, s_mid=200 if mid_ok else 100, legs=legs)
    # dop bars: same Ø, in the same row between main bars (b>=450: up to 3), else 2nd row (up to nm)
    slots = 3 if b >= 450 else 0
    dop = []; pos = [2]
    for top in (True, False):
        k = 2 if top else 1
        main = nm * AR(dm)
        reg = []
        for u, bot, tp, sw in prof:
            nd = (tp if top else bot) - main
            if nd > 1e-6: reg.append((u, nd))
        if not reg: continue
        # cluster
        cl = [[reg[0]]]
        for r in reg[1:]:
            if r[0] - cl[-1][-1][0] > 2500: cl.append([r])
            else: cl[-1].append(r)
        for g in cl:
            u0 = g[0][0] - 1000; u1 = g[-1][0] + 1000
            u0 = max(u0, B['END0'] + 20); u1 = min(u1, B['END1'] - 20)
            if u1 - u0 < 1500: c_ = (u0 + u1) / 2; u0, u1 = max(B['END0'] + 20, c_ - 750), min(B['END1'] - 20, c_ + 750)
            need = max(r[1] for r in g)
            dd = dm; n = math.ceil(need / AR(dd) - 1e-9)
            if slots and n <= slots: row = 1
            else: row = 2; n = min(n, nm)
            dop.append(dict(top=top, n=n, d=dd, u0=round(u0, -1), u1=round(u1, -1), row=row))
    # unify: dop around interior supports get the same n / Ø / row and symmetric length (max) -> one position
    refs = [((sp['a'] + sp['b']) / 2.0, k) for k, sp in enumerate(B['sup'])]
    nS = len(B['sup'])
    for top in (True, False):
        grp = [x for x in dop if x['top'] == top]
        inner = []
        for x in grp:
            on = [k for c_, k in refs if x['u0'] - 1 <= c_ <= x['u1'] + 1]
            x['sk'] = on[0] if len(on) == 1 else None
            if x['sk'] is not None and 0 < x['sk'] < nS - 1: inner.append(x)
        if inner:
            ext = max(max(refs[x['sk']][0] - x['u0'], x['u1'] - refs[x['sk']][0]) for x in inner)
            n_ = max(x['n'] for x in inner); d_ = max(x['d'] for x in inner); r_ = max(x['row'] for x in inner)
            ext = math.ceil(ext / 100.0) * 100
            for x in inner:
                c_ = refs[x['sk']][0]
                x.update(u0=max(B['END0'] + 20, c_ - ext), u1=min(B['END1'] - 20, c_ + ext), n=n_, d=d_, row=r_)
    # merge dop that overlap on the same face
    dop.sort(key=lambda x: (not x['top'], x['u0']))
    mg = []
    for x in dop:
        if mg and mg[-1]['top'] == x['top'] and x['u0'] <= mg[-1]['u1'] + 300 and max(mg[-1]['u1'], x['u1']) - mg[-1]['u0'] <= 11700:
            y = mg[-1]; y['u1'] = max(y['u1'], x['u1']); y['n'] = max(y['n'], x['n']); y['d'] = max(y['d'], x['d']); y['row'] = max(y['row'], x['row'])
        else: mg.append(x)
    # identical bars share a position number
    keyof = lambda x: (x['top'], x['n'], x['d'], x['row'], round(x['u1'] - x['u0'], -1))
    seen = {}
    for x in mg:
        k_ = keyof(x)
        if k_ not in seen: seen[k_] = 2 + len(seen)
        x['pos'] = seen[k_]
        x.pop('sk', None)
    B['dop'] = mg
    return B


def parts(B, maxL=22500):
    sup = B['sup']
    out = []; i0 = 0; start = B['END0']
    while True:
        # farthest support j such that drawn length fits
        best = None
        for j in range(i0, len(sup)):
            endu = B['END1'] if j == len(sup) - 1 else sup[j]['b'] + 700
            st = start if i0 == 0 else sup[i0]['a'] - 700
            if endu - st <= maxL: best = j
        if best is None: best = i0
        if best == len(sup) - 1 or (B['END1'] - (sup[i0]['a'] - 700 if i0 else B['END0'])) <= maxL:
            out.append(dict(i0=i0, i1=len(sup) - 1, brkL=i0 > 0, brkR=False)); break
        if best <= i0: best = i0 + 1
        out.append(dict(i0=i0, i1=best, brkL=i0 > 0, brkR=True))
        i0 = best
    return out


def sections(B):
    """distinct reinforcement arrangements -> section words with mark positions (one per type per part)"""
    def at(u):
        t = [x for x in B['dop'] if x['top'] and x['u0'] <= u <= x['u1']]
        bo = [x for x in B['dop'] if not x['top'] and x['u0'] <= u <= x['u1']]
        return (tuple((x['pos'], x['n'], x['d'], x['row']) for x in t), tuple((x['pos'], x['n'], x['d'], x['row']) for x in bo))
    cand = []
    sup = B['sup']
    cur = B['END0']
    segs = []
    for sp in sup:
        if sp['kind'] != 'col' and sp['kind'] != 'beam': continue
        if sp['a'] > cur + 1: segs.append((cur, sp['a']))
        cur = max(cur, sp['b'])
    if B['END1'] > cur + 1: segs.append((cur, B['END1']))
    for a, b in segs:
        for u in (a + 650, (a + b) / 2.0, b - 650):
            if a + 300 < u < b - 300: cand.append(u)
    types = {}; order = []
    for u in cand:
        k = at(u)
        if k not in types: types[k] = []; order.append(k)
        types[k].append(u)
    secs = []
    for i, k in enumerate(order):
        sc = dict(word=str(i + 1), at=types[k], top=list(k[0]), bot=list(k[1]))
        secs.append(sc)
    return secs


def all_beams():
    out = {}
    for m in MK:
        B = build(m); B = design(m, B); B['parts'] = parts(B); B['secs'] = sections(B)
        out[m['mark']] = B
    return out


if __name__ == '__main__':
    A = all_beams()
    json.dump(A, open(S + r'\beams_auto.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for k, B in A.items():
        print(k, B['levels'][0], '%dx%d' % (B['b'], B['h']), 'L=%d' % (B['END1'] - B['END0']), 'sup', [(s['a'], s['b'], s['kind'][0], s.get('axn', '')) for s in B['sup']],
              'hoop Ø%d %d/%d' % (B['hoop']['d'], B['hoop']['s_end'], B['hoop']['s_mid']),
              'dop', [(x['pos'], 'T' if x['top'] else 'B', x['n'], x['d'], x['row'], x['u0'], x['u1']) for x in B['dop']], 'parts', len(B['parts']), 'secs', len(B['secs']))
