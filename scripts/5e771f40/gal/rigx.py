# Rigel sheet along x (Рм-1/Рм-2/Рм-3) from the analog «Ресторан 6.1 Ригель Рм-1» (A4x3, 1:50), full pipeline:
#   python rigx.py <mark> <sheet no> <sheet x0> <prefix> [--import] [--run]
# Analog entities are addressed by tags <prefix><old handle>. Section 1-1 = clone ×2.5 of the edited 1:20 staging section
# (sec1.py, frame 172179,430000). Tables keep their formulas (inputs as numbers, formulas re-written).
import gx, json, sys, os
from rg import zones
from brk import breaks

SRC = gx.S + r'\an\a61.dwg'
AN0 = (-232572.0, 411799.0)                       # analog frame min
BEAMS = {
    'Рм-1': dict(cols=[(-125, 375), (6550, 7050), (13000, 13500), (19675, 20175)]),
    'Рм-2': dict(cols=[(-125, 475), (6500, 7100), (12950, 13550), (19575, 20175)]),
    'Рм-3': dict(cols=[(-125, 475), (6500, 7100), (12950, 13550), (19575, 20175)]),
}
AX = [0, 6800, 13250, 20050]
END0, END1 = -125, 20175
YT, YB, YTB, YBB = 468700.0, 468150.0, 468670.0, 468200.0
SPDS = dict(ax=['401290', '401291', '401295', '401299', '40129D', '4012A1'],
            brk=['40159D', '40159E', '4018B8', '4018B9', '4018BB', '4018BC', '4018BE', '4018BF', '4018C1', '4018C2', '4018C4', '4018C5'],
            pos2=['4274A9', '4274AB'], comb=['4038F4', '403949', '4039A1'], n1=['4015B1', '40671E', '40671F', '406720'],
            sk=['4015C2', '4069C0'], step='414D1E', sec=['4015BF', '40F7E4', '40F7E6', '4015C0', '40F7E5', '4274AC', '4274AD'],
            ml='42C86E', lm='4015A3', spec='406488', steel='4064CF', notes='40443D', no='404440', name='404442')


