# facade part 2: callouts, dop bars, splices, section marks, level, title
from rgen import *


def splices(B):
    """main-bar splice points (scheme coords) so that every piece <= 11700: top in mid-span, bottom near supports"""
    L = B['END1'] - B['END0'] - 40
    if L <= 11700: return [], []
    cols = [sp for sp in B['sup'] if sp['kind'] == 'col']
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
    bot = pick([sp['ax'] + 1100 + 250 for sp in cols if sp.get('ax') is not None] + [sp['ax'] - 1100 - 250 for sp in cols if sp.get('ax') is not None])
    return top, bot


def facade2(s, B, part, secmarks):
    A, add, D = s.A, s.add, s.D
    g = s.geo; X, YB, YT, YTB, YBB, yb, yu = g['X'], g['YB'], g['YT'], g['YTB'], g['YBB'], g['yb'], g['yu']
    u0, u1 = g['u0'], g['u1']
    on = lambda u: u0 - 1 <= u <= u1 + 1
    dd = B['main']['top'][1]
    # obstacles above the beam (vertical dim extension lines, axes) and placed shelves
    top_, bot_ = splices(B)
    obst = [sp['ax'] for sp in g['sup'] if sp.get('ax') is not None]
    obst += [e for dp in B.get('dop', []) if dp['top'] for e in (dp['u0'], dp['u1'])]
    obst += [c + d_ for c in top_ for d_ in (-250, 250)]
    obst += [c + d_ for c in bot_ for d_ in (-250, 250)]          # bottom comb leaders rise through the beam
    shelves = []
    def place_x(lo, hi, pref, left=False):
        L0, L1 = (650, 80) if left else (80, 700)
        cand = sorted(set([pref] + [pref + d_ for d_ in range(100, 6000, 100)] + [pref - d_ for d_ in range(100, 6000, 100)]), key=lambda v: abs(v - pref))
        for x in cand:
            if not (lo <= x <= hi): continue
            if any(x - L0 <= v <= x + L1 for v in obst): continue
            if any(not (x + L1 < a or x - L0 > b) for a, b in shelves): continue
            shelves.append((x - L0, x + L1)); return x
        shelves.append((pref - L0, pref + L1)); return pref
    s.place_x = place_x
    # dop bars (clones of analog pos 2) drawn 50 inside the main bar, callout + end dims
    k = 0
    for dp in B.get('dop', []):
        a, b = max(dp['u0'], u0), min(dp['u1'], u1)
        if b <= a + 1: continue
        k += 1
        y = (YTB - 50) if dp['top'] else (YBB + 50)
        tg = '%sDOP%d' % (s.P, k)
        add(t='clone', h=A(POS2['bar'][0]), base=[0, 0], to=[0, 0], tag=tg)
        add(t='plset', h=tg, p=[[X(a), y], [X(b), y]], layer='диам%d' % dp['d'])
        tn = '%sDOPN%d' % (s.P, k)
        add(t='clone', h=A(POS2['note'][0]), base=[0, 0], to=[0, 0], tag=tn)
        uc = place_x(a + 700, b - 150, a + 900 if dp['u0'] >= u0 else b - 600, left=True)
        xc = X(uc)
        add(t='spmove', h=tn, items=[[0, xc, yu(469289)], [1, xc, y]])
        add(t='mcset', h=tn, set={'FirstLine': str(dp['pos']), 'SecondLine': '(ф%d)' % dp['d']})
        # dims of the bar ends from the nearest axis
        for e, real in ((a, dp['u0'] >= u0 - 1), (b, dp['u1'] <= u1 + 1)):
            if not real: continue
            axs = [sp['ax'] for sp in g['sup'] if sp.get('ax') is not None]
            ax = min(axs, key=lambda q: abs(q - e))
            if abs(ax - e) < 300: continue
            td = '%sDOPD%d_%d' % (s.P, k, int(e))
            if dp['top']:
                add(t='clone', h=A('4038F1'), base=[0, 0], to=[0, 0], tag=td)
                add(t='dimpts', h=td, p1=[X(e), y, 0], p2=[X(ax), YT, 0], dl=[X(ax), yu(469559) + 0, 0])
            else:
                add(t='clone', h=A('403992'), base=[0, 0], to=[0, 0], tag=td)
                add(t='dimpts', h=td, p1=[X(e), y, 0], p2=[X(ax), YB, 0], dl=[X(ax), yb(467665), 0])
    add(t='erase', h=[A(h) for h in POS2['bar'] + POS2['note']])
    # «1 (ф25)» per clear segment (shelf above the beam), placed clear of dims / other shelves
    take, rest = pool(SPDS['n1'], s, 'N1')
    for a, b in g['segs']:
        x = X(place_x(a + 200, b - 900, (a + b) / 2.0))
        hn = take()
        add(t='spmove', h=hn, items=[[0, x, yu(469238.6)], [1, x, YBB], [2, x, YTB]])
        add(t='mcset', h=hn, set={'FirstLine': '1', 'SecondLine': '(ф%d)' % dd})
    add(t='erase', h=rest())
    # splices of the main bars (накладки Н3, staggered 2+2 bars, 500 apart)
    top, bot = splices(B)
    top = [c for c in top if on(c)]; bot = [c for c in bot if on(c)]
    def plate(h, c, y): add(t='plset', h=h, p=[[X(c) - 125, y - 15], [X(c) - 125, y + 15], [X(c) + 125, y + 15], [X(c) + 125, y - 15]], closed=True)
    used = []
    if top:
        c = top[0]; plate(A('4038F3'), c - 250, YTB); plate(A('4038F2'), c + 250, YTB)
        ev = [sp['ax'] for sp in g['sup'] if sp.get('ax') is not None] + [e for dp in B.get('dop', []) if dp['top'] for e in (dp['u0'], dp['u1'])]
        ax = max([e for e in ev if e < c - 250 - 1])
        add(t='dimpts', h=A('4038F1'), p1=[X(c - 250), YTB, 0], p2=[X(ax), YT, 0], dl=[X(ax), yu(469559), 0])
        add(t='dimpts', h=A('4038F5'), p1=[X(c + 250), YTB, 0], p2=[X(c - 250), YTB, 0], dl=[X(c - 250), yu(469559), 0])
        add(t='move', h=[A(SPDS['comb'][0])], d=[X(c - 250) - (185182 + D), 0])
        add(t='mcset', h=A(SPDS['comb'][0]), set={'FirstLine': 'Н3'})
        used += ['4038F3', '4038F2', '4038F1', '4038F5', SPDS['comb'][0]]
    for (p1, p2, d1, d2, cb, ax0), c in zip([('403948', '403947', '403992', '40394A', SPDS['comb'][1], 183682),
                                            ('4039A0', '40399F', '4039A5', '4039A2', SPDS['comb'][2], 192482)], bot):
        plate(A(p1), c - 250, YBB); plate(A(p2), c + 250, YBB)
        ev = [sp['ax'] for sp in g['sup'] if sp.get('ax') is not None] + [e for dp in B.get('dop', []) if not dp['top'] for e in (dp['u0'], dp['u1'])]
        ax = max([e for e in ev if e < c - 250 - 1])
        add(t='dimpts', h=A(d1), p1=[X(c - 250), YB, 0], p2=[X(ax), YB, 0], dl=[X(ax), yb(467665), 0])
        add(t='dimpts', h=A(d2), p1=[X(c + 250), YBB, 0], p2=[X(c - 250), YBB, 0], dl=[X(c - 250), yb(467665), 0])
        add(t='move', h=[A(cb)], d=[X(c - 250) - (ax0 + D), -150])
        add(t='mcset', h=A(cb), set={'FirstLine': 'Н3'})
        used += [p1, p2, d1, d2, cb]
    add(t='erase', h=[A(h) for h in PLATES + SPLD + SPDS['comb'] if h not in used])
    s.splices = (top, bot)
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
    add(t='move', h=[A(SPDS['title'])], d=[(X(u0) + X(u1)) / 2.0 - (185336 + D), 0])
    add(t='settext', h=A(SPDS['title']), s='Ригель ' + B['mark'] + (' (%d шт.)' % B['qty'] if B.get('qty', 1) > 1 else ''))
    # «Узел А» group lower, clear of the axis bubbles
    add(t='movewin', win=[172179 + D, 461900, 181979 + D, 465600], d=[0, -400])
