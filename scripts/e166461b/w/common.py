# Резервуар КЖ: лист 2 (схемы расположения на отм. -3.700 и -0.900, 1:100) и лист 3 (разрезы 1-1, 2-2, 1:50)
# Local plan coords: x from axis 1, y from axis А (mm). Section coords: x along cut, y = elevation in mm (0.000 = 0).
import json, sys, math

ops = []
def add(**k): ops.append(k); return k

# ---- geometry (AR outline + LIRA elements, decisions 31.10) ----
AX = {'1': 0, '2': 8250, '3': 14750}
AY = {'А': 0, 'Б': 4100, 'В': 8400, 'Г': 12500, 'Д': 17750}
T = 250; h = T / 2
XO, XE = -h, 14750 + h          # outer faces x
YO, YE = -h, 17750 + h          # outer faces y
CON = 500                        # Фм-1 console beyond the walls (Bekassyl 31.10: as in LIRA)
FXO, FXE, FYO, FYE = XO - CON, XE + CON, YO - CON, YE + CON
pil = {  # pilasters 400x400 flush with outer face; columns 400x400; junction 500x500
    'П1Б': (-h, 3900, 275, 4300), 'П1В': (-h, 8200, 275, 8600),
    'П3Б': (14475, 3900, XE, 4300), 'П3В': (14475, 8200, XE, 8600), 'П3Г': (14475, 12300, XE, 12700),
    'ПА2': (8050, -h, 8450, 275)}
cols = {'К2Б': (8050, 3900, 8450, 4300), 'К2В': (8050, 8200, 8450, 8600)}
col3 = (8000, 12250, 8500, 12750)
walls1 = {  # outer walls См-1 split at pilasters
    'А': [(XO, YO, 8050, h), (8450, YO, XE, h)],
    'Д': [(XO, 17625, XE, YE)],
    '1': [(XO, h, h, 3900), (XO, 4300, h, 8200), (XO, 8600, h, 17625)],
    '3': [(14625, h, XE, 3900), (14625, 4300, XE, 8200), (14625, 8600, XE, 12300), (14625, 12700, XE, 17625)]}
walls2 = [(h, 12375, 8000, 12625), (8125, 12750, 8375, 17625)]   # partition См-2
necks = {'N1': (625, 10375, 2125, 11875), 'N2': (625, 13125, 2125, 14625), 'N3': (625, 15125, 2625, 17125)}
tn = 150   # neck wall (LIRA)
pit = (4625, 13125, 5625, 14125)   # приямок 1000x1000, depth 500 (assumed), base 400 under it
pitb = (4225, 12725, 6025, 14525)
beams1 = [(8075, 275, 8425, 12250), (8450, 3925, 14475, 4275), (8450, 8225, 14475, 8575), (8500, 12325, 14475, 12675)]  # Бм-1 350x500
beams2 = [(275, 3925, 8050, 4275), (275, 8225, 8050, 8575)]   # Бм-2 350x600
Z = dict(top=-900, slb=-1200, b1=-1400, b2=-1500, fnd=-3700, fbot=-4100, prep=-4200, pitb=-4200, pitbot=-4600, pitprep=-4700, neck=100, gr=-300)

# ---- template sources ----
SRC = dict(fr100='33C2', fr100o=(71667.3, 271897.8), fr50='244FB', fr50o=(556617.3, 271897.8),
           stampf=(190467.3, 271897.8), stamp=['19522'], sname='19523', snum='19525',
           axis='3201', dim='3203', lev='3227', levbase=(89797.3, 293016.1), lev0='-2,000',
           plev='239E1', plevbase=(501388, 307683), plev0='-0,080',
           bound='3262', boundbase=(88320.2, 292616.2), sec='238E8', secbase=(472785.1, 297378.5),
           title='3230', titlebase=(96393, 305204))

CWD = 0.85                     # ISOCPEUR char width / height (measured on the plots, 31.10)
MARKQ = []
def flush_marks():
    while MARKQ: MARKQ.pop(0)()

