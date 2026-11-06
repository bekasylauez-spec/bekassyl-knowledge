# mark (design in relative u from endL) -> sheet fragments F for rig.build / rigsec / rigtab
import json, math
import sys
sys.path.insert(0, r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad\w')
AXX = [(0, '1'), (6000, '2'), (12000, '3'), (18000, '4'), (24000, '5'), (30000, '6'), (36000, '7'), (42000, '8'), (47500, '9'), (53500, '10'), (59500, '11'), (65900, '12'), (73100, '13'), (73750, '14')]
AXY = [(0, 'А'), (9000, 'Б'), (13900, 'В'), (21000, 'Г'), (27500, 'Д'), (36000, 'Е'), (39000, 'Ж')]
LEV = {-0.05: '-0.050', 4.5: '+4.500', 7.0: '+7.000'}
STOCK = 11700.0
import os
LINES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'w', 'lines2.json')))
MAXF = 21400.0


def supports(m):
    """supports in relative u: (f0, f1, kind, axis label, u axis); first/last = end supports"""
    r, p0 = m['r'], m['p0']
    E0 = p0['endL']
    ax = AXX if p0['d'] == 'X' else AXY
    sp = r['spans']
    faces = [(r['endL'], sp[0][0])] + [(sp[i][1], sp[i + 1][0]) for i in range(len(sp) - 1)] + [(sp[-1][1], r['endR'])]
    import design as DD
    ln = dict(z=p0['z'], d=p0['d'], c=p0['c'])
    fx = []
    for i, (a, b) in enumerate(faces):
        cs = DD.colsat(ln, E0 + (a + b) / 2.0)
        if cs:
            a2, b2 = min(c[0] for c in cs) - E0, max(c[1] for c in cs) - E0
            if i == 0: a2 = 0.0
            if i == len(faces) - 1: b2 = r['endR']
            fx.append((max(a2, fx[-1][1] + 100 if fx else -1e9), b2))
        else:
            fx.append((a, b))
    # beam supports at the ends: the whole supporting beam (width of an interior support, else 500)
    def cross(uabs):
        # perpendicular scheme beam at this point: (centre, width)
        best = None
        for l2 in LINES:
            if round(l2['z'], 2) != round(p0['z'], 2) or l2['d'] == p0['d']: continue
            if abs(l2['c'] - uabs) > 400: continue
            if not (l2['segs'][0][0] - 700 <= p0['c'] <= l2['segs'][-1][1] + 700): continue
            if best is None or abs(l2['c'] - uabs) < abs(best[0] - uabs): best = (l2['c'], l2['b'])
        return best
    for k in (0, len(fx) - 1):
        a, b = fx[k]
        if DD.colsat(ln, E0 + (a + b) / 2.0): continue
        cb = cross(E0 + (b if k == 0 else a) + (-125 if k == 0 else 125))
        if cb: fx[k] = (cb[0] - cb[1] / 2.0 - E0, cb[0] + cb[1] / 2.0 - E0)
        else: fx[k] = (b - 500, b) if k == 0 else (a, a + 500)
    off = -fx[0][0]
    faces = [(a + off, b + off) for a, b in fx]
    E0 = E0 - off
    out = []
    for i, (a, b) in enumerate(faces):
        import design as DD
        kind = 'col' if DD.colsat(dict(z=p0['z'], d=p0['d'], c=p0['c']), E0 + (a + b) / 2.0) else 'beam'
        uc = (a + b) / 2.0
        lab = [n for q, n in ax if abs(E0 + uc - q) < 450]
        out.append((a, b, kind, lab[0] if lab else None, (lab and [q for q, n in ax if n == lab[0]][0] - E0) or uc))
    m['_off'] = off
    return out


def splices(sup, e0, e1, top):
    """groups (centre u, reference axis u): top in span middles, bottom at axis + 1350"""
    if e1 - e0 <= STOCK: return []
    spans = [(sup[i][1], sup[i + 1][0]) for i in range(len(sup) - 1)]
    if top: cand = [((a + b) / 2.0, [s[4] for s in sup if s[4] <= a][-1] if any(s[4] <= a for s in sup) else a) for a, b in spans]
    else: cand = [(s[4] + 1350.0, s[4]) for s in sup[:-1] if s[3]]
    out = []; s = e0
    while e1 - s > STOCK - 300:
        ok = [c for c in cand if c[0] + 250 - s <= STOCK - 300 and c[0] - 250 > s + 1000]
        if not ok: break
        c = max(ok, key=lambda q: q[0]); out.append(c); s = c[0] - 250
    return out


