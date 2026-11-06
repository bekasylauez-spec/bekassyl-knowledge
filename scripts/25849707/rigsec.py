# Sections from the analog «Разрез 1-1» (1:1 above the analog frame) -> clone x2.5 onto the 1:50 sheet, then edited
SC0 = (-211276.0, 428183.0)                 # analog section: beam left-bottom corner
SBOT = ['40444B', '404886', '40488D', '40445E']; STOP = ['404468', '40490C', '404913', '40446F']; SHOOP = ['404492', '40600F']
SDH = ['404452', '40498B', '4049B4', '40499A', '404465']; SDTOT = '4044EF'
SDV = dict(bot='404455', hin='404458', top='40445B', tot='4044EE')
SOUT, SBRK = '40444A', ['4044B3', '4044B2']
SCT, SCB, SNH = '4044EA', '4044EB', '406008'
STIT, SLM, SML = '4044B4', '4044D9', '42C86F'
SALL = SBOT + STOP + SHOOP + SDH + [SDTOT] + list(SDV.values()) + [SOUT] + SBRK + [SCT, SCB, SNH, STIT, SLM, SML]
SDIMS = SDH + [SDTOT] + list(SDV.values())
SSPDS = SBRK + [SCT, SCB, SNH, SLM, SML]


def barx(b, n):
    if n == 3: return [50.0, b / 2.0, b - 50.0]
    s1 = round((b - 100) / 3.0 / 10.0) * 10; s2 = b - 100 - 2 * s1
    return [50.0, 50.0 + s1, 50.0 + s1 + s2, b - 50.0]


