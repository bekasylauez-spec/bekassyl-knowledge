# Parapet ПтМ-1 (+19.700 … +21.200) sheets after the Пм-4 set, from analog 5.2 (sheets «выпуск из плиты покрытия»,
# «Птм-1 опалубка», «Птм-1 армирование», parked at x≈4.67M…4.85M as V1/V2/V3):
#   7.33 Схема расположения выпуск из плиты покрытия на отм. +19.700   (dots of the outlets, legs, notes, chains, Разрез 1-1)
#   7.34 Схема расположения опалубочный чертеж парапет Птм-1 на отм +21.200 (scheme 2.5 plan + Разрез 1-1 (Опалубка))
#   7.35 Схема основное армирование парапета ПтМ-1 на отм. +21.200  (face bars, notes, chains, Разрез 1-1, tables)
# Sheets A2 1:100 like the slab sheets (the analog 1:50 plans do not fit: building 5 m longer). Bekassyl 05.11: Ø12 ш.200 as the analog.
import os, json, math
os.environ['SLAB'] = 'pm4'
import gx, lev
import gen_base as GB
import gen_dop as GD
SW = 59400.0
G = json.load(open(os.path.join(gx.S, 'w', 'ptm_groups.json')))
Y = 466756.885
K = [33, 34, 35]
SEG = [  # (name, along axis, a, b, outer-face coordinate, inward sign)
    ('bot', 'x', -125, 20175, -125, 1), ('left', 'y', 75, 22675, -125, 1), ('right', 'y', 75, 22675, 20175, -1),
    ('topL', 'x', -125, 10275, 22875, -1), ('topR', 'x', 13375, 20175, 22875, -1)]
LVL = {'+19.700': 'E3B6F', '+21.200': 'E3B71'}


def slot(k): return 172179.0 + SW * (k - 1)


