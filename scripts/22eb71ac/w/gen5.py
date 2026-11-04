# Резервуар КЖ: листы 5.1–5.4 — армирование плиты днища Фм-1 (A3, 1:100), по одному направлению/зоне на лист.
# Zones from LIRA mosaics on -3.700 (scr02`2 X низ, scr04 Y низ, scr01`2 X верх, scr03`2 Y верх), see zones.json.
import sys, json, math
import common as C
from common import *
from shapely.geometry import box
from shapely.ops import unary_union

LAP = lambda d: int(math.ceil(71 * d / 10.0) * 10)          # lap 71d (template notes)
ANCH = lambda d: int(math.ceil(40 * d / 50.0) * 50)          # dop bars beyond their zone
CV = 50                                                      # bar end from slab edge (template «50»)
pos = []
def P(n, d, L, cnt, face, note='', key=None):
    pos.append(dict(n=n, d=d, L=L, cnt=cnt, face=face, note=note, key=key)); return n
Lx = FXE - FXO - 2 * CV; Ly = FYE - FYO - 2 * CV
nX = int(Ly / 200) + 1; nY = int(Lx / 200) + 1               # bars along X are spread over Y and vice versa
P('1', 12, Lx + LAP(12), 2 * nX, 'низ+верх', 'пог.м.')
P('2', 12, Ly + LAP(12), 2 * nY, 'низ+верх', 'пог.м.')
nxt = [3]

SHEETS = [  # (num, x of frame, face, dir, zones [(d, rect, alongside base)])
    ('5.1', 113700.0, 'низ', 'x', [(28, (7200, 2500, 9300, 5700), True, 'L'), (28, (7200, 6800, 9300, 10000), True, 'L', 9225),
                                   (12, (6100, 2000, 9800, 11000), False, 'L', 6300), (12, (10800, 8900, 11700, 11000), False, 'R'),
                                   (14, (7700, 11400, 8800, 16800), False, 'R')]),
    ('5.2', 155700.0, 'низ', 'y', [(22, (5600, 7300, 10300, 10000), False), (22, (6100, 3000, 10300, 5200), False),
                                   (12, (1000, 11900, 5200, 13100), False)]),
    ('5.3', 197700.0, 'верх', 'x', [(12, (10200, 1000, 14750, 15800), False), (12, (1000, 2500, 5700, 8000), False),
                                    (12, (7700, 3500, 8800, 13100), False)]),
    ('5.4', 239700.0, 'верх', 'y', [(12, (4100, 0, 11800, 3100), False), (12, (2000, 14500, 6200, 16300), False),
                                    (12, (7200, 3500, 8800, 12500), False)])]
DIRN = {'x': 'в направлении осей 1-3', 'y': 'в направлении осей А-Д'}
up = unary_union([box(*r) for rs in walls1.values() for r in rs] + [box(*r) for r in walls2] +
                 [box(*r) for r in list(pil.values()) + list(cols.values()) + [col3]]).simplify(0.5)

