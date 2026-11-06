"""Фм-1 reinforcement schemes in the АБК manner (A2, 1:100), plan base copied from sheet 3.1.
python gen3s.py <sheet: 3.2|3.3|3.4|3.6> [run]"""
import sys, os, json, math, ezdxf
import ab, fm2 as F

SHEET = sys.argv[1]
X31, Y0 = -1107303.0, -1749172.0
SLOT = {'3.2': -1047903.0, '3.3': -988503.0, '3.4': -929103.0, '3.6': -869703.0}[SHEET]
DX = SLOT - X31
DY = -4500
TITLE = {'3.2': 'Схема расположения арматуры фундамента Фм-1 по буквенным осям',
         '3.3': 'Схема расположения арматуры фундамента Фм-1 по цифровым осям',
         '3.4': 'Схема расположения хомутов фундаментных балок Фм-1',
         '3.6': 'Выпуски из фундамента Фм-1 в колонны'}[SHEET]

# ---------------- plan base from 3.1
ab.run([{'t': 'list', 'win': [X31, Y0, X31 + 59400, Y0 + 42000]}], 'si')
E = []
for l in open(os.path.join(os.environ['TEMP'], 'ob_log.txt'), encoding='utf-8-sig'):
    f = l.rstrip('\n').split('\t')
    if f[0] == 'L' and len(f) >= 5:
        E.append(dict(t=f[1], h=f[2], lay=f[3], e=list(map(float, f[4][1:].split(','))),
                      pts=[tuple(map(float, q.split(',')[:2])) for q in f[5:] if ',' in q]))
ab.dxf(); D = ezdxf.readfile('w/live.dxf')
AXL = [e for e in E if e['t'] == 'SPDSCONSTRUCTIONLINE']
V = sorted([e for e in AXL if abs(e['pts'][0][0] - e['pts'][1][0]) < 1], key=lambda e: e['pts'][0][0])
H = sorted([e for e in AXL if abs(e['pts'][0][1] - e['pts'][1][1]) < 1], key=lambda e: e['pts'][0][1])
XA, YA = V[0]['pts'][0][0] + DX, H[0]['pts'][0][1] + DY
KEEPM = {3250, 4500, 6000, 12000, 32000}
base = [e['h'] for e in AXL]
base += [e['h'] for e in E if e['t'] == 'DIMENSION' and e['e'][1] > Y0 + 16000 and round(D.entitydb.get(e['h']).get_measurement()) in KEEPM]
base += [e['h'] for e in E if e['t'] == 'LWPOLYLINE' and e['lay'] == 'Размеры' and e['e'][1] > Y0 + 16000]
NOTE_T = next(e['h'] for e in E if e['t'] == 'SPDSNOTEPOSITION')
mts = [e for e in E if e['t'] == 'MTEXT' and e['lay'] == 'Размеры']
TTL = max(mts, key=lambda e: e['e'][3])['h']
DIM_T = next(e['h'] for e in E if e['t'] == 'DIMENSION' and round(D.entitydb.get(e['h']).get_measurement()) == 1000)

O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1},
     {'t': 'eraseregion', 'win': [SLOT - 1, Y0 - 1, SLOT + 59401, Y0 + 42001]},
     {'t': 'clonexf', 'hs': ['a2_31_3E425D', 'a2_31_3E425E', 'a2_31_3E425F', 'a2_31_3E4261'], 'd': [DX, 0], 'pre': 'fr%s_' % SHEET},
     {'t': 'clonexf', 'hs': base, 'd': [DX, DY], 'pre': 'b%s_' % SHEET},
     {'t': 'settext', 'h': 'fr%s_' % SHEET + ab.tagmap()['a2_31_3E4261'], 's': TITLE}, {'t': 'settext', 'h': 'fr%s_' % SHEET + ab.tagmap()['a2_31_3E425F'], 's': SHEET}]
_n = [0]


def tag():
    _n[0] += 1; return 's%s_%d' % (SHEET.replace('.', ''), _n[0])


def P(x, y): return [round(XA + x, 1), round(YA + y, 1)]


def ln(pts, layer, lw):
    O.append({'t': 'pl', 'p': [P(*q) for q in pts], 'layer': layer, 'lw': lw, 'tag': tag()})


