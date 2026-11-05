"""Shared helpers for the plan sheets (2.x) of «Помещение обезвоживания»."""
import math
import geo_ob

AX, AY = geo_ob.AX, geo_ob.AY
COLX, COLY = 700, 900          # column section in plan (along X, along Y)
TOPS = {}                      # column marks (axis index 0..7, row 0..2) -> mark


def colmark(i, j):
    if i in (6,):
        return 'Км-2'
    if i == 7:
        return 'Км-3'
    if j == 1 and i in (1, 2, 3, 4):
        return 'Км-1'
    if j == 1 and i in (0, 5):
        return 'Км-6'
    if i in (1, 2, 3, 4):
        return 'Км-4'
    return 'Км-5'


def fbeams():
    """foundation beams between pads: (mark, x0, y0, x1, y1) in mm (axis 1/A origin)"""
    out = []
    for y in AY:
        for a, b in zip(AX, AX[1:]):
            L = (b - 1000) - (a + 1000)
            mk = {1250: 'Фб-1', 2500: 'Фб-2', 4000: 'Фб-3'}[L]
            out.append((mk, a + 1000, y, b - 1000, y))
    for x in AX:
        for a, b in zip(AY, AY[1:]):
            out.append(('Фб-4', x, a + 1500, x, b - 1500))
    return out


class Ops:
    def __init__(self, tagpre):
        self.O = []; self.n = 0; self.pre = tagpre

    def tag(self):
        self.n += 1
        return '%s%d' % (self.pre, self.n)

    def add(self, o):
        self.O.append(o)

    def rect(self, tmpl, x0, y0, x1, y1, hatch=None):
        t = self.tag()
        pts = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        self.add({'t': 'clone', 'h': tmpl, 'tag': t}); self.add({'t': 'plset', 'h': t, 'p': pts, 'closed': True})
        if hatch:
            th = self.tag(); self.add({'t': 'clone', 'h': hatch, 'tag': th}); self.add({'t': 'hatchset', 'h': th, 'loops': [pts]})
        return t

    def ring(self, tmpl, pts):
        t = self.tag()
        self.add({'t': 'clone', 'h': tmpl, 'tag': t}); self.add({'t': 'plset', 'h': t, 'p': [[round(x, 1), round(y, 1)] for x, y in pts], 'closed': True})

    def dim(self, tmpl, p1, p2, dl, vertical=False, txt=None, tx=None):
        o = {'t': 'dim', 'h': tmpl, 'p1': list(p1), 'p2': list(p2), 'dl': list(dl), 'rot': math.pi / 2 if vertical else 0}
        if txt: o['txt'] = txt
        if tx: o['tx'] = list(tx)
        self.add(o)

    def chain(self, tmpl, pts, at, vertical=False):
        """consecutive dims through sorted points; horizontal: pts are x, at = y of dim line (ext origins on the line)"""
        pts = sorted(set(round(p, 1) for p in pts))
        for a, b in zip(pts, pts[1:]):
            if vertical:
                self.dim(tmpl, (at, a), (at, b), (at, a), True)
            else:
                self.dim(tmpl, (a, at), (b, at), (a, at))

    def note(self, tmpl, text, target, origin, text2=None):
        h = self.tag()
        self.add({'t': 'clone', 'h': tmpl, 'tag': h})
        self.add({'t': 'moveto', 'h': h, 'idx': 1, 'to': list(target)})
        s = {'FirstLine': text, 'Origin': list(origin)}
        if text2 is not None: s['SecondLine'] = text2
        self.add({'t': 'mcset', 'h': h, 'set': s})
        return h

    def bind(self, tmpl, c, half, at, vertical=False, out=450):
        """two small dims half|half about centre c on line 'at'; texts pushed outside the element"""
        if vertical:
            self.dim(tmpl, (at, c - half), (at, c), (at, c), True, tx=(at - 188, c - half - out))
            self.dim(tmpl, (at, c), (at, c + half), (at, c), True, tx=(at - 188, c + half + out))
        else:
            self.dim(tmpl, (c - half, at), (c, at), (c, at), tx=(c - half - out, at + 187))
            self.dim(tmpl, (c, at), (c + half, at), (c, at), tx=(c + half + out, at + 187))


