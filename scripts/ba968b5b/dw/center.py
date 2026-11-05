# -*- coding: utf-8 -*-
"""Атауларды астындағы сызбаның X-ортасына келтіру (05.11 пайдаланушы ережесі).
Кіріс: w/all.pkl (DXF: мәтіндер), w/listall.txt (AutoCAD GeometricExtents). Шығыс: moves.json [(handle, dx, sheet, text, info)]."""
import pickle, re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
SH, R = pickle.load(open('w/all.pkl', 'rb'))
TXT = {h: (t, txt, lay) for h, t, *_, txt, lay, hh in [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]) for r in R]}
E = {}
for l in open('w/listall.txt', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if p[0] != 'L': continue
    x0, y0, x1, y1 = map(float, p[4][1:].split(','))
    E[p[2]] = (p[1], p[3], x0, y0, x1, y1)
pat = re.compile(r'^\s*(Схема|Разрез|Сечение|Колонна|Ригель|Узел|Сетка|Фрагмент|План|Деталь|Вид|Каркас|Плита|Стена|Простенок|Опалубочн|Ополубочн|Армирование|Таблица|Ведомость деталей|Спецификация элементов|Выпуск)', re.I)
CORE = {'LINE', 'LWPOLYLINE', 'POLYLINE', 'HATCH', 'CIRCLE', 'ARC', 'INSERT', 'ELLIPSE', 'SPLINE', 'ACAD_TABLE', 'SOLID'}
def sheet_of(x, y):
    for k, (a, b, c, d) in SH.items():
        if a <= x <= c and b <= y <= d: return k
by_sheet = collections.defaultdict(list)
for h, (t, lay, x0, y0, x1, y1) in E.items():
    s = sheet_of((x0 + x1) / 2, (y0 + y1) / 2)
    if s: by_sheet[s].append((h, t, lay, x0, y0, x1, y1))
moves = []
for s, ents in sorted(by_sheet.items()):
    if s.startswith('8.') or s in ('1.1', '1.2'): continue
    fx0, fy0, fx1, fy1 = SH[s]
    sc = round((fy1 - fy0) / 420) if abs((fy1 - fy0) / 420 - round((fy1 - fy0) / 420)) < 0.02 else round((fy1 - fy0) / 297)
    sc = 50 if (fy1 - fy0) in (21000.0,) else (100 if (fy1 - fy0) == 42000 else sc)
    stamp = (fx1 - 185 * sc - 10 * sc, fy0, fx1, fy0 + 60 * sc)
    core = [e for e in ents if e[1] in CORE and not (e[3] > stamp[0] and e[4] < stamp[3])
            and not (e[5] - e[3] > 0.9 * (fx1 - fx0))
            and not (e[1] == 'LINE' and (e[6] - e[4] > 0.4 * (fy1 - fy0) or e[5] - e[3] > 0.3 * (fx1 - fx0)))]
    axes = [e for e in ents if e[1] == 'SPDSCONSTRUCTIONLINE' and (e[6] - e[4]) > 1.5 * (e[5] - e[3])]
    for h, t, lay, x0, y0, x1, y1 in ents:
        if t not in ('MTEXT', 'TEXT') or lay == 'О_Формат': continue
        info = TXT.get(h)
        if not info or not info[1] or not pat.match(info[1]) or len(info[1]) > 120: continue
        if x0 > stamp[0] and y0 < stamp[3]: continue
        tcx, tb = (x0 + x1) / 2, y0
        D, g = 45 * sc, 6 * sc
        ax = [e for e in axes if tb - 70 * sc <= e[6] <= tb + 1 * sc]
        if len(ax) >= 3:
            mt = max(e[6] for e in ax); ax = [e for e in ax if abs(e[6] - mt) < 2 * sc]
            # тек атауға жақын топ: x бойынша үзіліссіз (қадам < 15 м модельде)
            ax.sort(key=lambda e: (e[3] + e[5]) / 2)
            grp = [[ax[0]]]
            for e in ax[1:]:
                if (e[3] + e[5]) / 2 - (grp[-1][-1][3] + grp[-1][-1][5]) / 2 < 120 * sc: grp[-1].append(e)
                else: grp.append([e])
            grp = min(grp, key=lambda g_: abs(((g_[0][3] + g_[0][5]) / 2 + (g_[-1][3] + g_[-1][5]) / 2) / 2 - tcx))
            if len(grp) >= 3:
                c0 = (grp[0][3] + grp[0][5]) / 2; c1 = (grp[-1][3] + grp[-1][5]) / 2
                moves.append((h, round((c0 + c1) / 2 - tcx, 1), s, info[1].replace(chr(10), ' ')[:60], 'axes %d' % len(grp), [x0, y0, x1, y1], [c0, tb - 60 * sc, c1, tb]))
                continue
        # 1) кесте немесе ең үлкен тұйық контур (бетон қимасы / элемент)
        big = [e for e in core if e[1] in ('LWPOLYLINE', 'HATCH', 'ACAD_TABLE', 'POLYLINE') and tb - D <= e[6] <= tb + 1 * sc
               and e[5] > x0 - 0.3 * (x1 - x0) and e[3] < x1 + 0.3 * (x1 - x0) and (e[5] - e[3]) > 3 * sc and (e[6] - e[4]) > 3 * sc]
        if big:
            mt = max(e[6] for e in big); big = [e for e in big if e[6] >= mt - 12 * sc]
            bb = max(big, key=lambda e: (e[5] - e[3]) * (e[6] - e[4]))
            moves.append((h, round((bb[3] + bb[5]) / 2 - tcx, 1), s, info[1].replace(chr(10), ' ')[:60], 'contour %s %s' % (bb[1], bb[0]), [x0, y0, x1, y1], [bb[3], bb[4], bb[5], bb[6]]))
            continue
        seed = [e for e in core if tb - D <= e[6] <= tb + 1 * sc and e[5] > x0 - 0.5 * (x1 - x0) and e[3] < x1 + 0.5 * (x1 - x0)]
        if not seed: moves.append((h, 0, s, info[1], 'no seed', [x0, y0, x1, y1], None)); continue
        top = max(e[6] for e in seed)
        seed = [e for e in seed if e[6] >= top - 8 * sc]
        cl = {e[0]: e for e in seed}; grow = True
        while grow:
            grow = False
            bx0 = min(e[3] for e in cl.values()); bx1 = max(e[5] for e in cl.values())
            by0 = min(e[4] for e in cl.values()); by1 = max(e[6] for e in cl.values())
            for e in core:
                if e[0] in cl: continue
                if e[6] > tb + 1 * sc: continue          # атаудан жоғары емес
                for c in list(cl.values()):
                    if e[3] <= c[5] + g and e[5] >= c[3] - g and e[4] <= c[6] + g and e[6] >= c[4] - g:
                        cl[e[0]] = e; grow = True; break
        bx0 = min(e[3] for e in cl.values()); bx1 = max(e[5] for e in cl.values())
        dx = (bx0 + bx1) / 2 - tcx
        moves.append((h, round(dx, 1), s, info[1].replace('\n', ' ')[:60], 'n=%d w=%.0f sc=%d' % (len(cl), bx1 - bx0, sc), [x0, y0, x1, y1], [bx0, min(e[4] for e in cl.values()), bx1, max(e[6] for e in cl.values())]))
json.dump(moves, open('w/moves.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for m in moves: print('%-4s %-7s %8.1f мм(қағаз %.1f)  %-45s %s' % (m[2], m[0], m[1], m[1] / (50 if '4.' in m[2] else 100), m[3], m[4]))
