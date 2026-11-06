# marks.json (design) -> sheet parts for b4rig.py
import json, os, math, sys
LIRA = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\9a1000cd-e0d9-42b2-b432-f6f3db0e7099\scratchpad\lira'
sys.path.insert(0, LIRA)
AXX = {0: '32', 650: '33', 6650: '34', 12650: '35', 18650: '36', 24850: '37', 31850: '38', 38850: '39', 44850: '40'}
AXY = {0: 'А', 9000: 'Б', 13900: 'В', 21000: 'Г', 27500: 'Д', 36000: 'Е', 39000: 'Ж'}
BX = {500: [55, 185, 315, 445], 350: [45, 130, 215, 300], 250: [45, 125, 205]}
STOCK = 11700
PMAX = 21500                 # longest part of a rigel on one A4x3 sheet at 1:50
SY = 420000.0
SX0 = 172179.0
KY = 455939.0
SSC = 2.5


def mk(M):
    r0 = M['runs'][0]
    E0abs = r0['E0']
    ax = AXX if M['dir'] == 'X' else AXY
    M['axes'] = [(c - E0abs, v) for c, v in sorted(ax.items()) if -1 <= c - E0abs <= M['E'] + 1]
    M['slab'] = 200
    M['bx'] = BX[M['b']]
    bx = M['bx']
    w = bx[2] - bx[0] + 40
    M['X1'] = [w + 100, w, M['h'] - 60, M['h'] + 40]
    M['SK'] = [250, M['h'] - 100, 250]
    M['clear'] = sum(b - a for a, b in M['spans'])
    # splice stations for bars longer than the stock length
    spl = []
    if M['E'] - 40 > STOCK:
        mids = [(a + b) / 2.0 for a, b in M['spans'] if b - a > 2500]
        axes = [u for u, _ in M['axes']] or [0.0]
        def nearest_ax(c): return max([u for u in axes if u <= c] or [axes[0]])
        start = 0.0
        while M['E'] - 40 - start > STOCK:
            cand = [c for c in mids if start + 1500 < c - 250 and c + 250 - start <= STOCK]
            if not cand: break
            c = max(cand); spl.append(('top', c, nearest_ax(c))); start = c - 250
        sups = [(a + b) / 2.0 for a, b, _ in M['sups']]
        start = 0.0
        while M['E'] - 40 - start > STOCK:
            cand = [x + 1100 for x in sups if start + 1500 < x + 1100 and x + 1600 - start <= STOCK and x + 1600 < M['E'] - 500]
            if not cand: break
            c = max(cand); spl.append(('bot', c, c - 1100)); start = c
    M['spl'] = spl
    # spec rows: доп positions + накладки
    rows = {}
    for d in M['dops']:
        rows.setdefault(d['pos'], [d['pos'], 28, d['L'], 0])[3] += d['n']
    M['specrows'] = [tuple(rows[k]) for k in sorted(rows, key=int)]
    if spl: M['specrows'].append(('Н4', 28, 280, len(spl) * M['n'] * 2))
    return M


def parts(M):
    """split at support centres into parts <= PMAX"""
    E = M['E']
    if E <= PMAX: return [(0.0, E)]
    cuts = [(a + b) / 2.0 for a, b, _ in M['sups']]
    n = int(math.ceil(E / PMAX))
    out = []; start = 0.0
    while E - start > PMAX:
        cand = [c for c in cuts if start + 3000 < c <= start + PMAX]
        tgt = start + (E - start) / math.ceil((E - start) / PMAX)
        c = min(cand, key=lambda c: abs(c - tgt))
        out.append((start, c)); start = c
    out.append((start, E))
    return out


