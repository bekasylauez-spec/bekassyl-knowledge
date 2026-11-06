# Section «Разрез N-N» for БДМ Блок 3 rigels: clone of the analog 1:20 section 1-1 (staging S1:, frame 172179,430000) ×2.5
# onto the 1:50 sheet, then edited in place: b×h, slab 200, nT/nB Ø28 bars (main + доп between them), 2 hoops (b>300) or 1.
# Coordinates are written in staging units (1:20 real mm) and mapped by f().
import gx

HS = ['40444A', '40444B', '404452', '404455', '404458', '40445B', '40445E', '404465', '404468', '40446F', '404492',
      '4044B2', '4044B3', '4044B4', '4044D9', '4044EA', '4044EB', '4044EE', '4044EF', '404886', '40488D', '40490C',
      '404913', '40498B', '40499A', '4049B4', '406008', '40600F', '42C86F']
TYPES = {'404452': 'D', '404455': 'D', '404458': 'D', '40445B': 'D', '404465': 'D', '4044EE': 'D', '4044EF': 'D',
         '40498B': 'D', '40499A': 'D', '4049B4': 'D'}
SPDS = ['4044B2', '4044B3', '4044D9', '4044EA', '4044EB', '406008', '42C86F']
B0 = (173965.0, 431659.0)           # staging base point (section centre area)
xC = 173965.0                        # beam axis in staging
yb = 431384.0                        # beam bottom in staging (Galaxy sec1)
SLAB = 200


