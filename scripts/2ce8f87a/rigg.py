# Generic rigel sheet from the analog «Ресторан 6.1» kit (A4x3, 1:50) for beams with arbitrary supports, free ends,
# доп bars and several sections (Рм-4, Рм-5). python rigg.py Рм-4|Рм-5 --import --run
import gx, json, sys
from rg import zones
from brk import breaks
import rigx
from rigx import SPDS, AN0, SRC
YT, YB, YTB, YBB = rigx.YT, rigx.YB, rigx.YTB, rigx.YBB

BEAMS = {
    # Y-beams along axes 1-4: x = building y (mm). hoops = zone boundary lines; chain = hoop row [p, q, text, side]
    'Рм-4': dict(no='6.4', SX=298179.0, P='A4:', E=(-3275, 125),
                 sup=[(-1250, -750), (-125, 125)], axes=[(0, 'А/1')], row2=[-3275, -1250, -750, -125, 125], row3=[-3275, 0, 125],
                 hoops=[-3200, -1300, -700, -200], NH=20 + 6,
                 chain=[(-3275, -3200, '', 'L'), (-3200, -1300, '100х19', None), (-1300, -700, '', None), (-700, -200, '100х5', None), (-200, 0, '', 'R')],
                 n1x=[-450], dop=[dict(pos='2', top=True, a=-2250, b=-250, n=1, nx=-1900)],
                 secs=[('1', -2900, (), ()), ('2', -1600, (2,), ())]),
    'Рм-5': dict(no='6.5', SX=329679.0, P='A5:', E=(23050, 31175),
                 sup=[(23050, 23650), (28550, 29150)], axes=[(22750, 'В'), (28750, 'В/1')],
                 row2=[22750, 23050, 23650, 28550, 29150, 31175], row3=[22750, 28750, 31175],
                 hoops=[23700, 24900, 27300, 28500, 29200, 31100], NH=37 + 20,
                 chain=[(23350, 23700, '', 'L'), (23700, 24900, '100х12', None), (24900, 27300, '200х12', None), (27300, 28500, '100х12', None),
                        (28500, 29200, '', None), (29200, 31100, '100х19', None), (31100, 31175, '', 'R')],
                 n1x=[25500, 30300], dop=[dict(pos='2', top=True, a=27050, b=29650, n=3, nx=27500), dict(pos='3', top=False, a=23070, b=24670, n=1, nx=24400)],
                 secs=[('1', 26200, (), ()), ('2', 28200, (2,), ()), ('3', 23950, (), (3,))]),
}