def sheetinfo(win):
    """parse the 'list' op for a sheet window: axes, axis-chain dims, table, title mtext, stamp items"""
    import ab, os
    ab.run([{'t': 'list', 'win': win}], 'si')
    E = []
    for l in open(os.path.join(os.environ['TEMP'], 'ob_log.txt'), encoding='utf-8-sig'):
        f = l.rstrip('\n').split('\t')
        if f[0] != 'L' or len(f) < 5: continue
        ext = list(map(float, f[4][1:].split(',')))
        pts = [tuple(map(float, q.split(','))) for q in f[5:] if ',' in q]
        E.append(dict(t=f[1], h=f[2], lay=f[3], ext=ext, pts=pts))
    inside = lambda e: e['ext'][0] >= win[0] - 1 and e['ext'][2] <= win[2] + 1 and e['ext'][1] >= win[1] - 1 and e['ext'][3] <= win[3] + 1
    E = [e for e in E if inside(e)]
    ax = [e for e in E if e['t'] == 'SPDSCONSTRUCTIONLINE' and len(e['pts']) >= 2]
    V = sorted([e for e in ax if abs(e['pts'][0][0] - e['pts'][1][0]) < 1], key=lambda e: e['pts'][0][0])
    H = sorted([e for e in ax if abs(e['pts'][0][1] - e['pts'][1][1]) < 1], key=lambda e: e['pts'][0][1])
    dims = [e for e in E if e['t'] == 'DIMENSION' and e['lay'] == 'Размеры' and len(e['pts']) >= 4]
    hd = sorted([e for e in dims if abs(e['pts'][0][1] - e['pts'][1][1]) < 1], key=lambda e: (round(e['pts'][2][1]), e['pts'][0][0]))
    vd = sorted([e for e in dims if abs(e['pts'][0][0] - e['pts'][1][0]) < 1], key=lambda e: (round(e['pts'][2][0]), e['pts'][0][1]))
    keep = [e['h'] for e in E if e['t'] in ('SPDSFORMAT', 'ACAD_TABLE') or (e['t'] == 'INSERT' and e['ext'][1] < win[1] + 1000)
            or (e['t'] == 'MTEXT' and e['lay'] == 'О_Формат')]
    title = [e['h'] for e in E if e['t'] == 'MTEXT' and e['lay'] == 'Размеры' and e['ext'][3] - e['ext'][1] < 700]
    stamp = [e['h'] for e in E if e['t'] == 'MTEXT' and e['lay'] == 'О_Формат']
    table = [e['h'] for e in E if e['t'] == 'ACAD_TABLE']
    return dict(E=E, V=V, H=H, hd=hd, vd=vd, keep=keep, title=title, stamp=stamp, table=table)


def setup_axes(o, si, XS, YS, EB, EL, chain_y, over_y, left_x=(None, None), ytop=None, xright=None):
    """move the analog SPDS axes and axis chains of a plan sheet to the new grid; surplus ones erased"""
    V, H = si['V'], si['H']
    for i, e in enumerate(V):
        if i < len(XS): o.add({'t': 'axis', 'h': e['h'], 's': [XS[i], YS[-1] if ytop is None else ytop], 'e': [XS[i], EB], 'val': str(i + 1)})
        else: o.add({'t': 'erase', 'h': [e['h']]})
    for j, e in enumerate(H):
        if j < len(YS): o.add({'t': 'axis', 'h': e['h'], 's': [XS[-1] if xright is None else xright, YS[j]], 'e': [EL, YS[j]]})
        else: o.add({'t': 'erase', 'h': [e['h']]})
    hd = si['hd']
    Lx = lambda e: abs(e['pts'][1][0] - e['pts'][0][0])
    Ly = lambda e: abs(e['pts'][1][1] - e['pts'][0][1])
    ch = [e for e in hd if any(abs(Lx(e) - v) < 1 for v in (3250, 4500, 6000))]
    ov = [e for e in hd if any(abs(Lx(e) - v) < 1 for v in (60000, 32000, 20000))]
    for i, e in enumerate(ch):
        if i < len(XS) - 1:
            o.add({'t': 'dimset2', 'h': e['h'], 'p1': [XS[i], EB], 'p2': [XS[i + 1], EB], 'dl': [XS[i], chain_y], 'tx': [(XS[i] + XS[i + 1]) / 2, chain_y + 187]})
        else: o.add({'t': 'erase', 'h': [e['h']]})
    for k, e in enumerate(ov):
        if k == 0: o.add({'t': 'dimset2', 'h': e['h'], 'p1': [XS[0], EB], 'p2': [XS[-1], EB], 'dl': [XS[0], over_y], 'tx': [(XS[0] + XS[-1]) / 2, over_y + 187]})
        else: o.add({'t': 'erase', 'h': [e['h']]})
    vd = si['vd']
    xl1, xl2 = left_x
    small = [e for e in vd if abs(Ly(e) - 6000) < 1]
    big = [e for e in vd if abs(Ly(e) - 12000) < 1]
    for k, e in enumerate(small):
        if k < len(YS) - 1:
            o.add({'t': 'dimset2', 'h': e['h'], 'p1': [EL, YS[k]], 'p2': [EL, YS[k + 1]], 'dl': [xl1, YS[k]], 'tx': [xl1 - 188, (YS[k] + YS[k + 1]) / 2]})
        else: o.add({'t': 'erase', 'h': [e['h']]})
    for k, e in enumerate(big):
        if k == 0: o.add({'t': 'dimset2', 'h': e['h'], 'p1': [EL, YS[0]], 'p2': [EL, YS[-1]], 'dl': [xl2, YS[0]], 'tx': [xl2 - 188, (YS[0] + YS[-1]) / 2 + 1500]})
        else: o.add({'t': 'erase', 'h': [e['h']]})
    return [e['h'] for e in V + H + ch + ov + small + big]