def section(word, T, pre, b, h, nT, nB, dia, hoopd, legs, level, sx=2.5):
    f = lambda x, y: [T[0] + (x - B0[0]) * sx, T[1] + (y - B0[1]) * sx]
    F = lambda p: f(p[0], p[1])
    A = lambda hh: pre + hh
    ops = [dict(t='clone', h='S1:' + hh, base=list(B0), to=list(T), s=sx, tag=pre + hh) for hh in HS]
    ops.append(dict(t='dimset', h=[A(hh) for hh in HS if TYPES.get(hh) == 'D'], lfac=1.0 / sx, dscale=50))
    for hh in SPDS:
        if hh not in ('4044B2', '4044B3'): ops.append(dict(t='mcset', h=A(hh), set={'Scale': 50}))
    add = lambda **k: ops.append(k)
    xL, xR = xC - b / 2.0, xC + b / 2.0
    yt = yb + h; ys = yt - SLAB
    xa, xb = xL - 173, xR + 173
    add(t='plset', h=A('40444A'), p=[F((xR, yb)), F((xR, ys)), F((xb, ys)), F((xb, yt)), F((xa, yt)), F((xa, ys)), F((xL, ys)), F((xL, yb))], closed=True)
    YBOT, YTOP = yb + 50, yt - 30 - (0 if True else 0)
    def row(n):
        if n == 1: return [xC]
        return [xL + 50 + (b - 100) * i / (n - 1.0) for i in range(n)]
    # main bars are the outer/even ones of the row; templates: 4 bottom + 4 top inserts
    botT = ['40444B', '404886', '40488D', '40445E']; topT = ['404468', '40490C', '404913', '40446F']
    BXb, BXt = row(nB), row(nT)
    def put(tpls, xs, y, s):
        for i, x in enumerate(xs):
            hh = A(tpls[i]) if i < len(tpls) else None
            if hh is None:
                hh = '%s_%s%d' % (pre, s, i); add(t='clone', h=A(tpls[0]), tag=hh)
            add(t='insat', h=hh, at=F((x, y))); add(t='dyn', h=hh, prop='Вид', value='Ø%d' % dia)
        if len(xs) < len(tpls): add(t='erase', h=[A(x) for x in tpls[len(xs):]])
    put(botT, BXb, YBOT, 'B'); put(topT, BXt, YTOP, 'T')
    # hoops: 2 hoops over 3 bars each (b>300) or one over all
    hp = ['404492', '40600F']
    m4 = row(4) if b > 300 else row(3)
    spans = [(m4[0], m4[2]), (m4[1], m4[3])] if b > 300 else [(m4[0], m4[2])]
    for hh, (a, c) in zip(hp, spans):
        add(t='insat', h=A(hh), at=F((a, YBOT + 11)))
        add(t='dyn', h=A(hh), prop='Расстояние1', value=(c - a) * sx)
        add(t='dyn', h=A(hh), prop='Расстояние2', value=(YTOP - YBOT) * sx)
    if b <= 300: add(t='erase', h=[A('40600F')])
    # bottom chain: face | bars | face (by the main 4 / 3 bars), total width
    yd = 431078 - 160
    mb = m4
    cd = ['404452', '40498B', '4049B4', '40499A', '404465']
    stp = (mb[-1] - mb[0]) / (len(mb) - 1.0)
    chain = [(xL, mb[0], None), (mb[0], mb[-1], '%dх%d=%d' % (round(stp), len(mb) - 1, round(mb[-1] - mb[0]))), (mb[-1], xR, None)]
    for i, (p, q, txt) in enumerate(chain):
        add(t='dimpts', h=A(cd[i]), p1=F((q, yb)) + [0], p2=F((p, yb)) + [0], dl=F((p, yd)) + [0])
        add(t='dimtext', h=A(cd[i]), s=txt or '')
        if i == 0: add(t='dimtx', h=A(cd[i]), at=F((xL - 60, yd + 18)) + [0])
        elif i == 2: add(t='dimtx', h=A(cd[i]), at=F((xR + 60, yd + 18)) + [0])
        else:
            fits = (q - p) * sx >= len(txt or '') * 0.8 * 125 + 60
            add(t='dimtx', h=A(cd[i]), at=F(((p + q) / 2.0, yd + 18)) + [0] if fits else F((xR + 60 + (250 + len(txt) * 0.8 * 125 / 2.0) / sx, yd + 18)) + [0])
    add(t='erase', h=[A(x) for x in cd[3:]])
    add(t='dimpts', h=A('4044EF'), p1=F((xL, yb)) + [0], p2=F((xR, yb)) + [0], dl=F((xR, 430736 - 160)) + [0])
    xv = 173476 - (b - 450) / 2.0
    for hh, (p, q) in zip(['404455', '404458', '40445B'], [(yb, YBOT), (YBOT, YTOP), (YTOP, yt)]):
        add(t='dimpts', h=A(hh), p1=F((mb[0], p)) + [0], p2=F((mb[0], q)) + [0], dl=F((xv, q)) + [0])
    add(t='dimpts', h=A('4044EE'), p1=F((xa, yt)) + [0], p2=F((xL, yb)) + [0], dl=F((xv - 189, yb)) + [0])
    for hh, x in (('4044B2', xb), ('4044B3', xa)):
        p, q = F((x, ys)), F((x, yt))
        add(t='mcset', h=A(hh), set={'StartPoint': p, 'EndPoint': q, 'ClipZonePoint': q, 'Length': q[1] - p[1]})
    # level mark at the slab top (analog mark re-valued), analog multilayer stack removed
    add(t='erase', h=[A('42C86F')])
    lp = F((xa, yt))
    add(t='spmove', h=A('4044D9'), items=[[0, lp[0], lp[1]]])
    add(t='levelval', h=A('4044D9'), old='-0.100', value=level, tag=pre + 'LV')
    # combs: top bars / bottom bars, hoop note
    ytc = yt + 163
    add(t='combsegs', h=A('4044EA'), segs=[[F((x, YTOP - 1)), F((x + 88, ytc))] for x in BXt], start=F((BXt[-1] + 88, ytc)), end=F((BXt[0] + 88, ytc)))
    add(t='mcset', h=A('4044EA'), set={'SecondLine': '(ф%d)' % dia})
    yk = YBOT - 151
    add(t='combsegs', h=A('4044EB'), segs=[[F((x, YBOT - 2)), F((x + 70, yk))] for x in BXb], start=F((BXb[-1] + 110, yk)), end=F((BXb[0] + 70, yk)))
    add(t='mcset', h=A('4044EB'), set={'SecondLine': '(ф%d)' % dia})
    ym = (YBOT + YTOP) / 2
    add(t='spmove', h=A('406008'), items=[[0] + F((xR + 175, ym))])
    add(t='mcset', h=A('406008'), set={'SecondLine': '(ф%d)' % hoopd})
    add(t='settext', h=A('4044B4'), s='Разрез %s - %s' % (word, word))
    add(t='moveto', h=A('4044B4'), to=F((xC, yt + 400)) + [0])
    return ops
