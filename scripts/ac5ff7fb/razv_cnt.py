# 09.11 v2: «Развертка фасадных элементов» по аналогу ЦЕХ Блок 1 л.15/16 — колонны на всю высоту до балки покрытия,
# осевые линии каждой колонны, отметки и цепочки высот слева и справа, марки элементов; один торец = один лист A4x4 1:100.
# Openings — АР задание (Фасад D-A / A-D / 1/1-28 / 28-1/1), columns/beams — LIRA model2.json.
# Фахверк (user 09.11): РФ2 ригели и Ст1 стойки — □120x5.
import json, math, sys
sys.stdout.reconfigure(encoding='utf-8')
ops = []
T = [0]
def tag(p='z'):
    T[0] += 1; return '%s%d' % (p, T[0])
LAY = 'KOHTYP'
def pl(pts, closed=False, lw=5, layer=LAY):
    o = {'t': 'pl', 'p': [[float(a), float(b)] for a, b in pts], 'layer': layer, 'lw': lw}
    if closed: o['closed'] = True
    ops.append(o)
def rect(x0, y0, x1, y1, lw=5, layer=LAY): pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], True, lw, layer)
def mark(x, y, txt, vert=False):
    tg = tag('m'); ops.append({'t': 'clone', 'h': '5CA6D0', 'base': [1646496, -245439], 'to': [x, y], 'tag': tg})
    st = {'FirstLine': txt}
    if vert: st['Angle'] = math.pi / 2
    ops.append({'t': 'mcset', 'h': tg, 'set': st})
def hdim(x1, x2, y, ydl):
    tg = tag('d'); ops.append({'t': 'clone', 'h': '5CA555', 'base': [0, 0], 'to': [0, 0], 'tag': tg})
    ops.append({'t': 'dimpts', 'h': tg, 'p1': [x1, y, 0], 'p2': [x2, y, 0], 'dl': [(x1 + x2) / 2, ydl, 0]})
def vdim(x, y1, y2, xdl):
    tg = tag('d'); ops.append({'t': 'clone', 'h': '5CA5B0', 'base': [0, 0], 'to': [0, 0], 'tag': tg})
    ops.append({'t': 'dimpts', 'h': tg, 'p1': [x, y1, 0], 'p2': [x, y2, 0], 'dl': [xdl, (y1 + y2) / 2, 0]})
def axis(x, ytop, ybot, val):
    tg = tag('a'); ops.append({'t': 'clone', 'h': '5CA54B', 'base': [0, 0], 'to': [0, 0], 'tag': tg})
    ops.append({'t': 'axis', 'h': tg, 's': [x, ytop, 0], 'e': [x, ybot, 0], 'val': val})
LEV = []
def level(x, y, val, right=False):
    tg = tag('l'); ops.append({'t': 'clone', 'h': '61DDE5', 'base': [2601596.8, -196508.6], 'to': [x, y], 'tag': tg})
    s = 1 if right else -1
    ops.append({'t': 'mcset', 'h': tg, 'set': {'Scale': 100}})
    ops.append({'t': 'sp_set', 'h': tg, 'pts': [[1, x + s * 2300, y + 700], [2, x + s * 1600, y]]})
    LEV.append((tg, val))
def fmt(v):
    return '±0,000' if v == 0 else ('%+.3f' % (v / 1000.0)).replace('.', ',')
def title(x, y, txt):
    tg = tag('t'); ops.append({'t': 'clone', 'h': '571640', 'base': [1661764.9, -233945.3], 'to': [x, y], 'tag': tg})
    ops.append({'t': 'settext', 'h': tg, 's': '{\\L' + txt + '}'})
def sheet(FX, FY, num, name):
    tg = tag('f'); ops.append({'t': 'clone', 'h': '62BA70', 'base': [2820565.4, -274649.7], 'to': [FX, FY], 'tag': tg})
    ops.append({'t': 'mcset', 'h': tg, 'set': {'Multiplicity': 4}})
    ops.append({'t': 'mcset', 'h': tg, 'set': {'Scale': 100}})
    for h in ('62D713', '62D714', '62D716'):
        t2 = tag('s'); ops.append({'t': 'clone', 'h': h, 'base': [2852065.4, -274649.7], 'to': [FX + 84100, FY], 's': 2, 'tag': t2})
        if h == '62D714': ops.append({'t': 'settext', 'h': t2, 's': name})
        if h == '62D716': ops.append({'t': 'settext', 'h': t2, 's': str(num)})

