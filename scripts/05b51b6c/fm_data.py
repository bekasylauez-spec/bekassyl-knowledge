"""Фм-1 reinforcement data (расход с запасом). Lengths in mm, masses kg/m."""
import math
KG = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 28: 4.834}
NPAD = 24
PX, PY, PH, COV = 2000, 3000, 1000, 50


def grid(L, step, c=COV):
    """bar coordinates along a side of length L: c, c+step, ... and the last one at L-c"""
    xs = []
    v = c
    while v < L - c - 1e-6:
        xs.append(v); v += step
    xs.append(L - c)
    return xs


B1 = grid(PX, 150)          # pos.1 (along Y, bottom) — x coordinates
B2 = grid(PY, 150)          # pos.2 (along X, bottom) — y coordinates
T3 = grid(PX, 200)          # pos.3 (along Y, top)
T4 = grid(PY, 200)          # pos.4 (along X, top)
NSK = int(2 * (PX + PY) / 200)            # П-скобы по контуру
# column 700x900, 14Ø28: 4 bars on the 700 faces, 5 on the 900 faces, cover to centre 54
CC = 54
COLX = [-350 + CC + k * (700 - 2 * CC) / 3 for k in range(4)]
COLY = [-450 + CC + k * (900 - 2 * CC) / 4 for k in range(5)]
DOW = sorted(set([(x, COLY[0]) for x in COLX] + [(x, COLY[-1]) for x in COLX] + [(COLX[0], y) for y in COLY] + [(COLX[-1], y) for y in COLY]))
LAP28 = 1710                                # 61d, B25
L_DOW = (PH - COV - 40) + 200 + LAP28        # in the pad to the bottom mesh, foot 200, lap above the pad
X1_A, X1_B = round(700 - 2 * CC), round(900 - 2 * CC)
L_X1 = 2 * (X1_A + X1_B) + 2 * 100
L_SK = (PH - 80) + 2 * 1000
BEAM_LEN = 3 * (32000 - 8 * 2000) + 8 * (12000 - 3 * 3000)       # clear beam length between pads, m*1000
LINE_LEN = 3 * 32000 + 8 * 12000                                  # beam axis lines incl. pads
L_X2 = 2 * (280 + 530) + 2 * 100
N_X2 = math.ceil(BEAM_LEN / 150) + 2 * 37

POS = [  # (pos, star, d, cls, L or None (п.м.), count, note)
    ('1', '', 20, '500С', PY - 2 * COV, len(B1) * NPAD, 'подушка, низ, вдоль осей букв.'),
    ('2', '', 20, '500С', PX - 2 * COV, len(B2) * NPAD, 'подушка, низ, вдоль цифр. осей'),
    ('3', '', 16, '500С', PY - 2 * COV, len(T3) * NPAD, 'подушка, верх'),
    ('4', '', 16, '500С', PX - 2 * COV, len(T4) * NPAD, 'подушка, верх'),
    ('5', '', 20, '500С', None, round(LINE_LEN * 6 * 1.10 / 1000, 1), 'балки, 3+3 стержня, с нахлестами 1220'),
    ('6', '', 12, '500С', None, round(LINE_LEN * 2 * 1.10 / 1000, 1), 'балки, боковые'),
    ('Ск1', '*', 16, '500С', L_SK, NSK * NPAD, 'П-скоба по контуру подушки'),
    ('Вп1', '*', 28, '500С', L_DOW, len(DOW) * NPAD, 'выпуски в колонны'),
    ('Х1', '*', 8, '240', L_X1, 5 * NPAD, 'хомут выпусков'),
    ('Х2', '*', 10, '240', L_X2, N_X2, 'хомут балок, ш.150'),
]
V_CONC = NPAD * PX * PY * PH / 1e9 + BEAM_LEN * 350 * 600 / 1e9
V_PODG = (NPAD * (PX + 200) * (PY + 200) + BEAM_LEN * 550) * 100 / 1e9


def mass(p):
    pos, st, d, cls, L, n, note = p
    unit = KG[d] if L is None else round(L / 1000 * KG[d], 2)
    return unit, round(unit * n, 2)


if __name__ == '__main__':
    tot = 0
    for p in POS:
        u, m = mass(p); tot += m
        print(p[0] + p[1], 'Ø%d A%s' % (p[2], p[3]), p[4], p[5], u, m)
    print('total %.1f kg, concrete %.2f, podg %.2f' % (tot, V_CONC, V_PODG), len(DOW), L_DOW, L_X1, L_SK)
