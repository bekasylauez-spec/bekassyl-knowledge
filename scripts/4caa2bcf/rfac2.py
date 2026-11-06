# facade part 2: callouts, dop bars, splices, section marks, level, title
from rgen import *


def splices(B):
    """main-bar splice points (scheme coords) so that every piece <= 11700: top in mid-span, bottom near supports"""
    L = B['END1'] - B['END0'] - 40
    if L <= 11700: return [], []
    cols = [sp for sp in B['sup'] if sp['kind'] in ('col', 'beam')]
    spans = [(cols[i]['b'], cols[i + 1]['a']) for i in range(len(cols) - 1)]
    def pick(cands):
        out = []; last = B['END0'] + 20
        for c in sorted(cands):
            if c - 250 - last > 11700 - 500: break
        # greedy: farthest candidate keeping pieces <= 11700
        res = []; pos = B['END0'] + 20
        while B['END1'] - 20 - pos > 11700:
            ok = [c for c in cands if pos + 1500 < c - 250 and c + 250 - pos <= 11700]
            if not ok: raise Exception('no splice place')
            c = max(ok); res.append(c); pos = c - 250
        return res
    top = pick([(a + b) / 2.0 for a, b in spans])
    rf = [sp.get('ax', (sp['a'] + sp['b']) / 2.0) for sp in cols]
    bot = pick([r + 1100 + 250 for r in rf] + [r - 1100 - 250 for r in rf])
    return top, bot


