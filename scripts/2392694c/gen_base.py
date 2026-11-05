# Opalubka + main sheets of a slab whose plan differs from 2.2 (typical, roof): copy sheets 6.1 / 6.2 (analog 5.1 sheets
# reworked), wipe their plan, put the plan of scheme sheet 2.n (axes, walls, outer chains) and rebuild contour, openings,
# bars, Ск1/pos notes and chains (Bekassyl rule: 50 from the edge / rigel face, 200хN, rest).   env SLAB=pm3 python gen_base.py
import gx, os, math, json
import lev
import gen62 as G62
C = lev.CUR
SW = 59400.0
S61 = 172179.0
X22 = -184221.0
n = C['scheme']
XS = -243621.0 + SW * (n - 1)            # frame of scheme sheet 2.n
k1, k2 = C['k0'], C['k0'] + 1
x1, x2 = S61 + SW * (k1 - 1), S61 + SW * (k2 - 1)
X1, X2, Y = lev.ox(k1), lev.ox(k2), C['oy']
SX0, SY0, SX1, SY1 = C['rect']
dims = json.load(open(os.path.join(gx.S, 'w', 'dims24.json')))
EXCL_T = ('SPDSNOTEPOSITION', 'SPDSSECTION', 'SPDSFORMAT', 'MTEXT')


