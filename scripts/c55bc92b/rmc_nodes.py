# -*- coding: utf-8 -*-
# РМЦ узел паспорттары үшін құбыр ұштары / фасонка геометриясын есептеу (аналог Блок 1 «Конец трубы»)
import math
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union

def rect_s(P0, u, s0, s1, hw):
    n = (-u[1], u[0])
    pts = []
    for s, h in ((s0, -hw), (s1, -hw), (s1, hw), (s0, hw)):
        pts.append((P0[0] + u[0]*s + n[0]*h, P0[1] + u[1]*s + n[1]*h))
    return Polygon(pts)

class M:
    def __init__(s, name, P0, d, side, b, ti=8, tp=4, e=30, w=None, smin=0, fixed=None):
        L = math.hypot(*d); s.u = (d[0]/L, d[1]/L); s.name = name; s.P0 = P0; s.side = side
        s.b = b; s.ti = ti; s.tp = tp; s.e = e; s.w = w or b + 20; s.smin = smin; s.fixed = fixed
    def parts(s, sp, tg):
        yc = s.side*(tg/2 + s.ti/2)
        ins = rect_s(s.P0, s.u, sp-120, sp+100, s.w/2)
        plug = rect_s(s.P0, s.u, sp, sp+s.tp, s.w/2)
        tube = rect_s(s.P0, s.u, sp+s.tp, sp+3000, s.b/2)
        Yi = (min(s.side*tg/2, s.side*(tg/2+s.ti)), max(s.side*tg/2, s.side*(tg/2+s.ti)))
        Yt = (yc - s.b/2, yc + s.b/2)
        return [('ins', ins, Yi), ('plug', plug, (yc-s.w/2, yc+s.w/2)), ('tube', tube, Yt)]

def yover(a, b): return a[0] < b[1]-0.01 and b[0] < a[1]-0.01

def solve0(members, obst, tg, ins_forbid, step=5):
    placed = []
    for m in members:
        sp = m.fixed if m.fixed is not None else m.smin
        while True:
            ok = True
            P = m.parts(sp, tg)
            for nm, g, Y in P:
                if nm == 'ins' and ins_forbid is not None and g.intersection(ins_forbid).area > 0.5: ok = False; break
                for og, oY in obst:
                    if yover(Y, oY) and g.intersection(og).area > 0.5: ok = False; break
                if not ok: break
                for pm, psp in placed:
                    for nm2, g2, Y2 in pm.parts(psp, tg):
                        if yover(Y, Y2) and g.intersection(g2).area > 0.5: ok = False; break
                    if not ok: break
                if not ok: break
            if ok or m.fixed is not None: break
            sp += step
        if not ok: print('  !! fixed member conflicts:', m.name)
        placed.append((m, sp))
    return placed

def solve(members, obst, tg, ins_forbid, step=5):
    import itertools, copy
    best=None
    free=[m for m in members if m.fixed is None]
    for sides in itertools.product((1,-1), repeat=len(free)):
        for m,sd in zip(free,sides): m.side=sd
        pl=solve0(members,obst,tg,ins_forbid,step)
        sc=max(sp for m,sp in pl)
        if best is None or sc<best[0]: best=(sc,[ (m.side) for m in members])
    for m,sd in zip(members,best[1]): m.side=sd
    pl=solve0(members,obst,tg,ins_forbid,step)
    print('  жақтар:', ', '.join('%s %s' % (m.name, '+' if m.side>0 else '-') for m in members))
    return pl