PIE=[]
def elevation(X0, G, S):
    PIE.extend(S['pieces'])
    """S: dict(cols=[(u,w,top,mark)], beam=dict(pts=[(u,v)], h, mark), pieces=[(u0,v0,u1,v1,mark,vert)],
       opens=[(u0,v0,u1,v1)], chains=[[u..] or None-separated], axes=[(u,val)], levL=[v], levR=[v], vd=[(u,v1,v2)], title"""
    X = lambda u: X0 + u
    Y = lambda v: G + v
    cols = S['cols']; u0, u1 = cols[0][0], cols[-1][0]
    top = max(v for u, v in S['beam']['pts']) + S['beam']['h']
    title(X((u0 + u1) / 2), Y(top + S.get('tgap', 1300)), S['title'])
    pl([(X(u0 - 1500), Y(0)), (X(u1 + 1500), Y(0))], lw=5)                     # ground
    grid = set(u for u, v in S['axes'])
    for u, w, tv, mk in cols:
        rect(X(u - w / 2), Y(0), X(u + w / 2), Y(tv))
        if u not in grid: pl([(X(u), Y(-400)), (X(u), Y(tv + 400))], lw=5, layer='АР-РП  Осевая линия')
        if mk: mark(X(u - w / 2 - 90), Y(tv - 2600), mk, vert=True)
    # beam on the column tops (band of height h, axis line = given points)
    bp = S['beam']['pts']; h = S['beam']['h']
    pl([(X(u), Y(v)) for u, v in bp]); pl([(X(u), Y(v + h)) for u, v in bp])
    pl([(X(bp[0][0]), Y(bp[0][1])), (X(bp[0][0]), Y(bp[0][1] + h))]); pl([(X(bp[-1][0]), Y(bp[-1][1])), (X(bp[-1][0]), Y(bp[-1][1] + h))])
    if S['beam'].get('mark'):
        for um in S['beam'].get('at', [(u0 + u1) / 4]):
            vv = min(v for u, v in bp) if False else None
            # beam level at um (linear)
            for (a, va), (b, vb) in zip(bp, bp[1:]):
                if a <= um <= b: vv = va + (vb - va) * (um - a) / (b - a)
            mark(X(um - 450), Y(vv + h + 60), S['beam']['mark'])
    for a0, v0, a1, v1, mk, vert in S['pieces']:
        rect(X(a0), Y(v0), X(a1), Y(v1), lw=30 if mk in ('РФ2', 'Ст1', '') else 5)   # user 09.11: only □120x5 = 0.30, the rest 0.05
        if mk and mk.endswith('@L'):
            mark(X(a0 + 250), Y(v1 + 60), mk[:-2]); mk = None
        if mk:
            if vert: mark(X(a0 - 90), Y((v0 + v1) / 2 - 350), mk, vert=True)
            elif mk == 'Р1' and abs(v0 - 4970) < 1: mark(X((a0 + a1) / 2 - 450), Y(v0 - 430), mk)
            else: mark(X((a0 + a1) / 2 - 450), Y(v1 + 60), mk)
    for pts, lw in S.get('polys', []): pl([(X(a), Y(b)) for a, b in pts], lw=lw)
    for a, b, txt, vert in S.get('marks', []): mark(X(a), Y(b), txt, vert=vert)
    for a0, v0, a1, v1 in S['opens']: rect(X(a0), Y(v0), X(a1), Y(v1), lw=5, layer='Размеры')
    # horizontal dims: openings line, columns, grid axes, overall
    k = 0
    lines = S.get('chain_lines', [S['chains']] if S['chains'] else [])
    for li, line in enumerate(lines):
        for ch in line:
            for a, b in zip(ch, ch[1:]): hdim(X(a), X(b), Y(0), Y(-850 - 800 * li))
    k = len(lines)
    cu = [c[0] for c in cols]
    for a, b in zip(cu, cu[1:]): hdim(X(a), X(b), Y(0), Y(-850 - 800 * k))
    au = sorted(grid)
    if au != cu and len(au) > 2:
        k += 1
        for a, b in zip(au, au[1:]): hdim(X(a), X(b), Y(0), Y(-850 - 800 * k))
    k += 1
    hdim(X(au[0]), X(au[-1]), Y(0), Y(-850 - 800 * k))
    for u, val in S['axes']: axis(X(u), Y(top + 500), Y(-850 - 800 * k - 1000), val)
    # heights: chains + overall + levels, left and right
    for side, levs in ((-1, S['levL']), (1, S['levR'])):
        ue = u0 - cols[0][1] / 2 if side < 0 else u1 + cols[-1][1] / 2
        xs = ue + side * 1100; xo = ue + side * 2000; xl = ue + side * 2700
        lv = sorted(set([0] + levs))
        for a, b in zip(lv, lv[1:]): vdim(X(ue + side * 300), Y(a), Y(b), X(xs))
        vdim(X(ue + side * 300), Y(lv[0]), Y(lv[-1]), X(xo))
        for v in lv: level(X(xl), Y(v), fmt(v), right=(side > 0))
    for u, v1, v2 in S['vd']: vdim(X(u), Y(v1), Y(v2), X(u))
    for u, v, right in S.get('levIn', []): level(X(u), Y(v), fmt(v), right=right)

