# Dop sheets 6.3–6.6 of Пм-1 = analog 5.1 sheets 5.3–5.6 style on the frame of 6.2:
# zone = first + last bar (analog line, layer диам10), SPDS position note across the bars (analog 3-point note),
# chain across the bars «binding | 200х(n-1)» at the bar start, chain along the last bar split at axes.
# python gen_dop.py <key> <sheet k> ; key bot_x|top_x|bot_y|top_y ; k = 3..6
import gx, json, os, sys, math
import gen62 as G
S = gx.S
SW = 59400.0
OX2, OY = G.OX, G.OY                     # sheet 6.2 plan origin
AXX = [0, 6800, 13250, 20050]
AXY = [0, 5000, 14750, 22750, 28750]
SX0, SY0, SX1, SY1 = G.SX0, G.SY0, G.SX1, G.SY1
TITLES = {'bot_x': 'нижней зоны по буквенным осям', 'top_x': 'верхней зоны по буквенным осям',
          'bot_y': 'нижней зоны по цифровым осям', 'top_y': 'верхней зоны по цифровым осям'}
T_BAR, T_NOTE, T_DV, T_DH = '2B8500', '2B8538', '2B8502', '2B851E'
FRAME = ['2B479C', '2B47A1', '2B47A2']


def positions(R):
    """Obsidian §позиции: dop numbered by unique Ø+L in sheet order низ букв → верх букв → низ цифр → верх цифр; from 2"""
    pos, k = {}, 2
    for key in ('bot_x', 'top_x', 'bot_y', 'top_y'):
        for z in sorted(R[key], key=lambda z: (z['d'], z['s1'] - z['s0'])):
            t = (z['d'], int(round(z['s1'] - z['s0'])))
            if t not in pos: pos[t] = k; k += 1
    return pos