def report(title, placed, tg, support, extra_pts=(), sup_lines=()):
    print('=' * 8, title)
    pts = list(extra_pts)
    for m, sp in placed:
        ov = rect_s(m.P0, m.u, sp-120, sp-20, m.w/2)
        pts += list(ov.exterior.coords)[:-1]
    pts += list(support)
    hull = Polygon(pts).convex_hull if len(pts) > 2 else None
    for m, sp in placed:
        ang = math.degrees(math.atan2(m.u[1], m.u[0]))
        n = (-m.u[1], m.u[0])
        endf = (m.P0[0] + m.u[0]*(sp+m.tp), m.P0[1] + m.u[1]*(sp+m.tp))
        bc = (m.P0[0] + m.u[0]*(sp-70), m.P0[1] + m.u[1]*(sp-70))
        b1 = (bc[0] + n[0]*m.e, bc[1] + n[1]*m.e); b2 = (bc[0] - n[0]*m.e, bc[1] - n[1]*m.e)
        ins = rect_s(m.P0, m.u, sp-120, sp+100, m.w/2)
        dmin = min(LineString(l).distance(Point(b)) for l in sup_lines for b in (b1, b2)) if sup_lines else float('nan')
        print('  %-14s ang %6.2f  P0(%.1f,%.1f)  заглушка беті s=%d  құбыр ұшы (%.1f, %.1f) s=%d  фасонка жиегі s=%d  болт (%.1f,%.1f) (%.1f,%.1f)  шовтан max %.0f' % (
            m.name, ang, m.P0[0], m.P0[1], sp, endf[0], endf[1], sp+m.tp, sp-20, b1[0], b1[1], b2[0], b2[1], dmin))
        print('      вставка бұрыштары', [(round(x, 1), round(y, 1)) for x, y in list(ins.exterior.coords)[:-1]])
    if hull is not None:
        cut = unary_union([g.buffer(10, join_style=2) for m, sp in placed for nm, g, Y in m.parts(sp, tg) if nm in ('tube', 'plug')])
        gus = hull.difference(cut)
        if gus.geom_type == 'MultiPolygon':
            gus = max(gus.geoms, key=lambda p: p.area)
        gus = gus.simplify(0.5)
        hv = [(round(x), round(y)) for x, y in list(gus.exterior.coords)[:-1]]
        dmax = 0
        for m, sp in placed:
            n = (-m.u[1], m.u[0]); bc = (m.P0[0] + m.u[0]*(sp-70), m.P0[1] + m.u[1]*(sp-70))
            for k in (1, -1):
                b = (bc[0] + k*n[0]*m.e, bc[1] + k*n[1]*m.e)
                dmax = max(dmax, min(LineString(l).distance(Point(b)) for l in sup_lines))
        treq = next(t for t in (8, 10, 12, 14, 16, 20, 25) if 15*t >= dmax)
        print('  фасонка төбелері (құбырдан 10 мм ойық):', hv)
        print('  фасонка ауданы %.0f см2; шовтан ең алыс болт %.0f мм -> 15t бойынша t >= %d' % (gus.area/100, dmax, treq))
        return gus

ALL = (-1e4, 1e4)
print('\n##### Б2 / Б2а (СВ3, СВ4 төменгі ұшы, WP колонна осі +1,350) — x колонна осінен, z абс.')
for nm, top in (('СВ3', (5996, 5930)), ('СВ4', (6000, 3736))):
    d = (top[0], top[1]-1350)
    obst = [(box(-400, 870, 400, 900), ALL), (box(150, 900, 162, 1200), ALL), (box(-4, 870, 4, 4000), ALL)]
    m = M(nm, (0, 1350), d, -1, 140, ti=8, e=30)
    pl = solve([m], obst, 10, box(-100, 0, 19, 9000))
    report('Б2 ' + nm, pl, 10, [(4, 900), (150, 900), (4, 1350)], sup_lines=[((4, 900), (4, 2200)), ((4, 900), (150, 900))])