def bars_along(a, b):
    xs = [a + 50 + 200 * i for i in range(int((b - a - 100) // 200) + 1)]
    if b - 50 - xs[-1] > 1: xs.append(b - 50)
    return xs


def frame_ops(k, title):
    dx = slot(k) - 231579.0
    ops = [{'t': 'eraseregion', 'win': [slot(k) - 1, 455930, slot(k) + SW + 1, 497950]}]
    for h in GD.FRAME: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    ops.append({'t': 'clone', 'h': '2B47A5', 'base': [0, 0], 'to': [dx - 2500, -650], 'text': '{\\L\\C0;' + title + '}'})
    ops.append({'t': 'clone', 'h': '2B479D', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\C0;' + title + '}'})
    ops.append({'t': 'clone', 'h': '2B479F', 'base': [0, 0], 'to': [dx, 0], 'text': '7.%d' % k})
    ops.append({'t': 'trepl', 'win': [slot(k) - 5, 455900, slot(k) + SW + 5, 498000], 'pairs': [['КЖ-7.1 ... 7.8', 'КЖ-7.25 ... 7.36']]})
    return ops


def bg_ops(k, full):
    ops = []
    for t, h in GB.scheme_ents(not full):
        op = {'t': 'clone', 'h': h, 'base': [0, 0], 'to': [slot(k) - GB.XS, 0]}
        if t == 'LWPOLYLINE' and not full: op['lw'] = 5
        ops.append(op)
    return ops


def group_ops(name, src_list, k, to_xy, tagp):
    """clone an analog group so that its bbox top-left lands at to_xy (sheet-relative)"""
    ext = []
    for l in open(os.path.join(gx.S, 'w', src_list), encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if len(r) > 4 and r[2] in G[name] and r[4].startswith('E') and 'NaN' not in r[4]:
            ext.append(list(map(float, r[4][1:].split(','))))
    x0 = min(e[0] for e in ext); y1 = max(e[3] for e in ext)
    d = [slot(k) + to_xy[0] - x0, 455939 + to_xy[1] - y1]
    return [{'t': 'clone', 'h': h, 'base': [0, 0], 'to': d, 'tag': tagp + h} for h in G[name]]


def P(k, a, b): return [lev.ox(k) + a, Y + b, 0]


def dots_ops(k):
    ops = []
    for nm, ax, a, b, o, s in SEG:
        for off in (46, 154):
            c = o + s * off
            for t in bars_along(a, b):
                x, y = (t, c) if ax == 'x' else (c, t)
                ops.append({'t': 'pl', 'p': [P(k, x - 25, y), P(k, x + 25, y)], 'b': [1, 1], 'closed': True, 'w': 50, 'layer': 'диам12'})
    return ops


def face_lines_ops(k):
    ops = []
    for nm, ax, a, b, o, s in SEG:
        for off in (46, 154):
            c = o + s * off
            p, q = ((a + 30, c), (b - 30, c)) if ax == 'x' else ((c, a + 30), (c, b - 30))
            ops.append({'t': 'lineset', 'h': '2B8500', 's': P(k, *p), 'e': P(k, *q), 'layer': 'диам12'})
    return ops


def legs_ops(k, d):
    """chamfered inner polyline (legs of the outlets / U-bars), as the analog plan; open at the stair gap"""
    i0, i1, j0, j1, ch = -125 + d, 20175 - d, -125 + d, 22875 - d, 300
    pts = [(10275 - 50, j1), (i0 + ch, j1), (i0, j1 - ch), (i0, j0 + ch), (i0 + ch, j0), (i1 - ch, j0), (i1, j0 + ch), (i1, j1 - ch), (i1 - ch, j1), (13375 + 50, j1)]
    return [{'t': 'pl', 'p': [P(k, *q) for q in pts], 'layer': 'диам12', 'lw': 40}]


def chains_ops(k):
    ops = []
    for nm, ax, a, b, o, s in SEG:
        xs = bars_along(a, b)
        pts = [a, xs[0], xs[0] + 200 * (len(xs) - 2), xs[-1], b] if len(xs) > 2 else [a, xs[0], xs[-1], b]
        line = o - s * 700
        for p, q in zip(pts, pts[1:]):
            if q - p < 1: continue
            txt = '200х%d' % ((q - p) // 200) if q - p >= 400 and abs((q - p) % 200) < 1 else ''
            if ax == 'x':
                op = {'t': 'dim', 'h': GD.T_DH, 'p1': P(k, p, o), 'p2': P(k, q, o), 'dl': P(k, p, line), 'rot': 0, 'txt': txt}
                if q - p < 300: op['tx'] = P(k, p - 250 if p == a else q + 250, line + (180 if s > 0 else 180))
            else:
                op = {'t': 'dim', 'h': GD.T_DV, 'p1': P(k, o, p), 'p2': P(k, o, q), 'dl': P(k, line, p), 'rot': math.pi / 2, 'txt': txt}
                if q - p < 300: op['tx'] = P(k, line - 60, p - 250 if p == a else q + 250)
            if txt: op['tx'] = P(k, (p + q) / 2, line + 180) if ax == 'x' else P(k, line - 60, (p + q) / 2)
            ops.append(op)
    return ops


def note_ops(k, tag, l1, l2, shelf, arrows):
    ops = [{'t': 'clone', 'h': GD.T_NOTE, 'tag': tag}]
    items = [[0] + P(k, *shelf)[:2]] + [[i + 1] + P(k, *a)[:2] for i, a in enumerate(arrows[:2])]
    ops += [{'t': 'spmove', 'h': tag, 'items': items}, {'t': 'noteh', 'h': tag, 'l1': l1, 'l2': l2}]
    return ops


def levels_ops(tagp, pairs):
    """analog 6-char levels -> clone the 7-char marks of the scheme sections onto their places (gen_base method)"""
    import re
    ops = []
    m = gx.tagmap()
    for old, new in pairs:
        h = m[tagp + old]
        def pts(hh):
            o = gx.run([{'t': 'spmove', 'h': hh}], 'sp'); l = [q for q in o.splitlines() if q.startswith('spmove')][0]
            return [tuple(map(float, q.split(','))) for q in re.findall(r'\(([-\d.]+,[-\d.]+)\)', l)]
        a, b = pts(h)[0], pts(LVL[new])[0]
        ops += [{'t': 'clone', 'h': LVL[new], 'base': [b[0], b[1]], 'to': [a[0], a[1]]}, {'t': 'erase', 'h': [h]}]
    return ops


def run():
    import levfix
    POS_OUT = 42
    # 7.33 outlets
    k = K[0]
    ops = frame_ops(k, 'Схема расположения выпуск из плиты покрытия на отм. +19.700') + bg_ops(k, False)
    ops += dots_ops(k) + legs_ops(k, 550) + chains_ops(k)
    for i, (nm, ax, a, b, o, s) in enumerate(SEG):
        mid = (a + b) / 2 + (1500 if nm in ('left', 'right') else 0)
        if ax == 'x': ops += note_ops(k, 'PTN%d' % i, str(POS_OUT), 'ш.200', (mid, o + s * 1300), [(mid, o + s * 154), (mid, o + s * 550)])
        else: ops += note_ops(k, 'PTN%d' % i, str(POS_OUT), 'ш.200', (o + s * 1300, mid), [(o + s * 154, mid), (o + s * 550, mid)])
    ops += group_ops('v1sec', 'v1.txt', k, (40500, 37500), 'PV1_')
    ops.append({'t': 'save'})
    print('7.33', [l for l in gx.run(ops, 'pt33').splitlines() if 'ERR' in l or 'done' in l][:5])
    gx.run(levels_ops('PV1_', [('317CC5', '+19.700'), ('317CC6', '+21.200')]) + [{'t': 'save'}], 'pt33l')
    # 7.34 opalubka
    k = K[1]
    ops = frame_ops(k, 'Схема расположения опалубочный чертеж парапет Птм-1 на отм +21.200') + bg_ops(k, True)
    ops += group_ops('v2sec', 'v2.txt', k, (41000, 33500), 'PV2_')
    ops.append({'t': 'save'})
    print('7.34', [l for l in gx.run(ops, 'pt34').splitlines() if 'ERR' in l or 'done' in l][:5])
    gx.run(levels_ops('PV2_', [('318DE7', '+19.700'), ('318E35', '+21.200')]) + [{'t': 'save'}], 'pt34l')
    # 7.35 reinforcement + tables
    k = K[2]
    ops = frame_ops(k, 'Схема основное армирование парапета ПтМ-1 на отм. +21.200') + bg_ops(k, False)
    ops += face_lines_ops(k) + chains_ops(k)
    for i, (nm, ax, a, b, o, s) in enumerate(SEG):
        mid = (a + b) / 2 + (1500 if nm in ('left', 'right') else 0)
        if ax == 'x':
            ops += note_ops(k, 'PTA%d' % i, '1', 'ш.200', (mid - 1500, o + s * 1300), [(mid - 1500, o + s * 46), (mid - 1500, o + s * 154)])
            ops += note_ops(k, 'PTB%d' % i, '2', 'ш.200', (mid + 1500, o + s * 1300), [(mid + 1500, o + s * 100), (mid + 1500, o + s * 100)])
        else:
            ops += note_ops(k, 'PTA%d' % i, '1', 'ш.200', (o + s * 1300, mid - 1500), [(o + s * 46, mid - 1500), (o + s * 154, mid - 1500)])
            ops += note_ops(k, 'PTB%d' % i, '2', 'ш.200', (o + s * 1300, mid + 1500), [(o + s * 100, mid + 1500), (o + s * 100, mid + 1500)])
    ops += note_ops(k, 'PTS', 'Шп1', 'ш.400х400', (3000, 1300), [(3000, -25), (3000, -25)])
    ops += note_ops(k, 'PTC1', 'Ск1', 'ш.200', (9200, 21900), [(10225, 22775), (10225, 22775)])
    ops += note_ops(k, 'PTC2', 'Ск1', 'ш.200', (14400, 21900), [(13425, 22775), (13425, 22775)])
    ops += group_ops('v3sec', 'v3.txt', k, (42000, 38500), 'PV3_')
    ops.append({'t': 'save'})
    print('7.35', [l for l in gx.run(ops, 'pt35').splitlines() if 'ERR' in l or 'done' in l][:5])
    gx.run(levels_ops('PV3_', [('31ABE7', '+19.700'), ('31AC42', '+21.200')]) + [{'t': 'save'}], 'pt35l')
    # 7.36 (A3, analog frame of Птм-1 opalubka): спецификация, ведомость расхода стали, ведомость деталей of ПтМ-1
    k = 36; x0 = slot(k)
    ops = [{'t': 'eraseregion', 'win': [x0 - 1, 455930, x0 + 29701, 497950]}]
    d = [x0 - 4757079.0, 0]
    for h in ('318DD8', '318DDD', '318DD9', '318DDB', '318E38'): ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': d, 'tag': 'PS_' + h})
    ops.append({'t': 'settext', 'h': 'PS_318DD9', 's': '{\C0;Спецификация парапета ПтМ-1 на отм. +21.200}'})
    ops.append({'t': 'settext', 'h': 'PS_318DDB', 's': '7.36'})
    G['spec'] = ['31AA9D', '31AB40']; G['stal'] = ['31AA46']; G['det'] = [h for h in G['v3tab'] if h not in ('31AA9D', '31AB40', '31AA46')]
    ops += group_ops('spec', 'v3.txt', k, (1000, 41000), 'PT_') + group_ops('stal', 'v3.txt', k, (1000, 29500), 'PT_') + group_ops('det', 'v3.txt', k, (1000, 21500), 'PT_')
    ops.append({'t': 'trepl', 'win': [x0 - 5, 455900, x0 + 29705, 498000], 'pairs': [['КЖ-6.1...6.2', 'КЖ-7.25 ... 7.36'], ['КЖ-6.1..6.2', 'КЖ-7.25 ... 7.36']]})
    ops.append({'t': 'save'})
    print('7.36', [l for l in gx.run(ops, 'pt36').splitlines() if 'ERR' in l or 'done' in l][:5])
    for kk in K: levfix.fix(slot(kk))


if __name__ == '__main__':
    run()
