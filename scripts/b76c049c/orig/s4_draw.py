# -*- coding: utf-8 -*-
"""s4 ортақ геометрия/сызу функциялары (Третичный отстойник D10).
Барлық өлшем мм, r — осьтен радиус, z = отметка*1000 (s4_geo).
Қима функциялары (x, z) жазықтығында: x = таңбалы радиус (сол жақ x<0).
"""
import math
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
import s4_lib as L
from s4_lib import op, pl, hatch
from s4_geo import *

# ---------- қосымша геометрия (ШЕШІМДЕР.md, геометрия.md) ----------
R_CON = 6200.0                 # консоль сыртқы шеті
Z_CON_TIP = 1410.0             # консоль ұшының асты (t 90)
Z_CON_ROOT = 1240.0            # консоль түбінің асты, r 5300 (t 260)
R_LT_I, R_LT_O = 4350.0, 4500.0  # лоток қабырғасы ішкі/сыртқы беті
Z_LT_TOP = 1150.0              # лоток қабырғасының үсті
Z_LT_N = (500.0, 650.0)        # кәдімгі лоток түбі асты/үсті
Z_LT_D = (0.0, 150.0)          # тереңдетілген учаске (құбыр тұсы, ені 800)
LT_DEEP_W = 800.0
Z_PIPE, D_PIPE = 353.0, 350.0  # құбыр осі, диаметрі
PIPE_OUT = 500.0               # қабырғадан сыртқа шығуы
Z_WATER = 1200.0
Z_PLATE = (1200.0, 1500.0); R_PLATE = 1500.0
Z_WIN = (800.0, 1200.0)        # колонна терезелері; тіреулер 0°, 60°, ... (задание планы), терезе 30°, 90°, ...
R_CUSH = 6400.0                # подушка контуры
Z_CUSH = -4100.0; Z_CUSH_PIT = -5393.0
R_PIT_B = 1482.9 + 500.0       # шұңқыр түбі r <= 1483 + подушка шығуы
_PIT_K = (1913.4 - 1482.9) / (-3359.3 - (Z_SBOT - 100))        # приямок сыртқы бетінің dr/dz
R_PIT_T = R_PIT_B + _PIT_K * (Z_CUSH - Z_CUSH_PIT)             # шұңқыр жиегі -4.100 деңгейінде
D_PILE = 500.0

T = L.L_THIN; C = L.L_CONT; HL = 'Бетон штриховка'


# ---------- қима денелері ----------
def _half(side):
    """side: dict(deep, pipe, win) — бір жарты (x>=0). Қайтарады: (бөліктер, жік сызықтары, жіңішке сызықтар)."""
    deep, pipe, win = side.get('deep'), side.get('pipe'), side.get('win')
    fm = Polygon([(0, Z_HOLE), (R_HOLE, Z_HOLE), (R_HOLE, Z_SUMP), (R_SUMP_B, Z_SUMP), (R_SUMP_T, Z_F15), (R_VUT, Z_F45),
                  (R_IN, Z_VUT), (R_OUT, Z_VUT), (R_OUT, Z_WBOT), (R_FM, Z_WBOT), (R_FM, Z_FBOT), (R_BOT1, Z_FBOT),
                  (R_BOT2, Z_B2), (R_BOT3, Z_SBOT), (0, Z_SBOT)])
    wall = Polygon([(R_IN, Z_VUT), (R_OUT, Z_VUT), (R_OUT, Z_CON_ROOT), (R_CON, Z_CON_TIP), (R_CON, Z_TOP), (R_IN, Z_TOP)])
    zb, zt = Z_LT_D if deep else Z_LT_N
    lot = Polygon([(R_LT_I, zb), (R_IN, zb), (R_IN, zt), (R_LT_O, zt), (R_LT_O, Z_LT_TOP), (R_LT_I, Z_LT_TOP)])
    col = Polygon([(R_HOLE, Z_SUMP), (R_COLB, Z_SUMP), (R_COL, Z_COLB), (R_COL, Z_PLATE[0]), (R_HOLE, Z_PLATE[0])])
    plate = box(0, Z_PLATE[0], R_PLATE, Z_PLATE[1])
    thin = []
    if win:
        col = col.difference(box(R_HOLE, Z_WIN[0], R_COL, Z_WIN[1]))
        for y in (R_HOLE * math.sin(math.radians(75)), R_COL * math.sin(math.radians(75))):
            thin.append([(y, Z_WIN[0]), (y, Z_WIN[1])])
    if pipe:
        wall = wall.difference(box(R_IN - 1, Z_PIPE - D_PIPE / 2, R_OUT + 1, Z_PIPE + D_PIPE / 2))
    if deep:   # тереңдетілген учаскенің шеткі қабырғасы (көрініс): кәдімгі түбі үстінің сызығы
        thin.append([(R_LT_O, Z_LT_N[1]), (R_IN, Z_LT_N[1])])
    joints = [[(R_IN, Z_VUT), (R_OUT, Z_VUT)], [(R_HOLE, Z_SUMP), (R_COLB, Z_SUMP)]]
    if not win: joints.append([(R_HOLE, Z_PLATE[0]), (R_COL, Z_PLATE[0])])
    return [fm, wall, lot, col, plate], joints, thin