def zones_any(a, b):
    Lp = b - a - 100
    if Lp >= 1500: return zones(a, b)
    h0, h4 = a + 50, b - 50
    n = int(Lp // 100); r = Lp - 100 * n
    if 0 < r < 100 and n > 0: n -= 1; r += 100
    segs = [(h0, h0 + 100 * n, '100х%d' % n)] + ([(h0 + 100 * n, h4, '%d' % round(r))] if r else [])
    return segs, [h0, h0 + 100 * n, h4] if r else [h0, h4], n + 1 + (1 if r else 0)


def build(mark):
    B = BEAMS[mark]; SX, P = B['SX'], B['P']; E0, E1 = B['E']
    D = SX - 172179.0
    A = lambda h: P + h
    X = lambda x: 175182.0 + D + (x - E0)               # beam end E0 at the analog end position
    ops = []; add = lambda **k: ops.append(k)
    k = [0]
    def tag(s): k[0] += 1; return '%s_%s%d' % (P.rstrip(':'), s, k[0])
    def clone(h, s): t = tag(s); add(t='clone', h=h, tag=t); return t
    sup = B['sup']
    # ---- supports: column rects (pool + clones), breaks
    pool = [A(h) for h in ['40159B', '4018B7', '4018BA', '4018BD', '4018C0', '4018C3']]
    for (a, b) in sup:
        h = pool.pop(0)
        add(t='plset', h=h, p=[[X(a), 468797], [X(b), 468797], [X(b), 467970], [X(a), 467970]], closed=True)
    add(t='erase', h=pool + [A(h) for h in SPDS['brk']])
    ops.extend(breaks(sup, X, 468797.4, 467970.4, P.rstrip(':')))
    # ---- axes
    axp = [A(h) for h in SPDS['ax']]
    for (x, v) in B['axes']:
        add(t='axis', h=axp.pop(0), s=[X(x), 468700], e=[X(x), 466361], val=v)
    add(t='erase', h=axp)
    # ---- spans (beam rects between faces / free ends)
    faces = [E0] + [c for s in sup for c in s] + [E1]
    spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
    rp = [A(h) for h in ['40159C', '402404', '403897', '403898', '403899']]
    for (a, b) in spans:
        add(t='plset', h=rp.pop(0), p=[[X(b), YB], [X(b), YT], [X(a), YT], [X(a), YB]], closed=True)
    add(t='erase', h=rp)
    # ---- main bars, Ск1
    add(t='plset', h=A('4015A8'), p=[[X(E0 + 20), YTB], [X(E1 - 20), YTB]], layer='диам25')
    add(t='plset', h=A('4015AE'), p=[[X(E0 + 20), YBB], [X(E1 - 20), YBB]], layer='диам25')
    e0, e1, L = X(E0) + 20, X(E1) - 20, 250
    add(t='plset', h=A('4015C1'), p=[[e0 + L, YBB + 20], [e0 + 25, YBB + 20], [e0, YBB + 45], [e0, YTB - 45], [e0 + 25, YTB - 20], [e0 + L, YTB - 20]])
    add(t='plset', h=A('4069BF'), p=[[e1 - L, YBB + 20], [e1 - 25, YBB + 20], [e1, YBB + 45], [e1, YTB - 45], [e1 - 25, YTB - 20], [e1 - L, YTB - 20]])
    yk = (YBB + 20 + YTB - 20) / 2
    add(t='spmove', h=A(SPDS['sk'][0]), items=[[1, e0, yk]])
    add(t='move', h=[A(SPDS['sk'][1])], d=[e1 - (196562 + D), 0]); add(t='spmove', h=A(SPDS['sk'][1]), items=[[1, e1, yk]])
    # ---- доп bars (analog pos 2 bars / notes as prototypes)
    barp, notep = [A('4274A8'), A('4274AA')], [A(h) for h in SPDS['pos2']]
    for i, d in enumerate(B['dop']):
        y = YTB - 50 if d['top'] else YBB + 50
        hb = barp.pop(0) if barp else clone(A('4274A8'), 'DB')
        add(t='plset', h=hb, p=[[X(d['a']), y], [X(d['b']), y]], layer='диам25')
        hn = notep.pop(0) if notep else clone(A(SPDS['pos2'][0]), 'DN')
        xn = X(d['nx'])
        add(t='spmove', h=hn, items=[[0, xn, 469289], [1, xn, y]])
        add(t='mcset', h=hn, set={'FirstLine': d['pos'], 'SecondLine': '(ф25)'})
    add(t='erase', h=barp + notep)
    # ---- hoop zones: lines + chain dims (refs = support centres / free ends)
    HL = ['4015B6', '40389F', '4038A0', '4038A1', '4038A2', '4038A3', '4038A4', '4038A5', '4038A6', '4038A7', '4038A8', '4038A9',
          '4038AA', '4038AB', '4038AC', '4038AD', '4038AE', '4038AF', '4038B0']
    ZD = ['4033EB', '4033C1', '403439', '403749', '40371D', '403733', '403816', '403810', '403813', '403843', '40383D', '403840',
          '403870', '40386A', '40386D']
    ED = ['40347E', '403446', '403605', '40364D', '40364E', '403681', '403682', '4036B5', '4036B6', '4036E9']
    hl, zd, ed = [A(h) for h in HL], [A(h) for h in ZD], [A(h) for h in ED]
    for x in B['hoops']: add(t='plset', h=hl.pop(0), p=[[X(x), YBB], [X(x), YTB]], layer='диам10')
    for (p, q, txt, side) in B['chain']:
        h = zd.pop(0) if 'х' in txt else ed.pop(0)
        add(t='dimpts', h=h, p1=[X(p), YB, 0], p2=[X(q), YB, 0], dl=[X(q), 467342, 0])
        add(t='dimtext', h=h, s=txt)
        add(t='dimtx', h=h, at=[X(p) - 190 if side == 'L' else X(q) + 190 if side == 'R' else X((p + q) / 2.0), 467400, 0])
    NH = B['NH']
    add(t='erase', h=hl + zd + ed)
    # ---- row 2: faces chain; row 3: axes chain
    r2 = B['row2']
    cp = [A(h) for h in ['401296', '40129A', '40129E', '4012A2', '4012A5']]
    for p, q in zip(r2, r2[1:]):
        h = cp.pop(0)
        add(t='dimpts', h=h, p1=[X(p), 466361, 0], p2=[X(q), 466361, 0], dl=[X(q), 466773, 0])
        if q - p < 400: add(t='dimtx', h=h, at=[X(p) - 190 if p == r2[0] else X(q) + 190, 466830, 0])
    add(t='erase', h=cp)
    r3 = B['row3']
    for i, (p, q) in enumerate(zip(r3, r3[1:])):
        h = A('401292') if i == 0 else clone(A('401292'), 'R3')
        add(t='dimpts', h=h, p1=[X(p), 466361, 0], p2=[X(q), 466361, 0], dl=[X(q), 466411, 0])
        if q - p < 400: add(t='dimtx', h=h, at=[X(q) + 190, 466470, 0])
    add(t='dimpts', h=A('4015A4'), p1=[X(E0), YT, 0], p2=[X(E0), YB, 0], dl=[174210 + D, YB, 0])
    add(t='dimpts', h=A('4015AD'), p1=[X(E0), YB, 0], p2=[X(E0) + 20, YBB, 0], dl=[174745 + D, YBB, 0])
    add(t='dimpts', h=A('401933'), p1=[X(E0) + 20, YBB, 0], p2=[X(E0) + 20, YTB, 0], dl=[174745 + D, YTB, 0])
    # ---- no splices: plates, their dims and combs, node «А» + «а-а» removed (as analog 6.6)
    add(t='erase', h=[A(h) for h in ['4038F2', '4038F3', '403947', '403948', '40399F', '4039A0', '4038F1', '4038F5', '403992', '40394A', '4039A5', '4039A2']]
        + [A(h) for h in SPDS['comb']])
    add(t='eraseregion', win=[SX + 1000, 461900, SX + 8700, 465450])
    # ---- callouts «1 (ф25)» in the long spans, step note
    n1 = [A(h) for h in SPDS['n1']]
    for xx in B['n1x']:
        x = X(xx); h = n1.pop(0)
        add(t='spmove', h=h, items=[[0, x, 469238.6], [1, x, YBB], [2, x, YTB]])
        add(t='mcset', h=h, set={'SecondLine': '(ф25)'})
    add(t='erase', h=n1)
    add(t='move', h=[A(SPDS['step'])], d=[X(E1) - (196582 + D), -150])
    add(t='mcset', h=A(SPDS['step']), set={'FirstLine': 'Шаг хомута', 'SecondLine': 'Х1(ф10)'})
    # ---- section marks
    sp = [A(h) for h in SPDS['sec']]
    for (w, x, _, _) in B['secs']:
        h = sp.pop(0)
        add(t='sp_set', h=h, pts=[[0, X(x), 469793.5], [1, X(x), 465833.7]]); add(t='mcset', h=h, set={'Word': w})
    add(t='erase', h=sp)
    # ---- levels
    add(t='erase', h=[A(SPDS['ml'])])
    tg = P.rstrip(':') + '_ML'
    add(t='clone', h='B6:42FC64', base=[267758, 468285], to=[173261 + D, 468700], tag=tg)
    add(t='levelval', h=tg, old='+4.395', value='+3.950', tag=tg)
    return ops, NH, spans


def sections(mark):
    B = BEAMS[mark]; SX, P = B['SX'], B['P']; D = SX - 172179.0
    st = json.load(open(gx.S + r'\w\sec_stage.json'))
    import sec1
    mm = gx.tagmap()
    ops = []
    for j, (w, x, topx, botx) in enumerate(B['secs']):
        T = [SX + 8000 + 5000 * j, 463100]
        pre = '%sS%d_' % (P.rstrip(':'), j)
        f = lambda xx, yy: [T[0] + (xx - 173965) * 2.5, T[1] + (yy - 431659) * 2.5]
        ops += [dict(t='clone', h=h, base=[173965, 431659], to=T, s=2.5, tag=pre + h) for h in st['hs']]
        ops.append(dict(t='dimset', h=[pre + h for h in st['hs'] if st['types'][h] == 'DIMENSION'], lfac=0.4, dscale=50))
        for h in st['hs']:
            if st['types'][h].startswith('SPDS') and st['types'][h] != 'SPDSBREAK': ops.append(dict(t='mcset', h=pre + h, set={'Scale': 50}))
        ops.append(dict(t='settext', h=pre + '2CC85B' if False else pre + [h for h in st['hs'] if st['types'][h] == 'MTEXT'][0], s='Разрез %s - %s' % (w, w)))
        # extra bars of the доп positions
        for d in B['dop']:
            if d['pos'] not in [str(q) for q in topx + botx]: continue
            bx = [173965] if d['n'] == 1 else [(sec1.BX[i] + sec1.BX[i + 1]) / 2 for i in range(3)]
            y = sec1.YTOP if d['top'] else sec1.YBOT
            src = pre + mm['S1:404468' if d['top'] else 'S1:40444B']
            for i, xx in enumerate(bx):
                t = '%sD%s_%d' % (pre, d['pos'], i)
                ops.append(dict(t='clone', h=src, tag=t)); ops.append(dict(t='insat', h=t, at=f(xx, y)))
            # comb callout for the доп bars, to the left of the section
            cs = pre + ('2CB019' if d['top'] else '2CB01A')
            t = '%sDC%s' % (pre, d['pos'])
            ops.append(dict(t='clone', h=cs, tag=t))
            ys = 432240 if d['top'] else 431183
            ends = [[xx - 140, ys] for xx in bx]
            ops.append(dict(t='combsegs', h=t, segs=[[f(xx, y + (-1 if d['top'] else -2)), f(*e)] for xx, e in zip(bx, ends)],
                            start=f(min(e[0] for e in ends) - 260, ys), end=f(max(e[0] for e in ends), ys)))
            ops.append(dict(t='mcset', h=t, set={'FirstLine': d['pos'], 'SecondLine': '(ф25)'}))
    return ops


def tables(mark, NH, spans):
    B = BEAMS[mark]; P = B['P']; E0, E1 = B['E']
    A = lambda h: P + h
    sp, stl = A(SPDS['spec']), A(SPDS['steel'])
    m = gx.tagmap()
    F, I = '%lu2%pr2', '%lu2%pr0'
    clear = sum(b - a for a, b in spans)
    cells_t = [[2, 2, 'Ригель ' + mark]]
    nums = [[3, 3, 10, I], [3, 9, 1720, I], [4, 3, 16, I], [4, 9, 970, I], [5, 3, 25, I]]
    forms = [[3, 10, '%d*2' % NH, I], [3, 11, 'D4*D4*3.1415926/4*0.00785*J4/1000', F], [3, 12, 'L4*K4', F],
             [4, 10, '4*2', I], [4, 11, 'D5*D5*3.1415926/4*0.00785*J5/1000', F], [4, 12, 'L5*K5', F],
             [5, 10, '%.2f*8' % ((E1 - E0 - 40) / 1000.0), F], [5, 11, 'D6*D6*3.1415926/4*0.00785*1', F], [5, 12, 'L6*K6', F],
             [2, 12, 'Sum(M4:M8)', F], [9, 12, '0.45*0.30*%.2f' % (clear / 1000.0), F]]
    for i, d in enumerate(B['dop']):
        r = 6 + i; R = r + 1
        cells_t += [[r, 0, d['pos']], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L=']]
        nums += [[r, 3, 25, I], [r, 9, d['b'] - d['a'], I]]
        forms += [[r, 10, '%d' % d['n'], I], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]
    ops = [dict(t='tnum', h=sp, cells=nums), dict(t='tset', h=sp, cells=cells_t), dict(t='tformula', h=sp, cells=forms),
           dict(t='tset', h=stl, cells=[[5, 1, '%%C10'], [6, 0, 'Ригель ' + mark]]),
           dict(t='tformula', h=stl, cells=[[6, 1, 'Table({T:%s}).M4' % m[sp], F], [6, 2, 'Sum(B7:B7)', F], [6, 4, 'Table({T:%s}).M5' % m[sp], F],
                [6, 5, 'TEXT:---'], [6, 6, 'Table({T:%s}).Evaluate(Sum(M6:M8))' % m[sp], F], [6, 8, 'Sum(D7:H7)', F], [6, 9, 'I7+C7', F]])]

    return ops


if __name__ == '__main__':
    mark = sys.argv[1]; B = BEAMS[mark]
    if '--import' in sys.argv:
        hs = rigx.handles_in(AN0[0], AN0[1], -201072, 426649)
        out = gx.run([dict(t='import', file=SRC, h=hs, base=list(AN0), to=[B['SX'], 455939], pre=B['P'])], 'imp' + B['P'][:-1])
        print('import', [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
    if '--run' in sys.argv:
        ops, NH, spans = build(mark)
        ops += sections(mark) + rigx.text_ops(mark, B['no'], B['P'])
        out = gx.run(ops, 'rg' + B['P'][:-1])
        print('geom', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:12])
        out = gx.run(tables(mark, NH, spans) + [dict(t='tform', h=B['P'] + SPDS['spec']), dict(t='save')], 'rgt' + B['P'][:-1])
        print('tables', [l[:120] for l in out.splitlines() if 'ERR' in l or 'done' in l or l.startswith('F 2,12')][:12], 'NH', NH)
