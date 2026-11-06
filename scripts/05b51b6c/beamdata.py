"""Beams Бм-1…Бм-17 (sections as on sheets 2.3/2.4 = max of LIRA on the line). Reinforcement by Bekassyl's ригель rules, «с запасом»:
b<=300: 3+3; b>300: >=4+4 with 2 hoops each covering 3 bars (shared middle). Side bars Ø12 for h>=700. Hoops Ø10 A500С, zones 100/200/100 per span.
Ends: П-скобы Ск1 Ø16 (legs 10d of the main bar). Main bars continuous, joints by накладки Н (2 per joint, 10d) every 11700."""
import math, sys
sys.path.insert(0, r'D:\РАБОЧКА\Bekassyl\15_Проекты\ЖК Галакси\Инструменты')
import colgeo
import beams_ob as BO

KG = {10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853, 28: 4.834}
AX, AY = BO.AX, BO.AY
COLW = (700, 900)                          # column along X / along Y
STOCK = 11700
COV = 50                                   # to the bar axis (40 + Ø/2 rounded)


def lvl(mark):
    return 'B62' if mark in BO.B62 else 'B114'


def group(mark):
    return BO.B62 if mark in BO.B62 else BO.B114


def arm(b, h):
    d = 28                                                   # user 06.11: all main bars Ø28
    if b <= 300: nb = 3
    elif b <= 450: nb = 4
    else: nb = 5
    side = 0 if h < 700 else (1 if h < 800 else 2)        # per face
    hoops = 1 if b <= 300 else 2
    return dict(n=nb, d=d, side=side, hoops=hoops)


def supports(mark, seg):
    """supports along a segment: list of (pos along the segment axis, width along the beam, kind)"""
    x0, y0, x1, y1 = seg
    G = group(mark)
    hown = G[mark][1]
    alongX = y0 == y1
    ok = lambda hh, p, a, c: hh > hown or abs(p - a) < 1 or abs(p - c) < 1
    S = []
    if alongX:
        for x in AX:
            if x0 - 1 <= x <= x1 + 1 and y0 in AY: S.append((x, COLW[0], 'col'))
        for mk, (b, h, lv, segs) in G.items():
            for (a0, b0, a1, b1) in segs:
                if a0 == a1 and min(b0, b1) - 1 <= y0 <= max(b0, b1) + 1 and x0 - 1 <= a0 <= x1 + 1 and ok(h, a0, x0, x1) and not any(abs(s[0] - a0) < 1 for s in S):
                    S.append((a0, b, mk))
    else:
        for y in AY:
            if y0 - 1 <= y <= y1 + 1 and x0 in AX: S.append((y, COLW[1], 'col'))
        for mk, (b, h, lv, segs) in G.items():
            for (a0, b0, a1, b1) in segs:
                if b0 == b1 and min(a0, a1) - 1 <= x0 <= max(a0, a1) + 1 and y0 - 1 <= b0 <= y1 + 1 and ok(h, b0, y0, y1) and not any(abs(s[0] - b0) < 1 for s in S):
                    S.append((b0, b, mk))
    return sorted(S)