def _mir(g):
    from shapely import affinity
    return affinity.scale(g, -1, 1, origin=(0, 0))


def section_geom(left, right):
    """left/right: dict(deep=, pipe=, win=). Қайтарады dict(polys=[shapely Polygon], joints=[[(x,z)..]], thin=[[..]])"""
    pr, jr, tr = _half(right)
    pl_, jl, tl = _half(left)
    parts = pr + [_mir(p) for p in pl_]
    u = unary_union([p.buffer(0.01, join_style=2) for p in parts]).buffer(-0.01, join_style=2)
    polys = list(u.geoms) if hasattr(u, 'geoms') else [u]
    joints = jr + [[(-x, z) for x, z in s] for s in jl]
    thin = tr + [[(-x, z) for x, z in s] for s in tl]
    return dict(polys=polys, joints=joints, thin=thin)


def _clean(coords):
    pts = [(round(x, 1), round(z, 1)) for x, z in coords]
    if pts and pts[0] == pts[-1]: pts = pts[:-1]
    out = []
    for p in pts:
        if out and abs(p[0] - out[-1][0]) < 0.5 and abs(p[1] - out[-1][1]) < 0.5: continue
        out.append(p)
    # коллинеар нүктелерді алып таста
    res = []
    n = len(out)
    for i in range(n):
        a, b, c = out[i - 1], out[i], out[(i + 1) % n]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) > 1.0: res.append(b)
    return res


def draw_section(P, g, hatch_conc=True, cont=C, hpat='ANSI36', hsc=10, cut=None):
    """P(x, z) -> модель нүктесі. g = section_geom(...) / clip_geom(...).
    cut=(x0, z0, x1, z1): осы тіктөртбұрыш шекарасында жатқан қырлар контурмен сызылмайды (обрыв)."""
    def on_cut(a, b):
        if not cut: return False
        x0, z0, x1, z1 = cut
        return any(abs(a[i] - v) < 0.5 and abs(b[i] - v) < 0.5 for i, v in ((0, x0), (0, x1), (1, z0), (1, z1)))
    for poly in g['polys']:
        loops = [_clean(poly.exterior.coords)] + [_clean(i.coords) for i in poly.interiors]
        for lp in loops:
            n = len(lp)
            bad = [on_cut(lp[i], lp[(i + 1) % n]) for i in range(n)]
            if not any(bad):
                pl([P(x, z) for x, z in lp], layer=cont, closed=True); continue
            k = bad.index(True)
            run = []
            for j in range(1, n + 1):
                i = (k + j) % n
                if bad[i]:
                    if len(run) > 1: pl([P(x, z) for x, z in run], layer=cont)
                    run = []
                else:
                    if not run: run = [lp[i]]
                    run.append(lp[(i + 1) % n])
            if len(run) > 1: pl([P(x, z) for x, z in run], layer=cont)
        if hatch_conc:
            hatch([[P(x, z) for x, z in lp] for lp in loops], pat=hpat, sc=hsc, layer=HL)
    for s in g['joints']:
        pl([P(x, z) for x, z in s], layer=T)
    for s in g['thin']:
        pl([P(x, z) for x, z in s], layer=T)