def facade2(s, B, part, secmarks):
    A, add, D = s.A, s.add, s.D
    g = s.geo; X, YB, YT, YTB, YBB, yb, yu = g['X'], g['YB'], g['YT'], g['YTB'], g['YBB'], g['yb'], g['yu']
    u0, u1 = g['u0'], g['u1']
    on = lambda u: u0 - 1 <= u <= u1 + 1
    dd = B['main']['top'][1]
    # obstacles above the beam (vertical dim extension lines, axes) and placed shelves
    top_, bot_ = splices(B)
    obst = [(sp['ax'] if sp.get('ax') is not None else (sp['a'] + sp['b']) / 2.0) for sp in g['sup']]
    obst += [e for dp in B.get('dop', []) if dp['top'] for e in (dp['u0'], dp['u1'])]
    obst += [c + d_ for c in top_ for d_ in (-250, 250)]
    obst += [c + d_ for c in bot_ for d_ in (-250, 250)]          # bottom comb leaders rise through the beam
    obst += [(sp['ax'] if sp.get('ax') is not None else (sp['a'] + sp['b']) / 2.0) for sp in g['sup']]
    obst += [e for dp in B.get('dop', []) for e in (dp['u0'], dp['u1'])]
    obst += [g['u0'] + d_ for d_ in range(-200, 1200, 100)] if not part['brkL'] else []   # level mark + Ск1 note at the start
    obst += [g['u1'] - d_ for d_ in range(0, 900, 100)] if not part['brkR'] else []
    shelves = []
    def place_x(lo, hi, pref, left=False, strict=False):
        L0, L1 = (800, 150) if left else (300, 850)
        cand = sorted(set([pref] + [pref + d_ for d_ in range(100, 6000, 100)] + [pref - d_ for d_ in range(100, 6000, 100)]), key=lambda v: abs(v - pref))
        for x in cand:
            if not (lo <= x <= hi): continue
            if any(x - L0 <= v <= x + L1 for v in obst): continue
            if any(not (x + L1 < a or x - L0 > b) for a, b in shelves): continue
            shelves.append((x - L0, x + L1)); return x
        if strict: return None
        for x in cand:
            if lo <= x <= hi and not any(not (x + L1 < a or x - L0 > b) for a, b in shelves):
                shelves.append((x - L0, x + L1)); return x
        shelves.append((pref - L0, pref + L1)); return pref
    s.place_x = place_x
    # dop bars (clones of analog pos 2) drawn 50 inside the main bar, callout + end dims
    k = 0; ev_end = []; noted = set()
    for dp in B.get('dop', []):
        a, b = max(dp['u0'], u0), min(dp['u1'], u1)
        if b <= a + 1: continue
        k += 1
        y = ((YTB - 50) if dp['top'] else (YBB + 50)) if dp.get('row', 1) == 1 else ((YTB - 95) if dp['top'] else (YBB + 95))
        tg = '%sDOP%d' % (s.P, k)
        add(t='clone', h=A(POS2['bar'][0]), base=[0, 0], to=[0, 0], tag=tg)
        add(t='plset', h=tg, p=[[X(a), y], [X(b), y]], layer='диам%d' % dp['d'])
        if dp['pos'] in noted:
            ev_end.append((dp['top'], a, y, dp['u0'] >= u0 - 1)); ev_end.append((dp['top'], b, y, dp['u1'] <= u1 + 1))
            continue
        noted.add(dp['pos'])
        tn = '%sDOPN%d' % (s.P, k)
        add(t='clone', h=A(POS2['note'][0]), base=[0, 0], to=[0, 0], tag=tn)
        uc = place_x(a + 700, b - 150, a + 900 if dp['u0'] >= u0 else b - 600, left=True, strict=True)
        if uc is not None:
            xc = X(uc)
            add(t='spmove', h=tn, items=[[0, xc, yu(469289) - 140], [1, xc, y]])
        else:
            add(t='erase', h=[tn]); tn = '%sDOPR%d' % (s.P, k)
            add(t='clone', h=A(SPDS['n1'][0]), base=[0, 0], to=[0, 0], tag=tn)
            uc = place_x(a + 150, b - 700, a + 400 if dp['u0'] >= u0 else b - 1100)
            xc = X(uc)
            add(t='spmove', h=tn, items=[[0, xc, yu(469238.6) - 140], [1, xc, y], [2, xc, y]])
        add(t='mcset', h=tn, set={'FirstLine': str(dp['pos']), 'SecondLine': '(ф%d)' % dp['d']})
        ev_end.append((dp['top'], a, y, dp['u0'] >= u0 - 1)); ev_end.append((dp['top'], b, y, dp['u1'] <= u1 + 1))
    add(t='erase', h=[A(h) for h in POS2['bar'] + POS2['note']])
    for c in top_ + bot_: shelves.append((c - 250 - 150, c - 250 + 1250))
    # «1 (ф25)» per clear segment (shelf above the beam), placed clear of dims / other shelves
    take, rest = pool(SPDS['n1'], s, 'N1')
    longest = max(g['segs'], key=lambda t: t[1] - t[0]) if g['segs'] else None
    for a, b in g['segs']:
        if b - a < 2500 and (a, b) != longest: continue
        x = X(place_x(a + 200, b - 900, (a + b) / 2.0))
        hn = take()
        add(t='spmove', h=hn, items=[[0, x, yu(469238.6) - 140], [1, x, YBB], [2, x, YTB]])
        add(t='mcset', h=hn, set={'FirstLine': '1', 'SecondLine': '(ф%d)' % dd})
    add(t='erase', h=rest())
    # splices of the main bars (накладки Н3, staggered 2+2 bars, 500 apart)
    top, bot = splices(B)
    top = [c for c in top if on(c)]; bot = [c for c in bot if on(c)]
    def plate(h, c, y): add(t='plset', h=h, p=[[X(c) - 125, y - 15], [X(c) - 125, y + 15], [X(c) + 125, y + 15], [X(c) + 125, y - 15]], closed=True)
    used = []
    if top:
        c = top[0]; plate(A('4038F3'), c - 250, YTB); plate(A('4038F2'), c + 250, YTB)
        ev = [(sp['ax'] if sp.get('ax') is not None else (sp['a'] + sp['b']) / 2.0) for sp in g['sup']] + [e for dp in B.get('dop', []) if dp['top'] for e in (dp['u0'], dp['u1'])]
        ax = max([e for e in ev if e < c - 250 - 1])
        add(t='move', h=[A(SPDS['comb'][0])], d=[X(c - 250) - (185182 + D), 0])
        add(t='mcset', h=A(SPDS['comb'][0]), set={'FirstLine': 'Н%d' % {20: 1, 22: 2, 25: 3, 28: 4, 32: 5}[B['main']['top'][1]]})
        used += ['4038F3', '4038F2', SPDS['comb'][0]]
    for (p1, p2, d1, d2, cb, ax0), c in zip([('403948', '403947', '403992', '40394A', SPDS['comb'][1], 183682),
                                            ('4039A0', '40399F', '4039A5', '4039A2', SPDS['comb'][2], 192482)], bot):
        plate(A(p1), c - 250, YBB); plate(A(p2), c + 250, YBB)
        ev = [(sp['ax'] if sp.get('ax') is not None else (sp['a'] + sp['b']) / 2.0) for sp in g['sup']] + [e for dp in B.get('dop', []) if not dp['top'] for e in (dp['u0'], dp['u1'])]
        ax = max([e for e in ev if e < c - 250 - 1])
        add(t='move', h=[A(cb)], d=[X(c - 250) - (ax0 + D), -150])
        add(t='mcset', h=A(cb), set={'FirstLine': 'Н%d' % {20: 1, 22: 2, 25: 3, 28: 4, 32: 5}[B['main']['top'][1]]})
        used += [p1, p2, cb]
    add(t='erase', h=[A(h) for h in PLATES + SPDS['comb'] if h not in used])
    s.splices = (top, bot)
    # one dimension chain above (dop top ends + top splice plates) and one below, closed on the nearest axes
    refs = [(sp['ax'] if sp.get('ax') is not None else (sp['a'] + sp['b']) / 2.0) for sp in g['sup']]
    for face in (True, False):
        ev = [(u, y) for f_, u, y, real in ev_end if f_ == face and real]
        ev += [(c + d_, YTB if face else YBB) for c in (top if face else bot) for d_ in (-250, 250)]
        if not ev: continue
        pts = {round(u): (u, y, 'e') for u, y in ev}
        for r in refs:
            if u0 - 1 <= r <= u1 + 1 and round(r) not in pts: pts[round(r)] = (r, YT if face else YB, 'a')
        L_ = [pts[k_] for k_ in sorted(pts)]
        keep = [p for i, p in enumerate(L_) if p[2] == 'e' or (i > 0 and L_[i - 1][2] == 'e') or (i + 1 < len(L_) and L_[i + 1][2] == 'e')]
        for i, (p, q) in enumerate(zip(keep, keep[1:])):
            if p[2] == 'a' and q[2] == 'a': continue
            if q[0] - p[0] < 1: continue
            td = '%sCH%d_%d' % (s.P, 1 if face else 0, i)
            src = '4038F1' if face else '403992'
            row = yu(469559) if face else yb(467665)
            add(t='clone', h=A(src), base=[0, 0], to=[0, 0], tag=td)
            add(t='dimpts', h=td, p1=[X(q[0]), q[1], 0], p2=[X(p[0]), p[1], 0], dl=[X(p[0]), row, 0])
            zl = [zx for L_z in g['ZI'] for zx in L_z]
            mid = (p[0] + q[0]) / 2.0
            if not face and q[0] - p[0] >= 800 and any(abs(mid - zx) < 320 for zx in zl):
                for dx_ in (400, -400, 650, -650):
                    if p[0] + 250 < mid + dx_ < q[0] - 250 and all(abs(mid + dx_ - zx) > 320 for zx in zl):
                        add(t='dimtx', h=td, at=[X(mid + dx_), row + 60, 0], tmove=2); break
            if q[0] - p[0] < 800:
                nxt = keep[i + 2][0] if i + 2 < len(keep) else None
                side = 1 if (nxt is None or nxt - q[0] > 1500) else -1
                tx = X(q[0]) + 330 if side > 0 else X(p[0]) - 330
                add(t='dimtx', h=td, at=[tx, row + (60 if i % 2 == 0 else 230) * (1 if face else -1) + (0 if face else 120), 0], tmove=2)
    add(t='erase', h=[A(h) for h in SPLD])
    # step note, height dim «55» at the top
    add(t='move', h=[A(SPDS['step'])], d=[g['eb'] + 20 - (196582 + D), -150])
    add(t='mcset', h=A(SPDS['step']), set={'FirstLine': 'Шаг хомута', 'SecondLine': 'Х1(ф%d)' % B['hoop']['d']})
    xl = X(u0)
    add(t='dimpts', h=A('4015A9'), p1=[xl + 20, YTB, 0], p2=[xl, YT, 0], dl=[xl - 562, YT, 0])
    # section marks: secmarks = [(u, word)]
    take, rest = pool(SPDS['sec'], s, 'SEC')
    for u, w in secmarks:
        if not on(u): continue
        hs_ = take()
        add(t='sp_set', h=hs_, pts=[[0, X(u), yu(469793.5) + 300], [1, X(u), yb(465833.7)]])
        add(t='mcset', h=hs_, set={'Word': w})
    add(t='erase', h=rest())
    # level: single level mark (analog −0.100) moved to the beam start, multilayer erased
    add(t='erase', h=[A(SPDS['ml'])])
    add(t='move', h=[A(SPDS['lm'])], d=[xl + 500 - (175582 + D), YT - 468700])
    add(t='levelval', h=A(SPDS['lm']), old='-0.100', value=B['levels'][0], tag=A(SPDS['lm']))
    # title centred over the drawing
    add(t='move', h=[A(SPDS['title'])], d=[(X(u0) + X(u1)) / 2.0 - (185336 + D), 350])
    ttl = 'Ригель ' + B['mark']
    if len(B['parts']) > 1:
        an = [sp.get('axn') for sp in g['sup'] if sp.get('axn')]
        if an: ttl += ' (оси %s - %s)' % (an[0], an[-1])
    if B.get('qty', 1) > 1: ttl += ', %d шт.' % B['qty']
    add(t='settext', h=A(SPDS['title']), s=ttl, w=9000)
    # «Узел А» group lower, clear of the axis bubbles
    add(t='movewin', win=[172179 + D, 461900, 181979 + D, 465600], d=[0, -400])