print('\n##### Узел 7 (A/G): Р1 ригель осінде +8,641.6, СВ1 жоғарғы ұшы, ригель Б1 қалтасында (x ригель стенкасынан)')
for span in (5993, 5843):
    Z_TF, Z_BF = 8969.3, 8323.3
    obst = [(box(-125, Z_TF, 125, Z_TF+12), ALL), (box(-125, Z_BF-12, 125, Z_BF), ALL), (box(-160, 8286, 160, 8311), ALL),
            (box(-3, 8000, 3, 9100), ALL), (box(-4, 7000, 4, 8286), ALL)]
    r1 = M('Р1', (0, 8641.6), (1, 0), +1, 140, e=30)
    d = (span - 3 - 3, 6070 - 8541.6)
    sv = M('СВ1 span%d' % span, (3, 8541.6), d, -1, 140, e=30)
    pl = solve([r1, sv], obst, 12, box(-200, 0, 130, 20000))
    report('узел 7 A/G span %d' % span, pl, 12, [(3, Z_BF), (3, Z_TF), (125, Z_TF), (125, Z_BF)],
           sup_lines=[((3, Z_BF), (3, Z_TF)), ((3, Z_TF), (125, Z_TF)), ((3, Z_BF), (125, Z_BF))])

print('\n##### Узел 12а: тек Р1 ригельде (байланыссыз аралық, A/G басы)')
obst = [(box(-125, 8969.3, 125, 8981.3), ALL), (box(-125, 8311, 125, 8323.3), ALL), (box(-3, 8000, 3, 9100), ALL)]
pl = solve([M('Р1', (0, 8641.6), (1, 0), +1, 140)], obst, 12, box(-200, 0, 130, 20000))
report('узел 12а', pl, 12, [(3, 8323.3), (3, 8969.3), (125, 8969.3), (125, 8323.3)],
       sup_lines=[((3, 8323.3), (3, 8969.3)), ((3, 8969.3), (125, 8969.3)), ((3, 8323.3), (125, 8323.3))])

print('\n##### Узел 7D / 13: жота пластинасы −20 (y=18000), Р2 (+9,593), СВ2 жоғарғы ұшы (x ригель стенкасынан)')
for span in (5993, 5843):
    obst = [(box(-175, 9850, 175, 9868), ALL), (box(-175, 9318, 175, 9336), ALL), (box(-160, 9293, 160, 9318), ALL),
            (box(-4, 8000, 4, 9293), ALL)]
    r2 = M('Р2', (0, 9593), (1, 0), -1, 150, e=30)
    d = (span - 4 - 4, 6070 - 9493)
    sv = M('СВ2 span%d' % span, (4, 9493), d, +1, 140, e=30)
    pl = solve([r2, sv], obst, 20, box(-200, 0, 180, 20000))
    report('узел 7D span %d' % span, pl, 20, [(4, 9318), (4, 9868), (185, 9868), (185, 9318)],
           sup_lines=[((4, 9318), (4, 9868)), ((4, 9868), (175, 9868)), ((4, 9336), (175, 9336))])

print('\n##### Узел 8 (+6,000): Р1 + жоғарғы диагональ ұшы + төменгі ярус диагоналі (x колонна осінен)')
cases = [('8 A/G СВ1 (1–2, 10–11)', 5843, 8541.6, None), ('8 D СВ2 (1–2, 10–11)', 5843, 9493, None),
         ('8а A/D СВ1|СВ2 + СВ3 (4–5, 7–8)', 5993, 8541.6, ('СВ3', (5996, 1350))),
         ('8а D СВ2 + СВ3', 5993, 9493, ('СВ3', (5996, 1350))),
         ('8б G/A СВ1 + СВ5', 5993, 8541.6, ('СВ5', (6000, 3736)))]
for title, span, zup, low in cases:
    obst = [(box(-4, 4000, 4, 8000), ALL)]
    r1 = M('Р1', (0, 6000), (1, 0), +1, 140, fixed=146)
    up = M('upper', (4, 6070), (span - 3 - 4, zup - 6070), -1, 140)
    mem = [r1, up]
    if low:
        lw = M(low[0], (4, 5930), (low[1][0] - 4, low[1][1] - 5930), -1, 140)
        mem.append(lw)
    pl = solve(mem, obst, 10, box(-100, 0, 18, 20000))
    report(title, pl, 10, [(4, 5900), (4, 6100)], sup_lines=[((4, 5000), (4, 7000))])