def podg_loop(s=1):
    """подготовка t=100 (бір жақ, s=±1) — тұйық контур (x, z)"""
    podr = [(R_FM, Z_FBOT)] + POD + [(r, z) for r, z in reversed(BOT[1:])]
    return [(s * r, z) for r, z in podr]


def cushion_loop(s=1):
    """подушка t=1000 (бір жақ): үсті = подготовка асты, асты -4.100, приямок тұсында шұңқыр -5.393"""
    top = [(R_CUSH, Z_FBOT - 100)] + POD[1:]          # r 6400 -> 0 бойымен подготовка асты
    bot = [(0, Z_CUSH_PIT), (R_PIT_B, Z_CUSH_PIT), (R_PIT_T, Z_CUSH), (R_CUSH, Z_CUSH)]
    return [(s * r, z) for r, z in top + bot]


def pile(P, x, ztop, length=700, layer=C):
    """свая басы Ø500, ұзындығы обрывпен; x — ось"""
    h = D_PILE / 2; zb = ztop - length
    pl([P(x + h, zb), P(x + h, ztop), P(x - h, ztop), P(x - h, zb)], layer=layer)
    # обрыв (S-тәрізді жіңішке)
    pl([P(x - h - 60, zb), P(x - 60, zb), P(x - 25, zb + 70), P(x + 25, zb - 70), P(x + 60, zb), P(x + h + 60, zb)], layer=T)
    pl([P(x, ztop + 150), P(x, zb - 150)], layer=T, ltype='CENTER2', ltscale=10)


def piles_in_section(axis_deg, tol=D_PILE / 2):
    """Свая өрісінен қима жазықтығына (план бұрышы axis_deg бағытындағы түзу, центр арқылы) түсетін сваялар:
    қайтарады [(x_section, r)], x — қима бойындағы координата (axis_deg бағыты +)."""
    pts = [(0.0, 0.0)]
    pts += [(1000 * math.cos(math.radians(90 + i * 360 / 7.0)), 1000 * math.sin(math.radians(90 + i * 360 / 7.0))) for i in range(7)]
    pts += [(5150 * math.cos(math.radians(i * 360 / 33.0)), 5150 * math.sin(math.radians(i * 360 / 33.0))) for i in range(33)]
    for gx in (-3000, -1000, 1000, 3000):
        for gy in (-3000, -1000, 1000, 3000):
            if 1900 <= math.hypot(gx, gy) <= 4400: pts.append((float(gx), float(gy)))
    a = math.radians(axis_deg); ux, uy = math.cos(a), math.sin(a)
    res = []
    for x, y in pts:
        d = -x * uy + y * ux; s = x * ux + y * uy
        if abs(d) < tol: res.append((s, math.hypot(x, y)))
    return sorted(res)


def pile_top(r):
    return Z_CUSH_PIT if r <= R_PIT_B else Z_CUSH


# ---------- план ----------
def circle_pts(cx, cy, r, n=180, a0=0.0, a1=360.0):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + (0 if a1 - a0 >= 360 else 1))]


def circ(cx, cy, r, layer=C, **kw):
    d = dict(t='circle', c=[cx, cy], r=r, layer=layer); d.update(kw); return op(**d)


def ring_hatch(cx, cy, r_out, r_in, pat='ANSI36', sc=10):
    hatch([circle_pts(cx, cy, r_out), circle_pts(cx, cy, r_in)], pat=pat, sc=sc, layer=HL)


def axes(cx, cy, r, ext=500):
    AX = dict(layer=T, ltype='CENTER2', ltscale=20)
    pl([(cx - r - ext, cy), (cx + r + ext, cy)], **AX)
    pl([(cx, cy - r - ext), (cx, cy + r + ext)], **AX)