for num, fx, face, dr, zones in SHEETS:
    F = (fx, 340000.0)
    zone_name = 'нижняя' if face == 'низ' else 'верхняя'
    frame(*F, 100, 'Армирование плиты днища Фм-1\\P%s сетка, стержни %s' % (zone_name, DIRN[dr]), num, 'A3')
    S = Sheet(F[0] + 6600, F[1] + 6100, 100); S.cx, S.cy = 7375, 8875
    S.title('Фм-1. %s сетка. Стержни %s' % (zone_name.capitalize(), DIRN[dr]), 1200, FYE + 2600)
    S.pl(rect((FXO, FYO, FXE, FYE)))
    for g in getattr(up, 'geoms', [up]):
        for ring in [g.exterior] + list(g.interiors): S.thin([(round(x, 1), round(y, 1)) for x, y in ring.coords])
    S.thin(rect(pit), closed=True); S.hid(rect(pitb), closed=True)
    plan_axes(S, 'R' + num.replace('.', ''), (FXO, FYO, FXE, FYE))
    def bar(pts, d): add(t='pl', p=[S.P(*p) for p in pts], closed=False, layer='диам%d' % d)
    def bnote(n, tgt, l2='ш.200'):
        S.note(n, (tgt[0] + 400 * (1 if S.cx >= tgt[0] else -1), tgt[1] + 400 * (1 if S.cy >= tgt[1] else -1)), [tgt], l2=l2, arrow='oblique')
    # base bar of this direction
    if dr == 'x': bar([(FXO + CV, 600), (FXE - CV, 600)], 12); bnote('1', (FXO + 1800, 600))
    else: bar([(600, FYO + CV), (600, FYE - CV)], 12); bnote('2', (600, FYE - 2500))
    xs, ys = set(), set()
    for zi, zz in enumerate(zones):
        d, z, along = zz[:3]; side = zz[3] if len(zz) > 3 else None; at = zz[4] if len(zz) > 4 else None
        x0, y0, x1, y1 = z; a = ANCH(d); xs |= {x0, x1}; ys |= {y0, y1}
        add(t='pl', p=[S.P(*q) for q in rect(z)], closed=True, layer='Тонкая', ltype='CENTER2', ltscale=25)
        if dr == 'x':
            xa, xb = max(x0 - a, FXO + CV), min(x1 + a, FXE - CV); L = xb - xa
            n = int((y1 - y0) / 200) + (1 if along else 0); ym = at if at else y0 + 200 * int((y1 - y0) / 800) + (0 if along else 100)   # quarter, off the axes
            bar([(xa, ym), (xb, ym)], d); tgt = (xa + 250, ym)
            ax = min(AX.values(), key=lambda v: abs(v - (xa + xb) / 2))
            S.chain(sorted({xa, ax, xb}), ym, ym + 350)            # bar binding ABOVE the bar: text away from the bar
            right = (side == 'R') if side else (zi % 2 == 0)
            ex = xb + 300 if right else xa - 300
            S.chain(sorted({y0, y1} | {v for v in AY.values() if y0 < v < y1}), xb if ex > xb else xa, ex, vert=True)
        else:
            ya, yb = max(y0 - a, FYO + CV), min(y1 + a, FYE - CV); L = yb - ya
            n = int((x1 - x0) / 200) + (1 if along else 0); xm = x0 + 200 * int((x1 - x0) / 800) + (0 if along else 100)
            bar([(xm, ya), (xm, yb)], d); tgt = (xm, ya + 250)
            ay = min(AY.values(), key=lambda v: abs(v - (ya + yb) / 2))
            S.chain(sorted({ya, ay, yb}), xm, xm - 350, vert=True)   # binding LEFT of the bar
            ey = yb + 300 if zi % 2 == 0 else ya - 300
            S.chain(sorted({x0, x1} | {v for v in AX.values() if x0 < v < x1}), yb if ey > yb else ya, ey)
        key = (face, dr, d, int(L))
        old = [p for p in pos if p['key'] == key]
        if old: old[0]['cnt'] += n; nn = old[0]['n']
        else:
            nn = str(nxt[0]); nxt[0] += 1
            base = '1' if dr == 'x' else '2'
            P(nn, d, int(L), n, face, ('рядом с поз.' if along else 'между поз.') + base, key)
        if dr == 'x': S.note(nn, (tgt[0] + 400, tgt[1] - 800), [tgt], l2='ш.200', arrow='oblique')   # note below the bar
        else: S.note(nn, (tgt[0] + 400, tgt[1] + 400), [tgt], l2='ш.200', arrow='oblique')        # note right of the bar
    # zone boundaries: one chain outside the plan per side, bound to the axes (no dims inside the plan)

    notes(*F, 0, [
        'Общие указания см. лист 1. Схему расположения элементов см. лист 2.',
        'Основная арматура: поз. 1 (вдоль осей 1-3) и поз. 2 (вдоль осей А-Д) - %%C12 A500C шаг 200, нижняя и верхняя сетки.',
        'Дополнительные стержни - по результатам расчета (ЛИРА). Границы зон даны штрихпунктиром; стержни заводятся за границу зоны на 40d.',
        'Стержни "рядом с поз." укладывать вплотную к основным, "между поз." - посередине шага основных.',
        'Стыки внахлестку без сварки, длина нахлеста 71d; в одном сечении стыковать не более 50% стержней.',
        'Защитный слой бетона: низ - 50 мм, верх - 40 мм.',
        'Шпильки, разрезы и спецификацию см. листы 5.5, 5.6.'])

ops = [{'t': 'eraseregion', 'win': [113750, 339500, 281700, 370000], 'mode': 'intersect'}] + C.ops + [{'t': 'regen'}]
json.dump(ops, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(pos, open(sys.argv[1].replace('.json', '_pos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(ops), 'ops'); [print(p) for p in pos]