def hoops(a, b):
    if b - a >= 3000:
        p, z, s = colgeo.storey_hoops(a, b)
        return p
    S = b - a - 100                                  # first and last hoop 50 from the faces
    k = int(S // 100); r = S - 100 * k
    steps = [100.0] * k
    if r > 1e-6: steps.insert(len(steps) // 2, r)     # remainder inside the zone, not at the end
    pos = [a + 50]
    for st in steps: pos.append(pos[-1] + st)
    return pos


def line_data(mark, seg):
    b, h, lv, segs = group(mark)[mark]
    x0, y0, x1, y1 = seg
    S = supports(mark, seg)
    s0, s1 = (x0, x1) if y0 == y1 else (y0, y1)
    if not S or abs(S[0][0] - s0) > 1: S.insert(0, (s0, 0, 'end'))
    if abs(S[-1][0] - s1) > 1: S.append((s1, 0, 'end'))
    e0 = S[0][0] - S[0][1] / 2; e1 = S[-1][0] + S[-1][1] / 2          # beam ends = outer faces of the end supports
    spans = [(p[0] + p[1] / 2, q[0] - q[1] / 2) for p, q in zip(S, S[1:])]
    hz = [hoops(a, c) for a, c in spans]
    return dict(S=S, e0=e0, e1=e1, spans=spans, hz=hz, L=e1 - e0, clear=sum(c - a for a, c in spans))


def lap_count(L):
    return 0 if L <= STOCK else math.ceil((L - STOCK) / (STOCK - 0))


def schedule(mark):
    b, h, lv, segs = group(mark)[mark]
    A = arm(b, h)
    tot = dict(L1=0, L3=0, nh=0, nsk=0, nn=0, clear=0)
    lines = []
    for seg in segs:
        D = line_data(mark, seg); lines.append(D)
        Lb = D['L'] - 2 * 30
        tot['L1'] += Lb * A['n'] * 2
        tot['L3'] += Lb * A['side'] * 2
        tot['nh'] += sum(len(z) for z in D['hz'])
        tot['nsk'] += 2 * A['n']
        tot['nn'] += lap_count(Lb) * A['n'] * 2 * 2
        tot['clear'] += D['clear']
    leg = 10 * A['d']
    hx = (b - 2 * 30, h - 2 * 30)                                   # hoop centreline ~ (b-60) x (h-60)
    if A['hoops'] == 2:
        sp = (b - 2 * COV) / (A['n'] - 1)
        w2 = round(2 * sp + A['d'] + 10)                            # covers 3 bars
        hx1 = (w2, hx[1])
    else:
        hx1 = hx
    pos = [('1', A['d'], None, round(tot['L1'] / 2 / 1000, 1), 'низ, %d стержней' % A['n']),
           ('2', A['d'], None, round(tot['L1'] / 2 / 1000, 1), 'верх, %d стержней' % A['n'])]
    if A['side']: pos.append(('3', 12, None, round(tot['L3'] / 1000, 1), 'боковые %d+%d' % (A['side'], A['side'])))
    pos.append(('Х1', 10, 2 * sum(hx1) + 200, tot['nh'] * A['hoops'], 'хомут'))
    if A['side']: pos.append(('Шп1', 10, int(math.ceil(((b - 2 * COV) + 12 + 10 + 200) / 10) * 10), tot['nh'] * A['side'], 'шпилька боковых, на каждом хомуте'))
    pos.append(('Ск1', 16, (h - 2 * COV) + 2 * leg, tot['nsk'], 'П-скоба на концах'))
    if tot['nn']: pos.append(('Н', A['d'], 10 * A['d'], tot['nn'], 'накладки'))
    conc = b * h * tot['clear'] / 1e9
    return dict(b=b, h=h, lv=lv, segs=segs, A=A, lines=lines, pos=pos, hx1=hx1, leg=leg, conc=conc)


if __name__ == '__main__':
    G = {**BO.B62, **BO.B114}
    tot_all = 0
    for mk in G:
        s = schedule(mk)
        m = sum(((p[2] / 1000) if p[2] else 1) * p[3] * KG[p[1]] for p in s['pos'])
        tot_all += m
        L0 = s['lines'][0]
        print(mk, '%dx%d' % (s['b'], s['h']), s['lv'], 'n=%d Ø%d side %d hoops %d' % (s['A']['n'], s['A']['d'], s['A']['side'], s['A']['hoops']),
              'lines', len(s['segs']), 'spans', [round(c - a) for a, c in L0['spans']], 'S', [(round(q[0]), q[1], q[2]) for q in L0['S']], 'kg %.0f' % m)
    print('all beams kg %.0f' % tot_all)
