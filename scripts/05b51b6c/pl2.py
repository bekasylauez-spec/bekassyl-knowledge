"""Plan-sheet helpers v2 — Bekassyl rules (Obsidian 01_Общие правила, 05_Плиты):
outer chains in rows 1000 apart from the outermost contour (elements -> axes -> overall -> bubbles),
short dim texts on the outer side with a leader, marks = SPDS leader WITH arrow to the element edge facing the
plan centre, short 45 deg leader, shelf 400..600 off the element, shelf opposite to the arrow,
opening symbol = template broken line BL -> (0.3w, 0.75h) -> TR inside a thick contour."""
import math
import pl_ob

PI = math.pi
STEP = 750          # outer dim rows on A3 sheets (checklist #41)


class Ops(pl_ob.Ops):
    def dim2(self, tmpl, p1, p2, at, vertical=False, txt=None, tx=None):
        """dim with extension origins p1, p2 (on the element), dim line at 'at'"""
        if vertical:
            o = {'t': 'dim', 'h': tmpl, 'p1': list(p1), 'p2': list(p2), 'dl': [at, p1[1]], 'rot': PI / 2}
        else:
            o = {'t': 'dim', 'h': tmpl, 'p1': list(p1), 'p2': list(p2), 'dl': [p1[0], at], 'rot': 0}
        if txt: o['txt'] = txt
        if tx: o['tx'] = list(tx)
        self.add(o)

    def chain2(self, tmpl, pts, at, vertical=False, origin=None, out=1, small=700, origins=None, txo=None):
        """chain through sorted coordinates; ext origins at 'origin' (coordinate on the element side) or on the line.
        segments shorter than 'small' get the text on the outer side (out = +1 up/right, -1 down/left) beside their end."""
        pts = sorted(set(round(p, 1) for p in pts))
        segs = list(zip(pts, pts[1:]))
        for k, (a, b) in enumerate(segs):
            org = at if origin is None else origin
            o1 = origins.get(a, org) if origins else org
            o2 = origins.get(b, org) if origins else org
            tx = None
            if b - a < small:
                # outer side, at the end of the segment towards the shorter neighbour's far end
                end = b if (k == len(segs) - 1 or (k > 0 and False)) else a
                end = a if k == 0 else (b if k == len(segs) - 1 else (a + b) / 2)
                if vertical: tx = (at + out * 450, end)
                else: tx = (end, at + out * 450)
            if txo and k in txo: tx = txo[k]
            if vertical:
                self.dim2(tmpl, (o1, a), (o2, b), at, True, tx=tx)
            else:
                self.dim2(tmpl, (a, o1), (b, o2), at, tx=tx)

    def bind2(self, tmpl, c, half, at, vertical=False, out=1, org=None):
        """element binding half|half about axis c on line 'at'; texts on the outer side beside each end"""
        o = at if org is None else org
        if vertical:
            self.dim2(tmpl, (o, c - half), (o, c), at, True, tx=(at + out * 450, c - half - 250))
            self.dim2(tmpl, (o, c), (o, c + half), at, True, tx=(at + out * 450, c + half + 250))
        else:
            self.dim2(tmpl, (c - half, o), (c, o), at, tx=(c - half - 250, at + out * 450))
            self.dim2(tmpl, (c, o), (c + half, o), at, tx=(c + half + 250, at + out * 450))

    def mark(self, tmpl, text, tgt, dx, dy, off=500, text2=None):
        """SPDS mark: arrow at tgt (element edge), 45 deg leader to origin, shelf away from the arrow"""
        h = self.tag()
        org = (tgt[0] + dx * off, tgt[1] + dy * off)
        self.add({'t': 'clone', 'h': tmpl, 'tag': h})
        self.add({'t': 'moveto', 'h': h, 'idx': 1, 'to': list(tgt)})
        s = {'FirstLine': text, 'Origin': list(org), 'Angle': 0.0 if dx > 0 else PI, 'Arrow': 'Arrow'}
        if text2 is not None: s['SecondLine'] = text2
        self.add({'t': 'mcset', 'h': h, 'set': s})
        return h

    def opening(self, tmpl_thick, tmpl_thin, x0, y0, x1, y1):
        """slab opening: thick contour + template broken line BL -> (0.3w, 0.75h) -> TR"""
        self.ring(tmpl_thick, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        t = self.tag()
        self.add({'t': 'clone', 'h': tmpl_thin, 'tag': t})
        self.add({'t': 'plset', 'h': t, 'p': [[x0, y0], [x0 + 0.3 * (x1 - x0), y0 + 0.75 * (y1 - y0)], [x1, y1]], 'closed': False})
        self.add({'t': 'lw', 'h': t, 'v': 5}) if False else None


def rows(o, si, XS, YS, xmin, ymin, has_x_el, has_y_el, ytop=None, xright=None):
    """axes + axis chains placed in Bekassyl rows; returns (y of row1 bottom, x of row1 left, used handles)"""
    yb = [ymin - STEP * k for k in (1, 2, 3)]
    xl = [xmin - STEP * k for k in (1, 2, 3)]
    ax_row_y = yb[1] if has_x_el else yb[0]
    ov_row_y = yb[2] if has_x_el else yb[1]
    ax_row_x = xl[1] if has_y_el else xl[0]
    ov_row_x = xl[2] if has_y_el else xl[1]
    EB = ov_row_y - 500
    EL = ov_row_x - 500
    used = pl_ob.setup_axes(o, si, XS, YS, EB, EL, ax_row_y, ov_row_y, (ax_row_x, ov_row_x), ytop, xright)
    return yb[0], xl[0], EB, EL, used