def extra_x(bx, cnt):
    n = len(bx)
    mids = [(bx[i] + bx[i + 1]) / 2 for i in range(n - 1)]
    if cnt == 1: return [mids[len(mids) // 2]]
    if cnt == 2 and n == 4: return [mids[0], mids[2]]
    return mids[:cnt]


def section(S, F, j, word, T0, tops=0, bots=0, dpos=None):
    """section j (Разрез word-word); T0 = sheet point of the beam left-bottom corner;
       tops/bots = number of extra (доп) bars at top/bottom, dpos = dict(top=(pos,d), bot=(pos,d))"""
    b, h = float(F['b']), float(F['h']); hs = F.get('hslab', 200.0); fl = 173.0
    pre = '%sS%d_' % (S.P.rstrip(':'), j)
    f = lambda lx, ly: [T0[0] + 2.5 * lx, T0[1] + 2.5 * ly]
    ops = S.ops
    for hh in SALL:
        ops.append(dict(t='clone', h=S.A(hh), base=[SC0[0] + S.dx, SC0[1] + S.dy], to=list(T0), s=2.5, tag=pre + hh))
    ops.append(dict(t='dimset', h=[pre + hh for hh in SDIMS], lfac=0.4, dscale=50))
    for hh in SSPDS:
        if hh not in SBRK: ops.append(dict(t='mcset', h=pre + hh, set={'Scale': 50}))
    P = lambda hh: pre + hh
    ys = h - hs
    ops.append(dict(t='plset', h=P(SOUT), p=[f(b, 0), f(b, ys), f(b + fl, ys), f(b + fl, h), f(-fl, h), f(-fl, ys), f(0, ys), f(0, 0)], closed=True))
    for hh, x in ((SBRK[0], -fl), (SBRK[1], b + fl)):
        ops.append(dict(t='mcset', h=P(hh), set={'StartPoint': f(x, ys - 15), 'EndPoint': f(x, h + 15), 'ClipZonePoint': f(x, h + 15), 'Length': (hs + 30) * 2.5}))
    n = F['top']['n']; bx = barx(b, n)
    yb_, yt_ = 50.0, h - 50.0
    for pool, y, d in ((SBOT, yb_, F['bot']['d']), (STOP, yt_, F['top']['d'])):
        for i, hh in enumerate(pool):
            if i < n:
                ops.append(dict(t='insat', h=P(hh), at=f(bx[i], y))); ops.append(dict(t='dyn', h=P(hh), prop='Вид', value='Ø%d' % d))
            else:
                ops.append(dict(t='erase', h=[P(hh)]))
    hoops = [(0, 2)] if n == 3 else [(0, 2), (1, 3)]
    for k, hh in enumerate(SHOOP):
        if k < len(hoops):
            i0, i1 = hoops[k]
            ops.append(dict(t='insat', h=P(hh), at=f(bx[i0], yb_ + 11)))
            ops.append(dict(t='dyn', h=P(hh), prop='Расстояние1', value=(bx[i1] - bx[i0]) * 2.5))
            ops.append(dict(t='dyn', h=P(hh), prop='Расстояние2', value=(yt_ - yb_) * 2.5))
        else:
            ops.append(dict(t='erase', h=[P(hh)]))
    xtra = {}
    for key, cnt, y, src in (('top', tops, yt_, STOP[0]), ('bot', bots, yb_, SBOT[0])):
        mids = extra_x(bx, cnt) if cnt else []
        xtra[key] = mids
        for i, xx in enumerate(mids):
            t = '%sX%s%d' % (pre, key, i)
            ops.append(dict(t='clone', h=P(src), tag=t)); ops.append(dict(t='insat', h=t, at=f(xx, y)))
            ops.append(dict(t='dyn', h=t, prop='Вид', value='Ø%d' % dpos[key][1]))
    # horizontal chain: face | bars | face; equal steps as «s х k = L»
    yd = -306.0
    pts = [0.0] + bx + [b]
    hp = [P(hh) for hh in SDH]
    segs = list(zip(pts, pts[1:]))
    mid = segs[1:-1]
    eq = len(mid) > 1 and len(set(round(q - p) for p, q in mid)) == 1
    chain = [(segs[0][0], segs[0][1], None)]
    chain += [(mid[0][0], mid[-1][1], '%dх%d=%d' % (round(mid[0][1] - mid[0][0]), len(mid), round(mid[-1][1] - mid[0][0])))] if eq else [(p, q, None) for p, q in mid]
    chain += [(segs[-1][0], segs[-1][1], None)]
    for p, q, txt in chain:
        hh = hp.pop(0)
        ops.append(dict(t='dimpts', h=hh, p1=f(q, 0) + [0], p2=f(p, 0) + [0], dl=f(p, yd) + [0]))
        if txt: ops.append(dict(t='dimtext', h=hh, s=txt))
    ops.append(dict(t='erase', h=hp))
    ops.append(dict(t='dimpts', h=P(SDTOT), p1=f(0, 0) + [0], p2=f(b, 0) + [0], dl=f(b, -648) + [0]))
    xv, xt = -264.0, -453.0
    ops.append(dict(t='dimpts', h=P(SDV['bot']), p1=f(50, 0) + [0], p2=f(50, 50) + [0], dl=f(xv, 50) + [0]))
    ops.append(dict(t='dimpts', h=P(SDV['hin']), p1=f(50, 50) + [0], p2=f(50, h - 30) + [0], dl=f(xv, h - 30) + [0]))
    ops.append(dict(t='dimpts', h=P(SDV['top']), p1=f(50, h - 30) + [0], p2=f(50, h) + [0], dl=f(xv, h) + [0]))
    ops.append(dict(t='dimpts', h=P(SDV['tot']), p1=f(-fl, h) + [0], p2=f(0, 0) + [0], dl=f(xt, 0) + [0]))
    ys_t = yt_ + 213; ys_b = yb_ - 151
    ops.append(dict(t='combsegs', h=P(SCT), segs=[[f(x, yt_ - 1), f(x + 88, ys_t)] for x in bx] + [[f(bx[-1], yt_ - 1), f(bx[-1] + 88, ys_t)]] * (4 - n),
                    start=f(bx[-1] + 88, ys_t), end=f(bx[0] + 88, ys_t)))
    ops.append(dict(t='mcset', h=P(SCT), set={'FirstLine': F['top']['pos'], 'SecondLine': '(ф%d)' % F['top']['d']}))
    ops.append(dict(t='combsegs', h=P(SCB), segs=[[f(x, yb_ - 2), f(x + 70, ys_b)] for x in bx] + [[f(bx[-1], yb_ - 2), f(bx[-1] + 70, ys_b)]] * (4 - n),
                    start=f(bx[-1] + 110, ys_b), end=f(bx[0] + 70, ys_b)))
    ops.append(dict(t='mcset', h=P(SCB), set={'FirstLine': F['bot']['pos'], 'SecondLine': '(ф%d)' % F['bot']['d']}))
    ym = (yb_ + yt_) / 2
    hx = [bx[i1] for (i0, i1) in hoops]
    ops.append(dict(t='combsegs', h=P(SNH), segs=[[f(x + 15, ym), f(b + 175, ym)] for x in hx] + [[f(hx[-1] + 15, ym), f(b + 175, ym)]] * (2 - len(hx))))
    ops.append(dict(t='spmove', h=P(SNH), items=[[0] + f(b + 175, ym)]))
    ops.append(dict(t='mcset', h=P(SNH), set={'FirstLine': F['hoop']['pos'], 'SecondLine': '(ф%d)' % F['hoop']['d']}))
    for key, src, y in (('top', SCT, yt_), ('bot', SCB, yb_)):
        mids = xtra.get(key) or []
        if not mids: continue
        t = '%sXC%s' % (pre, key)
        ops.append(dict(t='clone', h=P(src), tag=t))
        if key == 'top':
            ysh = ys_t + 120; sg = [[f(x, y - 1), f(x + (ysh - y) * 88 / 213.0, ysh)] for x in mids]
        else:
            ysh = ys_b - 420; sg = [[f(x, y - 2), f(x + (y - ysh) * 70 / 151.0, ysh)] for x in mids]
        sg += [sg[-1]] * (4 - len(sg))
        xe = [q[1][0] for q in sg]
        ops.append(dict(t='combsegs', h=t, segs=sg, start=[max(xe) + (0 if key == 'top' else 100), sg[0][1][1]], end=[min(xe), sg[0][1][1]]))
        ops.append(dict(t='mcset', h=t, set={'FirstLine': dpos[key][0], 'SecondLine': '(ф%d)' % dpos[key][1]}))
    ops.append(dict(t='settext', h=P(STIT), s='Разрез %s - %s' % (word, word)))
    ops.append(dict(t='move', h=[P(STIT)], d=[2.5 * (b / 2.0 - 43.0), 2.5 * (h - 400.0)]))
    ops.append(dict(t='erase', h=[P(SML)]))
    ops.append(dict(t='move', h=[P(SLM)], d=[0, 2.5 * (h - 400.0)]))
    ops.append(dict(t='levelval', h=P(SLM), old='-0.100', value=F['level'], tag=P(SLM)))
    return 2.5 * (b + 2 * fl)