def note(l1, l2, tgt, org, arrow='Oblique'):
    h = tag(); O.append({'t': 'clone', 'h': NOTE_T, 'tag': h})
    O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': P(*tgt)})
    O.append({'t': 'mcset', 'h': h, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': P(*org), 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow}})


def dim(p1, p2, at, vertical=False, txt=None, tx=None, lfac=None):
    o = {'t': 'dim', 'h': DIM_T, 'p1': P(*p1), 'p2': P(*p2), 'dl': P(at, 0) if vertical else P(0, at), 'rot': math.pi / 2 if vertical else 0, 'txt': txt or ''}
    if tx: o['tx'] = P(*tx)
    if lfac: o['lfac'] = lfac
    O.append(o)


def chain(vals, at, vertical, fixed, texts=None, smalls=None):
    for k, (a, b) in enumerate(zip(vals, vals[1:])):
        p1 = (fixed, a) if vertical else (a, fixed); p2 = (fixed, b) if vertical else (b, fixed)
        tx = (smalls or {}).get(k)
        if tx is None and (texts or {}).get(k):
            off = 170 if at > fixed else -170
            tx = (at + (-off if vertical else 0) - (0 if not vertical else 0), (a + b) / 2) if vertical else ((a + b) / 2, at + 170)
            if vertical: tx = (at - 170, (a + b) / 2)
        dim(p1, p2, at, vertical, (texts or {}).get(k), tx)


def title(text):
    O.append({'t': 'mtext', 'at': P(16000, 12000 + 1500 + 2800), 'h': 300, 'att': 2, 'style': 'ISOCPEUR.', 'layer': 'Размеры', 's': '{\\L%s}' % text})


AXX, AYY = F.AX, F.AY
title(TITLE + ' на отм. -0.500...-1.500')


def cell_org(i, j, dx=1300, dy=1950):
    sx = 1 if i < len(AXX) - 1 else -1; sy = 1 if j < len(AYY) - 1 else -1
    return (AXX[i] + sx * dx, AYY[j] + sy * dy)


def steps(vals, step):
    """chain of bar positions -> (points, texts) with a «step x n = total» run"""
    pts = [vals[0], vals[1]]; texts = {}          # edge -> first bar and last bar -> edge are separate segments
    i = 1
    while i < len(vals) - 2:
        j = i
        while j + 1 < len(vals) - 2 and abs((vals[j + 1] - vals[j]) - step) < 1e-6 and abs((vals[j + 2] - vals[j + 1]) - step) < 1e-6: j += 1
        if j > i:
            texts[len(pts) - 1] = '%dх%d=%d' % (step, j + 1 - i, vals[j + 1] - vals[i]); pts.append(vals[j + 1]); i = j + 1
        else:
            pts.append(vals[i + 1]); i += 1
    pts.append(vals[-1])
    return pts, texts


if SHEET in ('3.2', '3.3'):
    alongX = SHEET == '3.2'
    for i, x in enumerate(AXX):
        for j, y in enumerate(AYY):
            if alongX:
                for v in F.P2: ln([(x - F.PX / 2 + 50, y - F.PY / 2 + v), (x + F.PX / 2 - 50, y - F.PY / 2 + v)], 'диам28', 40)
                for v in F.P4: ln([(x - F.PX / 2 + 50, y - F.PY / 2 + v), (x + F.PX / 2 - 50, y - F.PY / 2 + v)], 'диам28', 40)
                if (i, j) == (len(AXX) - 1, 0):
                    note('2(%%C28)', 'ш.150', (x + F.PX / 2 - 300, y - F.PY / 2 + F.P2[2]), (x + F.PX / 2 + 2600, y - F.PY / 2 - 900))
                    note('4(%%C28)', 'ш.200', (x + F.PX / 2 - 500, y - F.PY / 2 + F.P4[1]), (x + F.PX / 2 + 2600, y - F.PY / 2 - 2300))
            else:
                for v in F.P1: ln([(x - F.PX / 2 + v, y - F.PY / 2 + 50), (x - F.PX / 2 + v, y + F.PY / 2 - 50)], 'диам28', 40)
                for v in F.P3: ln([(x - F.PX / 2 + v, y - F.PY / 2 + 50), (x - F.PX / 2 + v, y + F.PY / 2 - 50)], 'диам28', 40)
                if (i, j) == (0, len(AYY) - 1):
                    note('1(%%C28)', 'ш.150', (x - F.PX / 2 + F.P1[2], y + F.PY / 2 - 300), (x - F.PX / 2 - 2200, y + F.PY / 2 + 1900))
                    note('3(%%C28)', 'ш.200', (x - F.PX / 2 + F.P3[1], y + F.PY / 2 - 500), (x - F.PX / 2 - 2200, y + F.PY / 2 + 1100))
    # beam bars
    if alongX:
        for j, y in enumerate(AYY):
            for b in F.BAR_B: ln([(AXX[0] - F.PX / 2 + 50, y + b), (AXX[-1] + F.PX / 2 - 50, y + b)], 'диам28', 40)
            xm = (AXX[5] + AXX[6]) / 2
            if j == 0:
                note('5(%%C28)', '4+4', (AXX[5] + F.PX / 2 + 800, y + F.BAR_B[-1]), (AXX[5] + F.PX / 2 + 1100, y + 900))
                note('6(%%C12)', '2 шт.', (AXX[5] + F.PX / 2 + 2300, y + F.BAR_B[-1]), (AXX[5] + F.PX / 2 + 2600, y + 900))
    else:
        for i, x in enumerate(AXX):
            for b in F.BAR_B: ln([(x + b, AYY[0] - F.PY / 2 + 50), (x + b, AYY[-1] + F.PY / 2 - 50)], 'диам28', 40)
            ym = (AYY[0] + AYY[1]) / 2
            if i == 0:
                note('5(%%C28)', '4+4', (x + F.BAR_B[-1], ym), (x + 900, ym - 600))
                note('6(%%C12)', '2 шт.', (x + F.BAR_B[-1], ym + 1300), (x + 900, ym + 700))
    # typical pad dims (pad 1/А): bar steps
    def ends(pts, far, vertical):
        sm = {}
        for k, (p_, q_) in enumerate(zip(pts, pts[1:])):
            if q_ - p_ < 700:
                c = p_ - 750 if k == 0 else q_ + 750
                sm[k] = (far, c) if vertical else (c, far)
        return sm
    if alongX:
        x, y = AXX[-1], AYY[0]
        for v_, st, xf, side, off in ((F.P2, 150, x + F.PX / 2, 1, 700), (F.P4, 200, x + F.PX / 2, 1, 1400)):
            pts, tx = steps([0] + v_ + [F.PY], st)
            pp = [y - F.PY / 2 + v for v in pts]
            sm_ = ends(pp, xf + side * (off + 170), True)
            chain(pp, xf + side * off, True, xf, tx, sm_)
    else:
        x, y = AXX[0], AYY[-1]
        for v_, st, yf, side, off, xc in ((F.P1, 150, y + F.PY / 2, 1, 700, AXX[1]), (F.P3, 200, y + F.PY / 2, 1, 700, AXX[3])):
            pts, tx = steps([0] + v_ + [F.PX], st)
            pp = [xc - F.PX / 2 + v for v in pts]
            sm_ = ends(pp, yf + side * (off + 170), False)
            chain(pp, yf + side * off, False, yf, tx, sm_)
    O.append({'t': 'mtext', 'at': [SLOT + 2300, Y0 + 13300], 'h': 250, 'w': 36000, 'layer': 'Размеры',
              's': ('1. Подушки Фм-1 (24 шт.) армируются одинаково: нижняя сетка %s, верхняя сетка %s. Позиции и шаг показаны на подушках по оси %s; остальные - аналогично.\P'
                    '2. Продольная арматура балок 350х600: поз. 5 (%%%%C28, 4 верх + 4 низ), поз. 6 (%%%%C12, 2 боковых) - непрерывно через подушки, стыки внахлест %s в пределах подушек, вразбежку.\P'
                    '3. Разрезы и спецификацию см. лист 3.5, хомуты балок - лист 3.4, выпуски - лист 3.6.')
              % (('поз. 2 (%%C28 ш.150)', 'поз. 4 (%%C28 ш.200)', '8/А', '1710 (%%C28), 730 (%%C12)') if alongX else
                 ('поз. 1 (%%C28 ш.150)', 'поз. 3 (%%C28 ш.200)', 'В', '1710 (%%C28), 730 (%%C12)'))})

if SHEET == '3.4':
    seen = {}
    for kind, a, b, line in F.spans():
        hz = F.hoops(a, b)
        for z in hz:
            if kind == 'x': ln([(z, line - 145), (z, line + 145)], 'диам10', 30)
            else: ln([(line - 145, z), (line + 145, z)], 'диам10', 30)
        seen.setdefault((kind, round(b - a)), (a, b, line, hz))

    def runs_of(a, b, hz):
        pts = [a] + hz + [b]; dd = [round(q - p) for p, q in zip(pts, pts[1:])]; R_ = []; k = 0
        while k < len(dd):
            m = k
            while m + 1 < len(dd) and dd[m + 1] == dd[k]: m += 1
            R_.append((pts[k], pts[m + 1], dd[k], m - k + 1)); k = m + 1
        return R_

    note('Х1(%%C10)', 'см. примечание', (AXX[6] + 1800, AYY[0] + 140), (AXX[6] + 2300, AYY[0] + 1900))
    rows = []
    for key in sorted(seen):
        a, b, line, hz = seen[key]
        rr = runs_of(a, b, hz)
        rows.append('пролет %d (%s): %s - %d шт.' % (key[1], 'буквенные оси' if key[0] == 'x' else 'цифровые оси',
                    ', '.join(('%dх%d' % (r[2], r[3])) if r[3] > 1 else '%d' % r[2] for r in rr), len(hz)))
    O.append({'t': 'mtext', 'at': [SLOT + 2300, Y0 + 13300], 'h': 250, 'w': 36000, 'layer': 'Размеры',
              's': '1. Хомуты Х1 (%%C10 А500С) фундаментных балок 350х600 ставятся только в пролетах между подушками; в подушках - сетки поз. 1...4 (листы 3.2, 3.3).\\P'
                   '2. Шаг хомутов от грани подушки: 50, приопорные четверти пролета - шаг 100, середина - шаг 200. Шаг хомутов по типам пролетов:\\P'
                   + '\\P'.join('    ' + r for r in rows)})

if SHEET == '3.6':
    for i, x in enumerate(AXX):
        for j, y in enumerate(AYY):
            ln([(x - 350, y - 450), (x + 350, y - 450), (x + 350, y + 450), (x - 350, y + 450), (x - 350, y - 450)], 'Размеры', 30)
    note('Вп1', 'см. узел 1', (AXX[0] - 350, AYY[0] - 300), (AXX[0] - 1900, AYY[0] - 2300))
    note('Вп2', 'см. узел 1', (AXX[0] - 350, AYY[0] + 100), (AXX[0] - 1900, AYY[0] - 1500))
    O.append({'t': 'mtext', 'at': [SLOT + 2300, Y0 + 13300], 'h': 250, 'w': 36000, 'layer': 'Размеры',
              's': '1. Выпуски Вп1 (4 угловых, выступают на 600) и Вп2 (10 средних, выступают на 1200) %%C28 А500С - одинаковые во всех 24 подушках под колоннами Км-1...Км-6; привязка - по узлу 1.\\P'
                   '2. Выпуски опираются на нижнюю сетку подушки (лапка 200), фиксируются хомутами Х2 (%%C10, 4 шт.: 2 ряда сверху и 2 снизу), устанавливаются до бетонирования.\\P'
                   '3. Стыковка с продольной арматурой колонн - накладками Н2 (ГОСТ 14098-2014, С21-Рн), вразбежку (см. листы 4.1...4.6).'})

    def Q(cx, cy, k): return lambda x, y: [round(cx + k * x, 1), round(cy + k * y, 1)]

    def lnw(pts, layer, lw, closed=False):
        O.append({'t': 'pl', 'p': pts, 'layer': layer, 'lw': lw, 'closed': closed, 'tag': tag()})

    def dimw(p1, p2, at, vertical, lfac, txt=None, tx=None):
        o = {'t': 'dim', 'h': DIM_T, 'p1': p1, 'p2': p2, 'dl': [at, p1[1]] if vertical else [p1[0], at], 'rot': math.pi / 2 if vertical else 0, 'txt': txt or '', 'lfac': lfac}
        if tx: o['tx'] = tx
        O.append(o)

    def notew(l1, l2, tgt, org, arrow='Oblique'):
        h = tag(); O.append({'t': 'clone', 'h': NOTE_T, 'tag': h})
        O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': tgt})
        O.append({'t': 'mcset', 'h': h, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': org, 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow}})

    def ttlw(text, x, y):
        t = tag(); O.append({'t': 'clone', 'h': TTL, 'tag': t, 'base': [0, 0], 'to': [0, 0]})
        O.append({'t': 'settext', 'h': t, 's': '{\\L%s}' % text}); O.append({'t': 'moveto', 'h': t, 'idx': 0, 'to': [x, y]})

    S = Q(SLOT + 9000, Y0 + 6300, 4)
    lnw([S(-350, -450), S(350, -450), S(350, 450), S(-350, 450)], 'Размеры', 30, True)
    for (bx, by) in F.DOW:
        c = S(bx, by); r = 56
        O.append({'t': 'circle', 'c': c, 'r': r, 'layer': 'диам28'})
        O.append({'t': 'hatch', 'pat': 'SOLID', 'layer': 'диам28', 'loops': [[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]]})
    a2, b2 = F.X2
    lnw([S(-a2 / 2, -b2 / 2), S(a2 / 2, -b2 / 2), S(a2 / 2, b2 / 2), S(-a2 / 2, b2 / 2)], 'диам10', 30, True)
    xs = [-350] + F.COLX + [350]; ys = [-450] + F.COLY + [450]
    for k, (p, q) in enumerate(zip(xs, xs[1:])):
        tx = S(p - 120, -450 - 330) if k == 0 else (S(q + 120, -450 - 330) if k == len(xs) - 2 else None)
        dimw(S(p, -450), S(q, -450), S(0, -450 - 250)[1], False, 0.25, None, tx)
    dimw(S(-350, -450), S(350, -450), S(0, -450 - 450)[1], False, 0.25)
    for k, (p, q) in enumerate(zip(ys, ys[1:])):
        tx = S(-350 - 330, p - 120) if k == 0 else (S(-350 - 330, q + 120) if k == len(ys) - 2 else None)
        dimw(S(-350, p), S(-350, q), S(-350 - 250, 0)[0], True, 0.25, None, tx)
    dimw(S(-350, -450), S(-350, 450), S(-350 - 450, 0)[0], True, 0.25)
    notew('Вп1', '4 шт.', S(F.COLX[-1], F.COLY[-1]), S(600, 650), 'None')
    notew('Вп2', '10 шт.', S(F.COLX[-1], F.COLY[2]), S(600, 150), 'None')
    notew('Х2(%%C10)', '4 шт.', S(a2 / 2, -200), S(600, -350))
    ttlw('Узел 1. Выпуски в подушке (план)', SLOT + 9000 - 3000, Y0 + 11000)
    T2 = Q(SLOT + 25000, Y0 + 5600, 2)
    lnw([T2(-1500, -1500), T2(1500, -1500), T2(1500, -500), T2(-1500, -500)], 'Размеры', 30, True)
    lnw([T2(-1600, -1600), T2(1600, -1600), T2(1600, -1500), T2(-1600, -1500)], 'Размеры', 5, True)
    lnw([T2(-450, -500), T2(-450, 1400)], 'Размеры', 5); lnw([T2(450, -500), T2(450, 1400)], 'Размеры', 5)
    lnw([T2(-1450, -1436), T2(1450, -1436)], 'диам28', 40); lnw([T2(-1375, -564), T2(1375, -564)], 'диам28', 40)
    zb = -1500 + 50 + 28 + 28 + 14
    for y in F.COLY:
        top = -500 + (600 if y in (F.COLY[0], F.COLY[-1]) else 1200)
        s_ = -1 if y < 0 else 1
        lnw([T2(y + s_ * 200, zb), T2(y, zb), T2(y, top)], 'диам28', 40)
    for z in (-640, -700, -1300, -1350):
        lnw([T2(-F.X2[1] / 2, z), T2(F.X2[1] / 2, z)], 'диам10', 30)
    for p, q in ((-1500, -500), (-500, 100), (100, 700)):
        dimw(T2(1500, p), T2(1500, q), T2(1500 + 450, 0)[0], True, 0.5)
    dimw(T2(1500, -1600), T2(1500, -1500), T2(1500 + 450, 0)[0], True, 0.5, None, T2(1500 + 700, -1700))
    notew('Вп1', '(%%C28)', T2(F.COLY[-1], 0), T2(F.COLY[-1] + 500, 700))
    notew('Вп2', '(%%C28)', T2(F.COLY[3], 400), T2(F.COLY[-1] + 500, 1300))
    notew('Х2(%%C10)', '4 шт.', T2(-F.X2[1] / 2, -1300), T2(-1500 - 300, -300))
    ttlw('Узел 1. Разрез по подушке', SLOT + 25000 - 2500, Y0 + 11000)

O.append({'t': 'save'})
json.dump(O, open('ops/g3s_%s.json' % SHEET, 'w', encoding='utf-8'), ensure_ascii=False)
print(SHEET, len(O), 'ops; base', len(base), 'XA,YA', XA, YA)
if len(sys.argv) > 2:
    out = ab.run(O, 'g3s', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'clonexf' in l)[-2000:])