def diam(cx, cy, r, ang_deg, sc, trad=None, side=1):
    """диаметр размері (центр арқылы); мәтін r=trad радиусында (сызық үстінде)"""
    a = math.radians(ang_deg)
    p1 = (cx + r * math.cos(a), cy + r * math.sin(a)); p2 = (cx - r * math.cos(a), cy - r * math.sin(a))
    tr = trad if trad is not None else r * 0.6
    off = 110 * sc / 50.0
    tx = (cx + tr * math.cos(a) - off * math.sin(a), cy + tr * math.sin(a) + off * math.cos(a))
    return L.dim(p1, p2, p1, rot=a - math.pi, sc=sc, txt='%%c' + str(int(round(2 * r))), tx=tx)


# ---------- кесте ----------
def table(x0, ytop, colw, rows, hdr_h=750, row_h=400, th=125, hdr=None, align=None):
    """colw — бағандар ені (модель бірлігі); hdr — тақырып мәтіндері; rows — жолдар (тізім тізімі).
    Сыртқы және баған сызықтары C (0.30), жол аралық сызықтары T. Қайтарады табанының y-ін."""
    W = sum(colw); H = hdr_h + row_h * len(rows)
    yb = ytop - H
    pl([(x0, ytop), (x0 + W, ytop), (x0 + W, yb), (x0, yb)], layer=C, closed=True)
    xs = [x0]
    for w in colw: xs.append(xs[-1] + w)
    for x in xs[1:-1]: pl([(x, ytop), (x, yb)], layer=C)
    pl([(x0, ytop - hdr_h), (x0 + W, ytop - hdr_h)], layer=C)
    for i in range(1, len(rows)):
        y = ytop - hdr_h - row_h * i
        pl([(x0, y), (x0 + W, y)], layer=T)
    def cell(s, i, yc, w):
        if not s: return
        op(t='mtext', at=[(xs[i] + xs[i + 1]) / 2, yc], h=th, att=5, s=s, style='Isocpeur', layer=L.L_TXT, w=w - 60)
    if hdr:
        for i, s in enumerate(hdr): cell(s, i, ytop - hdr_h / 2, colw[i])
    for j, r in enumerate(rows):
        for i, s in enumerate(r): cell(s, i, ytop - hdr_h - row_h * (j + 0.5), colw[i])
    return yb


def note(l1, l2, origin, target, sc=50, arrow='none'):
    """СПДС выноска: полка всегда в сторону от стрелки (если цель правее начала полки — полка влево, Angle=pi)."""
    d = L.note(l1, l2, origin, target, sc=sc, arrow=arrow)
    if target[0] > origin[0]: d['angle'] = math.pi
    return d


def clip_geom(g, x0, z0, x1, z1):
    """section_geom нәтижесін тіктөртбұрышпен қиып алу (фрагмент қима, мыс. 4.1 қабырға қимасы)"""
    b = box(x0, z0, x1, z1)
    polys = []
    for p in g['polys']:
        c = p.intersection(b)
        polys += [q for q in (list(c.geoms) if hasattr(c, 'geoms') else [c]) if q.geom_type == 'Polygon' and q.area > 1]
    def cl(lines):
        out = []
        for s in lines:
            c = LineString(s).intersection(b)
            for q in (list(c.geoms) if hasattr(c, 'geoms') else [c]):
                if q.geom_type == 'LineString' and q.length > 1: out.append(list(q.coords))
        return out
    return dict(polys=polys, joints=cl(g['joints']), thin=cl(g['thin']))


def break_line(P, x, z0, z1, layer=T):
    """тік обрыв сызығы x бойынша z0..z1 (ортасында S)"""
    zm = (z0 + z1) / 2
    pl([P(x, z0 - 80), P(x, zm - 40), P(x - 60, zm - 15), P(x + 60, zm + 15), P(x, zm + 40), P(x, z1 + 80)], layer=layer)