# ---------------------------------------------------------------- торцы (LIRA x=0 / x=162)
COLTOP = {0: 14490, 24: 15090, 36: 15090, 60: 14490, 6: 14640, 12: 14790, 18: 14940, 27: 15160, 33: 15160, 42: 14940, 48: 14790, 54: 14640}
BEAM = [(0, 14490), (24, 15090), (27, 15160), (29.85, 15240), (30.15, 15240), (33, 15160), (36, 15090), (60, 14490)]
def torec(view_from_west, opens_y, ttl):
    # u along the wall from the left edge of the view; west view (ось 1): left = M (y=60); east view (ось 28): left = A (y=0)
    U = (lambda y: (60 - y) * 1000) if view_from_west else (lambda y: y * 1000)
    cols = []
    for y, tv in COLTOP.items():
        w = 589 if y in (0, 24, 36, 60) else 300
        cols.append((U(y), w, tv - 150, None if w == 589 else 'СФ1'))
    cols.sort()
    beam = sorted((U(y), v - 150) for y, v in BEAM)
    fac = lambda i, s: cols[i][0] + s * cols[i][1] / 2
    pieces = [(fac(i, 1), 6150, fac(i + 1, -1), 6250, 'РФ1', False) for i in range(len(cols) - 1)]
    opens, chains, vd, levs, levin = [], [], [], set(), []
    for (ya, yb, hgt, kind) in opens_y:
        a, b = sorted((U(ya), U(yb)))
        cl = max(c[0] for c in cols if c[0] < a); cr = min(c[0] for c in cols if c[0] > b)
        opens.append((a, 0, b, hgt))
        if kind == 'gate6':           # posts up to the РФ1 bottom
            pieces += [(a - 120, 0, a, 6150, 'Ст1', True), (b, 0, b + 120, 6150, 'Ст1', True), (a, hgt, b, hgt + 120, 'РФ2', False)]
        else:                         # door: posts + РФ2 lintel between the neighbouring columns
            il = [c for c in cols if c[0] == cl][0]; ir = [c for c in cols if c[0] == cr][0]
            pieces += [(a - 120, 0, a, hgt, 'Ст1', True), (b, 0, b + 120, hgt, 'Ст1', True),
                       (cl + il[1] / 2, hgt, cr - ir[1] / 2, hgt + 120, 'РФ2', False)]
            levs.add(hgt)
        chains.append([cl, a, b, cr]); vd.append((a + 450, 0, hgt))
    axes = [(U(y), v) for y, v in ((60, 'M'), (36, 'H'), (24, 'E'), (0, 'A'))]
    return dict(cols=cols, beam=dict(pts=beam, h=300, mark='БП1', at=[12000, 48000]), pieces=pieces, opens=opens, chains=chains,
                axes=axes, levL=sorted(levs | {6200, 14490}), levR=sorted({6200, 14490}), vd=vd, title=ttl)

