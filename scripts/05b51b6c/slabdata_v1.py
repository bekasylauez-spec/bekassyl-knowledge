"""Slabs: Пм-1 (по грунту, 0.000, t=120, 2 сетки Ø12 ш.200) and Пм-2 (+6.200 / уклон к оси 8, t=200, Ø14 ш.200 верх+низ, доп. 2Ø14 у проёмов)."""
import math
import beams_ob as BO

KG = {12: 0.888, 14: 1.208}
STOCK = 11700
LAP = {12: 730, 14: 860}
SL = BO.SLAB62                                      # (-350, -450, 32350, 12450)
OPEN = BO.OPEN62
STEP = 200
C0 = 50


def intervals(a, b, cuts):
    """[a, b] minus cuts [(c0, c1)] -> list of intervals"""
    out = [(a, b)]
    for c0, c1 in cuts:
        nxt = []
        for p, q in out:
            if c1 <= p or c0 >= q: nxt.append((p, q)); continue
            if c0 > p: nxt.append((p, c0 - 30))
            if c1 < q: nxt.append((c1 + 30, q))
        out = nxt
    return [(p, q) for p, q in out if q - p > 300]


def bar_len(L, d):
    n = 1 if L <= STOCK else math.ceil((L - STOCK) / (STOCK - LAP[d])) + 1
    return L + (n - 1) * LAP[d]


def mesh(x0, y0, x1, y1, openings, d):
    """one layer, both directions: total length (mm) incl. laps, bars along X and along Y"""
    tot = 0; nx = ny = 0
    y = y0 + C0
    while y <= y1 - C0 + 1:
        cuts = [(o[0], o[2]) for o in openings if o[1] - 30 <= y <= o[3] + 30]
        for p, q in intervals(x0 + 30, x1 - 30, cuts): tot += bar_len(q - p, d); nx += 1
        y += STEP
    x = x0 + C0
    while x <= x1 - C0 + 1:
        cuts = [(o[1], o[3]) for o in openings if o[0] - 30 <= x <= o[2] + 30]
        for p, q in intervals(y0 + 30, y1 - 30, cuts): tot += bar_len(q - p, d); ny += 1
        x += STEP
    return tot, nx, ny


def pm1():
    x0, y0, x1, y1 = SL
    L, nx, ny = mesh(x0, y0, x1, y1, [], 12)
    area = (x1 - x0) * (y1 - y0) / 1e6
    pos = [('1', 12, None, round(2 * L / 1000, 1), 'сетки верх и низ, ш.200')]
    return dict(t=120, pos=pos, conc=area * 0.12, area=area, nx=nx, ny=ny)


def pm2():
    x0, y0, x1, y1 = SL
    ops = list(OPEN.values())
    L, nx, ny = mesh(x0, y0, x1, y1, ops, 14)
    area = (x1 - x0) * (y1 - y0) / 1e6 - sum((o[2] - o[0]) * (o[3] - o[1]) for o in ops) / 1e6
    n_add = 0; L_add = 0
    for o in ops:
        for side in ((o[2] - o[0]), (o[2] - o[0]), (o[3] - o[1]), (o[3] - o[1])):
            L_add += (side + 2 * 600) * 2 * 2      # 2 bars, top + bottom
            n_add += 4
    pos = [('1', 14, None, round(L / 1000, 1), 'низ, ш.200 в обоих направлениях'),
           ('2', 14, None, round(L / 1000, 1), 'верх, ш.200 в обоих направлениях'),
           ('3', 14, None, round(L_add / 1000, 1), 'доп. у проёмов 2%%C14 с каждой стороны')]
    return dict(t=200, pos=pos, conc=area * 0.2, area=area, nx=nx, ny=ny)


if __name__ == '__main__':
    for nm, f in (('Пм-1', pm1), ('Пм-2', pm2)):
        s = f(); m = sum(p[3] * KG[p[1]] for p in s['pos'])
        print(nm, s['pos'], 'kg %.0f conc %.2f area %.1f' % (m, s['conc'], s['area']), s['nx'], s['ny'])
