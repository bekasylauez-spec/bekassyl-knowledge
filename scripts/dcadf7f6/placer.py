# -*- coding: utf-8 -*-
"""Post-process lib.OPS: move SPDS notes / plane levels to free places (no text over line / text)."""
import math
from shapely.geometry import LineString, box, Point
from shapely.strtree import STRtree

CW = 0.75


def tw(s, h):
    return max(1, sum(0.85 if c.isdigit() else CW for c in s)) * h


def dim_geom(o):
    p1, p2, dl = o['p1'], o['p2'], o['dl']; rot = o.get('rot', 0.0); k = o.get('dscale', 100) / 100.0
    segs, boxes = [], []
    if abs(rot) < 1e-6:
        y = dl[1]; segs += [LineString([(p1[0], p1[1]), (p1[0], y)]), LineString([(p2[0], p2[1]), (p2[0], y)]), LineString([(p1[0], y), (p2[0], y)])]
        L = abs(p2[0] - p1[0]); t = o.get('txt') or '%d' % round(L); w = tw(t, 250 * k)
        xm = (p1[0] + p2[0]) / 2
        if w + 200 * k > L: xm = max(p1[0], p2[0]) + w / 2 + 150 * k
        boxes.append(box(xm - w / 2, y + 60 * k, xm + w / 2, y + 60 * k + 250 * k))
    else:
        x = dl[0]; segs += [LineString([(p1[0], p1[1]), (x, p1[1])]), LineString([(p2[0], p2[1]), (x, p2[1])]), LineString([(x, p1[1]), (x, p2[1])])]
        L = abs(p2[1] - p1[1]); t = o.get('txt') or '%d' % round(L); w = tw(t, 250 * k)
        ym = (p1[1] + p2[1]) / 2
        if w + 200 * k > L: ym = max(p1[1], p2[1]) + w / 2 + 150 * k
        boxes.append(box(x - 60 * k - 250 * k, ym - w / 2, x - 60 * k, ym + w / 2))
    return segs, boxes


def collect(ops, tagpos):
    segs, boxes = [], []
    for o in ops:
        t = o.get('t')
        if t == 'pl':
            p = o['p'] + ([o['p'][0]] if o.get('closed') else [])
            for a, b in zip(p, p[1:]): segs.append(LineString([tuple(a), tuple(b)]))
        elif t == 'dim':
            s, b = dim_geom(o); segs += s; boxes += b
        elif t == 'axis':
            segs.append(LineString([tuple(o['s']), tuple(o['e'])]))
            k = o.get('scale', 100) / 100.0; e = o['e']; boxes.append(Point(e).buffer(500 * k))
        elif t == 'mtext':
            h = o['h']; lines = o['s'].split('\\P'); w = max(tw(l.replace('{\\L', '').replace('}', ''), h) for l in lines)
            if o.get('w'): w = min(w, o['w'])
            n = len(lines) if not o.get('w') else max(len(lines), int(sum(tw(l, h) for l in lines) / max(o['w'], 1)) + len(lines))
            x, y = o['at']; att = o.get('att', 1); H = n * h * 1.6
            dx = {1: 0, 2: -w / 2, 0: -w}[att % 3]; dy = {0: -H, 1: -H / 2, 2: 0}[(att - 1) // 3]
            boxes.append(box(x + dx, y + dy, x + dx + w, y + dy + H))
        elif t == 'moveto' and o.get('h', '').startswith('pv'):
            pass
    return segs, boxes


def note_shapes(o, org):
    k = o['scale'] / 100.0; h = 250 * k
    w = max(tw(o['l1'], h), tw(o.get('l2', '') or '', h)) + 150 * k
    tx, ty = o['target']; ox, oy = org
    right = ox >= tx
    x0, x1 = (ox, ox + w) if right else (ox - w, ox)
    shelf = LineString([(x0, oy), (x1, oy)])
    lead = LineString([(tx, ty), (ox, oy)])
    tb = [box(x0, oy + 40 * k, x1, oy + 40 * k + h * 1.15)]
    if o.get('l2'): tb.append(box(x0, oy - 40 * k - h * 1.15, x1, oy - 40 * k))
    return shelf, lead, tb


def place(ops, log=None):
    segs, boxes = collect(ops, {})
    tree = STRtree(segs) if segs else None
    placed = []
    nmoved = 0
    for o in ops:
        if o.get('t') != 'note': continue
        k = o['scale'] / 100.0
        tx, ty = o['target']; ox, oy = o['origin']
        d0 = (ox - tx, oy - ty)
        sx0 = 1 if d0[0] >= 0 else -1; sy0 = 1 if d0[1] >= 0 else -1
        cands = []
        for r in (1.0, 1.5, 2.0, 2.6, 3.3, 4.0):
            for sx, sy in ((sx0, sy0), (sx0, -sy0), (-sx0, sy0), (-sx0, -sy0)):
                cands.append((tx + sx * 400 * k * r, ty + sy * 400 * k * r))
        tgt = Point(tx, ty).buffer(60 * k)
        best = None
        for i, c in enumerate(cands):
            shelf, lead, tb = note_shapes(o, c)
            bad = 0
            for g in tb + [shelf]:
                if tree is not None:
                    for j in tree.query(g):
                        sg = segs[j]
                        if sg.intersects(g) and not sg.intersection(g).within(tgt): bad += 1
                for b in boxes + placed:
                    if b.intersects(g): bad += 2
            if tree is not None:
                for j in tree.query(lead):
                    sg = segs[j]
                    if sg.intersects(lead) and not sg.intersection(lead).within(tgt) and sg.distance(Point(tx, ty)) > 5:
                        bad += 0.5
            for b in boxes + placed:
                if b.intersects(lead): bad += 1
            score = bad * 100 + i
            if best is None or score < best[0]: best = (score, c, tb, shelf)
            if bad == 0: break
        if list(best[1]) != [ox, oy]: nmoved += 1
        o['origin'] = [best[1][0], best[1][1]]
        placed += best[2]
    if log is not None: log.append('placer moved %d notes' % nmoved)
    return nmoved