def scheme_ents(keep_dims_only):
    out = []
    for l in open(os.path.join(gx.S, 'w', 'all.txt'), encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if f[0] != 'L': continue
        a = list(map(float, f[4][1:].split(',')))
        if not (a[0] >= XS and a[2] <= XS + SW and a[1] >= 455900): continue
        if f[1] in EXCL_T or (f[1] == 'INSERT' and f[3] == 'Размеры'): continue
        if f[1] == 'LWPOLYLINE' and a[2] - a[0] > 20000 and a[3] - a[1] > 20000: continue      # slab contour of the scheme
        if keep_dims_only and f[1] == 'DIMENSION' and f[2] not in dims['keep']: continue
        out.append((f[1], f[2]))
    return out


def P(X, a, b): return [X + a, Y + b, 0]


def run():
    notes = 'КЖ-6.%d ... 6.%d' % (k1, k1 + 7)
    wipe = lambda x0, X: {'t': 'eraseregion', 'win': [x0 + 1, 455950, X + 23500, 495990]}
    ops = [{'t': 'eraseregion', 'win': [x0 - 1, 455930, x0 + SW + 1, 497950]} for x0 in (x1, x2)]
    ops += [{'t': 'clonewin', 'win': [S61 - 5, 455900, S61 + SW + 5, 498000], 'd': [x1 - S61, 0]},
            {'t': 'clonewin', 'win': [S61 + SW - 5, 455900, S61 + 2 * SW + 5, 498000], 'd': [x2 - S61 - SW, 0]}]
    ops += [wipe(x1, X1), wipe(x2, X2)]
    gx.run(ops, 'b1')
    # copied chains of 6.2 above the plan (their texts reach over the wipe window)
    gx.run([{'t': 'list', 'win': [x2, 494300, x2 + 40000, 497900]}], 'ls')
    hs = [l.split('	')[2] for l in open(os.environ['TEMP'] + '/pl_log.txt', encoding='utf-8').read().splitlines() if '	DIMENSION	' in l]
    gx.run([{'t': 'erase', 'h': hs}], 'b1e')
    ops = []
    # --- opalubka: scheme plan, contour (analog polyline 2B43FD, 0.50), openings, section mark, level, texts
    for t, h in scheme_ents(False):
        ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [x1 - XS, 0]})
    ops.append({'t': 'clone', 'h': '2B43FD', 'tag': 'BC%s' % C['tag']})
    ops.append({'t': 'plset', 'h': 'BC%s' % C['tag'], 'p': [P(X1, SX0, SY0), P(X1, SX1, SY0), P(X1, SX1, SY1), P(X1, SX0, SY1)], 'closed': True})
    for i, (a, b, c, d) in enumerate(C['openings']):
        tg = 'BO%s_%d' % (C['tag'], i)
        ops.append({'t': 'clone', 'h': '2B43FE', 'tag': tg})
        ops.append({'t': 'plset', 'h': tg, 'p': [P(X1, a, b), P(X1, c, b), P(X1, c, d), P(X1, a, d)], 'closed': True})
        w, hh = c - a, d - b
        ops.append({'t': 'pl', 'p': [P(X1, a, b), P(X1, a + 0.15 * w, b + 0.89 * hh), P(X1, c, d)], 'layer': '_0', 'lw': 20})
    ops.append({'t': 'clone', 'h': '2B449A', 'base': [lev.ox(1), 463756.885], 'to': [X1, Y]})
    # --- main: scheme plan with axis chains only, contour 0.05, bars, Ск1, notes, chains
    for t, h in scheme_ents(True):
        op = {'t': 'clone', 'h': h, 'base': [0, 0], 'to': [x2 - XS, 0], 'tag': C['bgp'] + h}
        if t == 'LWPOLYLINE': op['lw'] = 5
        ops.append(op)
    ops.append({'t': 'pl', 'p': [P(X2, SX0, SY0), P(X2, SX1, SY0), P(X2, SX1, SY1), P(X2, SX0, SY1)], 'closed': True, 'layer': '0', 'lw': 5, 'tag': C['bgp'] + 'SLAB'})
    YB, XB = 10500, 4000
    for s, e in ((P(X2, SX0, YB), P(X2, SX1, YB)), (P(X2, XB, SY0), P(X2, XB, SY1))):
        ops.append({'t': 'lineset', 'h': '2B8500', 's': s, 'e': e, 'layer': 'диам12'})
    for s, e in ((P(X2, SX0, YB + 20), P(X2, SX0 + 710, YB + 20)), (P(X2, SX1 - 710, YB + 20), P(X2, SX1, YB + 20)),
                 (P(X2, XB - 20, SY0), P(X2, XB - 20, SY0 + 710)), (P(X2, XB - 20, SY1 - 710), P(X2, XB - 20, SY1))):
        ops.append({'t': 'lineset', 'h': '2B8500', 's': s, 'e': e, 'layer': 'диам12'})
    dxn = SW * (k2 - 2); dyn = Y - 463756.885
    G = G62
    for h, dy in (('2B483E', 0), ('2B4840', 0), ('2B4845', 0), ('2B4842', SY0 - G.SY0), ('2B4844', SY1 - G.SY1)):
        ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dxn, dyn + dy]})
    ops.append({'t': 'clone', 'h': '2B47A4', 'base': [0, 0], 'to': [dxn, dyn]})
    # chains: positions of the bars (no rigels on this slab -> one bay each way)
    for vert, (lo, hi, strips) in ((False, (SX0, SX1, C['rx'])), (True, (SY0, SY1, C['ry']))):
        pts = G.chain(lo, hi, strips)
        for p, q, t in pts:
            op = {'t': 'dim', 'h': '2B8502' if vert else '2B851E', 'rot': math.pi / 2 if vert else 0, 'txt': t or ''}
            CH = 600
            if vert: op.update(p1=P(X2, SX1, p), p2=P(X2, SX1, q), dl=P(X2, SX1 + CH, p))
            else: op.update(p1=P(X2, p, SY1), p2=P(X2, q, SY1), dl=P(X2, p, SY1 + CH))
            if not t and q - p < 700:
                c = p - 300 if abs(p - lo) < 1 else q + 300
                op['tx'] = P(X2, SX1 + CH - 60, c) if vert else P(X2, c, SY1 + CH + 190)
            ops.append(op)
    # texts / level
    for k, num in ((k1, '6.1'), (k2, '6.2')):
        x0 = S61 + SW * (k - 1)
        ops.append({'t': 'trepl', 'win': [x0, 455900, x0 + SW, 498000],
                    'pairs': [['КЖ-6.1 ... 6.8', '@@N'], [num, '6.%d' % k], ['@@N', notes], ['Пм-1', C['name']], ['-0.100', C['mark']]]})
    ops.append({'t': 'save'})
    out = gx.run(ops, 'b2')
    print([l for l in out.splitlines() if 'ERR' in l or 'trepl' in l or 'done' in l][:8])
    # level mark of the copied Разрез 1-1
    gx.run([{'t': 'list', 'win': [x1, 455900, x1 + SW, 498000]}], 'ls')
    lv = [l.split('\t')[2] for l in open(os.environ['TEMP'] + '/pl_log.txt', encoding='utf-8').read().splitlines() if '\tSPDSLEVELMARK\t' in l]
    print(gx.run([{'t': 'levelval', 'h': h, 'old': '-0,100', 'value': C['lvl']} for h in lv] + [{'t': 'save'}], 'lv')[-80:])


if __name__ == '__main__':
    run()