print('\n##### Узел 12: тек Р1 колонна стенкасында +6,000')
pl = solve([M('Р1', (0, 6000), (1, 0), +1, 140, fixed=146)], [(box(-4, 4000, 4, 8000), ALL)], 8, box(-100, 0, 18, 20000))
report('узел 12', pl, 8, [(4, 5900), (4, 6100)], sup_lines=[((4, 5000), (4, 7000))])

print('\n##### Узел 11 (Б4 деңгейі, WP колонна осі +3,736): СВ4 жоғарғы ұшы (Б4 астында), СВ5 төменгі ұшы (Б4 үстінде)')
B4 = box(24, 3572, 3000, 3900)
for nm, d in (('СВ4', (6000, 1350 - 3736)), ('СВ5', (5996, 5930 - 3736))):
    m = M(nm, (0, 3736), d, -1, 140)
    pl = solve([m], [(B4, ALL), (box(-4, 0, 4, 9000), ALL)], 10, box(-100, 0, 18, 20000))
    if nm == 'СВ4':
        report('узел 11 ' + nm, pl, 10, [(4, 3572), (24, 3572)], sup_lines=[((4, 0), (4, 3572)), ((24, 3572), (3000, 3572))])
    else:
        report('узел 11 ' + nm, pl, 10, [(4, 3900), (24, 3900)], sup_lines=[((4, 3900), (4, 9000)), ((24, 3900), (3000, 3900))])

print('\n##### Узел 14/15: горизонталь фасонка ригель стенкасында (x стенкадан, y түйіннен ригель бойымен); Р3 үстінде (+), ГС астында (−)')
for hwf, title in ((125, 'B/F y=6000 (Б1, полка 250)'), (140, 'C/E y=12000 (Б2, полка 280)')):
    for ang in (45.0, 42.34):
        mem = [M('Р3', (0, 0), (1, 0), +1, 120, e=30),
               M('ГС +y', (0, 0), (math.cos(math.radians(ang)), math.sin(math.radians(ang))), -1, 80, ti=6, e=25),
               M('ГС -y', (0, 0), (math.cos(math.radians(ang)), -math.sin(math.radians(ang))), -1, 80, ti=6, e=25)]
        pl = solve(mem, [(box(-3, -3000, 3, 3000), ALL)], 8, box(-100, -3000, hwf + 5, 3000))
        report('%s ГС бұрышы %.2f' % (title, ang), pl, 8, [(3, -150), (3, 150)], sup_lines=[((3, -3000), (3, 3000))])
    pl = solve([M('Р3', (0, 0), (1, 0), +1, 120, e=30)], [(box(-3, -3000, 3, 3000), ALL)], 8, box(-100, -3000, hwf + 5, 3000))
    report('%s тек Р3 (узел 14)' % title, pl, 8, [(3, -90), (3, 90)], sup_lines=[((3, -3000), (3, 3000))])

print('\n##### Узел 15б: ГС колонна ішкі бетінде (A/G, WP y=532) және жотада (WP y=18000∓266) — бір бағыт')
for hwf, ang, title in ((125, 42.34, 'A/G карниз, Б1'), (175, 43.70, 'D жота, Б3')):
    mem = [M('ГС', (0, 0), (math.cos(math.radians(ang)), math.sin(math.radians(ang))), -1, 80, ti=6, e=25)]
    pl = solve(mem, [(box(-3, -3000, 3, 3000), ALL)], 8, box(-100, -3000, hwf + 5, 3000))
    report(title, pl, 8, [(3, 0), (3, 150)], sup_lines=[((3, -3000), (3, 3000))])

