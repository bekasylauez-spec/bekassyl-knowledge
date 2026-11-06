# facade of a rigel sheet (see rgen.py for the conventions)
from rgen import *


def facade(s, B, part):
    """B: beam (beams.py); part: dict(i0, i1, brkL, brkR) — supports i0..i1 drawn on this sheet"""
    A, add, D = s.A, s.add, s.D
    h = B['h']
    dU = min(h - 550, 300) if h > 550 else h - 550
    dD = (h - 550) - dU
    YB = 468150.0 - dD; YT = YB + h
    YTB, YBB = YT - 55, YB + 55
    yb = lambda y: y - dD          # galaxy y below the beam
    yu = lambda y: y + dU          # above the beam
    sup = B['sup'][part['i0']:part['i1'] + 1]
    U0 = sup[0]['ax'] if sup[0].get('ax') is not None else sup[0]['a']
    T1 = 175307.0 + D
    X = lambda u: T1 + (u - U0)
    u0 = (sup[0]['a'] - 700) if part['brkL'] else B['END0']
    u1 = (sup[-1]['b'] + 700) if part['brkR'] else B['END1']
    s.geo = dict(X=X, YB=YB, YT=YT, YTB=YTB, YBB=YBB, u0=u0, u1=u1, dU=dU, dD=dD, sup=sup, yb=yb, yu=yu)
    if dU: add(t='movewin', win=[172179 + D, 468701, 199300 + D, 470700], d=[0, dU])
    if dD: add(t='movewin', win=[172179 + D, 465650, 199300 + D, 468149], d=[0, -dD])
    # columns / walls with break marks
    takeC, restC = pool(COLS, s, 'COL')
    for k, sp in enumerate(sup):
        hC = takeC()
        top = YT + 97 if sp['kind'] == 'col' else YB
        add(t='plset', h=hC, p=[[X(sp['a']), top], [X(sp['b']), top], [X(sp['b']), yb(467970)], [X(sp['a']), yb(467970)]], closed=True)
        for src, y, kk in (('A:42F9FB', top + 0.4, 't'), ('A:42F9FC', yb(467970.4), 'b')):
            if kk == 't' and sp['kind'] != 'col': continue
            tg = '%sBR%d%s' % (s.P, k, kk)
            add(t='clone', h=src, base=[0, 0], to=[0, 0], tag=tg)
            add(t='mcset', h=tg, set={'StartPoint': [X(sp['a']) - 30, y], 'EndPoint': [X(sp['b']) + 30, y],
                                      'ClipZonePoint': [X(sp['b']) + 30, y], 'Length': X(sp['b']) - X(sp['a']) + 60})
    add(t='erase', h=restC() + [A(h) for h in SPDS['brk']])
    for flag, u in ((part['brkL'], u0), (part['brkR'], u1)):
        if not flag: continue
        tg = '%sBRV%d' % (s.P, int(u))
        add(t='clone', h='A:42F9FB', base=[0, 0], to=[0, 0], tag=tg)
        add(t='mcset', h=tg, set={'StartPoint': [X(u), YB - 100], 'EndPoint': [X(u), YT + 100], 'ClipZonePoint': [X(u), YT + 100], 'Length': h + 200})
    # axes
    takeA, restA = pool(SPDS['ax'], s, 'AX')
    axes = [(sp['ax'], sp['axn']) for sp in sup if sp.get('ax') is not None]
    for u, nm in axes:
        add(t='axis', h=takeA(), s=[X(u), YT], e=[X(u), yb(466361)], val=nm)
    add(t='erase', h=restA())
    # outlines of the clear parts
    segs = []; cur = u0
    for sp in sup:
        if sp['kind'] != 'col': continue
        if sp['a'] > cur + 1: segs.append((cur, sp['a']))
        cur = max(cur, sp['b'])
    if u1 > cur + 1: segs.append((cur, u1))
    takeO, restO = pool(OUTL, s, 'OUT')
    for a, b in segs:
        add(t='plset', h=takeO(), p=[[X(b), YB], [X(b), YT], [X(a), YT], [X(a), YB]], closed=True)
    add(t='erase', h=restO())
    s.geo['segs'] = segs
    # main bars pos 1, Ск1 at the real ends
    ea = X(u0) + (0 if part['brkL'] else 20); eb = X(u1) - (0 if part['brkR'] else 20)
    add(t='plset', h=A('4015A8'), p=[[ea, YTB], [eb, YTB]], layer='диам25')
    add(t='plset', h=A('4015AE'), p=[[ea, YBB], [eb, YBB]], layer='диам25')
    L = 250; yk = (YBB + 20 + YTB - 20) / 2
    if not part['brkL']:
        add(t='plset', h=A('4015C1'), p=[[ea + L, YBB + 20], [ea + 25, YBB + 20], [ea, YBB + 45], [ea, YTB - 45], [ea + 25, YTB - 20], [ea + L, YTB - 20]], layer='диам16')
        add(t='move', h=[A(SPDS['sk'][0])], d=[ea - (175202 + D), 0]); add(t='spmove', h=A(SPDS['sk'][0]), items=[[1, ea, yk]])
    else:
        add(t='erase', h=[A('4015C1'), A(SPDS['sk'][0])])
    if not part['brkR']:
        add(t='plset', h=A('4069BF'), p=[[eb - L, YBB + 20], [eb - 25, YBB + 20], [eb, YBB + 45], [eb, YTB - 45], [eb - 25, YTB - 20], [eb - L, YTB - 20]], layer='диам16')
        add(t='move', h=[A(SPDS['sk'][1])], d=[eb - (196562 + D), 0]); add(t='spmove', h=A(SPDS['sk'][1]), items=[[1, eb, yk]])
    else:
        add(t='erase', h=[A('4069BF'), A(SPDS['sk'][1])])
    s.geo.update(ea=ea, eb=eb)
    # hoop zones per clear segment
    takeH, restH = pool(HL, s, 'HL'); takeZ, restZ = pool(ZD, s, 'ZD'); takeE, restE = pool(ED, s, 'ED')
    NH = 0; ZI = []
    def ref(u):
        for sp in sup:
            if abs(sp['b'] - u) < 1 or abs(sp['a'] - u) < 1:
                return sp['ax'] if sp.get('ax') is not None else u
        return u
    for a, b in segs:
        free_a = abs(a - u0) < 1; free_b = abs(b - u1) < 1
        sEnd, sMid = B['hoop']['s_end'], B['hoop']['s_mid']
        if free_a or free_b: sMid = sEnd
        zs, lines, cnt = zones2(a, b, sEnd, sMid)
        NH += cnt; ZI.append(lines)
        for x in lines:
            add(t='plset', h=takeH(), p=[[X(x), YBB], [X(x), YTB]], layer='диам%d' % B['hoop']['d'])
        for z0, z1, txt in zs:
            hz = takeZ()
            add(t='dimpts', h=hz, p1=[X(z0), YB, 0], p2=[X(z1), YB, 0], dl=[X(z1), yb(467342), 0])
            add(t='dimtext', h=hz, s=txt if 'х' in txt else '')
        pa = a if free_a else ref(a); pb = b if free_b else ref(b)
        for k, (p, q) in enumerate(((pa, lines[0]), (lines[-1], pb))):
            if abs(p - q) < 1: continue
            he = takeE()
            add(t='dimpts', h=he, p1=[X(q), YB, 0], p2=[X(p), YB, 0], dl=[X(p), yb(467342), 0])
            add(t='dimtx', h=he, at=[X(lines[0]) + 34, yb(467096), 0] if k == 0 else [X(p) - 19, yb(466980), 0])
    add(t='erase', h=restH() + restZ() + restE())
    s.geo['ZI'] = ZI; s.NH = NH
    # axis chain (+ beam ends) and total
    takeD, restD = pool(AXD, s, 'AXD')
    pts = [u for u, _ in axes]
    if not part['brkL'] and abs(B['END0'] - pts[0]) > 1: pts = [B['END0']] + pts
    if not part['brkR'] and abs(B['END1'] - pts[-1]) > 1: pts = pts + [B['END1']]
    for p, q in zip(pts, pts[1:]):
        add(t='dimpts', h=takeD(), p1=[X(p), yb(466361), 0], p2=[X(q), yb(466361), 0], dl=[X(q), yb(466773), 0])
    add(t='erase', h=restD())
    add(t='dimpts', h=A('401292'), p1=[X(pts[0]), yb(466361), 0], p2=[X(pts[-1]), yb(466361), 0], dl=[X(pts[-1]), yb(466411), 0])
    xl = X(u0)
    add(t='dimpts', h=A('4015A4'), p1=[xl, YT, 0], p2=[xl, YB, 0], dl=[xl - 1097, YB, 0])
    add(t='dimpts', h=A('4015AD'), p1=[xl, YB, 0], p2=[xl + 20, YBB, 0], dl=[xl - 562, YBB, 0])
    add(t='dimpts', h=A('401933'), p1=[xl + 20, YBB, 0], p2=[xl + 20, YTB, 0], dl=[xl - 562, YTB, 0])
    return s.geo
