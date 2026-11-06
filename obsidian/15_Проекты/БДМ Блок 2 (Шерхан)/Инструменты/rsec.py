# rigel cross-sections: analog section 1-1 (1:20) imported to a staging place, edited in real mm, cloned x2 (1:25) onto the sheet
from rgen import *

XLA, YBA = -211276.0, 428183.0          # analog section: beam left face / bottom
SC = 2.0                                 # 1:50 sheet, section drawn 1:25


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


def build_stage(B, sec, OX, OY, P):
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
    nt = sec.get('top_dop', (0, 0))[1]; nb = sec.get('bot_dop', (0, 0))[1]
    mT, dT, chT = bar_x(b, 4, nt); mB, dB, chB = bar_x(b, 4, nb)
    dia = B['main']['top'][1]
    for hh, x in zip(SEC['bot'], mB):
        add(t='insat', h=S(hh), at=[xL + x, YBOT]); add(t='dyn', h=S(hh), prop='Вид', value='Ø%d' % B['main']['bot'][1])
    for hh, x in zip(SEC['top'], mT):
        add(t='insat', h=S(hh), at=[xL + x, YTOP]); add(t='dyn', h=S(hh), prop='Вид', value='Ø%d' % dia)
    extra = []
    for i, x in enumerate(dT + dB):
        tg = '%sD%d' % (P, i); y = YTOP if i < len(dT) else YBOT
        add(t='clone', h=S(SEC['bot'][0]), base=[0, 0], to=[0, 0], tag=tg); add(t='insat', h=tg, at=[xL + x, y]); extra.append(tg)
    # two hoops, each over 3 main bars (shared middle)
    for hh, x in zip(SEC['hoop'], mB[:2]):
        add(t='insat', h=S(hh), at=[xL + x, YBOT + 11])
        add(t='dyn', h=S(hh), prop='Расстояние1', value=mB[2] - mB[0])
        add(t='dyn', h=S(hh), prop='Расстояние2', value=YTOP - YBOT)
    # bottom chain: 55 | step x n | 55 (dop slots define the step), total width
    allx = sorted(mB + dB)
    yd = yb - 306
    d = SEC['dimb']
    add(t='dimpts', h=S(d[0]), p1=[xL + allx[0], yb, 0], p2=[xL, yb, 0], dl=[xL, yd, 0])
    add(t='dimtx', h=S(d[0]), at=[xL - 75, yd + 40, 0])
    add(t='dimpts', h=S(d[1]), p1=[xL + allx[-1], yb, 0], p2=[xL + allx[0], yb, 0], dl=[xL + allx[0], yd, 0])
    add(t='dimtext', h=S(d[1]), s=chB)
    add(t='dimtx', h=S(d[1]), at=[xL + b / 2.0, yd + 40, 0])
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
    # dop combs: shelf at the side of the section, at the height of their row (analog 2-2 «2 (ф12)»)
    for flag, lst, y0, ysh, src, nm, dd_ in ((nt, dT, YTOP, YTOP - 170, SEC['ctop'], 'CDT', dia), (nb, dB, YBOT, YBOT + 170, SEC['cbot'], 'CDB', B['main']['bot'][1])):
        if not flag: continue
        tg = P + nm; add(t='clone', h=S(src), base=[0, 0], to=[0, 0], tag=tg); extra.append(tg)
        sg = [[[xL + x + 14, y0 + (ysh - y0) * 14.0 / (xR + 120 - xL - x)], [xR + 120, ysh]] for x in lst]
        add(t='combsegs', h=tg, segs=sg, start=[xR + 560, ysh], end=[xR + 120, ysh])
        add(t='mcset', h=tg, set={'FirstLine': str((sec['top_dop'] if nm == 'CDT' else sec['bot_dop'])[0]), 'SecondLine': '(ф%d)' % dd_})
    ym = (YBOT + YTOP) / 2
    add(t='combsegs', h=S(SEC['cx1']), segs=[[[xL + mB[2] + 15, ym], [xR + 175, ym]], [[xL + mB[3] + 15, ym], [xR + 175, ym]]])
    add(t='spmove', h=S(SEC['cx1']), items=[[0, xR + 175, ym]])
    add(t='mcset', h=S(SEC['cx1']), set={'FirstLine': 'Х1', 'SecondLine': '(ф%d)' % B['hoop']['d']})
    # level: single-line multilayer from the analog 6.6 section, title
    add(t='erase', h=[S(SEC['ml']), S(SEC['lev'])])
    tl = P + 'ML'
    add(t='clone', h='A:4308C2', base=[2936684, 428802], to=[xL - 619, yt + 120], tag=tl); extra.append(tl)
    add(t='levelval', h=tl, old='+4.395', value=B['levels'][0], tag=tl)
    add(t='settext', h=S(SEC['title']), s='Разрез %s - %s' % (sec['word'], sec['word']))
    add(t='move', h=[S(SEC['title'])], d=[(xL + xR) / 2.0 - (OX + 43), h - 400])
    tags = [S(x) for x in hs if x not in SEC['brk'] or slab] + extra
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