FX0, FY = 2925000.0, -274649.7
# ---- лист 27: по оси 1 (ВР-1 4540x6020 y 27.827..32.367; ДНГ-1 1000x2100 y 16.2..17.2)
FX = FX0
sheet(FX, FY, 29, 'Развертка фасадных элементов\\Pпо оси 1')
S1 = torec(True, [(27.827, 32.367, 6020, 'gate6'), (16.2, 17.2, 2100, 'door')], 'Развертка фасадных элементов по оси 1'); S1['tgap'] = 1000
elevation(FX + 9000, FY + 12200, S1)

# ---- лист 28: по оси 1/1 (пристройка) + ведомость + примечания
FX = FX0 + 84100
sheet(FX, FY, 30, 'Развертка фасадных элементов\\Pпо оси 1/1')
U = lambda y: (60 - y) * 1000
cols2 = sorted((U(y), 200, 5700, 'СФ2') for y in (60, 54, 48, 42, 36))
p2, op2, ch2, vd2 = [], [], [], []
for g0, g1 in ((1000, 5000), (13300, 17300), (19300, 23300)):
    cl = max(c[0] for c in cols2 if c[0] < g0); cr = min(c[0] for c in cols2 if c[0] > g1)
    p2 += [(g0 - 120, 0, g0, 4000, 'Ст1', True), (g1, 0, g1 + 120, 4000, 'Ст1', True), (cl + 100, 4000, cr - 100, 4120, 'РФ2', False)]
    op2.append((g0, 0, g1, 4000)); ch2.append([cl, g0, g1, cr]); vd2.append((g0 + 450, 0, 4000))
S2 = dict(cols=cols2, beam=dict(pts=[(-100, 5700), (24100, 5700)], h=270, mark='Пр2', at=[3000]), pieces=p2, opens=op2, chains=ch2,
          axes=[(0, 'M'), (24000, 'H')], levL=[4000, 5700], levR=[4000, 5700], vd=vd2, title='Развертка фасадных элементов по оси 1/1')
elevation(FX + 9000, FY + 17500, S2)
# ведомость элементов фахверка (header + rows of the main ведомость, x0.5; the main table is 3169 higher since 21:44)
DY = 3169.0
B = (2782567.0, -200087.0 + DY); TV = (FX + 44000, FY + 27000); F = 0.5
M = lambda x, y: [TV[0] + (x - B[0]) * F, TV[1] + (y - B[1]) * F]
for h in ['625706','625707','625708','625709','62570A','62570B','62570C','62570D','62570E','62570F','625710','625711','625712','625713','625714','625715','625716']:
    ops.append({'t': 'clone', 'h': h, 'base': list(B), 'to': list(TV), 's': F})
tt = tag('vt'); ops.append({'t': 'clone', 'h': '625717', 'base': list(B), 'to': list(TV), 's': F, 'tag': tt})
ops.append({'t': 'settext', 'h': tt, 's': 'Ведомость элементов фахверка'})
ROWS = [('СФ1', '1', '40Ш2', '3', 'торцы', 'I'), ('СФ2', '2', '□200x6', '3', 'пристройка', 'B'),
        ('РФ1', '3', '□100x5', '3', '+6.200', 'B'), ('РФ2', '4', '□120x5', '3', 'над проемами', 'B'),
        ('Ст1', '5', '□120x5', '3', 'у проемов', 'B')]
VL = {'625718': (2782567, -200087), '625719': (2786145, -200087), '62571A': (2789723, -202471), '62571B': (2792109, -202471),
      '62571C': (2795687, -200087), '62571D': (2799265, -202471), '62571E': (2802843, -202471), '62571F': (2806421, -200087),
      '625720': (2808807, -200087), '625721': (2813577, -200087), '625722': (2819565, -200087)}
YB = -204858.0 - len(ROWS) * 1670.0 + DY
for h, (x, yt) in VL.items():
    t2 = tag('vl'); ops.append({'t': 'clone', 'h': h, 'base': list(B), 'to': list(TV), 's': F, 'tag': t2})
    ops.append({'t': 'plset', 'h': t2, 'p': [M(x, YB), M(x, yt + DY)]})