def handles_in(x0, y0, x1, y1):
    hs = []
    for l in open(gx.S + r'\an\list61.txt', encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if l.startswith('L\t'):
            e = [float(v) for v in r[4][1:].split(',')]
            if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5: hs.append(r[2])
        elif l.startswith('N\t'):
            x, y = map(float, r[4].split(','))
            if x0 <= x <= x1 and y0 <= y <= y1: hs.append(r[2])
    return hs + ['407C02']


def build(mark, no, SX, P):
    cols = BEAMS[mark]['cols']
    D = SX - 172179.0
    A = lambda h: P + h
    T1 = 175307.0 + D
    X = lambda x: T1 + x
    ops = []; add = lambda **k: ops.append(k)
    # columns + breaks + axes
    for h, (a, b) in zip(['40159B', '4018B7', '4018BD', '4018C3'], cols):
        add(t='plset', h=A(h), p=[[X(a), 468797], [X(b), 468797], [X(b), 467970], [X(a), 467970]], closed=True)
    add(t='erase', h=[A('4018BA'), A('4018C0')] + [A(h) for h in SPDS['brk']])
    ops.extend(breaks(cols, X, 468797.4, 467970.4, P.rstrip(':')))
    for h, x, v in zip([SPDS['ax'][i] for i in (0, 1, 3, 5)], AX, '1234'):
        add(t='axis', h=A(h), s=[X(x), 468700], e=[X(x), 466361], val=v)
    add(t='erase', h=[A(SPDS['ax'][2]), A(SPDS['ax'][4])])
    # outline, bars, Ск1
    faces = [(cols[i][1], cols[i + 1][0]) for i in range(3)]
    for h, (a, b) in zip(['40159C', '402404', '403897'], faces):
        add(t='plset', h=A(h), p=[[X(b), YB], [X(b), YT], [X(a), YT], [X(a), YB]], closed=True)
    add(t='erase', h=[A('403898'), A('403899')])
    add(t='plset', h=A('4015A8'), p=[[X(END0 + 20), YTB], [X(END1 - 20), YTB]], layer='диам25')
    add(t='plset', h=A('4015AE'), p=[[X(END0 + 20), YBB], [X(END1 - 20), YBB]], layer='диам25')
    L = 250
    e0, e1 = X(END0) + 20, X(END1) - 20
    add(t='plset', h=A('4015C1'), p=[[e0 + L, YBB + 20], [e0 + 25, YBB + 20], [e0, YBB + 45], [e0, YTB - 45], [e0 + 25, YTB - 20], [e0 + L, YTB - 20]])
    add(t='plset', h=A('4069BF'), p=[[e1 - L, YBB + 20], [e1 - 25, YBB + 20], [e1, YBB + 45], [e1, YTB - 45], [e1 - 25, YTB - 20], [e1 - L, YTB - 20]])
    add(t='erase', h=[A('4274A8'), A('4274AA')] + [A(h) for h in SPDS['pos2']])
    # hoop zones
    HL = ['4015B6', '40389F', '4038A0', '4038A1', '4038A2', '4038A3', '4038A4', '4038A5', '4038A6', '4038A7', '4038A8', '4038A9',
          '4038AA', '4038AB', '4038AC', '4038AD', '4038AE', '4038AF', '4038B0']
    ZD = ['4033EB', '4033C1', '403439', '403749', '40371D', '403733', '403816', '403810', '403813', '403843', '40383D', '403840',
          '403870', '40386A', '40386D']
    ED = ['40347E', '403446', '403605', '40364D', '40364E', '403681', '403682', '4036B5', '4036B6', '4036E9']
    hl, zd, ed = list(HL), list(ZD), list(ED)
    NH = 0; ZI = []
    for i, (a, b) in enumerate(faces):
        segs, lines, cnt = zones(a, b); NH += cnt; ZI.append(lines)
        for x in lines:
            add(t='plset', h=A(hl.pop(0)), p=[[X(x), YBB], [X(x), YTB]], layer='диам10')
        for s0, s1, txt in segs:
            h = A(zd.pop(0))
            add(t='dimpts', h=h, p1=[X(s0), YB, 0], p2=[X(s1), YB, 0], dl=[X(s1), 467342, 0])
            add(t='dimtext', h=h, s=txt if 'х' in txt else '')
        for k, (p, q) in enumerate(((AX[i], lines[0]), (lines[-1], AX[i + 1]))):
            hh = A(ed.pop(0))
            add(t='dimpts', h=hh, p1=[X(q), YB, 0], p2=[X(p), YB, 0], dl=[X(p), 467342, 0])
            add(t='dimtx', h=hh, at=[X(lines[0]) + 34, 467096, 0] if k == 0 else [X(p) - 19, 466980, 0])
    add(t='erase', h=[A(h) for h in hl + zd + ed])
    # axis chain, total, heights
    for h, (p, q) in zip(['401296', '40129A', '40129E'], zip(AX, AX[1:])):
        add(t='dimpts', h=A(h), p1=[X(p), 466361, 0], p2=[X(q), 466361, 0], dl=[X(q), 466773, 0])
    add(t='erase', h=[A('4012A2'), A('4012A5')])
    add(t='dimpts', h=A('401292'), p1=[X(AX[0]), 466361, 0], p2=[X(AX[-1]), 466361, 0], dl=[X(AX[-1]), 466411, 0])
    add(t='dimpts', h=A('4015A4'), p1=[X(END0), YT, 0], p2=[X(END0), YB, 0], dl=[174210 + D, YB, 0])
    add(t='dimpts', h=A('4015AD'), p1=[X(END0), YB, 0], p2=[X(END0) + 20, YBB, 0], dl=[174745 + D, YBB, 0])
    add(t='dimpts', h=A('401933'), p1=[X(END0) + 20, YBB, 0], p2=[X(END0) + 20, YTB, 0], dl=[174745 + D, YTB, 0])
    # splices Н3
    mid = (AX[1] + AX[2]) / 2.0
    TOPC = [mid - 250, mid + 250]
    BOT = [[AX[1] + 500, AX[1] + 1000], [AX[2] + 500, AX[2] + 1000]]
    def plate(h, c, y): add(t='plset', h=A(h), p=[[X(c) - 125, y - 15], [X(c) - 125, y + 15], [X(c) + 125, y + 15], [X(c) + 125, y - 15]], closed=True)
    plate('4038F3', TOPC[0], YTB); plate('4038F2', TOPC[1], YTB)
    plate('403948', BOT[0][0], YBB); plate('403947', BOT[0][1], YBB)
    plate('4039A0', BOT[1][0], YBB); plate('40399F', BOT[1][1], YBB)
    add(t='dimpts', h=A('4038F1'), p1=[X(TOPC[0]), YTB, 0], p2=[X(AX[1]), YT, 0], dl=[X(AX[1]), 469559, 0])
    add(t='dimpts', h=A('4038F5'), p1=[X(TOPC[1]), YTB, 0], p2=[X(TOPC[0]), YTB, 0], dl=[X(TOPC[0]), 469559, 0])
    for (h1, h2), (c1, c2), ax in zip([('403992', '40394A'), ('4039A5', '4039A2')], BOT, AX[1:3]):
        add(t='dimpts', h=A(h1), p1=[X(c1), YB, 0], p2=[X(ax), YB, 0], dl=[X(ax), 467665, 0])
        add(t='dimpts', h=A(h2), p1=[X(c2), YBB, 0], p2=[X(c1), YBB, 0], dl=[X(c1), 467665, 0])
    # analog positions of the combs (sheet 6.1 frame) -> ours
    add(t='move', h=[A(SPDS['comb'][0])], d=[X(TOPC[0]) - (185182 + D), 0])
    add(t='move', h=[A(SPDS['comb'][1])], d=[X(BOT[0][0]) - (183682 + D), -150])
    add(t='move', h=[A(SPDS['comb'][2])], d=[X(BOT[1][0]) - (192482 + D), -150])
    for h in SPDS['comb']: add(t='mcset', h=A(h), set={'FirstLine': 'Н3'})
    # callouts «1 (ф25)», Ск1, step note
    cx = [ZI[0][1] + 300, ZI[1][2] - 300, ZI[2][1] + 300]
    for h, x in zip(SPDS['n1'][:3], cx):
        add(t='spmove', h=A(h), items=[[0, X(x), 469238.6], [1, X(x), YBB], [2, X(x), YTB]])
        add(t='mcset', h=A(h), set={'SecondLine': '(ф25)'})
    add(t='erase', h=[A(SPDS['n1'][3])])
    yk = (YBB + 20 + YTB - 20) / 2
    add(t='spmove', h=A(SPDS['sk'][0]), items=[[1, e0, yk]])
    add(t='move', h=[A(SPDS['sk'][1])], d=[e1 - (196562 + D), 0]); add(t='spmove', h=A(SPDS['sk'][1]), items=[[1, e1, yk]])
    add(t='move', h=[A(SPDS['step'])], d=[X(END1) - (196582 + D), -150])
    add(t='mcset', h=A(SPDS['step']), set={'FirstLine': 'Шаг хомута', 'SecondLine': 'Х1(ф10)'})
    sx = [ZI[0][2] - 700, ZI[1][2] + 400, ZI[2][2] - 700]
    for h, x in zip(SPDS['sec'][:3], sx):
        add(t='sp_set', h=A(h), pts=[[0, X(x), 469793.5], [1, X(x), 465833.7]])
        add(t='mcset', h=A(h), set={'Word': '1'})
    add(t='erase', h=[A(h) for h in SPDS['sec'][3:]])
    # levels: −0.100 (analog) + one-line multilayer +3.950 (analog 6.6)
    add(t='erase', h=[A(SPDS['ml'])])
    tg = P.rstrip(':') + '_ML'
    add(t='clone', h='B6:42FC64', base=[267758, 468285], to=[173261 + D, 468700], tag=tg)
    add(t='levelval', h=tg, old='+4.395', value='+3.950', tag=tg)
    return ops, NH, cols


def section_ops(SX, P):
    st = json.load(open(gx.S + r'\w\sec_stage.json'))
    D = SX - 172179.0
    B = [173965, 431659]; T = [185300 + D, 462700]
    pre = P.rstrip(':') + 'S_'
    ops = [dict(t='clone', h=h, base=B, to=T, s=2.5, tag=pre + h) for h in st['hs']]
    ops.append(dict(t='dimset', h=[pre + h for h in st['hs'] if st['types'][h] == 'DIMENSION'], lfac=0.4, dscale=50))
    for h in st['hs']:
        if st['types'][h].startswith('SPDS') and st['types'][h] != 'SPDSBREAK':
            ops.append(dict(t='mcset', h=pre + h, set={'Scale': 50}))
    return ops


def table_ops(mark, no, P, NH, cols):
    A = lambda h: P + h
    sp, stl = A(SPDS['spec']), A(SPDS['steel'])
    clear = (END1 - END0) - sum(b - a for a, b in cols)
    F, I = '%lu2%pr2', '%lu2%pr0'
    m = gx.tagmap()
    ops = [dict(t='tnum', h=sp, cells=[[3, 3, 10, I], [3, 9, 1720, I], [4, 3, 16, I], [4, 9, 970, I], [5, 3, 25, I], [6, 3, 25, I], [6, 9, 250, I]]),
           dict(t='tset', h=sp, cells=[[2, 2, 'Ригель ' + mark], [6, 0, 'Н3']]),
           dict(t='tformula', h=sp, cells=[[3, 10, '%d*2' % NH, I], [3, 11, 'D4*D4*3.1415926/4*0.00785*J4/1000', F], [3, 12, 'L4*K4', F],
                [4, 10, '4*2', I], [4, 11, 'D5*D5*3.1415926/4*0.00785*J5/1000', F], [4, 12, 'L5*K5', F],
                [5, 10, '%.2f*8' % ((END1 - END0 - 40) / 1000.0), F], [5, 11, 'D6*D6*3.1415926/4*0.00785*1', F], [5, 12, 'L6*K6', F],
                [6, 10, '3*4*2', I], [6, 11, 'D7*D7*3.1415926/4*0.00785*J7/1000', F], [6, 12, 'L7*K7', F],
                [2, 12, 'Sum(M4:M8)', F], [9, 12, '0.45*0.30*%.2f' % (clear / 1000.0), F]]),
           dict(t='tset', h=stl, cells=[[5, 1, '%%C10'], [6, 0, 'Ригель ' + mark]]),
           dict(t='tformula', h=stl, cells=[[6, 1, 'Table({T:%s}).M4' % m[sp], F], [6, 2, 'Sum(B7:B7)', F], [6, 4, 'Table({T:%s}).M5' % m[sp], F],
                [6, 5, 'TEXT:---'], [6, 6, 'Table({T:%s}).Evaluate(Sum(M6:M7))' % m[sp], F], [6, 8, 'Sum(D7:H7)', F], [6, 9, 'I7+C7', F]]),
           dict(t='evalf')]
    return ops


def text_ops(mark, no, P):
    A = lambda h: P + h
    # Ведомость деталей: Х1 Ø10 (по осям проволоки: низ 270, верх 370 с крюком, стойки 490 / 590), Ск1 Ø16 250+470+250
    T = {'406493': '370', '40648A': '270', '40648B': '490', '40648D': '590', '406499': '1720',
         '4064A7': '470', '4064A8': '250', '4064AB': '250', '4064B0': '970'}
    ops = [dict(t='settext', h=A(h), s=v) for h, v in T.items()]
    ops += [dict(t='settext', h=A(SPDS['no']), s=no), dict(t='settext', h=A(SPDS['name']), s='Ригель ' + mark),
            dict(t='settext', h=A('4038B1'), s='Ригель ' + mark),
            dict(t='settext', h=A(SPDS['notes']), s='\\pxi-3.3333,l3.3333,t3.3333;1.\tОбщие указания см. л. - 1.1\\P2.\tДанный лист читать '
                 'совместно с л. КЖ-2.1 ... 2.7\\P3.\tСтержни, указанные в "Ведомости деталей", должны гнуться механическим способом '
                 'в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня')]
    return ops


if __name__ == '__main__':
    mark, no, SX, P = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    if '--import' in sys.argv:
        hs = handles_in(AN0[0], AN0[1], -201072, 426649)
        out = gx.run([dict(t='import', file=SRC, h=hs, base=list(AN0), to=[SX, 455939], pre=P)], 'imp' + P[:-1])
        print('import', [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
    if '--run' in sys.argv:
        ops, NH, cols = build(mark, no, SX, P)
        ops += section_ops(SX, P) if '--nosec' not in sys.argv else []
        ops += text_ops(mark, no, P)
        out = gx.run(ops, 'rx' + P[:-1])
        print('geom', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:12])
        out = gx.run(table_ops(mark, no, P, NH, cols) + [dict(t='tform', h=P + SPDS['spec']), dict(t='save')], 'rt' + P[:-1])
        print('tables', [l[:120] for l in out.splitlines() if 'ERR' in l or 'done' in l or l.startswith('F 2,12')][:12], 'NH', NH)
