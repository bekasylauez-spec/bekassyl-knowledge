# rigel cross-sections: analog section 1-1 (1:20) imported to a staging place, edited in real mm, cloned x2 (1:25) onto the sheet
from rgen import *
import math

XLA, YBA = -211276.0, 428183.0          # analog section: beam left face / bottom
SC = 2.0                                 # 1:50 sheet, section drawn 1:25


def side_rows(B):
    # side (боковые) bars Ø28 for h >= 700: rows at <= 400 mm
    if B['h'] < 700: return []
    n = max(1, int(math.ceil((B['h'] - 110) / 400.0)) - 1)
    return list(range(n))


def bar_x(b, n_main, n_dop):
    """bar centres from the left face: 7 slots 55 + 65k when dop present, main at even slots"""
    if n_dop == 0:
        st = (b - 110) / 3.0
        return [55 + st * i for i in range(4)], [], '%dх3=%d' % (round(st), round(3 * st))
    st = (b - 110) / 6.0
    slots = [55 + st * i for i in range(7)]
    main = [slots[i] for i in (0, 2, 4, 6)]
    dsl = {1: [3], 2: [1, 5], 3: [1, 3, 5]}[n_dop]
    return main, [slots[i] for i in dsl], '%dх6=%d' % (round(st), round(6 * st))