def sections(M, u0, u1):
    """cuts of this part: one per distinct set of доп bars present (top/bottom), main-only first"""
    cand = []
    axes = [u for u, _ in M['axes']]
    spl = [c for _, c, _ in M.get('spl', [])]
    for z in M['zones']:
        a, b = max(z['fL'], u0), min(z['fR'], u1)
        if b - a < 800: continue
        for x in (a + 500, a + 800, (a + b) / 2.0, (a + b) / 2.0 + 400, b - 800, b - 500):
            if all(abs(x - q) > 1000 for q in axes) and all(abs(x - q) > 900 for q in spl) and u0 + 400 < x < u1 - 400:
                cand.append(x)
    seen = {}; out = []
    for x in cand:
        ds = tuple(sorted((d['pos'], d['top']) for d in M['dops'] if d['a'] + 100 <= x <= d['b'] - 100))
        if ds in seen: continue
        seen[ds] = x
    if not seen: seen[()] = (u0 + u1) / 2.0
    keys = sorted(seen, key=lambda k: (len(k) > 0, seen[k]))[:3]
    xs = sorted(seen[k] for k in keys)
    for i, x in enumerate(xs):
        dops = [d for d in M['dops'] if d['a'] + 100 <= x <= d['b'] - 100]
        out.append((str(i + 1), x, dops))
    return out


def place(M, secs, SX, splices, elev_len):
    """section origins (beam bottom-left), sheet units. One row, equal gaps, same baseline."""
    h, b = M['h'], M['b']
    top_lim = (465611 - KY) - (h - 550) - 350
    left = 2050.0; right = SSC * (b + 190) + 950
    below = SSC * 560 + 250; above = SSC * (h + 470) + 250
    bands = [((8900.0 if splices else 1300.0), 21900.0, 5400.0, top_lim), (10400.0, 21900.0, 3500.0, top_lim)]
    ee = 3003.0 + elev_len + 2500
    if ee < 16000: bands.append((ee, 21900.0, 3500.0, 14300.0))
    W = len(secs) * (left + right)
    for x0, x1, yb, yt in bands:
        if x0 + W <= x1 and yb + below + above <= yt:
            gap = min(1200.0, (x1 - x0 - W) / (len(secs) + 1))
            x = x0 + gap; out = []
            for s in secs:
                out.append([SX + x + left, SY + yb + below]); x += left + right + gap
            return out
    raise RuntimeError('no room for sections of %s (%d)' % (M['mark'], len(secs)))


def build(marks, first_no=1):
    sheets = []; k = 0
    for M in marks:
        mk(M)
        pp = parts(M)
        for i, (u0, u1) in enumerate(pp):
            SX = SX0 + 31500.0 * k
            spl = [q for q in M['spl'] if u0 + 300 < q[1] < u1 - 800]
            secs = sections(M, u0, u1)
            part = dict(P='B%d' % (k + 1), SX=SX, SY=SY, u0=u0, u1=u1, no='6.%d' % (first_no + k), secs=secs,
                        spl=spl, tables=(i == len(pp) - 1),
                        suffix='' if len(pp) == 1 else ' (%d/%d)' % (i + 1, len(pp)))
            while True:
                try:
                    part['secpos'] = place(M, secs, SX, bool(spl), u1 - u0); break
                except RuntimeError:
                    if len(secs) == 1: raise
                    # keep the cuts with the most доп bars
                    secs = sorted(sorted(secs, key=lambda q: -sum(d['n'] for d in q[2]))[:len(secs) - 1], key=lambda q: q[1])
                    secs = [(str(i + 1), x, ds) for i, (_, x, ds) in enumerate(secs)]
                    part['secs'] = secs
            sheets.append((M, part)); k += 1
    return sheets


if __name__ == '__main__':
    marks = json.load(open(os.path.join(LIRA, 'marks.json'), encoding='utf-8'))
    sh = build(marks)
    for M, p in sh:
        print(p['no'], M['mark'], M['level'], '%dx%d' % (M['b'], M['h']), 'u %.0f-%.0f' % (p['u0'], p['u1']), p['suffix'], 'secs', [(w, round(x)) for w, x, _ in p['secs']], 'spl', len(p['spl']))
    print(len(sh), 'sheets')