def build_F(m, mark, posmap=None):
    r, p0 = m['r'], m['p0']
    sup = supports(m)
    n = r['n']
    F = dict(mark=mark, level=LEV[round(p0['z'], 2)], h=p0['h'], b=p0['b'], top=dict(n=n, d=r['top']['d'], pos='1'),
             bot=dict(n=n, d=r['bot']['d'], pos='1' if r['bot']['d'] == r['top']['d'] else '2'),
             sk=dict(d=16, pos='Ск1'), hoop=dict(d=r['hoop']['d'], pos='Х1'))
    # доп positions by unique (Ø, L)
    nxt = 2 if F['bot']['pos'] == '1' else 3
    pos = {}
    dop = []
    for key in ('top', 'bot'):
        zs = r[key]['dop']
        if not zs: continue
        Lmax = max(z['u1'] - z['u0'] for z in zs)
        p_ = str(nxt); nxt += 1
        for z in zs:
            off = m.get('_off', 0.0)
            c = (z['u0'] + z['u1']) / 2.0 + off
            u0 = max(sup[0][0] + 30, c - Lmax / 2.0); u1 = min(sup[-1][1] - 30, u0 + Lmax); u0 = u1 - Lmax
            dop.append(dict(pos=p_, top=key == 'top', u0=u0, u1=u1, k=min(z['k'], n - 1), kk=z['k'], d=z['d'], nx=c, L=Lmax))
    F['dopall'] = dop
    e0, e1 = sup[0][0] + 20, sup[-1][1] - 20
    F['splall'] = dict(top=splices(sup, e0, e1, True), bot=splices(sup, e0, e1, False))
    F['supall'] = sup
    return F


LASTF = 17000.0          # the sheet with the tables: facade must end left of the spec table


def fragments(F):
    """split supports into sheets; cut at a support (shown on both sheets); last sheet (tables) <= LASTF"""
    sup = F['supall']; n = len(sup)
    npos = 3 + (0 if F['top']['d'] == F['bot']['d'] else 1) + len(set(d['pos'] for d in F['dopall'])) + len(set([F['top']['d']] if F['splall']['top'] else []) | set([F['bot']['d']] if F['splall']['bot'] else []))
    LASTF = 17000.0 if npos > 5 else 19000.0
    if sup[-1][1] - sup[0][0] <= LASTF: return [(0, n - 1)]
    i0 = n - 2
    while i0 > 0 and sup[-1][1] - sup[i0 - 1][0] + 600 <= LASTF: i0 -= 1
    out = [(i0, n - 1)]
    L = sup[i0][1] - sup[0][0]
    k = max(1, math.ceil(L / (MAXF - 600)))
    tgt = L / k
    pre = []; i = 0
    while i < i0:
        j = i + 1
        while j < i0 and sup[j + 1][1] - sup[i][0] <= min(MAXF - 600, tgt * 1.2): j += 1
        pre.append((i, j)); i = j
    return pre + out


def sheetF(F, frag):
    i, j = frag
    sup = F['supall']
    G = dict(F)
    cutL, cutR = i > 0, j < len(sup) - 1
    G['u0'] = sup[i][0] - (600 if cutL else 0)
    G['u1'] = sup[j][1] + (600 if cutR else 0)
    G['endL'] = 'cut' if cutL else 'end'; G['endR'] = 'cut' if cutR else 'end'
    G['sup'] = sup[i:j + 1]
    inr = lambda u: G['u0'] < u < G['u1']
    G['dop'] = [d for d in F['dopall'] if d['u1'] > G['u0'] and d['u0'] < G['u1']]
    G['dop'] = [dict(d, u0=max(d['u0'], G['u0']), u1=min(d['u1'], G['u1']), nx=min(max(d['nx'], G['u0'] + 600), G['u1'] - 600)) for d in G['dop']]
    G['spl'] = dict(top=[c for c in F['splall']['top'] if inr(c[0])], bot=[c for c in F['splall']['bot'] if inr(c[0])])
    # sections: one per span (+ near supports with top доп); words global per mark (same word = same bars on every sheet)
    W = F.setdefault('words', {})
    spans = [(G['sup'][q][1], G['sup'][q + 1][0]) for q in range(len(G['sup']) - 1)]
    conf = []
    busy = [(min(ua, c - 250) - 200, max(ua, c + 250) + 200) for c, ua in G['spl']['top']] + [(c - 450, c + 450) for c, ua in G['spl']['bot']]
    dist = lambda x: min([0 if p <= x <= q else min(abs(x - p), abs(x - q)) for p, q in busy] + [1e9])
    for a, b in spans:
        cand = [a + (b - a) * t for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8, 0.12, 0.88)]
        conf.append(max(cand, key=dist))
        if any(d['top'] and d['u0'] < a + 600 < d['u1'] for d in F['dopall']) and q_not_first(G, a): conf.append(a + 600)
    secs = []; used = []
    for u in sorted(set(round(x) for x in conf)):
        if not (G['u0'] < u < G['u1']): continue
        dt = [d for d in F['dopall'] if d['top'] and d['u0'] < u < d['u1']]
        db = [d for d in F['dopall'] if not d['top'] and d['u0'] < u < d['u1']]
        key = (sum(d['k'] for d in dt), sum(d['k'] for d in db), dt[0]['d'] if dt else 0, db[0]['d'] if db else 0)
        if key not in W: W[key] = (str(len(W) + 1), dict(top=[[], dt[0]['d']] if dt else None, bot=[[], db[0]['d']] if db else None))
        for kk, lst in (('top', dt), ('bot', db)):
            for d in lst:
                if d['pos'] not in W[key][1][kk][0]: W[key][1][kk][0].append(d['pos'])
        secs.append((W[key][0], u))
        if key not in used: used.append(key)
    G['secs'] = secs
    G['secdefs'] = [(W[k][0], k[0], k[1], {kk: ((';'.join(sorted(v[0], key=int)), v[1]) if v else None) for kk, v in W[k][1].items()}) for k in sorted(used, key=lambda k: int(W[k][0]))]
    return G


def q_not_first(G, a):
    return abs(a - G['sup'][0][1]) > 1