def occupied(kinds=None):
    # everything already drawn (model coords) as shapely geometry: lines, dims, axes, texts, notes - for free-spot search
    from shapely.geometry import LineString as _L, box as _B
    g = []
    for o in ops:
        t = o.get('t')
        if kinds and t not in kinds: continue
        try:
            if t == 'pl':
                pts = [tuple(p) for p in o['p']] + ([tuple(o['p'][0])] if o.get('closed') else [])
                if len(pts) > 1: g.append(_L(pts))
            elif t == 'dim':
                p1, p2, dl = o['p1'], o['p2'], o['dl']
                ds = o.get('dscale', 100) * (o.get('lfac', 1) if o.get('lfac') else 1); t_ = 2.5 * ds   # text height in model units
                if abs(o.get('rot', 0)) < 0.1:
                    g += [_L([p1, (p1[0], dl[1])]), _L([p2, (p2[0], dl[1])])]
                    if not o.get('tx'): g.append(_B(min(p1[0], p2[0]), dl[1] - 0.4 * t_, max(p1[0], p2[0]), dl[1] + 1.6 * t_))
                else:
                    g += [_L([p1, (dl[0], p1[1])]), _L([p2, (dl[0], p2[1])])]
                    if not o.get('tx'): g.append(_B(dl[0] - 1.6 * t_, min(p1[1], p2[1]), dl[0] + 0.4 * t_, max(p1[1], p2[1])))
                if o.get('tx'):
                    w_ = len(o.get('txt') or '0000') * CWD * t_ / 2 + 0.2 * t_; v_ = abs(o.get('rot', 0)) > 0.1
                    cx_, cy_ = o['tx'][0] - (0.9 * t_ if v_ else 0), o['tx'][1] + (0 if v_ else 0.9 * t_)   # with the DIMTAD lift
                    g.append(_B(o['tx'][0] - (1.8 * t_ if v_ else w_ + 0.6 * t_), o['tx'][1] - (w_ + 0.6 * t_ if v_ else 1.8 * t_), o['tx'][0] + (1.8 * t_ if v_ else w_ + 0.6 * t_), o['tx'][1] + (w_ + 0.6 * t_ if v_ else 1.8 * t_)))   # moved text: AutoCAD places it at the leader end - generous box
                    g.append(_L([((p1[0] + p2[0]) / 2 if not v_ else dl[0], (p1[1] + p2[1]) / 2 if v_ else dl[1]), (cx_, cy_)]))   # leader
            elif t == 'axis': g.append(_L([tuple(o['s']), tuple(o['e'])]))
            elif t == 'mtext':
                w, h = o.get('w', 1000), o.get('h', 250); x, y = o['at']
                g.append(_B(x - w / 2, y - h, x + w / 2, y + h))
            elif t == 'note':
                x, y = o['origin']; sc = o.get('scale', 100); n_ = max(len(o.get('l1', '')), len(o.get('l2', ''))) * CWD * 2.5 * sc + sc
                lft = sum(q[0] for q in o['targets']) / len(o['targets']) > x
                g.append(_B(x - n_ if lft else x, y - (3.5 * sc if o.get('l2') else 1.0 * sc), x if lft else x + n_, y + 3.5 * sc))   # incl. under the shelf
                for q in o['targets']: g.append(_L([(x, y), tuple(q)]))
        except Exception:
            pass
    return g

def rect(r): x0, y0, x1, y1 = r; return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

