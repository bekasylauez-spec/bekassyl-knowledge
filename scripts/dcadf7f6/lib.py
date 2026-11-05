# -*- coding: utf-8 -*-
"""Аэротенк КЖ: op builders over ab.cs (analog objects of КЖ Резервуар cloned)."""
import math, json
OPS = []
_n = [0]

def op(**k):
    OPS.append(k); return k

def tag(p):
    _n[0] += 1; return '%s%d' % (p, _n[0])

FMT = {'A1': (841, 594), 'A2': (594, 420), 'A3': (420, 297), 'A4': (297, 210)}
A_FRAME = '1163FF'            # SPDSFORMAT A3 book (Резервуар 2.1), scale 100
A_STAMP = '116400'; A_STAMP_MIN = (10700, 340500)   # крпкер, 1:100 = 18500x5500
A_SNAME = '116401'; A_SNUM = '116403'
A_AXV = '116434'               # vertical axis, [0] top, [1] bottom marker
A_AXH = '116437'               # horizontal axis, [0] right, [1] left marker
A_DIM = '11644B'               # rotated dim, СПДС style, 1:100
A_PLEV = '116857'              # plane level mark "-3,700"
A_SEC = '11685D'               # section mark (Word 1)
A_TABLE = '11685F'             # spec of elements (12 rows x 13 cols)
A_LEV = '3227'               # level mark (section) -3,700 @ Y 345700, zero 349400 (2.3, scale 50)
A_LEV_ZERO = 295016.137

L_CONT = 'Несущие колонны'     # 0.30
L_THIN = 'Тонкая'              # 0.05
L_DIM = 'Размеры'
L_TXT = 'О_Формат'


class Sheet:
    def __init__(self, num, name, title, X0, Y0, fmt='A1', sc=100, horiz=True):
        self.num, self.name, self.title = num, name, title
        self.X0, self.Y0, self.fmt, self.sc = X0, Y0, fmt, sc
        w, h = FMT[fmt]
        if not horiz: w, h = h, w
        self.W, self.H = w * sc, h * sc
        self.horiz = horiz
        k = sc / 100.0
        t = tag('fr')
        op(t='clone', h=A_FRAME, tag=t)
        op(t='mcset', h=t, set={'Format': fmt, 'Name': fmt, 'Horizontal': horiz, 'Scale': sc})
        op(t='mcset', h=t, set={'Origin': [X0, Y0]})
        sx, sy = X0 + self.W - 500 * k - 18500 * k, Y0 + 500 * k
        for h, txt in ((A_STAMP, None), (A_SNAME, name), (A_SNUM, num)):
            d = dict(t='clone', h=h, base=list(A_STAMP_MIN), to=[sx, sy], s=k, tag=tag('st'))
            if txt is not None: d['text'] = txt
            op(**d)
        self.stamp = (sx, sy, sx + 18500 * k, sy + 5500 * k)
        if title:
            self.text(title_u(title), X0 + self.W / 2 + 10 * k * 100 / 100, Y0 + self.H - 1500 * k, 300 * k, att=8, layer='0')

    def k(self):
        return self.sc / 100.0

    def text(self, s, x, y, h=None, att=1, layer=L_TXT, w=None, rot=None):
        d = dict(t='mtext', at=[x, y], h=h or 250 * self.k(), att=att, s=s, style='Isocpeur', layer=layer)
        if w: d['w'] = w
        if rot is not None: d['rot'] = rot
        return op(**d)

    def notes(self, lines, x=None, y=None, w=None):
        k = self.k()
        s = '\\pxi-3.3333,l3.3333,ql,t3.3333;' + '\\P'.join('%d.	%s' % (i + 1, l) for i, l in enumerate(lines))
        if x is None: x = self.stamp[0]
        if y is None: y = self.stamp[3] + 462 * k
        return self.text(s, x, y, 250 * k, att=7, w=w or 18500 * k)


def title_u(s):
    return '{\\L' + s + '}'


def pl(pts, layer=L_CONT, closed=False, lw=None, ltype=None, ltscale=None, color=None):
    d = dict(t='pl', p=[list(map(float, p)) for p in pts], layer=layer, closed=closed)
    if lw is not None: d['lw'] = lw
    if ltype: d['ltype'] = ltype
    if ltscale: d['ltscale'] = ltscale
    if color is not None: d['color'] = color
    return op(**d)


def rect(x0, y0, x1, y1, **k):
    return pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, **k)


