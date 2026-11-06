# БДМ Блок 3 — rigel sheet from the analog «Ресторан 6.1 Ригель Рм-1» (A4x3, 1:50), generalised from Galaxy rigx/rigg:
# up to 5 spans per sheet, any section height (everything above the beam is lifted by dY = h - 550), Ø28 main bars,
# free ends with Ск1 or a break (beam continues on the next sheet), доп bars, splices Н4 (Ø28, L=280).
# Analog entities are addressed by tags <P><old handle>. Coordinates: beam coordinate x (mm) -> sheet X(x).
import gx, json, sys
from rg import zones
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
    for (a, b) in sup:
        hh = pool.pop(0) if pool else clone(A('40159B'), 'COL')
        add(t='plset', h=hh, p=[[X(a), COLT + dY], [X(b), COLT + dY], [X(b), COLB], [X(a), COLB]], closed=True)
    add(t='erase', h=pool + [A(x) for x in SPDS['brk']])
    ops.extend(breaks(sup, X, COLT + dY + 0.4, COLB + 0.4, P.rstrip(':')))
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
        segs, lines, cnt = zones(a, b); NH += cnt; ZI.append(lines)
        for x in lines:
            add(t='plset', h=hl.pop(0) if hl else clone(A(HL[0]), 'HL'), p=[[X(x), YBB], [X(x), YTB]], layer='диам10')
        for s0, s1, txt in segs:
            hh = zd.pop(0) if zd else clone(A(ZD[0]), 'ZD')
            add(t='dimpts', h=hh, p1=[X(s0), YB, 0], p2=[X(s1), YB, 0], dl=[X(s1), 467342, 0])
            add(t='dimtext', h=hh, s=txt if 'х' in txt else '')
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
    # ---- height dims at the left end
    add(t='dimpts', h=A('4015A4'), p1=[X(E0), YT, 0], p2=[X(E0), YB, 0], dl=[174210 + D, YB, 0])
    add(t='dimpts', h=A('4015AD'), p1=[X(E0), YB, 0], p2=[X(E0), YBB, 0], dl=[174745 + D, YBB, 0])
    add(t='dimpts', h=A('401933'), p1=[X(E0), YBB, 0], p2=[X(E0), YTB, 0], dl=[174745 + D, YTB, 0])
    # ---- splices Н4: plates + dims + combs (top groups B['spT'], bottom groups B['spB'] = [(c1, c2, axis)])
    PL = {'T': [('4038F3', '4038F2')], 'B': [('403948', '403947'), ('4039A0', '40399F')]}
    def plate(hh, c, y): add(t='plset', h=hh, p=[[X(c) - 140, y - 15], [X(c) - 140, y + 15], [X(c) + 140, y + 15], [X(c) + 140, y - 15]], closed=True)
    cT, cB = A(SPDS['comb'][0]), [A(SPDS['comb'][1]), A(SPDS['comb'][2])]
    extraT = [clone(cT, 'CB') for _ in B['spT'][1:]]
    extraB = [clone(cB[0], 'CB') for _ in B['spB'][2:]]
    used = []
    for j, (c1, c2, ax) in enumerate(B['spT']):
        p1, p2 = (A(PL['T'][0][0]), A(PL['T'][0][1])) if j == 0 else (clone(A('4038F3'), 'PT'), clone(A('4038F2'), 'PT'))
        plate(p1, c1, YTB); plate(p2, c2, YTB)
        d1 = A('4038F1') if j == 0 else clone(A('4038F1'), 'PD'); d2 = A('4038F5') if j == 0 else clone(A('4038F5'), 'PD')
        add(t='dimpts', h=d1, p1=[X(c1), YTB, 0], p2=[X(ax), YT, 0], dl=[X(ax), 469559 + dY, 0])
        add(t='dimpts', h=d2, p1=[X(c2), YTB, 0], p2=[X(c1), YTB, 0], dl=[X(c1), 469559 + dY, 0])
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
        cb = cB[j] if j < 2 else extraB[j - 2]
        add(t='move', h=[cb], d=[X(c1) - (REFB[min(j, 1)] if j < 2 else REFB[0]) - D, -150]); used.append(cb)
    for j in range(len(B['spB']), 2):
        add(t='erase', h=[A(PL['B'][j][0]), A(PL['B'][j][1]), A(BD[j][0]), A(BD[j][1]), cB[j]])
    for cb in used: add(t='mcset', h=cb, set={'FirstLine': 'Н4'})
    # ---- callouts «1 (ф28)» (one per span, in the 200 zone), step note
    n1 = [A(x) for x in SPDS['n1']]
    for i, lines in enumerate(ZI):
        x = X((lines[1] + lines[2]) / 2.0 + (300 if i % 2 == 0 else -300))
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
        add(t='sp_set', h=hh, pts=[[0, X(x), 469793.5 + dY], [1, X(x), 465833.7]]); add(t='mcset', h=hh, set={'Word': w})
    add(t='erase', h=sp)
    # ---- level: analog level mark (lm) re-valued, analog multilayer stack removed
    add(t='erase', h=[A(SPDS['ml'])])
    add(t='move', h=[A(SPDS['lm'])], d=[0, dY])
    add(t='levelval', h=A(SPDS['lm']), old='-0.100', value=B['level'], tag=P.rstrip(':') + '_LM')
    # lift everything above the beam that is not set explicitly (title, ведомость деталей stays)
    add(t='move', h=[A('4038B1')], d=[0, dY])
    return ops, NH, spans, ZI


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