def build(key, k, R, pos):
    dx = SW * (k - 2)
    X, Y = OX2 + dx, OY
    def P(a, b): return [X + a, Y + b, 0]
    x0 = 231579 + dx
    ops = [{'t': 'eraseregion', 'win': [x0 + 1, 455940, x0 + SW - 1, 497938]}]
    # frame, stamp, notes, title, sheet number
    for h in FRAME: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    name = 'Дополнительное армирование плиты перекрытия Пм-1 %s на отм -0.100' % TITLES[key]
    ops.append({'t': 'clone', 'h': '2B47A5', 'base': [0, 0], 'to': [dx - 2500, -650], 'text': '{\\L\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479D', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479F', 'base': [0, 0], 'to': [dx, 0], 'text': '6.%d' % k})
    # plan background = the 2.2 clones of sheet 6.2
    mp = gx.tagmap()
    for tg, h in mp.items():
        if tg.startswith('P62_'): ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    along_x = key.endswith('_x')
    TH = 300                                   # text height incl. gap, mm on the plan (2.5 mm × 100 + gap)

    def R_(a, b, c, d): return (min(a, c), min(b, d), max(a, c), max(b, d))

    def tw(t): return 175 * len(t) + 60

    def hit(r, occ, skip=()):
        return any(not (r[2] < o[0] or r[0] > o[2] or r[3] < o[1] or r[1] > o[3]) for i, o in enumerate(occ) if i not in skip)

    occ = []
    zl = R[key]
    bar_ix = {}
    for zi, z in enumerate(zl):            # all bars first
        bar_ix[zi] = []
        for p in sorted({z['p0'], z['p1']}):
            r = R_(z['s0'], p - 40, z['s1'], p + 40) if along_x else R_(p - 40, z['s0'], p + 40, z['s1'])
            bar_ix[zi].append(len(occ)); occ.append(r)
    for zi, z in enumerate(zl):
        n = z['n']; d = z['d']; L = int(round(z['s1'] - z['s0']))
        p0, p1, s0, s1 = z['p0'], z['p1'], z['s0'], z['s1']
        num = pos[(d, L)]
        own = set(bar_ix[zi])
        for p in sorted({p0, p1}):
            s, e = (P(s0, p), P(s1, p)) if along_x else (P(p, s0), P(p, s1))
            ops.append({'t': 'lineset', 'h': T_BAR, 's': s, 'e': e})
        # --- chain along a bar: above the last bar or below the first one
        ax2 = AXX if along_x else AXY
        pts = [s0] + [a for a in ax2 if s0 + 300 < a < s1 - 300] + [s1]
        segs = list(zip(pts, pts[1:]))
        chosen = None
        for side, base in ((1, p1), (-1, p0), (1, p1 + 400), (-1, p0 - 400)):
            off = 300 if side > 0 else -650
            rects = []
            for a2, b2 in segs:
                t = str(int(round(b2 - a2))); c = (a2 + b2) / 2
                tc = base + off + 180
                rects.append(R_(c - tw(t) / 2, tc - TH / 2, c + tw(t) / 2, tc + TH / 2) if along_x else R_(tc - TH / 2, c - tw(t) / 2, tc + TH / 2, c + tw(t) / 2))
            if not any(hit(r, occ, own) for r in rects): chosen = (base + off, rects); break
        if chosen is None: chosen = (p1 + 300, rects)
        for a2, b2 in segs:
            if along_x: ops.append({'t': 'dim', 'h': T_DH, 'p1': P(a2, p1 if chosen[0] > p1 else p0), 'p2': P(b2, p1 if chosen[0] > p1 else p0), 'dl': P(a2, chosen[0]), 'rot': 0, 'txt': ''})
            else: ops.append({'t': 'dim', 'h': T_DV, 'p1': P(p1 if chosen[0] > p1 else p0, a2), 'p2': P(p1 if chosen[0] > p1 else p0, b2), 'dl': P(chosen[0], a2), 'rot': math.pi / 2, 'txt': ''})
        occ += chosen[1]
        # --- chain across the bars: binding to the nearest axis/edge + 200х(n-1), at the start or the end of the bars
        axes = AXY if along_x else AXX
        edge0 = SY0 if along_x else SX0
        cand = [a for a in axes + [edge0] if a <= p0 - 100]
        b0 = max(cand) if cand else None
        cp = ([b0] if b0 is not None and 300 <= p0 - b0 < 6000 else []) + [p0] + ([p1] if p1 > p0 else [])
        csegs = list(zip(cp, cp[1:]))
        chosen = None
        for at, off in ((s0, -350), (s1, 350), (s0, -800), (s1, 800)):
            rects = []
            for a2, b2 in csegs:
                t = '200х%d' % (n - 1) if (a2, b2) == (p0, p1) else str(int(round(b2 - a2))); c = (a2 + b2) / 2
                tc = at + off + (-180 if off < 0 else 180)
                rects.append(R_(tc - TH / 2, c - tw(t) / 2, tc + TH / 2, c + tw(t) / 2) if along_x else R_(c - tw(t) / 2, tc - TH / 2, c + tw(t) / 2, tc + TH / 2))
            if not any(hit(r, occ, own) for r in rects): chosen = (at, at + off, rects); break
        if chosen is None: chosen = (s0, s0 - 350, rects)
        for a2, b2 in csegs:
            txt = '200х%d' % (n - 1) if (a2, b2) == (p0, p1) else ''
            if along_x: ops.append({'t': 'dim', 'h': T_DV, 'p1': P(chosen[0], a2), 'p2': P(chosen[0], b2), 'dl': P(chosen[1], a2), 'rot': math.pi / 2, 'txt': txt})
            else: ops.append({'t': 'dim', 'h': T_DH, 'p1': P(a2, chosen[0]), 'p2': P(b2, chosen[0]), 'dl': P(a2, chosen[1]), 'rot': 0, 'txt': txt})
        occ += chosen[2]
        # --- position note across the bars at a free place
        best = None
        mid = (p0 + p1) / 2
        for f in (0.5, 0.35, 0.65, 0.25, 0.75, 0.15, 0.85, 0.05, 0.95):
            c = s0 + f * (s1 - s0)
            r = R_(c - 1000, mid - 380, c - 20, mid + 380) if along_x else R_(mid - 1000, c - 380, mid - 20, c + 380)
            if not hit(r, occ, own): best = (c, r); break
        if best is None: best = (s0 + 0.5 * (s1 - s0), r)
        c = best[0]; occ.append(best[1])
        tg = 'N%s_%d' % (key, zi)
        ops.append({'t': 'clone', 'h': T_NOTE, 'tag': tg})
        if along_x: items = [[0, X + c, Y + mid], [1, X + c, Y + p1], [2, X + c, Y + p0]]
        else: items = [[0, X + mid, Y + c], [1, X + p1, Y + c], [2, X + p0, Y + c]]
        if p0 == p1:
            items[0] = [0, items[0][1] + (0 if along_x else 300), items[0][2] + (300 if along_x else 0)]
        ops.append({'t': 'spmove', 'h': tg, 'items': items})
        ops.append({'t': 'noteh', 'h': tg, 'l1': str(num), 'l2': 'ш.200'})
    ops.append({'t': 'save'})
    return ops


if __name__ == '__main__':
    R = json.load(open(os.path.join(S, 'arm', 'pm1_design.json')))
    pos = positions(R)
    json.dump({'%d_%d' % t: v for t, v in pos.items()}, open(os.path.join(S, 'arm', 'pm1_pos.json'), 'w'))
    key, k = sys.argv[1], int(sys.argv[2])
    out = gx.run(build(key, k, R, pos), 'dop_' + key)
    print(key, len(R[key]), [l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'eraseregion' in l][:12])