def hatch(loops, pat='ANSI36', sc=20, layer=L_DIM, lw=5, ang=None):
    d = dict(t='hatch', pat=pat, sc=sc, layer=layer, lw=lw, loops=[[list(map(float, p)) for p in lp] for lp in loops])
    if ang is not None: d['ang'] = ang
    return op(**d)


def axis(val, s, e, sc=100, vertical=True):
    t = tag('ax')
    op(t='clone', h=A_AXV if vertical else A_AXH, tag=t)
    op(t='axis', h=t, s=list(s), e=list(e), val=val, scale=sc)
    return t


def dim(p1, p2, dl, rot=0.0, sc=100, txt=None, tx=None):
    """rot 0 = horizontal (measures dx), pi/2 = vertical"""
    d = dict(t='dim', h=A_DIM, p1=list(p1), p2=list(p2), dl=list(dl), rot=rot, dscale=sc, layer=L_DIM)
    if txt: d['txt'] = txt
    if tx: d['tx'] = list(tx)
    return op(**d)


def chain_h(xs, y_ext, y_dl, sc=100, texts=None):
    """horizontal chain: ext points at y_ext, dim line at y_dl"""
    for i in range(len(xs) - 1):
        t = texts[i] if texts else None
        dim((xs[i], y_ext), (xs[i + 1], y_ext), (xs[i], y_dl), 0.0, sc, txt=t)


def chain_v(ys, x_ext, x_dl, sc=100, texts=None):
    for i in range(len(ys) - 1):
        t = texts[i] if texts else None
        dim((x_ext, ys[i]), (x_ext, ys[i + 1]), (x_dl, ys[i]), math.pi / 2, sc, txt=t)


def note(l1, l2, origin, target, sc=100, arrow='arrow', align='Center'):
    d = dict(t='note', l1=l1, l2=l2 or '', origin=list(origin), target=list(target), scale=sc, ts=2.5, arrow=arrow, layer=L_DIM, align=align)
    return op(**d)


def plev(value, at, sc=100):
    """plane level mark (in plans): clone '-3,700' and replace value text"""
    t = tag('pl')
    op(t='clone', h=A_PLEV, tag=t)
    k0 = sc / 100.0
    op(t='moveto', h=t, idx=0, to=list(at), _box=[at[0] - 30 * k0, at[1] - 30 * k0, at[0] + 1224 * k0, at[1] + 460 * k0])
    t2 = tag('pv')
    op(t='levelval', h=t, old='-3,700', value=value, tag=t2)
    if sc != 100: op(t='mcscale', h=t2, v=sc)
    return t2


def lev(y_zero, at, sc=100, ref=None, side='L', ext=None):
    """section level mark: shows (Y - y_zero)/1000; at = point on the level line (idx0)"""
    t = tag('lv')
    op(t='clone', h=A_LEV, tag=t)
    t2 = tag('lb')
    op(t='levbase', h=t, old=A_LEV_ZERO, new=y_zero, tag=t2)
    v = (at[1] - y_zero) / 1000.0
    txt = ('+' if v > 0.0005 else ('-' if v < -0.0005 else '')) + ('%.3f' % abs(v)).replace('.', ',')
    if abs(v) < 0.0005: txt = '0,000'
    t3 = tag('lt')
    op(t='levelval', h=t2, old='-2,000', value=txt, tag=t3)
    op(t='mcscale', h=t3, v=sc)
    k = sc / 100.0
    _e = (ext if ext is not None else 2902 * k) + 1254 * k
    _bx = [at[0] - _e, at[1] - 30 * k, at[0], at[1] + 650 * k] if side == 'L' else [at[0], at[1] - 30 * k, at[0] + _e, at[1] + 650 * k]
    op(t='moveto', h=t3, idx=0, to=list(at), _box=_bx)
    e = ext if ext is not None else 2902 * k
    sg = -1 if side == 'L' else 1
    if sc != 100 or side != 'L' or ext is not None:
        op(t='sp_set', h=t3, pts=[[2, at[0] + sg * e, at[1]], [1, at[0] + sg * (e + 1254 * k), at[1] + 600 * k]])
    return t3


def section(word, p0, p1, sc=100):
    t = tag('se')
    op(t='clone', h=A_SEC, tag=t)
    op(t='sp_set', h=t, pts=[[0, p0[0], p0[1]], [1, p1[0], p1[1]]])
    op(t='mcset', h=t, set={'Word': str(word), 'Scale': sc})
    return t


def dump(path):
    json.dump(OPS, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
