"""Фм-1 (as in LIRA): pads ФП 2000(X)x3000(Y)x1000, -1.500...-0.500; tie beams ЛФ 350x600 on all axes, axis -1.000 (-1.300...-0.700).
Reinforcement «с запасом». Positions numbered for the АБК-style set: 3.2 (along letter axes = X), 3.3 (digit axes = Y), 3.4 hoops, 3.5 spec, 3.6 dowels."""
import math, sys
sys.path.insert(0, r'D:\РАБОЧКА\Bekassyl\15_Проекты\ЖК Галакси\Инструменты')
import colgeo

KG = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 28: 4.834}
AX = [0, 3250, 7750, 12250, 16750, 20000, 26000, 32000]
AY = [0, 6000, 12000]
PX, PY, PH = 2000, 3000, 1000           # pad
BB, BH = 350, 600                       # beam
STOCK = 11700
LAP = {20: 1220, 12: 730, 16: 980}      # 61d, B25 (lap table of the analog)


def gbot(L, step=150, c=50):
    xs = list(range(c, L - c, step)); xs.append(L - c); return xs


def gtop(L, step=200, c=125):
    xs = list(range(c, L - c, step))
    if xs[-1] != L - c: xs.append(L - c)
    return xs


# even, symmetric grids: no bar on the pad axis (beam bars there), bottom/top never on the same plan line
P1 = list(range(175, 1826, 150))     # x of bottom bars along Y (pos 1), 12 pcs, ш.150
P2 = list(range(75, 2926, 150))      # y of bottom bars along X (pos 2), 20 pcs, ш.150
P3 = list(range(100, 1901, 200))     # x of top bars along Y (pos 3), 10 pcs, ш.200
P4 = list(range(200, 2801, 200))     # y of top bars along X (pos 4), 14 pcs, ш.200
NP = len(AX) * len(AY)
BAR_B = [-117, 0, 117]   # beam bars in plan (top 3 + bottom 3 project on these lines)

# beam lines: along X on every row from the outer pad faces, along Y on every axis
LX = (AX[-1] + PX / 2 - 50) - (AX[0] - PX / 2 + 50)
LY = (AY[-1] + PY / 2 - 50) - (AY[0] - PY / 2 + 50)


def bar_len(L, d):
    n = max(1, math.ceil((L - STOCK) / (STOCK - LAP[d])) + 1) if L > STOCK else 1
    return L + (n - 1) * LAP[d]


M5 = (len(AY) * 6 * bar_len(LX, 20) + len(AX) * 6 * bar_len(LY, 20)) / 1000          # п.м.
M6 = (len(AY) * 2 * bar_len(LX, 12) + len(AX) * 2 * bar_len(LY, 12)) / 1000


def spans():
    """clear spans of the beams between pad faces: (kind, a, b, line) along X (kind 'x', line = y) and Y"""
    s = []
    for y in AY:
        for a, b in zip(AX, AX[1:]): s.append(('x', a + PX / 2, b - PX / 2, y))
    for x in AX:
        for a, b in zip(AY, AY[1:]): s.append(('y', a + PY / 2, b - PY / 2, x))
    return s


def hoops(a, b):
    p, z, st = colgeo.storey_hoops(a, b + 50 - 50) if b - a >= 1200 else (None, None, None)
    if p is None:                                     # short span: uniform 100
        n = int((b - a - 100) // 100) + 1
        return [a + 50 + 100 * k for k in range(n)]
    return p


N_X1 = sum(len(hoops(a, b)) for k, a, b, l in spans())
CLEAR = sum(b - a for k, a, b, l in spans())
CC = 56
COLX = [-350 + CC + k * (700 - 2 * CC) / 3 for k in range(4)]
COLY = [-450 + CC + k * (900 - 2 * CC) / 4 for k in range(5)]
DOW = sorted(set([(x, COLY[0]) for x in COLX] + [(x, COLY[-1]) for x in COLX] + [(COLX[0], y) for y in COLY] + [(COLX[-1], y) for y in COLY]))
CORN = [(x, y) for x in (COLX[0], COLX[-1]) for y in (COLY[0], COLY[-1])]
DOW_IN = PH - 50 - 40                     # in the pad down to the bottom mesh
L_VP1 = DOW_IN + 200 + 600
L_VP2 = DOW_IN + 200 + 1200
X1 = (280, 530); X2 = (626, 826)
L_X1 = 2 * sum(X1) + 200; L_X2 = 2 * sum(X2) + 200
L_SK = (PH - 80) + 2 * 1000
NSK = int(2 * (PX + PY) / 200)

POS = [  # (pos, star, d, cls, L or None (п.м.), count, sheet note)
    ('1', '', 20, '500С', PY - 100, len(P1) * NP, 'подушка, низ, вдоль цифровых осей'),
    ('2', '', 20, '500С', PX - 100, len(P2) * NP, 'подушка, низ, вдоль буквенных осей'),
    ('3', '', 16, '500С', PY - 100, len(P3) * NP, 'подушка, верх, вдоль цифровых осей'),
    ('4', '', 16, '500С', PX - 100, len(P4) * NP, 'подушка, верх, вдоль буквенных осей'),
    ('5', '', 20, '500С', None, round(M5, 1), 'балки, 3+3, нахлест 1220'),
    ('6', '', 12, '500С', None, round(M6, 1), 'балки, боковые 2, нахлест 730'),
    ('Ск1', '*', 16, '500С', L_SK, NSK * NP, 'П-скоба по контуру подушки'),
    ('Х1', '*', 10, '500С', L_X1, N_X1, 'хомут балок'),
    ('Х2', '*', 10, '500С', L_X2, 3 * NP, 'хомут выпусков'),
    ('Вп1', '*', 28, '500С', L_VP1, len(CORN) * NP, 'выпуски угловые (+600)'),
    ('Вп2', '*', 28, '500С', L_VP2, (len(DOW) - len(CORN)) * NP, 'выпуски средние (+1200)'),
]
V_CONC = NP * PX * PY * PH / 1e9 + CLEAR * BB * BH / 1e9
V_PODG = (NP * (PX + 200) * (PY + 200) + CLEAR * (BB + 200)) * 100 / 1e9


def mass(p):
    pos, st, d, cls, L, n, note = p
    unit = KG[d] if L is None else round(L / 1000 * KG[d], 2)
    return unit, round(unit * n, 2)


if __name__ == '__main__':
    tot = 0
    for p in POS:
        u, m = mass(p); tot += m
        print(p[0] + p[1], 'Ø%d A%s' % (p[2], p[3]), p[4], p[5], u, m)
    print('total %.1f kg, concrete %.2f, podg %.2f, clear %.0f, hoops %d' % (tot, V_CONC, V_PODG, CLEAR, N_X1), len(P1), len(P2), len(P3), len(P4), P3, P4)