class Sheet:
    def __init__(s, ox, oy, sc): s.ox, s.oy, s.sc = ox, oy, sc; s.avoid_x = list(AX.values()); s.avoid_y = list(AY.values())
    def P(s, x, y): return [round(s.ox + x, 2), round(s.oy + y, 2)]
    def pl(s, pts, layer='Несущие колонны', closed=True, **k):
        return add(t='pl', p=[s.P(*p) for p in pts], closed=closed, layer=layer, **k)
    def hatch(s, loops, pat='ANSI36', sc=20, layer='Размеры', **k):
        # concrete as in the template (Bekassyl 31.10): ANSI36, scale 20 on any sheet scale, layer Размеры, 0.05 mm
        return add(t='hatch', loops=[[s.P(*p) for p in lp] for lp in loops], pat=pat, sc=sc, layer=layer, lw=5, **k)
    def solid(s, r, pat='ANSI36', **k):
        s.pl(rect(r)); s.hatch([rect(r)], pat=pat, **k)
    def hid(s, pts, closed=False):
        return add(t='pl', p=[s.P(*p) for p in pts], closed=closed, layer='Тонкая', ltype='HIDDEN2', ltscale=s.sc / 4)
    def thin(s, pts, closed=False):
        return add(t='pl', p=[s.P(*p) for p in pts], closed=closed, layer='Тонкая')
    def dim(s, a, b, off, vert=False, tx=None, txt=None):
        # chain dimension between coordinates a,b along axis; off = dim line position on the other axis
        # tx = (along, perp) text centre in local coords along the dim / across it
        if vert: p1, p2, dl, rot = s.P(off[0], a), s.P(off[0], b), s.P(off[1], a), math.pi / 2
        else: p1, p2, dl, rot = s.P(a, off[0]), s.P(b, off[0]), s.P(a, off[1]), 0
        if tx is None:                                    # №32: no axis/level line through the text
            av = getattr(s, 'avoid_y' if vert else 'avoid_x', [])
            th = 2.5 * s.sc; lo, hi = min(a, b), max(a, b); mid = (a + b) / 2
            w = len(txt or str(int(round(hi - lo)))) * CWD * th
            hit = [v for v in av if abs(v - mid) < w / 2 + 0.3 * th]
            if hit and hi - lo >= 7 * s.sc:
                v = hit[0]; right = (hi - v) >= (v - lo)
                along = v + (w / 2 + 0.5 * th) if right else v - (w / 2 + 0.5 * th)
                tx = (along, off[1])        # on the dim line: DIMTAD lifts the text by DIMGAP itself (Bekassyl sample 31.10)
                if txt and max(hi - v, v - lo) < w + 0.6 * th:   # «200xN» too long for either half: text on the far side of the
                    out = 1 if off[1] >= off[0] else -1          # dim line, clear of the extension lines
                    tx = (along, off[1] + out * 1.4 * th)
                elif max(hi - v, v - lo) < w + 0.6 * th:          # axis in the middle of a short dim: text beside, past the end
                    out = 1 if off[1] >= off[0] else -1
                    tx = (hi + w / 2 + 0.5 * th, off[1] + out * 1.6 * th)
        k = dict(t='dim', h=SRC['dim'], p1=p1, p2=p2, dl=dl, rot=rot, dscale=s.sc)
        if tx: k['tx'] = s.P(tx[1], tx[0]) if vert else s.P(tx[0], tx[1])
        if txt: k['txt'] = txt
        return add(**k)
    def chain(s, pts, base, line, vert=False, inside=False, end_in=False):
        # Bekassyl 31.10 sample: a short dim whose text does not fit between its extension lines keeps the text at its own
        # segment, moved OUT of the dim line (AutoCAD adds the leader). If an axis/level line runs through it there, the text
        # goes past the OUTER end (first/last segment) or towards the longer neighbour (middle segment).
        th = 2.5 * s.sc; n = len(pts) - 1
        out = 1 if line >= base else -1                     # away from the element the chain measures
        av = getattr(s, 'avoid_y' if vert else 'avoid_x', [])
        segs = [abs(b - a) for a, b in zip(pts, pts[1:])]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            L = abs(b - a); tx = None; lo, hi = min(a, b), max(a, b)
            wt = len(str(int(round(L)))) * CWD * th            # real ISOCPEUR digit width (0.85 h)
            if L < wt + 1.0 * th:                              # needs ~1.25 mm clear at each extension line
                g = wt / 2 + 0.4 * th
                hit = lambda al: any(abs(v - al) < g for v in av)
                al = (a + b) / 2
                if hit(al):
                    beyond_lo, beyond_hi = lo - g, hi + g
                    up = pts[1] > pts[0]                         # chain runs in +direction
                    if i == 0: c = [beyond_lo if up else beyond_hi]
                    elif i == n - 1: c = [beyond_hi if up else beyond_lo]
                    else:
                        prv, nxt = segs[i - 1], segs[i + 1]
                        c = [beyond_lo, beyond_hi] if (prv >= nxt) == up else [beyond_hi, beyond_lo]
                    c += [beyond_lo, beyond_hi]
                    al = next((q for q in c if not hit(q)), c[0])
                # free spot against everything already drawn (contours, walls, dims): along x across candidates
                from shapely.geometry import box as _B
                from shapely.ops import unary_union as _U
                OC = _U(occupied())
                def tbox(al_, pp_):
                    if vert: (x0_, y0_), (x1_, y1_) = s.P(pp_ - 0.6 * th, al_ - wt / 2), s.P(pp_ + 0.6 * th, al_ + wt / 2)
                    else: (x0_, y0_), (x1_, y1_) = s.P(al_ - wt / 2, pp_ - 0.6 * th), s.P(al_ + wt / 2, pp_ + 0.6 * th)
                    return _B(min(x0_, x1_), min(y0_, y1_), max(x0_, x1_), max(y0_, y1_))
                g2 = wt / 2 + 0.4 * th
                alongs = [al, (a + b) / 2, lo - g2, hi + g2, lo - g2 - th, hi + g2 + th, lo - g2 - 2 * th, hi + g2 + 2 * th]
                pick = None
                for pp in (line + out * 2.7 * th, line + out * 1.9 * th, line + out * 3.4 * th, line - out * 1.9 * th):
                    for q in alongs:
                        if not hit(q) and not tbox(q, pp).intersects(OC): pick = (q, pp); break
                    if pick: break
                if pick is None: pick = (al, line + out * 2.7 * th); print('WARNING short dim text without a free spot', L)
                # DIMTAD lift ~0.9 th (-x for vertical dims, +y for horizontal) is compensated
                tx = (pick[0], pick[1] + (0.9 * th if vert else -0.9 * th))
            s.dim(a, b, (base, line), vert, tx)
    def axis(s, tag, val, st, en):
        add(t='clone', h=SRC['axis'], tag=tag)
        add(t='axis', h=tag, s=s.P(*st), e=s.P(*en), val=val, scale=s.sc)
    def level(s, tag, val, x, y, down=False, right=False, ax=None):
        b = SRC['levbase']
        add(t='clone', h=SRC['lev'], base=list(b), to=s.P(x, y), tag=tag)
        add(t='levbase', h=tag, old=295016.137, new=s.oy, tol=0.5, tag=tag)   # zero level of this drawing
        add(t='levelval', h=tag, old=SRC['lev0'], value=val, tag=tag)
        if s.sc != 100: add(t='mcscale', h=tag, v=s.sc)
        f = s.sc / 100   # x = contour face; arrow 1800 (at 1:50) left of it, shelf like the template
        add(t='moveto', h=tag, idx=0, to=s.P(x, y))
        # close marks must not overlap (Bekassyl 31.10): lower one turned down (shelf below, arrow up) or put on the right
        k = 1 if right else -1; up = -1 if down else 1
        axp = ax if ax is not None else x + k * 36 * s.sc
        add(t='sp_set', h=tag, pts=[[2] + s.P(axp, y), [1] + s.P(axp + k * 1254 * f, y + up * 600 * f)])
    def plevel(s, tag, val, x, y):
        add(t='clone', h=SRC['plev'], base=list(SRC['plevbase']), to=s.P(x, y), tag=tag)
        add(t='levelval', h=tag, old=SRC['plev0'], value=val, tag=tag)
    def note(s, l1, org, tgts, l2='', arrow='arrow'):
        # shelf on the side opposite the arrow (Bekassyl 31.10): target to the right -> shelf to the left (Angle = pi)
        ang = math.pi if sum(q[0] for q in tgts) / len(tgts) > org[0] else 0
        add(t='note', l1=l1, l2=l2, origin=s.P(*org), targets=[s.P(*q) for q in tgts], scale=s.sc, arrow=arrow, layer='Размеры', angle=ang)
    def mark(s, *a, **k):                       # queued: placed after all lines/dims of the drawing exist (flush_marks)
        MARKQ.append(lambda: s._mark(*a, **k))
    def _mark(s, l1, r, face=None, at=None, d=400, dx=None, dy=None, l2=''):
        # Bekassyl 31.10: arrow on the element edge facing the drawing centre (s.cx, s.cy), shelf start 300..600 from it,
        # shelf opposite the arrow (note()). Free-spot search («неге қайталадың»): the label box must not touch anything
        # already drawn, the leader must not cross elements/axes; the given face first, then the other faces.
        from shapely.geometry import box as _B, LineString as _L
        from shapely.ops import unary_union as _U
        x0, y0, x1, y1 = r; cx, cy = s.cx, s.cy
        dxc = cx - min(max(cx, x0), x1); dyc = cy - min(max(cy, y0), y1)
        if face is None: face = ('x1' if dxc > 0 else 'x0') if abs(dxc) > abs(dyc) else ('y1' if dyc > 0 else 'y0')
        OCC = _U(occupied()); OEL = _U(occupied(('pl', 'axis'))); th = 2.5 * s.sc
        wl = max(len(l1), len(l2)) * CWD * th + 0.5 * th
        def lab(ox_, oy_, tx_, ty_):
            P = s.P(ox_, oy_); lft = tx_ > ox_
            return _B(P[0] - wl if lft else P[0], P[1] - (1.4 * th if l2 else 0.2 * th), P[0] if lft else P[0] + wl, P[1] + 1.4 * th)
        def base(fc, at_):
            if fc in ('x0', 'x1'):
                tx = x0 if fc == 'x0' else x1; ty = at_ if at_ is not None else min(max(cy, y0), y1)
            else:
                ty = y0 if fc == 'y0' else y1; tx = at_ if at_ is not None else min(max(cx, x0), x1)
            sx = 1 if cx >= tx else -1; sy = 1 if cy >= ty else -1
            if fc == 'x1': sx = 1
            if fc == 'x0': sx = -1
            if fc == 'y1': sy = 1
            if fc == 'y0': sy = -1
            # См-1 sample: clearance edge -> top of the text 4 mm; a note BELOW the element drops by the text band
            band = 4 * s.sc if fc == 'y0' and dy is None else 0
            return tx, ty, sx, sy, tx + sx * (dx if dx is not None else d), ty + sy * ((dy if dy is not None else d) + band)
        faces = [face] + [f for f in ('x0', 'x1', 'y0', 'y1') if f != face]
        best = None
        for fc in faces:
            tx, ty, sx, sy, ox, oy = base(fc, at if fc == face else None)
            for dd in (0, 200, 400, 700, 1000, 1400, 2000):
                for sh in (0, 300, -300, 600, -600, 900, -900, 1500, -1500, 2200, -2200):
                    if fc in ('x0', 'x1'):
                        ty2 = min(max(ty + sh, y0 + 50), y1 - 50); tx2 = tx; ox2 = ox + sx * dd; oy2 = oy + sh   # label may slide past a short face
                    else:
                        tx2 = min(max(tx + sh, x0 + 50), x1 - 50); ty2 = ty; ox2 = ox + sh; oy2 = oy + sy * dd
                    T = s.P(tx2, ty2); ld = _L([s.P(ox2, oy2), T])
                    if not lab(ox2, oy2, tx2, ty2).intersects(OCC) and not ld.crosses(OEL.difference(_B(T[0] - 60, T[1] - 60, T[0] + 60, T[1] + 60))):
                        best = (ox2, oy2, tx2, ty2); break
                if best: break
            if best: break
        if best is None:
            tx, ty, sx, sy, ox, oy = base(face, at); print('WARNING mark without a free spot:', l1); best = (ox, oy, tx, ty)
        s.note(l1, (best[0], best[1]), [(best[2], best[3])], l2=l2)
    def title(s, text, x, y, cx=None):
        # Bekassyl 31.10 sample: one line, underlined, layer 0, Standard, 3 mm on paper, centred (MText middle-centre)
        h = 3.0 * s.sc; w = len(text) * 0.75 * h + 2 * h
        c = cx if cx is not None else x + w / 2
        add(t='mtext', at=s.P(c, y - h / 2), h=h, w=w, att=5, style='Standard', layer='0', s='{\\L' + text + '}')
    def section(s, tag, word, a, b, d=-1):
        add(t='clone', h=SRC['sec'], base=list(SRC['secbase']), to=s.P(*a), tag=tag)
        add(t='sp_set', h=tag, pts=[[0] + s.P(*a), [1] + s.P(*b)])
        add(t='mcset', h=tag, set={'Word': word, 'Dir': d})
    def bound(s, tag, a, b):
        add(t='clone', h=SRC['bound'], base=list(SRC['boundbase']), to=s.P(*a), tag=tag)
        add(t='sp_set', h=tag, pts=[[0] + s.P(*a), [1] + s.P(*b)])
        if s.sc != 100: add(t='mcscale', h=tag, v=s.sc)

