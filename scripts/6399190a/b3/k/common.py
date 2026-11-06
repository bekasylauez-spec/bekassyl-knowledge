# -*- coding: utf-8 -*-
import math
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union
import lib
from lib import *
from geo import *

ROW_Y = 450000
A1W = 84100


def polys(g):
    if g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    return [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]


def outline(g, ox, oy, layer=L_CONT, ltype=None, ltscale=None):
    for p in polys(g):
        for ring in [p.exterior] + list(p.interiors):
            pts = [(x + ox, y + oy) for x, y in list(ring.coords)[:-1]]
            pl(pts, layer=layer, closed=True, ltype=ltype, ltscale=ltscale)


def hatch_geom(g, ox, oy, pat='ANSI36', sc=20):
    for p in polys(g):
        loops = [[(x + ox, y + oy) for x, y in list(p.exterior.coords)[:-1]]]
        for r in p.interiors: loops.append([(x + ox, y + oy) for x, y in list(r.coords)[:-1]])
        hatch(loops, pat=pat, sc=sc)


def walls_geom():
    W = [box(*wall_rect(w)) for w in WALLS_OUT + WALLS_IN]
    return W


def col_sq(c, a=500):
    return box(c[0] - a / 2, c[1] - a / 2, c[0] + a / 2, c[1] + a / 2)


def wall_pieces(cols):
    """each wall hatched separately; junction squares go to the first wall; columns cut out"""
    done = unary_union(cols) if cols else None
    out = []
    for w in walls_geom():
        g = w if done is None else w.difference(done)
        if not g.is_empty: out.append(g)
        done = w if done is None else done.union(w)
    return out


def axes(PX, PY, xs, ys, x_lo, x_hi, y_lo, y_hi, sc=100, bub_x=None, bub_y=None):
    """digit axes: vertical lines from y_hi to bubble at y_lo; letter axes from x_hi to bubble at x_lo"""
    for k, x in xs.items():
        axis(k, (PX + x, PY + y_hi), (PX + x, PY + y_lo), sc, True)
    for k, y in ys.items():
        axis(k, (PX + x_hi, PY + y), (PX + x_lo, PY + y), sc, False)


KG = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 18: 1.998, 20: 2.466, 22: 2.984, 25: 3.853, 28: 4.834}
LRB = {d: 'ф%d_арм' % d for d in (8, 10, 12, 14, 16, 18, 20, 22, 25, 28)}


def rbar(pts, d=20):
    pl(pts, layer=LRB.get(d, 'ф20_арм'), lw=40)


def rdots(pts, d=20):
    for x, y in pts: op(t='circle', c=[x, y], r=max(d / 2.0, 6), layer=LRB.get(d, 'ф20_арм'), lw=40)


def spec_table(X, Ytop, sc, title, rows, group='Детали:'):
    """rows: (pos, oboz, name, qty_text, mass_unit_text, mass_total_float) ; returns total mass"""
    k = sc / 100.0
    tb = tag('tb')
    op(t='clone', h=A_TABLE, base=[10700, 356330], to=[X, Ytop], s=k, tag=tb)
    need = 4 + len(rows)
    if need > 12: op(t='trows', h=tb, mode='ins', at=11, **{'from': 10}, n=need - 12)
    elif need < 12: op(t='trows', h=tb, mode='del', at=need, n=12 - need)
    cells = [[0, 0, '{\C256;%s}' % title], [1, 11, 'Масса ед. кг'], [1, 12, 'Масса всего, кг']]
    cells += [[2, 0, ''], [2, 1, ''], [2, 2, group], [2, 10, ''], [2, 11, ''], [2, 12, '']]
    r = 3; tot = 0.0
    for pos, ob, name, q, mu, mt in rows:
        tot += mt
        cells += [[r, 0, pos], [r, 1, ob], [r, 2, name], [r, 10, q], [r, 11, mu], [r, 12, '%.1f' % mt]]; r += 1
    cells += [[r, 0, ''], [r, 1, ''], [r, 2, 'Итого, кг'], [r, 10, ''], [r, 11, ''], [r, 12, '%.1f' % tot]]
    op(t='tset', h=tb, cells=cells)
    op(t='ttext', h=tb, th=250 * k, rh=633 * k, rh1=1500 * k)
    return tot, (need * 633 + 900) * k


def rowL(pos, d, L, n, cls='A500C'):
    """bar of length L mm, n pcs"""
    mu = round(L / 1000.0 * KG[d], 2)
    return (pos, 'ГОСТ 34028-2016', '%%%%C%d %s, L=%d' % (d, cls, L), str(int(n)), '%.2f' % mu, mu * n)


def rowPM(pos, d, m, cls='A500C'):
    return (pos, 'ГОСТ 34028-2016', '%%%%C%d %s (п.м)' % (d, cls), '%.0f' % m, '%.3f' % KG[d], KG[d] * m)
