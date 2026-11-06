# БДМ Блок 3 — rigel sheet from the analog «Ресторан 6.1 Ригель Рм-1» (A4x3, 1:50), generalised from Galaxy rigx/rigg:
# up to 5 spans per sheet, any section height (everything above the beam is lifted by dY = h - 550), Ø28 main bars,
# free ends with Ск1 or a break (beam continues on the next sheet), доп bars, splices Н4 (Ø28, L=280).
# Analog entities are addressed by tags <P><old handle>. Coordinates: beam coordinate x (mm) -> sheet X(x).
import gx, json, sys
from rg import zones
from rigg import zones_any as _za


def zones_b3(fL, fR):
    # 100хN1 | 200хN2 | 100хN3 with no odd remainder: the remainder (<200) is split between the two end gaps (50 + r/2)
    Lp = fR - fL - 100
    n1 = int(round(Lp / 4 / 100.0)); n3 = n1
    rest = Lp - 100 * (n1 + n3); n2 = int(rest // 200); r = rest - 200 * n2
    if r >= 100: n3 += 1; r -= 100
    h0, h4 = fL + 50 + r / 2.0, fR - 50 - r / 2.0
    segs = [(h0, h0 + 100 * n1, '100х%d' % n1), (h0 + 100 * n1, h0 + 100 * n1 + 200 * n2, '200х%d' % n2), (h4 - 100 * n3, h4, '100х%d' % n3)]
    lines = [h0, h0 + 100 * n1, h4 - 100 * n3, h4]
    return segs, lines, n1 + n2 + n3 + 1


def zones_any(a, b):
    # spans / cantilevers shorter than 3 m: one zone ш.100 (analog-style chain stays readable)
    if b - a - 100 >= 3000: return zones_b3(a, b)
    h0, h4 = a + 50, b - 50; Lp = h4 - h0
    n = int(Lp // 100); rr = Lp - 100 * n
    h0, h4 = h0 + rr / 2.0, h4 - rr / 2.0
    return [(h0, h4, '100х%d' % n)], [h0, h4], n + 1
from brk import breaks
import rigx
from rigx import SPDS, AN0, SRC

YB0, YT0 = rigx.YB, rigx.YT          # 468150 / 468700 (Galaxy 550 high beam)
COLT, COLB = 468797.0, 467970.0      # column outline top / bottom
DIA = 28


def build(B):
    SX, P = B['SX'], B['P']; E0, E1 = B['E']; h = B['h']
    dY = h - 550
    YB, YT = YB0, YT0 + dY
    YBB, YTB = YB + 50, YT - 30                      # bar axes: bottom 50, top 30 (analog)
    D = SX - 172179.0
    A = lambda hh: P + hh
    X = lambda x: 175182.0 + D + (x - E0)
    ops = []; add = lambda **k: ops.append(k)
    k = [0]
    def tag(s): k[0] += 1; return '%s_%s%d' % (P.rstrip(':'), s, k[0])
    def clone(hh, s): t = tag(s); add(t='clone', h=hh, tag=t); return t
    sup = B['sup']
    # ---- columns + breaks
    pool = [A(x) for x in ['40159B', '4018B7', '4018BA', '4018BD', '4018C0', '4018C3']]
    kinds = B.get('supk') or [['c', 0]] * len(sup)
    cols = []
    for (a, b), (kd, hg) in zip(sup, kinds):
        hh = pool.pop(0) if pool else clone(A('40159B'), 'COL')
        if kd == 'c':
            add(t='plset', h=hh, p=[[X(a), COLT + dY], [X(b), COLT + dY], [X(b), COLB], [X(a), COLB]], closed=True); cols.append((a, b))
        else:   # supporting girder in section: top flush with the beam top, its own height, no break marks
            add(t='plset', h=hh, p=[[X(a), YT], [X(b), YT], [X(b), YT - hg], [X(a), YT - hg]], closed=True)
    add(t='erase', h=pool + [A(x) for x in SPDS['brk']])
    ops.extend(breaks(cols, X, COLT + dY + 0.4, COLB + 0.4, P.rstrip(':')))
    # ---- axes
    axp = [A(x) for x in SPDS['ax']]
    for (x, v) in B['axes']:
        add(t='axis', h=axp.pop(0) if axp else clone(A(SPDS['ax'][0]), 'AX'), s=[X(x), YT0 + dY], e=[X(x), 466361], val=v)
    add(t='erase', h=axp)
    # ---- beam outline between faces
    faces = [E0] + [c for s in sup for c in s] + [E1]
    spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
    rp = [A(x) for x in ['40159C', '402404', '403897', '403898', '403899']]
    for (a, b) in spans:
        add(t='plset', h=rp.pop(0) if rp else clone(A('40159C'), 'SP'), p=[[X(b), YB], [X(b), YT], [X(a), YT], [X(a), YB]], closed=True)
    add(t='erase', h=rp)
    # ---- main bars + ends
    c0 = 20 if B['ends'][0] == 'sk' else 0
    c1 = 20 if B['ends'][1] == 'sk' else 0
    add(t='plset', h=A('4015A8'), p=[[X(E0) + c0, YTB], [X(E1) - c1, YTB]], layer='диам25')
    add(t='plset', h=A('4015AE'), p=[[X(E0) + c0, YBB], [X(E1) - c1, YBB]], layer='диам25')
    e0, e1, L = X(E0) + 20, X(E1) - 20, 280
    yk = (YBB + 20 + YTB - 20) / 2
    if B['ends'][0] == 'sk':
        add(t='plset', h=A('4015C1'), p=[[e0 + L, YBB + 20], [e0 + 25, YBB + 20], [e0, YBB + 45], [e0, YTB - 45], [e0 + 25, YTB - 20], [e0 + L, YTB - 20]])
        add(t='spmove', h=A(SPDS['sk'][0]), items=[[1, e0, yk]])
    else:
        add(t='erase', h=[A('4015C1'), A(SPDS['sk'][0])])
    if B['ends'][1] == 'sk':
        add(t='plset', h=A('4069BF'), p=[[e1 - L, YBB + 20], [e1 - 25, YBB + 20], [e1, YBB + 45], [e1, YTB - 45], [e1 - 25, YTB - 20], [e1 - L, YTB - 20]])
        add(t='move', h=[A(SPDS['sk'][1])], d=[e1 - (196562 + D), dY]); add(t='spmove', h=A(SPDS['sk'][1]), items=[[1, e1, yk]])
    else:
        add(t='erase', h=[A('4069BF'), A(SPDS['sk'][1])])
    add(t='move', h=[A(SPDS['sk'][0])] if B['ends'][0] == 'sk' else [], d=[0, dY])
    # ---- доп bars
    barp, notep = [A('4274A8'), A('4274AA')], [A(x) for x in SPDS['pos2']]
    for d in B['dop']:
        y = YTB - 50 if d['top'] else YBB + 50
        hb = barp.pop(0) if barp else clone(A('4274A8'), 'DB')
        add(t='plset', h=hb, p=[[X(d['a']), y], [X(d['b']), y]], layer='диам25')
        hn = notep.pop(0) if notep else clone(A(SPDS['pos2'][0]), 'DN')
        xn = X(d['nx'])
        add(t='spmove', h=hn, items=[[0, xn, 469289 + dY], [1, xn, y]])
        add(t='mcset', h=hn, set={'FirstLine': d['pos'], 'SecondLine': '(ф%d)' % DIA})
    add(t='erase', h=barp + notep)
    # ---- hoop zones per span (lines + chain), ends: axis/free end -> first hoop
    HL = ['4015B6', '40389F', '4038A0', '4038A1', '4038A2', '4038A3', '4038A4', '4038A5', '4038A6', '4038A7', '4038A8', '4038A9',
          '4038AA', '4038AB', '4038AC', '4038AD', '4038AE', '4038AF', '4038B0']
    ZD = ['4033EB', '4033C1', '403439', '403749', '40371D', '403733', '403816', '403810', '403813', '403843', '40383D', '403840',
          '403870', '40386A', '40386D']
    ED = ['40347E', '403446', '403605', '40364D', '40364E', '403681', '403682', '4036B5', '4036B6', '4036E9']
    hl, zd, ed = [A(x) for x in HL], [A(x) for x in ZD], [A(x) for x in ED]
    NH = 0; ZI = []
    ref = B['refs']                       # per span: (left ref, right ref) = axis or free end coordinate
    for i, (a, b) in enumerate(spans):
        segs, lines, cnt = zones_any(a, b); NH += cnt; ZI.append(lines)
        for x in lines:
            add(t='plset', h=hl.pop(0) if hl else clone(A(HL[0]), 'HL'), p=[[X(x), YBB], [X(x), YTB]], layer='диам10')
        for s0, s1, txt in segs:
            hh = zd.pop(0) if zd else clone(A(ZD[0]), 'ZD')
            add(t='dimpts', h=hh, p1=[X(s0), YB, 0], p2=[X(s1), YB, 0], dl=[X(s1), 467342, 0])
            add(t='dimtext', h=hh, s=('%s=%d' % (txt, round(s1 - s0))) if 'х' in txt else '')
            if 'х' not in txt: add(t='dimtx', h=hh, at=[X((s0 + s1) / 2.0), 467342 - 150, 0])
        for kk, (p, q) in enumerate(((ref[i][0], lines[0]), (lines[-1], ref[i][1]))):
            hh = ed.pop(0) if ed else clone(A(ED[0]), 'ED')
            add(t='dimpts', h=hh, p1=[X(q), YB, 0], p2=[X(p), YB, 0], dl=[X(p), 467342, 0])
            add(t='dimtx', h=hh, at=[X(lines[0]) + 34, 467096, 0] if kk == 0 else [X(p) - 19, 466980, 0])
    add(t='erase', h=hl + zd + ed)
    # ---- row 2 (axes chain), total
    r2 = B['row2']
    cp = [A(x) for x in ['401296', '40129A', '40129E', '4012A2', '4012A5']]
    for p, q in zip(r2, r2[1:]):
        hh = cp.pop(0) if cp else clone(A('401296'), 'R2')
        add(t='dimpts', h=hh, p1=[X(p), 466361, 0], p2=[X(q), 466361, 0], dl=[X(q), 466773, 0])
        if q - p < 400: add(t='dimtx', h=hh, at=[X(p) - 190 if p == r2[0] else X(q) + 190, 466830, 0])
    add(t='erase', h=cp)
    add(t='dimpts', h=A('401292'), p1=[X(r2[0]), 466361, 0], p2=[X(r2[-1]), 466361, 0], dl=[X(r2[-1]), 466411, 0])
    tc = (r2[0] + r2[-1]) / 2.0
    if any(abs(x - tc) < 700 for x in r2[1:-1]):
        segs_ = sorted(zip(r2, r2[1:]), key=lambda pq: abs((pq[0] + pq[1]) / 2.0 - tc))
        tc = (segs_[0][0] + segs_[0][1]) / 2.0
    add(t='dimtx', h=A('401292'), at=[X(tc), 466411 + 60, 0])
    # ---- height dims at the left end
    add(t='dimpts', h=A('4015A4'), p1=[X(E0), YT, 0], p2=[X(E0), YB, 0], dl=[174210 + D, YB, 0])
    add(t='dimpts', h=A('4015AD'), p1=[X(E0), YB, 0], p2=[X(E0), YBB, 0], dl=[174745 + D, YBB, 0])
    add(t='dimpts', h=A('401933'), p1=[X(E0), YBB, 0], p2=[X(E0), YTB, 0], dl=[174745 + D, YTB, 0])
    add(t='dimpts', h=A('4015A9'), p1=[X(E0), YTB, 0], p2=[X(E0), YT, 0], dl=[174745 + D, YT, 0])
    add(t='dimtx', h=A('4015A9'), at=[174745 + D - 60, YT + 190, 0])
    add(t='dimtx', h=A('4015AD'), at=[174745 + D - 60, YB - 190, 0])
    add(t='dimtx', h=A('401933'), at=[174745 + D - 60, (YBB + YTB) / 2.0, 0])
    add(t='dimtx', h=A('4015A4'), at=[174210 + D - 60, (YB + YT) / 2.0, 0])
    add(t='moveto', h=A('4038B1'), to=[X((E0 + E1) / 2.0), 470114, 0])
    # ---- splices Н4: plates + dims + combs (top groups B['spT'], bottom groups B['spB'] = [(c1, c2, axis)])
    PL = {'T': [('4038F3', '4038F2')], 'B': [('403948', '403947'), ('4039A0', '40399F')]}
    YSPT = 469559 + min(dY, 150)
    vx = sorted(set([x for ln in [zones_any(a, b)[1] for a, b in spans] for x in ln] + [c for s_ in sup for c in s_] + [x for x, _ in B['axes']] + [E0, E1] + [c for g_ in B['spT'] + B['spB'] for c in g_] + [x for _, x in B['secs']]))
    def freex(p, q, txt):
        w = len(txt) * 0.85 * 125 + 60
        cands = [(p + q) / 2.0 + k * 50 * sg for k in range(0, 60) for sg in (1, -1)]
        for c in cands:
            if all(abs(X(v) - X(c)) > w / 2.0 for v in vx): return X(c)
        return X((p + q) / 2.0)
    def plate(hh, c, y): add(t='plset', h=hh, p=[[X(c) - 140, y - 15], [X(c) - 140, y + 15], [X(c) + 140, y + 15], [X(c) + 140, y - 15]], closed=True)
    cT, cB = A(SPDS['comb'][0]), [A(SPDS['comb'][1]), A(SPDS['comb'][2])]
    extraT = [clone(cT, 'CB') for _ in B['spT'][1:]]
    extraB = [clone(cB[0], 'CB') for _ in B['spB'][2:]]
    used = []
    for j, (c1, c2, ax) in enumerate(B['spT']):
        p1, p2 = (A(PL['T'][0][0]), A(PL['T'][0][1])) if j == 0 else (clone(A('4038F3'), 'PT'), clone(A('4038F2'), 'PT'))
        plate(p1, c1, YTB); plate(p2, c2, YTB)
        d1 = A('4038F1') if j == 0 else clone(A('4038F1'), 'PD'); d2 = A('4038F5') if j == 0 else clone(A('4038F5'), 'PD')
        add(t='dimpts', h=d1, p1=[X(c1), YTB, 0], p2=[X(ax), YT, 0], dl=[X(ax), YSPT, 0])
        add(t='dimpts', h=d2, p1=[X(c2), YTB, 0], p2=[X(c1), YTB, 0], dl=[X(c1), YSPT, 0])
        add(t='dimtx', h=d1, at=[freex(min(c1, ax), max(c1, ax), '%d' % abs(c1 - ax)), YSPT + 60, 0])
        add(t='dimtx', h=d2, at=[freex(c1, c2, '500'), YSPT + 60, 0])
        cb = cT if j == 0 else extraT[j - 1]
        add(t='move', h=[cb], d=[X(c1) - (185182 + D), dY]); used.append(cb)
    if not B['spT']: add(t='erase', h=[A(x) for x in ('4038F3', '4038F2', '4038F1', '4038F5')] + [cT])
    BD = [('403992', '40394A'), ('4039A5', '4039A2')]
    REFB = [183682, 192482]
    for j, (c1, c2, ax) in enumerate(B['spB']):
        if j < 2: p1, p2 = A(PL['B'][j][0]), A(PL['B'][j][1]); h1, h2 = A(BD[j][0]), A(BD[j][1])
        else: p1, p2 = clone(A('403948'), 'PB'), clone(A('403947'), 'PB'); h1, h2 = clone(A('403992'), 'PD'), clone(A('40394A'), 'PD')
        plate(p1, c1, YBB); plate(p2, c2, YBB)
        add(t='dimpts', h=h1, p1=[X(c1), YB, 0], p2=[X(ax), YB, 0], dl=[X(ax), 467665, 0])
        add(t='dimpts', h=h2, p1=[X(c2), YBB, 0], p2=[X(c1), YBB, 0], dl=[X(c1), 467665, 0])
        add(t='dimtx', h=h1, at=[freex(min(c1, ax), max(c1, ax), '%d' % abs(c1 - ax)), 467665 + 60, 0])
        add(t='dimtx', h=h2, at=[freex(c1, c2, '500'), 467665 + 60, 0])
        cb = cB[j] if j < 2 else extraB[j - 2]
        add(t='move', h=[cb], d=[X(c1) - (REFB[min(j, 1)] if j < 2 else REFB[0]) - D, -150]); used.append(cb)
    for j in range(len(B['spB']), 2):
        add(t='erase', h=[A(PL['B'][j][0]), A(PL['B'][j][1]), A(BD[j][0]), A(BD[j][1]), cB[j]])
    for cb in used: add(t='mcset', h=cb, set={'FirstLine': 'Н4'})
    # ---- callouts «1 (ф28)» (one per span, in the 200 zone), step note
    n1 = [A(x) for x in SPDS['n1']]
    for i, lines in enumerate(ZI):
        avoid = [c for g in B['spT'] + B['spB'] for c in g[:2]] + [g[0] - 600 for g in B['spT'] + B['spB']] + [d['nx'] for d in B['dop']] + [x for _, x in B['secs']]
        l1, l2 = (lines[1], lines[2]) if len(lines) >= 4 else (lines[0], lines[-1])
        cand = [l1 + 200 + 100 * k for k in range(max(0, int((l2 - l1 - 400) // 100) + 1))] or [(l1 + l2) / 2.0]
        xb = max(cand, key=lambda c: min([abs(c - a) for a in avoid] + [1e9]))
        x = X(xb)
        hh = n1.pop(0) if n1 else clone(A(SPDS['n1'][0]), 'N1')
        add(t='spmove', h=hh, items=[[0, x, 469238.6 + dY], [1, x, YBB], [2, x, YTB]])
        add(t='mcset', h=hh, set={'SecondLine': '(ф%d)' % DIA})
    add(t='erase', h=n1)
    add(t='move', h=[A(SPDS['step'])], d=[X(E1) - (196582 + D), -150])
    add(t='mcset', h=A(SPDS['step']), set={'FirstLine': 'Шаг хомута', 'SecondLine': 'Х1(ф%d)' % B['hoopd']})
    # ---- section marks
    sp = [A(x) for x in SPDS['sec']]
    for (w, x) in B['secs']:
        hh = sp.pop(0) if sp else clone(A(SPDS['sec'][0]), 'SC')
        add(t='sp_set', h=hh, pts=[[0, X(x), 469793.5 + min(dY, 150)], [1, X(x), 465833.7]]); add(t='mcset', h=hh, set={'Word': w})
    add(t='erase', h=sp)
    # ---- level: analog level mark (lm) re-valued, analog multilayer stack removed
    add(t='erase', h=[A(SPDS['ml'])])
    add(t='move', h=[A(SPDS['lm'])], d=[0, dY])
    add(t='levelval', h=A(SPDS['lm']), old='-0.100', value=B['level'], tag=P.rstrip(':') + '_LM')
    # lift everything above the beam that is not set explicitly (title, ведомость деталей stays)
    return ops, NH, spans, ZI


def text_ops(B, NH):
    SX, P = B['SX'], B['P']; D = SX - 172179.0; A = lambda hh: P + hh
    b, h = B['b'], B['h']
    n = 4 if b > 300 else 3
    s = (b - 100) / (n - 1.0)
    yy = h - 30 - 50
    bot = int(round((2 * s + DIA + B['hoopd']) / 5.0) * 5) if b > 300 else int(round(((n - 1) * s + DIA + B['hoopd']) / 5.0) * 5)
    top = bot + 100; p1 = int(round((yy + DIA + B['hoopd'] - 18) / 5.0) * 5); p2 = p1 + 100
    LX = bot + top + p1 + p2
    sk = yy - 2 * 20 + 20     # Ск1 height between bar axes (as fasad)
    LS = sk + 2 * 10 * DIA
    T = {'406493': str(top), '40648A': str(bot), '40648B': str(p1), '40648D': str(p2), '406499': str(LX),
         '4064A7': str(sk), '4064A8': str(10 * DIA), '4064AB': str(10 * DIA), '4064B0': str(LS)}
    ops = [dict(t='settext', h=A(k), s=v) for k, v in T.items()]
    ops += [dict(t='settext', h=A('4038B1'), s='Ригель ' + B['mark']),
            dict(t='settext', h=A(SPDS['notes']), s=r'\pxi-3.3333,l3.3333,t3.3333;1.	Общие указания см. л. - 1.1\P2.	Данный лист читать '
                 r'совместно с л. КЖ-2.1 ... 2.4\P3.	Стержни, указанные в "Ведомости деталей", должны гнуться механическим способом '
                 'в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня')]
    # oc.py fixes of analog content: node «А» lists only our splice plate, shelf texts lifted off their lines, right column in
    ops += [dict(t='settext', h=A('407B8C'), s='Н4-%%%%C%d' % DIA), dict(t='erase', h=[A('407B8E'), A('407B8F'), A('407B8D')]),
            dict(t='move', h=[A('407B95')], d=[-70, 0]), dict(t='move', h=[A('407BBE')], d=[0, -60]), dict(t='settext', h=A('407BC3'), s='Н4'),
            dict(t='move', h=[A('406499'), A('4064A4'), A('4064B0'), A('4064B9')], d=[-200, 0]),
            dict(t='move', h=[A(SPDS['notes'])], d=[-250, 0])]
    # stamp: the analog «крпкер» block reference is pointed at the scheme stamp Штамп№1 (×0.5 kept), fields re-texted
    to = [203429 + D, 456026]
    ops.append(dict(t='setblock', h=A('40443F'), name='Штамп№1', at=to))
    ops.append(dict(t='settext', h=A(SPDS['no']), s=B['no']))
    ops.append(dict(t='move', h=[A(SPDS['no'])], d=[-106, -226]))
    ops.append(dict(t='settext', h=A(SPDS['name']), s='Ригель %s на отм. %s' % (B['mark'], B['level']) + (' (ч.%d из %d)' % tuple(B['part']) if B['part'][1] > 1 else '')))
    ops.append(dict(t='move', h=[A(SPDS['name'])], d=[0, -164]))
    return ops, dict(LX=LX, LS=LS)


def tables(B, NH, spans, L):
    P = B['P']; A = lambda hh: P + hh
    sp, stl = A(SPDS['spec']), A(SPDS['steel'])
    if B['part'][0] < B['part'][1]:
        return [dict(t='erase', h=[sp, stl])]
    E0, E1 = B['full']; spans = B['spans_full']
    NH = sum(zones_any(a, b)[2] for a, b in spans)
    m = gx.tagmap()
    F, I = '%lu2%pr2', '%lu2%pr0'
    b, h = B['b'], B['h']; n = 4 if b > 300 else 3; nh = 2 if b > 300 else 1
    clear = sum(q - p for p, q in spans)
    ng = B['nspl']
    c0 = c1 = 20
    cells_t = [[2, 2, 'Ригель ' + B['mark']], [6, 0, 'Н4']]
    nums = [[3, 3, B['hoopd'], I], [3, 9, L['LX'], I], [4, 3, 16, I], [4, 9, L['LS'], I], [5, 3, DIA, I], [6, 3, DIA, I], [6, 9, 10 * DIA, I]]
    forms = [[3, 10, '%d*%d' % (NH, nh), I], [3, 11, 'D4*D4*3.1415926/4*0.00785*J4/1000', F], [3, 12, 'L4*K4', F],
             [4, 10, '%d*2' % n, I], [4, 11, 'D5*D5*3.1415926/4*0.00785*J5/1000', F], [4, 12, 'L5*K5', F],
             [5, 10, '%.2f*%d' % ((E1 - E0 - c0 - c1) / 1000.0, 2 * n), F], [5, 11, 'D6*D6*3.1415926/4*0.00785*1', F], [5, 12, 'L6*K6', F],
             [6, 10, '%d*%d*2' % (ng, n), I], [6, 11, 'D7*D7*3.1415926/4*0.00785*J7/1000', F], [6, 12, 'L7*K7', F]]
    ops = []
    nd = len(B['dop'])
    if nd > 1: ops.append({'t': 'trows', 'h': sp, 'mode': 'ins', 'at': 8, 'n': nd - 1, 'from': 7})
    for i, d in enumerate(B['dop']):
        r = 7 + i; R = r + 1
        cells_t += [[r, 0, d['pos']], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L=']]
        nums += [[r, 3, DIA, I], [r, 9, d['b'] - d['a'], I]]
        forms += [[r, 10, '%d' % d['n'], I], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]
    last = 6 + max(nd, 1)          # last item row (0-based) before «Материалы»
    rc = last + 2                  # concrete row
    forms += [[2, 12, 'Sum(M4:M%d)' % (last + 1), F], [rc, 12, '%.2f*%.2f*%.2f' % (b / 1000.0, (h - 200) / 1000.0, clear / 1000.0), F]]
    if ng == 0:     # no splices: the Н4 row is emptied
        nums = [c for c in nums if c[0] != 6]; forms = [c for c in forms if c[0] != 6]
        cells_t = [c for c in cells_t if c[0] != 6] + [[6, k, ''] for k in range(13)]
    ops += [dict(t='tnum', h=sp, cells=nums), dict(t='tset', h=sp, cells=cells_t), dict(t='tformula', h=sp, cells=forms),
            dict(t='tset', h=stl, cells=[[5, 1, '%%%%C%d' % B['hoopd'], ], [6, 0, 'Ригель ' + B['mark']]]),
            dict(t='tformula', h=stl, cells=[[6, 1, 'Table({T:%s}).M4' % m[sp], F], [6, 2, 'Sum(B7:B7)', F],
                 [6, 3, 'TEXT:---'], [6, 4, 'Table({T:%s}).M5' % m[sp], F], [6, 5, 'TEXT:---'], [6, 6, 'TEXT:---'],
                 [6, 7, 'Table({T:%s}).Evaluate(Sum(M6:M%d))' % (m[sp], last + 1), F], [6, 8, 'Sum(D7:H7)', F], [6, 9, 'I7+C7', F]])]
    return ops


if __name__ == '__main__':
    B = json.load(open(sys.argv[1], encoding='utf-8'))
    if '--import' in sys.argv:
        hs = rigx.handles_in(AN0[0], AN0[1], -201072, 426649)
        out = gx.run([dict(t='import', file=SRC, h=hs, base=list(AN0), to=[B['SX'], 455939], pre=B['P'])], 'imp' + B['P'][:-1])
        print('import', [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
    if '--run' in sys.argv:
        ops, NH, spans, ZI = build(B)
        out = gx.run(ops + [dict(t='save')], 'rb' + B['P'][:-1])
        print('geom', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:20], 'NH', NH)
        import sec3
        sops = []
        for j, s_ in enumerate(B['secdefs']):
            sops += sec3.section(s_['w'], [B['SX'] + 13300 + 5600 * j, 462700], '%sS%d_' % (B['P'].rstrip(':'), j), B['b'], B['h'],
                                 s_['nT'], s_['nB'], DIA, B['hoopd'], 4, B['level'])
        tops, L = text_ops(B, NH)
        out = gx.run(sops + tops + [dict(t='save')], 'rs' + B['P'][:-1])
        print('sec+text', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:20])
        out = gx.run(tables(B, NH, spans, L) + ([dict(t='tform', h=B['P'] + SPDS['spec'])] if B['part'][0] == B['part'][1] else []) + [dict(t='save')], 'rt' + B['P'][:-1])
        print('tables', [l[:140] for l in out.splitlines() if 'ERR' in l or 'done' in l or l.startswith('F 2,12')][:12])