SHW = {'A2': 59400, 'A3': 42000, 'A3P': 29700}   # sheet width at 1:100
SPEC_H = lambda n: 2300 + 633 * n               # spec 11BF4 height with n rows (measured 2.1/2.2)

def frame(fx, fy, sc, name, num, fmt='A2'):
    if fmt in ('A3', 'A3P'): src, so = '1A0B3', (294417.3, 271897.8)  # A3 1:100 frame of the template
    else: src, so = (SRC['fr100'], SRC['fr100o']) if sc == 100 else (SRC['fr50'], SRC['fr50o'])
    add(t='clone', h=src, base=list(so), to=[fx, fy], tag='frame' + num)
    if fmt == 'A3P': add(t='mcset', h='frame' + num, set={'Horizontal': False})   # portrait (McFormat.Horizontal)
    if fmt in ('A3', 'A3P') and sc != 100: add(t='mcscale', h='frame' + num, v=sc)
    f = sc / 100
    sb = list(SRC['stampf'])
    sb[0] += 59400 - SHW[fmt]                                       # stamp to the right edge of the sheet
    for hh in SRC['stamp']:
        add(t='clone', h=hh, base=sb, to=[fx, fy], s=f, tag='stamp' + num)
    add(t='clone', h=SRC['sname'], base=sb, to=[fx, fy], s=f, text=name, tag='sname' + num)
    add(t='clone', h=SRC['snum'], base=sb, to=[fx, fy], s=f, text=num, tag='snum' + num)

