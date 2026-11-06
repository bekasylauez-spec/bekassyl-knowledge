# Column sheet generator: clones analog sheet x4.1 (Обезвоживание Км-1, A2 1:50) and rebuilds it for a column type.
# Facade 1:50 real size, sections/mesh x2 (1:25). Main bars Ø28, hoops Ø10 (analog), meshes С1 Ø10, П-elements Ø16.
import json, math, sys
import mb, colgeo
_sh = colgeo.storey_hoops
def _short(lo, bb):
    a, b = lo + 50.0, bb - 50.0; S_ = b - a
    if S_ >= 1800: return _sh(lo, bb)
    n = int(S_ // 100); r = S_ - 100 * n
    steps = [100.0] * n
    if r > 1e-6: steps.insert(n // 2, r)
    pos = [a]
    for st in steps: pos.append(pos[-1] + st)
    return pos, (n, 0, 0), steps
colgeo.storey_hoops = _short

O0 = (-691502.7, -1749172.2)            # analog sheet x4.1 origin
SL0 = -1552803.1                        # first slot (right of scheme 4.1)
SW = 29700
EXT = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\d50da53a-3ac3-4689-a264-f515b6d8bdb3\scratchpad\s\w\ext4.txt'
KG = {28: 4.834, 16: 1.578, 10: 0.617}

def ext_rows():
    out = []
    for line in open(EXT, encoding='utf-8-sig'):
        p = line.rstrip('\n').split('|')
        if len(p) < 8 or p[3] == '': continue
        bb = [float(v) for v in p[3:7]]
        out.append(dict(h=p[0], t=p[1], lay=p[2], x0=bb[0] - O0[0], y0=bb[1] - O0[1], x1=bb[2] - O0[0], y1=bb[3] - O0[1], info='|'.join(p[7:-1])))
    return out
RR = ext_rows()
SHEET = [r['h'] for r in RR if r['x0'] >= -5 and r['x1'] <= SW + 5 and r['y0'] >= -5 and r['y1'] <= 21005]
def inwin(x0, y0, x1, y1, lay=None, t=None):
    return [r['h'] for r in RR if r['x0'] >= x0 and r['x1'] <= x1 and r['y0'] >= y0 and r['y1'] <= y1
            and (lay is None or r['lay'] == lay) and (t is None or r['t'] == t)]

def build(T, k, sheetno):
    O = (SL0 + k * SW, O0[1])
    pre = 'C%d:' % k
    def A(x, y): return [O[0] + x, O[1] + y]
    def A0(x, y): return [O0[0] + x, O0[1] + y]          # analog absolute (prototype positions)
    def S(h): return pre + h
    ops = []
    def add(**q): ops.append(q); return q
    n = [0]
    def tg(): n[0] += 1; return '%sg%d' % (pre, n[0])
    def plc(proto, pts, closed=None):                   # clone a polyline prototype and set its vertices
        t = tg(); add(t='clone', h=proto, tag=t); o = add(t='plset', h=t, p=pts)
        if closed is not None: o['closed'] = closed
        return t
    def dim(proto, p1, p2, dl, rot, txt=None, tx=None, lfac=None):
        o = add(t='dim', h=proto, p1=p1, p2=p2, dl=dl, rot=rot, tag=tg())
        if txt is not None: o['txt'] = txt
        if tx is not None: o['tx'] = tx
        if lfac is not None: o['lfac'] = lfac
    HP = math.pi / 2
    b, h, nb, nh = T['b'], T['h'], T['nb'], T['nh']
    levels, beams = T['levels'], T['beams']               # rel col bottom; beam heights at each upper level
    Df = T['df']; Htop = levels[-1]
    YB = 6950.0                                           # column bottom on the sheet
    XL = 4150.0                                           # column left face (facade shows face h)
    # ---------- clone the analog sheet ----------
    add(t='clonexf', hs=SHEET, d=[O[0] - O0[0], 0], pre=pre)
    # erase parts that are rebuilt
    er = []
    er += inwin(4100, 6900, 5100, 13700, lay='диам10')                       # facade hoops + meshes
    er += [r['h'] for r in RR if '4E94D0' <= r['h'] <= '4E94E3']             # facade bars, выпуски, накладки
    er += ['4E954E', '4E9560', '4E956D', '4E957A', '4E9587', '4E9599', '4E9541', '4E951A', '4E9527', '4E9534']
    er += inwin(8550, 16250, 10050, 18150, t='CIRCLE') + inwin(8550, 16250, 10050, 18150, t='HATCH')
    er += ['4E95D3', '4E95D4', '4E95D5', '4E95D6']                           # inner hoops (X1 is re-set)
    er += inwin(7500, 15300, 10600, 16320, t='DIMENSION') + inwin(7500, 15800, 8620, 18700, t='DIMENSION')
    er += inwin(13150, 16250, 14650, 18150, t='CIRCLE') + inwin(13150, 16250, 14650, 18150, t='HATCH') + inwin(13150, 16250, 14650, 18150, lay='диам16')
    er += inwin(14150, 11450, 15550, 13250, lay='диам10') + ['4E9770', '4E977D', '4E978F', '4E979C', '4E97AE', '4E97BB', '4E97CD', '4E97DA']
    er += inwin(9700, 8450, 10700, 9850, lay='диам28') + inwin(9700, 9000, 10700, 9800, lay='диам10') + ['4E96F6', '4E9708', '4E9715']
    add(t='erase', h=[S(x) for x in sorted(set(er))])
    # ---------- facade: stretch heights / width ----------
    yb_top = YB + Htop - beams[-1]
    PARK = ['4E95A6', '4E95A8', '4E95AA', '4E95AC', '4E95AD', '4E95AE', '4E95AF', '4E95B0', '4E95B1', '4E95B2', '4E95B3', '4E8F9B', '4E8F97']
    add(t='move', h=[S(x) for x in PARK], d=[300000, 0])
    add(t='pmap', win=A(0, 4500) + A(7400, 16200), axis='y',
        pairs=[[O[1] + 5950, O[1] + YB - Df], [O[1] + 6950, O[1] + YB], [O[1] + 12850, O[1] + yb_top], [O[1] + 13650, O[1] + YB + Htop]])
    add(t='pmap', win=A(3000, 4500) + A(7400, 16200), axis='x', pairs=[[O[0] + 4150, O[0] + XL], [O[0] + 5050, O[0] + XL + h]])
    XR = XL + h
    Hc = Htop - beams[-1]
    topd = (YB + Htop) - 13650
    f = min(1.0, (Hc - 200) / 2800.0)
    H1 = (levels[0] - beams[0]) if len(levels) > 1 else Hc
    NB0, NST = (950, 550) if H1 >= 4000 else (450, 400)
    drop1 = (len(levels) == 1 and Hc < 4000)
    drop2 = (len(levels) == 1 and Hc < 3000)
    i0 = 0
    _P, _segs = colgeo.chain([0.0] + list(levels), list(beams))
    y11 = [y2 for (y1, y2, st, c) in _segs if st == 100 and c > 1][0]
    DY = {'4E95AC': topd, '4E95AA': (YB + Htop - beams[-1]) - 12850, '4E95A8': 0, '4E95A6': (YB - Df) - 5950,
          '4E95AD': (YB + NB0 + 2 * NST) - 9000, '4E95AE': (YB + NB0 + (1 if drop2 else (2 if drop1 else 3)) * NST) - 9550, '4E95B0': (YB + NB0 + NST) - 8450, '4E95B1': (YB + NB0) - 7900,
          '4E95AF': topd, '4E95B2': 0, '4E95B3': 0, '4E8F9B': topd, '4E8F97': (YB + Htop - beams[-1] / 2) - 13250, '4E8F98': topd,
          '4E8FA1': (YB + y11) - 11054}
    for hh in PARK:
        add(t='move', h=[S(hh)], d=[-300000, DY[hh]])
    ysec = YB + (11054 - 6950) * (Hc / 5900.0)
    add(t='sp_set', h=S('4E8F9B'), pts=[[0] + A(XR + 1300, YB + Htop + 600)])
    bnd = sorted({v for sg in _segs for v in sg[:2]})
    nnote = 4 - (1 if drop1 else 0) - (1 if drop2 else 0)
    lo_ = NB0 + (nnote - 1) * NST + 300
    if len(levels) > 1 and (Hc - levels[-2]) >= 1500:
        lo_ = levels[-2] + 200; hi_ = Hc - 300 - 250 - 400
    else:
        hi_ = (levels[0] - beams[0]) - 300 - 250 - 400
    ys1r = None
    for y in range(int(lo_), int(hi_) + 1, 20):
        if not any(-90 < v - y < 400 for v in bnd): ys1r = y; break
    if ys1r is None: ys1r = lo_
    ys1 = YB + ys1r
    kc = YB + Htop - beams[-1] / 2.0
    add(t='sp_set', h=S('4E8F97'), pts=[[1] + A(XL - 700, YB + Htop + 250)])
    add(t='sp_set', h=S('4E8FA1'), pts=[[0] + A(XL - 350, ys1), [1] + A(XR + 350, ys1)])
    # bars, выпуски, накладки
    xs = [XL + 56 + i * (h - 112) / (nh - 1) for i in range(nh)]
    for i, x in enumerate(xs):
        z0 = 600 if i in (0, nh - 1) else 1200
        plc('4E94D0', [A(x, YB + z0), A(x, YB + Htop - 20)])
        plc('4E94D3', [A(x, YB - Df + 60), A(x, YB + z0)])
        plc('4E94D1', [A(x - 14, YB + z0 - 140), A(x - 42, YB + z0 - 140), A(x - 42, YB + z0 + 140), A(x - 14, YB + z0 + 140)], True)
        plc('4E94D2', [A(x + 14, YB + z0 - 140), A(x + 42, YB + z0 - 140), A(x + 42, YB + z0 + 140), A(x + 14, YB + z0 + 140)], True)
    # hoops + node meshes
    P, segs = colgeo.chain([0.0] + list(levels), list(beams))
    for z in P:
        plc('4E94E4', [A(XL + 37, YB + z), A(XR - 37, YB + z)])
    nmesh = []
    for L, hb in zip(levels, beams):
        zz = [L - hb + 50 + 100 * j for j in range(int(round((hb - 100) / 100)) + 1)]
        nmesh.append(len(zz))
        for z in zz:
            plc('4E9511', [A(XL + 20, YB + z), A(XR - 20, YB + z)])
    # mid nodes: beam stubs, level marks, С1 note
    for L, hb in zip(levels[:-1], beams[:-1]):
        dy0 = (YB + L - hb) - 12850; dy1 = (YB + L) - 13650
        for hh, dy in (('4E94C8', dy0), ('4E94CC', dy0), ('4E94C9', dy1), ('4E94CD', dy1)):
            t = tg(); add(t='clone', h=hh, base=A0(0, 0), to=[O[0], O0[1] + dy], tag=t)
            if hh in ('4E94CC', '4E94CD'): add(t='move', h=[t], d=[h - 900, 0])
        for hh in ('4E94CA', '4E94CE'):
            t = tg(); add(t='clone', h=hh, base=A0(0, 0), to=[O[0], O0[1] + (dy0 + dy1) / 2], tag=t)
            if hh == '4E94CE': add(t='move', h=[t], d=[h - 900, 0])
    # chain dims right
    DLR = XR + 1000
    for (y1, y2, st, cnt) in segs:
        if cnt > 1:
            dim('4E9560', A(XR, YB + y1), A(XR, YB + y2), A(DLR, YB + y1), HP, txt='%dх%d' % (st, cnt), lfac=1)
        elif abs(y2 - y1 - 50) < 1 or (y2 - y1) < 400:
            dim('4E954E', A(XR, YB + y1), A(XR, YB + y2), A(DLR, YB + y1), HP, tx=A(DLR + 260 + (0 if abs(y2 - y1 - 50) < 1 else 60), YB + (y1 + y2) / 2))
        else:
            dim('4E9599', A(XR, YB + y1), A(XR, YB + y2), A(DLR, YB + y1), HP, txt='', lfac=1)
    # left dims: Фм/ригель below | storeys | beams ; total
    pts = [-Df, 0.0]
    for L, hb in zip(levels, beams): pts += [L - hb, L]
    for a, c in zip(pts, pts[1:]):
        dim('4E9527', A(XL, YB + a), A(XL, YB + c), A(3050, YB + a), HP, txt='', lfac=1)
    dim('4E9541', A(XL, YB - Df), A(XL, YB + Htop), A(2650, YB - Df), HP, txt='', lfac=1)
    # level marks: texts (values are stored as text in the SPDS mark)
    def lv(v):
        if abs(v) < 0.5: return '±0,000'
        return ('+' if v > 0 else '-') + '%d,%03d' % (abs(v) // 1000, abs(v) % 1000)
    base = T['base']
    ana = {'4E95AC': '+6,200', '4E95AA': '+5,400', '4E95A8': '-0,500', '4E95A6': '-1,500'}
    for L, hb in zip(levels[:-1], beams[:-1]):
        for hh, z in (('4E95AC', L), ('4E95AA', L - hb)):
            t = tg(); add(t='clone', h=S(hh), tag=t)
            add(t='move', h=[t], d=[0, (YB + z) - (YB + (Htop if hh == '4E95AC' else Htop - beams[-1]))])
            add(t='levelval', h=t, old=ana[hh], value=lv(base + z), tag=t + 'v')
    for hh, v in (('4E95AC', base + Htop), ('4E95AA', base + Htop - beams[-1]), ('4E95A8', base), ('4E95A6', base - Df)):
        add(t='levelval', h=S(hh), old=ana[hh], value=lv(v), tag=S(hh) + 'v')
    # facade notes
    add(t='notetxt', h=S('4E95AF'), l2='%d шт.' % nmesh[-1])
    if True:
        add(t='sp_set', h=S('4E95AF'), pts=[[0] + A(3920, YB + Htop - beams[-1] - 300), [1] + A(XL + 30, YB + Htop - beams[-1] + 150)])
    for i, (L, hb) in enumerate(zip(levels[:-1], beams[:-1])):
        t = tg(); add(t='clone', h=S('4E95AF'), tag=t)
        add(t='sp_set', h=t, pts=[[0] + A(3920, YB + L - hb - 300), [1] + A(XL + 30, YB + L - hb + 150)])
        add(t='notetxt', h=t, l2='%d шт.' % nmesh[i])
    vp = T.get('vp', 'см. фундамент')
    add(t='notetxt', h=S('4E95B2'), l2=vp); add(t='notetxt', h=S('4E95B3'), l2=vp)
    ys_ = [r for r in ('4E95AD', '4E95AE')]
    add(t='sp_set', h=S('4E95AE'), pts=[[1] + A(xs[1], YB + NB0 + (1 if drop2 else (2 if drop1 else 3)) * NST - 300)])
    if drop1: add(t='erase', h=[S('4E95AD')])
    if drop2: add(t='erase', h=[S('4E95B0')])
    add(t='sp_set', h=S('4E95AD'), pts=[[1] + A(xs[0], YB + NB0 + 2 * NST - 300)])
    add(t='sp_set', h=S('4E95B1'), pts=[[1] + A(xs[0] - 42, YB + 600)])
    zx = min(P, key=lambda z: abs(z - (NB0 + NST - 150)))
    add(t='sp_set', h=S('4E95B0'), pts=[[1] + A(XL + 37, YB + zx)])
    # ---------- section 1-1 (x2) ----------
    SX, SY = 8600.0, 16300.0
    def cov(L, n):
        for c in (56, 55, 57, 54, 58):
            if (L - 2 * c) % (n - 1) == 0: return c
        return 56
    def sp(i, n, L):
        c = cov(L, n); return 2 * (c + i * (L - 2 * c) / (n - 1))
    bx = [SX + sp(i, nb, b) for i in range(nb)]; by = [SY + sp(j, nh, h) for j in range(nh)]
    bars = [(x, y) for x in bx for y in by if x in (bx[0], bx[-1]) or y in (by[0], by[-1])]
    add(t='plset', h=S('4E95B4'), p=[A(SX, SY), A(SX + 2 * b, SY), A(SX + 2 * b, SY + 2 * h), A(SX, SY + 2 * h)], closed=True)
    for (x, y) in bars:
        for proto, c in (('4E95B5', A0(8712, 16412)), ('4E95B6', A0(8712, 16412))):
            add(t='clone', h=proto, base=c, to=A(x, y), tag=tg())
    add(t='plset', h=S('4E95D1'), p=[A(bx[0] - 38, by[0] - 38), A(bx[-1] + 38, by[0] - 38), A(bx[-1] + 38, by[-1] + 38), A(bx[0] - 38, by[-1] + 38)], closed=True)
    add(t='move', h=[S('4E95D2')], d=[(bx[0] - 38) - 8674, (by[-1] + 38) - 18026])
    def groups(m):
        if m == 2: return [(1, 2)]
        if m == 3: return [(1, 3)]
        if m == 4: return [(1, 2), (3, 4)]
        if m == 5: return [(1, 3), (3, 5)]
        return [(1, m)]
    gb, gh = groups(nb - 2), groups(nh - 2)
    x2w = []; x3h = []
    for (i, j) in gb:   # X2: around interior columns, full height
        x0, x1 = bx[i] - 38, bx[j] + 38; y0, y1 = by[0] - 14, by[-1] + 14
        plc('4E95D3', [A(x0, y0), A(x1, y0), A(x1, y1), A(x0, y1)], True)
        t = tg(); add(t='clone', h='4E95D4', base=A0(9066, 18002), to=A(x0, y1), tag=t)
        x2w.append(round((x1 - x0) / 2))
    for (i, j) in gh:   # X3: around interior rows, full width
        x0, x1 = bx[0] - 14, bx[-1] + 14; y0, y1 = by[i] - 38, by[j] + 38
        plc('4E95D5', [A(x0, y0), A(x1, y0), A(x1, y1), A(x0, y1)], True)
        t = tg(); add(t='clone', h='4E95D6', base=A0(8698, 17632), to=A(x0, y1), tag=t)
        x3h.append(round((y1 - y0) / 2))
    # section dims (СПДС М2, lfac 0.5)
    yd1, yd2 = SY - 522, SY - 922
    dim('4E95D7', A(SX, SY), A(bx[0], SY), A(SX, yd1), 0, tx=A(SX - 260, yd1 - 340))
    sb_ = round((bx[1] - bx[0]) / 2); tb_ = '%dх%d=%d' % (sb_, nb - 1, sb_ * (nb - 1))
    small = (bx[-1] - bx[0]) < len(tb_) * 0.8 * 125 + 150
    if small: tb_ = '%dх%d' % (sb_, nb - 1)
    dim('4E95E6', A(bx[0], SY), A(bx[-1], SY), A(bx[0], yd1), 0, txt=tb_, tx=None)
    dim('4E960D', A(bx[-1], SY), A(SX + 2 * b, SY), A(SX, yd1), 0, tx=A(SX + 2 * b + 260, yd1 - 340))
    dim('4E961C', A(SX, SY), A(SX + 2 * b, SY), A(SX, yd2), 0)
    xd1, xd2 = SX - 617, SX - 1017
    dim('4E9629', A(SX, SY), A(SX, by[0]), A(xd1, SY), HP, tx=A(xd1 - 340, SY - 260))
    sh_ = round((by[1] - by[0]) / 2); th_ = ('%dх%d' % (sh_, nh - 1)) if small else '%dх%d=%d' % (sh_, nh - 1, sh_ * (nh - 1))
    dim('4E9638', A(SX, by[0]), A(SX, by[-1]), A(xd1, by[0]), HP, txt=th_, tx=None)
    dim('4E966C', A(SX, by[-1]), A(SX, SY + 2 * h), A(xd1, SY), HP, tx=A(xd1 - 340, SY + 2 * h + 260))
    dim('4E967B', A(SX, SY), A(SX, SY + 2 * h), A(xd2, SY), HP)
    # section notes: move with the right edge, targets
    dxs = 2 * (b - 700); dys = 2 * (h - 900)
    NX = SX + 2 * b + 600
    tgt = {'4E9688': (bx[-1], by[-1]), '4E9689': (bx[-1], by[-2]), '4E968A': (bx[-1] + 14, by[gh[0][0]] + 20),
           '4E968B': (bx[-1] + 38, (by[0] + by[1]) / 2), '4E968C': (bx[gb[0][1]] + 38, by[0] + 120)}
    st5 = min(520, (2 * h + 1000) / 4.0); top5 = SY + 2 * h + (0 if h >= 900 else 400)
    yrow = {'4E9688': top5 - 60, '4E9689': top5 - 60 - st5, '4E968A': top5 - 60 - 2 * st5, '4E968B': top5 - 60 - 3 * st5, '4E968C': top5 - 60 - 4 * st5}
    for hh, (tx_, ty_) in tgt.items():
        add(t='sp_set', h=S(hh), pts=[[0] + A(NX, yrow[hh]), [1] + A(tx_, ty_)])
    add(t='move', h=[S('4E968D'), S('4E96B5')], d=[0, dys])
    # ---------- section 2-2 (П-elements) ----------
    QX = 13200.0 + max(0, dxs)
    qbx = [QX + (x - SX) for x in bx]
    add(t='plset', h=S('4E968F'), p=[A(QX, SY), A(QX + 2 * b, SY), A(QX + 2 * b, SY + 2 * h), A(QX, SY + 2 * h)], closed=True)
    for (x, y) in bars:
        for proto in ('4E9691', '4E9690'):
            pass
    for (x, y) in bars:
        add(t='clone', h='4E95B5', base=A0(8712, 16412), to=A(QX + (x - SX), y), tag=tg())
        add(t='clone', h='4E95B6', base=A0(8712, 16412), to=A(QX + (x - SX), y), tag=tg())
    for x in qbx: plc('4E96AC', [A(x, by[0]), A(x, by[-1])])
    for y in by[1:-1]: plc('4E96B0', [A(qbx[0], y), A(qbx[-1], y)])
    add(t='sp_set', h=S('4E96B3'), pts=[[0] + A(QX + 2 * b + 500, SY + 2 * h - 400), [1] + A(qbx[-2], SY + 2 * h - 900)])
    add(t='sp_set', h=S('4E96B4'), pts=[[0] + A(QX + 2 * b + 500, SY + 300), [1] + A(qbx[-1] - 160, by[1])])
    add(t='move', h=[S('4E96B5')], d=[max(0, dxs), 0])
    # ---------- Сетка С1 sketch (x2): x-dir b-40, y-dir h-40 ----------
    MX, MY = 14200.0, 11500.0
    mb_, mh_ = b - 40, h - 40
    def mlines(L):
        c = int((L - 60) // 100) + 1; e = (L - 100 * (c - 1)) / 2
        return c, e
    cy, ey = mlines(mh_); cx, ex = mlines(mb_)
    for j in range(cy): plc('4E9760', [A(MX, MY + 2 * (ey + 100 * j)), A(MX + 2 * mb_, MY + 2 * (ey + 100 * j))])
    for i in range(cx): plc('4E9769', [A(MX + 2 * (ex + 100 * i), MY), A(MX + 2 * (ex + 100 * i), MY + 2 * mh_)])
    dim('4E9770', A(MX, MY), A(MX + 2 * mb_, MY), A(MX, MY - 582), 0)
    dim('4E978F', A(MX + 2 * ex, MY), A(MX + 2 * (mb_ - ex), MY), A(MX, MY - 302), 0, txt='100х%d' % (cx - 1))
    dim('4E977D', A(MX, MY), A(MX + 2 * ex, MY), A(MX, MY - 302), 0, tx=A(MX - 260, MY - 302 - 100))
    dim('4E979C', A(MX + 2 * (mb_ - ex), MY), A(MX + 2 * mb_, MY), A(MX, MY - 302), 0, tx=A(MX + 2 * mb_ + 700, MY - 302 - 100))
    RX = MX + 2 * mb_
    dim('4E97AE', A(RX, MY), A(RX, MY + 2 * mh_), A(RX + 582, MY), HP)
    dim('4E97CD', A(RX, MY + 2 * ey), A(RX, MY + 2 * (mh_ - ey)), A(RX + 302, MY), HP, txt='100х%d' % (cy - 1))
    dim('4E97BB', A(RX, MY), A(RX, MY + 2 * ey), A(RX + 302, MY), HP, tx=A(RX + 302 + 100, MY - 420))
    dim('4E97DA', A(RX, MY + 2 * (mh_ - ey)), A(RX, MY + 2 * mh_), A(RX + 302, MY), HP, tx=A(RX + 302 + 100, MY + 2 * mh_ + 260))
    add(t='sp_set', h=S('4E97EC'), pts=[[0] + A(MX - 580, MY + 2 * mh_ - 150), [1] + A(MX + 2 * (ex + 100 * (cx // 2)), MY + 2 * mh_ - 400)])
    add(t='sp_set', h=S('4E97ED'), pts=[[1] + A(MX + 2 * mb_ - 300, MY + 2 * (ey + 100 * (cy // 2)))])
    add(t='move', h=[S('4E97EE')], d=[0, (MY + 2 * mh_ + 285) - 13505])
    # ---------- Узел Б: top node, beam hb, face h ----------
    hb = beams[-1]
    add(t='pmap', win=A(8400, 8000) + A(12500, 11000), axis='y', pairs=[[O[1] + 9000, O[1] + 9000], [O[1] + 9800, O[1] + 9000 + hb]])
    add(t='pmap', win=A(8400, 8000) + A(12500, 11000), axis='x', pairs=[[O[0] + 9750, O[0] + 9750], [O[0] + 9770, O[0] + 9770], [O[0] + 10630, O[0] + 9750 + h - 20], [O[0] + 10650, O[0] + 9750 + h]])
    for x in xs: plc('4E96E9', [A(9750 + (x - XL), 8500), A(9750 + (x - XL), 9000 + hb - 20)])
    zz = [50 + 100 * j for j in range(int(round((hb - 100) / 100)) + 1)]
    for z in zz: plc('4E96EE', [A(9770, 9000 + z), A(9750 + h - 20, 9000 + z)])
    UR = 9750 + h
    dim('4E96F6', A(UR, 9000), A(UR, 9050), A(UR + 700, 9000), HP, tx=A(UR + 700 + 390, 9025))
    dim('4E9708', A(UR, 9050), A(UR, 9000 + hb - 50), A(UR + 700, 9000), HP, txt='100х%d' % (len(zz) - 1))
    dim('4E9715', A(UR, 9000 + hb - 50), A(UR, 9000 + hb), A(UR + 700, 9000), HP, tx=A(UR + 700 + 390, 9000 + hb - 25))
    add(t='notetxt', h=S('4E975F'), l2='%d шт.' % len(zz))
    # ---------- texts ----------
    mk = T['mark']
    add(t='settext', h=S('4E8834'), s='{\\LКолонна %s (%d шт.)}' % (mk, T['n']))
    add(t='settext', h=S('4E89A2'), s='Колонна %s' % mk)
    add(t='settext', h=S('4E8FA3'), s=sheetno)
    add(t='settext', h=S('4E89CE'), s=T['notes'])
    # ведомость деталей
    X1a, X1b = b - 74, h - 74
    LX1 = 2 * (X1a + X1b) + 200
    LX2 = 2 * (x2w[0] + X1b) + 200 if x2w else 0
    LX3 = 2 * (X1a + x3h[0]) + 200 if x3h else 0
    LS1, LS2 = (h - 68) + 560, (b - 68) + 560
    for hh, s in (('4E96C1', X1a), ('4E96C2', X1b), ('4E96C9', x2w[0]), ('4E96CA', X1b), ('4E96D1', X1a), ('4E96D2', x3h[0]),
                  ('4E96D8', h - 68), ('4E96DE', b - 68)):
        add(t='settext', h=S(hh), s=str(s))
    for hh, L in (('4E96BE', LX1), ('4E96C6', LX2), ('4E96CE', LX3)):
        add(t='settext', h=S(hh), s='%%%%C10 A500С  L=%d' % L)
    add(t='settext', h=S('4E96D6'), s='%%%%C16 A500С  L=%d' % LS1)
    add(t='settext', h=S('4E96DC'), s='%%%%C16 A500С  L=%d' % LS2)
    # ---------- specification + steel ----------
    NH = len(P)
    L1, L2 = Htop - 20 - 600, Htop - 20 - 1200
    nmesh_t = sum(nmesh)
    m10L, m11L = mb_, mh_
    c10, c11 = cy, cx                       # pos10 L=b-40 count = lines along h ; pos11 L=h-40 count = lines along b
    rows = [(1, 28, L1, 4), (2, 28, L2, 2 * (nb - 2) + 2 * (nh - 2)), (3, 10, LX1, NH), (4, 10, LX2, NH * len(gb)),
            (5, 10, LX3, NH * len(gh)), (6, 16, LS1, nb), (7, 16, LS2, nh - 2), (8, 28, 280, 2 * (2 * nb + 2 * (nh - 2)))]
    cells = []; tot = {10: 0.0, 16: 0.0, 28: 0.0}
    for r, d, L, c in rows:
        m1 = KG[d] * L / 1000.0
        cells += [[r, 3, str(d)], [r, 9, str(int(L))], [r, 10, str(int(c))], [r, 11, '%.2f' % m1], [r, 12, '%.2f' % (m1 * c)]]
        tot[d] += m1 * c
    mesh1 = KG[10] * (m10L * c10 + m11L * c11) / 1000.0
    cells += [[9, 10, str(nmesh_t)], [9, 11, '%.2f' % mesh1], [9, 12, '%.2f' % (mesh1 * nmesh_t)]]
    tot[10] += mesh1 * nmesh_t
    cells += [[13, 9, str(int(m10L))], [13, 10, str(c10)], [13, 11, '%.2f' % (KG[10] * m10L / 1000)], [13, 12, '%.2f' % (KG[10] * m10L / 1000 * c10)],
              [14, 9, str(int(m11L))], [14, 10, str(c11)], [14, 11, '%.2f' % (KG[10] * m11L / 1000)], [14, 12, '%.2f' % (KG[10] * m11L / 1000 * c11)]]
    vol = b * h * Htop / 1e9
    allm = sum(tot.values())
    cells += [[0, 2, 'Колонна %s' % mk], [0, 12, '%.2f' % allm], [11, 12, '%.2f' % vol]]
    add(t='tset', h=S('4E8C66'), cells=cells)
    st = [[6, 0, 'Колонна %s' % mk], [6, 1, '0.00'], [6, 2, '0.00'], [6, 3, '0.00'], [6, 4, '%.2f' % tot[10]], [6, 5, '%.2f' % tot[16]],
          [6, 6, '%.2f' % tot[28]], [6, 7, '%.2f' % allm], [6, 8, '%.2f' % allm]]
    add(t='tset', h=S('4E8E29'), cells=st)
    info = dict(mark=mk, sheet=sheetno, mass=round(allm, 2), vol=round(vol, 2), As=round(T['ns'] * 6.158, 2), hoops=NH, mesh=nmesh_t,
                origin=O, nbars=T['ns'])
    return ops, info

if __name__ == '__main__':
    TY = json.load(open(mb.S + r'\coltypes.json', encoding='utf-8'))
    sel = sys.argv[1:]
    res = {}
    for k, T in enumerate(TY):
        if sel and T['mark'] not in sel: continue
        ops, info = build(T, k, '4.%d' % (k + 2))
        ops.append({'t': 'save'})
        print(mb.run(ops, 'col_%d' % k, 2400)[-1500:])
        res[T['mark']] = info
        print(info)
    json.dump(res, open(mb.S + r'\w\colinfo_%s.json' % ('_'.join(sel) or 'all'), 'w', encoding='utf-8'), ensure_ascii=False)