def build_stage(B, sec, OX, OY, P, withML=True):
    """sec = dict(word, top_dop=(pos, n), bot_dop=(pos, n)); returns ops, handle tags to clone, base point"""
    ops = []; add = lambda **k: ops.append(k)
    S = lambda h: P + h
    hs = sec_handles()
    add(t='import', file=gx.S + r'\an\a61.dwg', h=hs, base=[XLA, YBA], to=[OX, OY], pre=P)
    b, h = B['b'], B['h']
    xL, xR, yb, yt = OX, OX + b, OY, OY + h
    YBOT, YTOP = yb + 55, yt - 55
    slab = B.get('slab', 0)
    if slab:
        ys = yt - slab; xa, xb = xL - 173, xR + 173
        add(t='plset', h=S(SEC['outl']), p=[[xR, yb], [xR, ys], [xb, ys], [xb, yt], [xa, yt], [xa, ys], [xL, ys], [xL, yb]], closed=True)
        for hh, x in ((SEC['brk'][0], xa), (SEC['brk'][1], xb)):
            add(t='mcset', h=S(hh), set={'StartPoint': [x, ys], 'EndPoint': [x, yt], 'ClipZonePoint': [x, yt], 'Length': slab})
    else:
        add(t='plset', h=S(SEC['outl']), p=[[xR, yb], [xR, yt], [xL, yt], [xL, yb]], closed=True)
        add(t='erase', h=[S(x) for x in SEC['brk']])
    nm = B['main']['top'][0]
    def lay(lst):
        r1 = [x for x in lst if x[3] == 1]; r2 = [x for x in lst if x[3] == 2]
        return r1, r2
    t1, t2 = lay([tuple(x) for x in sec.get('top', [])]); b1, b2 = lay([tuple(x) for x in sec.get('bot', [])])
    def xs(n1):
        if nm == 3:
            st = (b - 110) / 2.0
            return [55 + st * i for i in range(3)], [], '%dх2=%d' % (round(st), round(2 * st))
        return bar_x(b, 4, n1)
    mT, dT, chT = xs(sum(x[1] for x in t1)); mB, dB, chB = xs(sum(x[1] for x in b1))
    def row2x(n):
        if n >= nm: return list(mB)
        if n == 1: return [mB[len(mB) // 2]]
        if n == 2: return [mB[0], mB[-1]]
        return [mB[0], mB[1], mB[-1]]
    dia = B['main']['top'][1]
    extra = []
    nb_ = [0]
    def bar(xx, y, dd_):
        # bar dot: circle + solid hatch (the analog bar block renders empty in this drawing)
        r = dd_ / 2.0; tg = '%sB%d' % (P, nb_[0]); th = '%sH%d' % (P, nb_[0]); nb_[0] += 1
        add(t='circle', c=[xL + xx, y], r=r, layer='диам%d' % dd_, tag=tg)
        poly = [[xL + xx + r * math.cos(a_ * math.pi / 12), y + r * math.sin(a_ * math.pi / 12)] for a_ in range(24)]
        add(t='hatch', pat='SOLID', loops=[poly], layer='диам%d' % dd_, tag=th)
        extra.extend([tg, th])
    for x in mB: bar(x, YBOT, B['main']['bot'][1])
    for x in mT: bar(x, YTOP, dia)
    add(t='erase', h=[S(h_) for h_ in SEC['bot'] + SEC['top']])
    groups = []
    k_ = [0]
    def put(xx, y, dd_): bar(xx, y, dd_)
    for grp, y, top in ((t1, YTOP, True), (b1, YBOT, False)):
        xx = dT if top else dB; i = 0
        for (pos, n, dd_, row) in grp:
            sel = xx[i:i + n]; i += n
            for x in sel: put(x, y, dd_)
            groups.append((top, 1, pos, dd_, sel, y))
    for grp, y, top in ((t2, YTOP - 98, True), (b2, YBOT + 98, False)):
        for (pos, n, dd_, row) in grp:
            sel = row2x(n)
            for x in sel: put(x, y, dd_)
            groups.append((top, 2, pos, dd_, sel, y))
    # hoops: two (each over 3 bars) for 4 main bars, one for 3
    if nm == 4:
        for hh, x in zip(SEC['hoop'], mB[:2]):
            add(t='insat', h=S(hh), at=[xL + x, YBOT + 11])
            add(t='dyn', h=S(hh), prop='Расстояние1', value=mB[2] - mB[0])
            add(t='dyn', h=S(hh), prop='Расстояние2', value=YTOP - YBOT)
    else:
        add(t='insat', h=S(SEC['hoop'][0]), at=[xL + mB[0], YBOT + 11])
        add(t='dyn', h=S(SEC['hoop'][0]), prop='Расстояние1', value=mB[2] - mB[0])
        add(t='dyn', h=S(SEC['hoop'][0]), prop='Расстояние2', value=YTOP - YBOT)
        add(t='erase', h=[S(SEC['hoop'][1])])
    nt = len(t1) + len(t2); nb = len(b1) + len(b2)
    # bottom chain: 55 | step x n | 55 (dop slots define the step), total width
    allx = sorted(mB + dB)
    yd = yb - 306
    d = SEC['dimb']
    add(t='dimpts', h=S(d[0]), p1=[xL + allx[0], yb, 0], p2=[xL, yb, 0], dl=[xL, yd, 0])
    add(t='dimtx', h=S(d[0]), at=[xL - 75, yd + 40, 0])
    add(t='dimpts', h=S(d[1]), p1=[xL + allx[-1], yb, 0], p2=[xL + allx[0], yb, 0], dl=[xL + allx[0], yd, 0])
    add(t='dimtext', h=S(d[1]), s=chB)
    add(t='dimtx', h=S(d[1]), at=[xL + b / 2.0, (yd - 90) if b >= 500 else (yb - 648 - 150), 0], tmove=2)
    add(t='erase', h=[S(d[2]), S(d[3])])
    add(t='dimpts', h=S(d[4]), p1=[xR, yb, 0], p2=[xL + allx[-1], yb, 0], dl=[xL + allx[-1], yd, 0])
    add(t='dimtx', h=S(d[4]), at=[xR + 75, yd + 40, 0])
    add(t='dimpts', h=S(SEC['dimw']), p1=[xL, yb, 0], p2=[xR, yb, 0], dl=[xR, yb - 648, 0])
    xv = xL - 264
    for hh, (p, q) in zip(SEC['dimv'], [(yb, YBOT), (YBOT, YTOP), (YTOP, yt)]):
        add(t='dimpts', h=S(hh), p1=[xL + mB[0], p, 0], p2=[xL + mB[0], q, 0], dl=[xv, q, 0])
    add(t='dimpts', h=S(SEC['dimh']), p1=[xL, yt, 0], p2=[xL, yb, 0], dl=[xL - 453, yb, 0])
    # callouts: main top / bottom combs, dop combs (clones), hoop note
    ytop_sh = yt + 163
    add(t='combsegs', h=S(SEC['ctop']), segs=[[[xL + x, YTOP - 1], [xL + x + 88, ytop_sh]] for x in mT],
        start=[xL + mT[-1] + 88, ytop_sh], end=[xL + mT[0] + 88, ytop_sh])
    add(t='mcset', h=S(SEC['ctop']), set={'FirstLine': '1', 'SecondLine': '(ф%d)' % dia})
    yk = YBOT - 151
    add(t='combsegs', h=S(SEC['cbot']), segs=[[[xL + x, YBOT - 2], [xL + x + 70, yk]] for x in mB],
        start=[xR + 330, yk], end=[xL + mB[0] + 70, yk])
    add(t='mcset', h=S(SEC['cbot']), set={'FirstLine': '1', 'SecondLine': '(ф%d)' % B['main']['bot'][1]})
    # side bars (both faces) + Шп1 pins in every side row
    srows = side_rows(B)
    sy = [YBOT + (YTOP - YBOT) * (i + 1) / (len(srows) + 1.0) for i in range(len(srows))]
    for yy in sy:
        bar(mB[0], yy, B['side_d']); bar(mB[-1], yy, B['side_d'])
        tp_ = '%sPIN%d' % (P, int(yy))
        add(t='clone', h=B['pin_src'], base=[0, 0], to=[0, 0], tag=tp_ + ':19EC6')
        add(t='brscale', h=tp_ + ':19EC6', s=1, rot=0)
        add(t='insat', h=tp_ + ':19EC6', at=[xL + mB[0] - 12, yy])
        add(t='dyn', h=tp_ + ':19EC6', prop='Расстояние1', value=mB[-1] - mB[0])
        extra.append(tp_ + ':19EC6')
    # right-hand callouts stacked by height, min 230 apart, inside the band yb-230 .. yt+40
    items = []
    for gi, (top, row, pos, dd_, sel, y0) in enumerate(groups):
        items.append(dict(y=y0, kind='dop', top=top, pos=pos, d=dd_, sel=sel, y0=y0, gi=gi))
    if sy: items.append(dict(y=sum(sy) / len(sy), kind='side', sy=sy))
    ym = (YBOT + YTOP) / 2
    items.append(dict(y=ym + (60 if sy else 0), kind='x1'))
    items.sort(key=lambda it: -it['y'])
    hi_, lo_ = yt + 40, yb - 230
    ys = []
    for it in items:
        y_ = min(it['y'], hi_ if not ys else ys[-1] - 230); ys.append(y_)
    if ys and ys[-1] < lo_:
        sh_ = lo_ - ys[-1]; ys = [min(hi_, v + sh_) for v in ys]
        for i in range(1, len(ys)): ys[i] = min(ys[i], ys[i - 1] - 230)
    for it, ysh in zip(items, ys):
        if it['kind'] == 'dop':
            top = it['top']; y0 = it['y0']
            tg = '%sC%d' % (P, it['gi']); add(t='clone', h=S(SEC['ctop'] if top else SEC['cbot']), base=[0, 0], to=[0, 0], tag=tg); extra.append(tg)
            sg = [[[xL + x + 14, y0 + (ysh - y0) * 14.0 / max(1.0, (xR + 120 - xL - x))], [xR + 120, ysh]] for x in it['sel']]
            add(t='combsegs', h=tg, segs=sg, start=[xR + 560, ysh], end=[xR + 120, ysh])
            add(t='mcset', h=tg, set={'FirstLine': str(it['pos']), 'SecondLine': '(ф%d)' % it['d']})
        elif it['kind'] == 'side':
            tg = '%sCS' % P; add(t='clone', h=S(SEC['cbot']), base=[0, 0], to=[0, 0], tag=tg); extra.append(tg)
            sg = [[[xL + mB[-1] + 14, yy], [xR + 120, ysh]] for yy in it['sy']]
            add(t='combsegs', h=tg, segs=sg, start=[xR + 560, ysh], end=[xR + 120, ysh])
            add(t='mcset', h=tg, set={'FirstLine': str(B['side_pos']), 'SecondLine': '(ф%d)' % B['side_d']})
        else:
            add(t='combsegs', h=S(SEC['cx1']), segs=[[[xL + mB[-2] + 15, ym], [xR + 175, ysh]], [[xL + mB[-1] + 15, ym], [xR + 175, ysh]]])
            add(t='spmove', h=S(SEC['cx1']), items=[[0, xR + 175, ysh]])
            add(t='mcset', h=S(SEC['cx1']), set={'FirstLine': 'Х1; Шп1' if sy else 'Х1', 'SecondLine': '(ф%d)' % B['hoop']['d']})
    # level: single-line multilayer from the analog 6.6 section, title
    add(t='erase', h=[S(SEC['ml']), S(SEC['lev'])])
    if withML:
        tl = P + 'ML'
        add(t='clone', h='A:4308C2', base=[2936684, 428802], to=[xL - 619, yt + 120], tag=tl); extra.append(tl)
        add(t='levelval', h=tl, old='+4.395', value=B['levels'][0], tag=tl)
    add(t='settext', h=S(SEC['title']), s='Разрез %s - %s' % (sec['word'], sec['word']))
    add(t='move', h=[S(SEC['title'])], d=[(xL + xR) / 2.0 - (OX + 43), h - 400])
    tags = [S(x) for x in hs if (x not in SEC['brk'] or slab) and x not in SEC['bot'] + SEC['top'] and not (nm == 3 and x == SEC['hoop'][1])] + extra
    tags = [t_ for t_ in tags if t_ not in (S(SEC['ml']), S(SEC['lev']), S(SEC['dimb'][2]), S(SEC['dimb'][3]))]
    return ops, tags, [OX + b / 2.0, OY]


def place(s, tags, base, to, types):
    """clone the staged section x2 onto the sheet; dims to dimscale 50 / lfac 0.5, SPDS scale 50"""
    pre = s.P + 'X' + str(int(to[0])) + '_'
    ops = [dict(t='clone', h=h, base=base, to=to, s=SC, tag=pre + h.replace(':', '_')) for h in tags]
    ops.append(dict(t='dimset', h=[pre + h.replace(':', '_') for h in tags if types.get(h) == 'DIMENSION'], lfac=1.0 / SC * 1.0 * 1.0, dscale=50))
    for h in tags:
        ty = types.get(h, '')
        if ty.startswith('SPDS') and ty != 'SPDSBREAK': ops.append(dict(t='mcset', h=pre + h.replace(':', '_'), set={'Scale': 50}))
    s.ops += ops
    return pre