def spec(fx, fy, tag, title, rows, W=42000, top=28700):
    # clone the template scheme spec 11BF4 (18 rows) above the stamp, left edge = stamp left edge
    add(t='clone', h='11BF4', base=[49980, 305086], to=[fx + W - 19000, fy + top], tag=tag)
    n = 2 + len(rows)
    if n < 18: add(t='trows', h=tag, mode='del', at=n, n=18 - n)
    cells = [[0, 0, '{\C256;' + title + '}']]
    for i, r in enumerate(rows):
        k = 2 + i
        if len(r) == 1: cells += [[k, 0, ''], [k, 1, ''], [k, 2, r[0]], [k, 10, ''], [k, 11, ''], [k, 12, '']]
        else: cells += [[k, 0, r[0]], [k, 1, r[1]], [k, 2, r[2]], [k, 10, r[3]], [k, 11, ''], [k, 12, r[4] if len(r) > 4 else '']]
    add(t='tset', h=tag, cells=cells)

def notes(fx, fy, top, lines, sc=100, W=42000):
    txt = '\pxi-3.3333,l3.3333,ql,t3.3333;' + '\P'.join('%d.	%s' % (i + 1, l) for i, l in enumerate(lines))
    # Bekassyl 31.10: notes sit right above the stamp (bottom-left anchored at stamp top + 250)
    f = sc / 100.0
    add(t='mtext', at=[fx + (W - 19000) * f, fy + (500 + 5712 + 250) * f], h=250 * f, w=18500 * f, att=7, style='Isocpeur', layer='О_Формат', s=txt)

def plan_axes(s, pre, ext=(XO, YO, XE, YE), row=1):
    x0, y0, x1, y1 = ext; R0 = 10 * s.sc * (row - 1)
    for k, x in AX.items(): s.axis(pre + 'ax' + k, k, (x, y1 + 400), (x, y0 - R0 - 2500))   # free end 4 mm: clear of a chain at 10 mm
    for k, y in AY.items(): s.axis(pre + 'ay' + k, k, (x1 + 400, y), (x0 - R0 - 2500, y))
    xs = [x0] + list(AX.values()) + [x1]; ys = [y0] + list(AY.values()) + [y1]
    # outer dimension = between the extreme axes, not the whole element (Bekassyl 31.10)
    R = 10 * s.sc                                         # №28/30: first row 10 mm from the contour, next +10 mm
    s.chain(xs, y0, y0 - R0 - R, end_in=True); s.dim(AX['1'], AX['3'], (y0, y0 - R0 - 2 * R))   # corner 625: text over its own segment
    s.chain(ys, x0, x0 - R0 - R, vert=True, end_in=True); s.dim(AY['А'], AY['Д'], (x0, x0 - R0 - 2 * R), vert=True)

