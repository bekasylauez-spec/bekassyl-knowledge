# -*- coding: utf-8 -*-
"""Auto placement of SPDS notes (выноски): shelf+text must not touch any line, text, hatch, other note.
Shelf extends to the RIGHT of origin (SPDS behaviour) -> candidates only with origin to the right of target
(полка стрелкаға қарсы жақта). Obstacles are built from the ops of the current sheet."""
import math
from shapely.geometry import LineString, Polygon, box, Point
from shapely.strtree import STRtree

CW = 0.72


def tw(s):
    return sum(0.85 if ch.isdigit() else CW for ch in s)


def note_box(o, l1, l2, sc):
    h = 2.5 * sc
    w = (max(tw(l1), tw(l2 or ''), 1.5)) * h + 1.2 * h
    y0 = o[1] - (1.6 * h if l2 else 0.25 * h)
    return box(o[0] - 0.2 * h, y0, o[0] + w, o[1] + 1.6 * h)


def dim_geo(d):
    p1, p2, dl, rot = d['p1'], d['p2'], d['dl'], d.get('rot', 0.0)
    sc = d.get('dscale', 100); h = 2.5 * sc
    if abs(rot) < 1e-6:
        y = dl[1]; a, b = sorted((p1[0], p2[0]))
        lines = [LineString([(a, y), (b, y)]), LineString([(p1[0], p1[1]), (p1[0], y)]), LineString([(p2[0], p2[1]), (p2[0], y)])]
        L = b - a; txt = d.get('txt') or ('%d' % round(L))
        w = tw(txt) * h
        if w + 2 * h < L: tb = box((a + b) / 2 - w / 2, y + 0.3 * h, (a + b) / 2 + w / 2, y + 1.3 * h)
        else: tb = box(b + 0.5 * h, y + 0.3 * h, b + 0.5 * h + w, y + 1.3 * h)
    else:
        x = dl[0]; a, b = sorted((p1[1], p2[1]))
        lines = [LineString([(x, a), (x, b)]), LineString([(p1[0], p1[1]), (x, p1[1])]), LineString([(p2[0], p2[1]), (x, p2[1])])]
        L = b - a; txt = d.get('txt') or ('%d' % round(L))
        w = tw(txt) * h
        if w + 2 * h < L: tb = box(x - 1.3 * h, (a + b) / 2 - w / 2, x - 0.3 * h, (a + b) / 2 + w / 2)
        else: tb = box(x - 1.3 * h, b + 0.5 * h, x - 0.3 * h, b + 0.5 * h + w)
    return lines, tb


def collect(ops):
    lines, polys, texts = [], [], []
    for d in ops:
        t = d.get('t')
        if t == 'pl':
            p = d['p']
            if d.get('closed'): p = p + p[:1]
            for a, b in zip(p, p[1:]):
                if a != b: lines.append(LineString([a, b]))
        elif t == 'hatch':
            for lp in d['loops']:
                try: polys.append(Polygon(lp).buffer(0))
                except Exception: pass
        elif t == 'dim':
            ls, tb = dim_geo(d); lines += ls; texts.append(tb)
        elif t == 'axis':
            sc = d.get('scale', 100); s, e = d['s'], d['e']
            lines.append(LineString([s, e])); texts.append(Point(e).buffer(4.5 * sc))
        elif t == 'circle':
            texts.append(Point(d['c']).buffer(d['r']))
        elif t == 'mtext':
            s = d['s']; h = d['h']
            import re
            plain = re.sub(r'\\[A-Za-z][^;]*;|[{}]|\\L|\\P', ' ', s)
            n = max(1, s.count('\\P') + 1); w = d.get('w') or tw(plain) * h
            x, y = d['at']; att = d.get('att', 1)
            H = n * h * 1.6
            dx = {1: 0, 2: -w / 2, 3: -w}[(att - 1) % 3 + 1]; dy = {0: -H, 1: -H / 2, 2: 0}[(att - 1) // 3]
            texts.append(box(x + dx, y + dy, x + dx + w, y + dy + H))
        if d.get('_box'):
            texts.append(box(*d['_box']))
    return lines, polys, texts


def resolve(ops, start, rmax=None):
    sheet = ops[start:]
    notes = [d for d in sheet if d.get('t') == 'note' and not d.get('fixed')]
    lines, polys, texts = collect(sheet)
    lt = STRtree(lines) if lines else None
    pt = STRtree(polys) if polys else None
    placed = []
    for d in notes:
        tx, ty = d['target']; sc = d['scale']; k = sc / 100.0
        prefer_up = d['origin'][1] >= ty
        own = Point(tx, ty).buffer(30 * k)
        cands = []
        RM = rmax or (3001 if k < 0.5 else 2401)
        for dx in range(250, RM, 125):
            for dyv in range(300, RM, 150):
                for sy in (1, -1):
                    dy = sy * dyv
                    dist = math.hypot(dx, dy) + abs(abs(dx) - abs(dy)) * 0.3 + (0 if (dy > 0) == prefer_up else 150)
                    cands.append((dist, tx + dx * k, ty + dy * k))
        cands.sort()
        tb_tree = STRtree(texts) if texts else None
        best = None
        for i, (_, ox, oy) in enumerate(cands):
            o = (ox, oy)
            nb = note_box(o, d['l1'], d['l2'], sc)
            ld = LineString([(tx, ty), o])
            bad = 0
            if lt is not None:
                for j in lt.query(nb):
                    ln = lines[j]
                    if not ln.intersects(nb): continue
                    if ln.distance(own) < 1 and ln.intersection(nb).length < 1: continue
                    bad += 1
            if pt is not None:
                for j in pt.query(nb):
                    if polys[j].intersects(nb): bad += 1
            if tb_tree is not None:
                ldo = ld.difference(own)
                for j in tb_tree.query(nb.union(ld.envelope)):
                    tb = texts[j]
                    if tb.intersects(nb) or tb.intersects(ldo): bad += 1
            for pb, pl_ in placed:
                if pb.intersects(nb) or pb.intersects(ld) or pl_.intersects(nb): bad += 1
                if pl_.crosses(ld): bad += 3
            if lt is not None:
                for j in lt.query(ld):
                    ln = lines[j]
                    if ln.crosses(ld) and ln.distance(own) > 1: bad += 0.2
            score = bad * 100000 + i
            if best is None or score < best[0]: best = (score, o, nb, ld)
            if bad == 0: break
        _, o, nb, ld = best
        d['origin'] = [o[0], o[1]]
        placed.append((nb, ld))
        texts.append(nb)
    return len(notes)