for i, (mk, pos, sec, grp, nt, sk) in enumerate(ROWS):
    if sk == 'I': src = {'mk': '625724', 'pos': '625727', 'sec': '625725', 'grp': '625728', 'st': '625726', 'nt': '625729', 'sk': ['62572A']}; r0 = 0
    else: src = {'mk': '625734', 'pos': '625737', 'sec': '625735', 'grp': '625738', 'st': '625736', 'nt': '625739', 'sk': ['62573A', '62573B']}; r0 = 2
    to = [TV[0], TV[1] - 1670.0 * (i - r0) * F]
    for key, val in (('mk', mk), ('pos', pos), ('sec', sec), ('grp', grp), ('st', 'С255'), ('nt', nt)):
        ops.append({'t': 'clone', 'h': src[key], 'base': list(B), 'to': to, 's': F, 'text': val})
    for h in src['sk']: ops.append({'t': 'clone', 'h': h, 'base': list(B), 'to': to, 's': F})
    ops.append({'t': 'clone', 'h': '625723', 'base': list(B), 'to': [TV[0], TV[1] - 1670.0 * i * F], 's': F})
tn = tag('n'); ops.append({'t': 'clone', 'h': '61DDE8', 'base': [2783185, -254674], 'to': [FX + 65300, FY + 12600], 's': 0.5, 'tag': tn})
ops.append({'t': 'mtw', 'h': tn, 'w': 18300})
ops.append({'t': 'settext', 'h': tn, 's':
    '1. Ригели РФ2 и стойки Ст1 фахверка - труба □120x5 по ГОСТ 30245-2003, сталь С255.\\P'
    '2. Проемы - по заданию АР (Фасады D-A, A-D, 1/1-28, 28-1/1).\\P'
    '3. Стойки Ст1 приваривать к ригелям РФ1, РФ2 по контуру, катет шва 5 мм.\\P'
    '4. Развертки фасадных элементов см. листы 29 - 37; ведомость элементов - лист 13.'})
# ---- лист 29: по оси 28 (вид с востока: слева А, справа М; ДНГ-1 y 16.2..17.2, ВР-1 4520x6000 y 27.85..32.37)
FX = FX0 + 2 * 84100
sheet(FX, FY, 31, 'Развертка фасадных элементов\\Pпо оси 28')
S3 = torec(False, [(16.2, 17.2, 2100, 'door'), (27.85, 32.37, 6000, 'gate6')], 'Развертка фасадных элементов по оси 28'); S3['tgap'] = 1000
elevation(FX + 9000, FY + 12200, S3)

# ---------------------------------------------------------------- бойлық фасадтар (ряд A: y=0, вид с юга; ряд M: y=60, вид с севера)
RIB = lambda x0: (x0 + 500, x0 + 5500)
def long_openings(row):
    O = []          # (x0, x1, v0, v1, kind)  kind: win / door
    if row == 'A':
        for i in range(27): a, b = RIB(i * 6000); O.append((a, b, 5320, 6820, 'win'))
    else:
        for i in range(27):
            if i * 6000 in (72000, 78000, 84000): continue
            a, b = RIB(i * 6000); O.append((a, b, 5320, 6820, 'win'))
        for a in (73000, 76000, 79000): O.append((a, a + 1500, 5320, 6820, 'win'))
        for a in (73000, 76000, 79000, 85000, 91000, 97000): O.append((a, a + 1500, 1020, 2520, 'win'))
        O.append((64100, 65100, 0, 2100, 'door'))
    return O
BRACED = (6000, 48000, 108000, 150000)
def long_part(row, k):
    # part k = 0,1,2 of 9 bays; view: row A from the south (x grows to the right), row M from the north (x decreases)
    if row == 'A': xL, xR = k * 54000, (k + 1) * 54000; U = lambda x: x - xL
    else: xL, xR = 162000 - k * 54000, 162000 - (k + 1) * 54000; U = lambda x: xL - x
    lo, hi = min(xL, xR), max(xL, xR)
    xs = list(range(lo, hi + 1, 6000))
    cols = sorted((U(x), 300, 14490, None) for x in xs)
    if row == 'M' and k == 2: cols.append((U(-7000), 200, 5700, 'СФ2'))          # пристройка, ось 1/1
    cols.sort()
    pieces, polys, marks, chains, vd, opens = [], [], [], [], [], []
    fx = lambda x, s: U(x) + s * 150                                              # column face toward s (in u)
    # Р1 □100x5 (LIRA) at +5.020 / +10.340 in the column plane (row M: none at +5.020 in axes 13-19)
    for x in xs[:-1]:
        a, b = sorted((U(x), U(x + 6000)))
        for zc in (5020, 10340):
            if row == 'M' and zc == 5020 and 72000 <= x < 108000: continue
            pieces.append((a + 150, zc - 50, b - 150, zc + 50, 'Р1', False))
    # СВ1 □160x5 (два яруса) + СВ2 □100x5 (верх) in the braced bays
    for x in BRACED:
        if not (lo <= x < hi): continue
        a, b = sorted((U(x), U(x + 6000))); m = (a + b) / 2
        for (p, q, mk) in (((a + 150, 0), (m, 4970), 'СВ1'), ((b - 150, 0), (m, 4970), None),
                           ((m, 5070), (a + 150, 10290), 'СВ1'), ((m, 5070), (b - 150, 10290), None),
                           ((m, 10390), (a + 150, 14490), 'СВ2'), ((m, 10390), (b - 150, 14490), None)):
            polys.append(([p, q], 5))
            if mk: marks.append(((p[0] + q[0]) / 2 + 120, (p[1] + q[1]) / 2, mk, False))
    # площадка ряда M: Б1 25Б1 на +4.000 (оси 13-19) и +7.600 (оси 13-16)
    if row == 'M':
        for x0, x1, z in ((72000, 108000, 4000), (72000, 90000, 7600)):
            for x in range(x0, x1, 6000):
                if lo <= x < hi:
                    a, b = sorted((U(x), U(x + 6000))); pieces.append((a + 150, z - 124, b - 150, z + 124, 'Б1', False))
    # openings + фахверк
    O = [o for o in long_openings(row) if lo <= o[0] < hi]
    bays = {}
    for o in O: bays.setdefault((o[0] // 6000) * 6000, []).append(o)
    up, lw_ = [], []
    lastb = max(sorted(U(xb) for xb in bays) or [0])
    for xb, oo in sorted(bays.items()):
        a_ax, b_ax = sorted((U(xb), U(xb + 6000)))
        cut = set()
        for (x0, x1, v0, v1, kind) in oo:
            a, b = sorted((U(x0), U(x1))); cut |= {a, b}
            opens.append((a, v0, b, v1))
            if kind == 'win':
                pieces += [(a - 120, v0, a, v1, 'Ст1', True), (b, v0, b + 120, v1, 'Ст1', True)]
            else:
                pieces += [(a - 120, 0, a, v1, 'Ст1', True), (b, 0, b + 120, v1, 'Ст1', True)]
                vd.append((a + 450, 0, v1))
        for v0, v1 in sorted(set((o[2], o[3]) for o in oo)):
            og = [o for o in oo if (o[2], o[3]) == (v0, v1)]
            if all(o[1] - o[0] == 5000 for o in og): xm = (a_ax + b_ax) / 2
            else:
                posts = sorted([(a_ax, a_ax + 150), (b_ax - 150, b_ax)] + [(min(U(o[0]), U(o[1])) - 120, max(U(o[0]), U(o[1])) + 120) for o in og])
                xm = max((q[0] - p[1], (p[1] + q[0]) / 2) for p, q in zip(posts, posts[1:]))[1]
            if v0 > 0:
                pieces.append((a_ax + 150, v0 - 120, b_ax - 150, v0, '', False))            # под проемом
                marks.append((xm - 450, v0 + 60, 'РФ2', False))
            pieces.append((a_ax + 150, v1, b_ax - 150, v1 + 120, '', False))                 # над проемом
            marks.append((xm - 450, v1 + 180, 'РФ2', False))
        for grp, dst in (([o for o in oo if o[2] >= 5000], up), ([o for o in oo if o[2] < 5000], lw_)):
            if not grp: continue
            pts = sorted(set(sum(([min(U(o[0]), U(o[1])), max(U(o[0]), U(o[1]))] for o in grp), [])))
            ch = [a_ax] + pts + [b_ax]
            if b_ax - pts[-1] < 800 and b_ax < max(c[0] for c in cols if c[3] is None): ch = ch[:-1]
            dst.append(ch)
    chains = up
    axes = [(U(x), str(x // 6000 + 1)) for x in xs]
    if row == 'M' and k == 2: axes.append((U(-7000), '1/1'))
    lev = {5320, 6820, 14490}
    if any(o[2] == 1020 for o in O): lev |= {1020, 2520}
    levR = {5020, 10340, 14490} | ({2100} if any(o[4] == 'door' for o in O) else set())
    if row == 'M' and k == 2: levR |= {5700}
    beam = [(U(lo) - 150, 14490), (U(hi) + 150, 14490)] if row == 'A' else [(U(hi) - 150, 14490), (U(lo) + 150, 14490)]
    beam = sorted(beam)
    n1, n2 = (xL // 6000 + 1, xR // 6000 + 1)
    ttl = 'Развертка фасадных элементов по ряду %s (оси %d - %d)' % (row, n1, n2) if not (row == 'M' and k == 2) else \
          'Развертка фасадных элементов по ряду M (оси 10 - 1/1)'
    return dict(cols=cols, beam=dict(pts=beam, h=270, mark='Пр1', at=[13500, 40500]), pieces=pieces, opens=opens, chains=chains,
                axes=axes, levL=sorted(lev), levR=sorted(levR), vd=vd, title=ttl, polys=polys, marks=marks, tgap=1000,
                chain_lines=[l for l in (up, lw_) if l]), ttl
num = 32
for row in ('A', 'M'):
    for k in range(3):
        FX = FX0 + (num - 29) * 84100
        S, ttl = long_part(row, k)
        sheet(FX, FY, num, ttl.replace('Развертка фасадных элементов ', 'Развертка фасадных элементов\\P'))
        elevation(FX + 9000, FY + 12200, S)
        num += 1

# ---- основная ведомость (лист 13): + РФ2 (поз. 29), Ст1 (поз. 30); table bottom now at -250118
ops.append({'t': 'stretchwin', 'win': [2782000, -250250, 2820000, -250000], 'sel': [2782000, -250250, 2820000, -250000], 'd': [0, -3340.0]})
for j in (1, 2): ops.append({'t': 'clone', 'h': '6257CA', 'base': [0, 0], 'to': [0, 1670.0 * j]})
SRC = {'mk': '6257CB', 'pos': '6257CE', 'sec': '6257CC', 'grp': '6257CF', 'st': '6257CD', 'nt': '6257D0'}
for k, (mk, pos, sec, nt) in ((7, ('РФ2', '29', '□120x5', 'фахверк')), (8, ('Ст1', '30', '□120x5', 'фахверк'))):
    pass
for k, mk, pos, nt in ((7, 'РФ2', '29', 'фахверк'), (8, 'Ст1', '30', 'фахверк')):
    dy = -1670.0 * k
    for key, val in (('mk', mk), ('pos', pos), ('sec', '□120x5'), ('grp', '3'), ('st', 'С255'), ('nt', nt)):
        ops.append({'t': 'clone', 'h': SRC[key], 'base': [0, 0], 'to': [0, dy], 'text': val})
    for h in ('6257A6', '6257A7'): ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [0, -8227 + dy]})
for tg_, val in LEV: ops.append({'t': 'levtext', 'h': tg_, 'value': val})
ops.append({'t': 'sysvar', 'set': {'FILEDIA': 1, 'CMDDIA': 1, 'SECURELOAD': 1}}); ops.append({'t': 'save'})
json.dump(ops, open('C:/Users/Admin/AppData/Local/Temp/claude/204b4b97c8536327/ac5ff7fb-6571-471e-9426-80def9c2be5c/scratchpad/razv_dummy.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ops', len(ops))

import collections
T=collections.defaultdict(lambda:[0,0.0])
for a0,v0,a1,v1,mk,vert in PIE:
    m=(mk or '').replace('@L','')
    L=abs(v1-v0) if vert else abs(a1-a0)
    T[m][0]+=1; T[m][1]+=L
for k,v in T.items(): print(repr(k), v[0], round(v[1]/1000,1),'m')

