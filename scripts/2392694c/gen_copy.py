# Opalubka + main sheets of the next slab = copies of the finished Пм-1 sheets 6.1/6.2 (themselves analog 5.1 sheets
# reworked), with title/level/number/openings changed. env SLAB=pm2 ...  python gen_copy.py
import gx, os, math
import lev
C = lev.CUR
SW = 59400.0
S61 = 172179.0
OX61, OY = -173564.0 + (S61 - -184221.0), 463756.885
OLD_OPEN = [(6925, 15475, 10275, 17775), (6925, 18025, 10275, 20575), (10525, 15475, 13125, 20575)]


def listwin(x0, x1):
    gx.run([{'t': 'list', 'win': [x0, 455900, x1, 498000]}], 'ls')
    out = []
    for l in open(os.environ['TEMP'] + '/pl_log.txt', encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if len(r) > 4 and r[0] == 'L': out.append((r[1], r[2], r[3], [float(v) for v in r[4][1:].split(',')]))
        elif len(r) > 4 and r[0] == 'N': out.append((r[1], r[2], r[3], None))
    return out


def texts(k, num_old, num_new, notes_new):
    x0 = S61 + SW * (k - 1)
    return {'t': 'trepl', 'win': [x0, 455900, x0 + SW, 498000],
            'pairs': [['КЖ-6.1 ... 6.8', '@@N'], [num_old, num_new], ['@@N', notes_new], ['Пм-1', C['name']], ['-0.100', C['mark']]]}


def run():
    k1, k2 = C['k0'], C['k0'] + 1
    notes = 'КЖ-6.%d ... 6.%d' % (C['k0'], C['k0'] + 7)
    d1, d2 = SW * (k1 - 1), SW * (k2 - 2)
    for k in (k1, k2):
        x0 = S61 + SW * (k - 1)
        gx.run([{'t': 'eraseregion', 'win': [x0 + 1, 455940, x0 + SW - 1, 497938]}], 'er')
    out = gx.run([{'t': 'clonewin', 'win': [S61 - 5, 455900, S61 + SW + 5, 498000], 'd': [d1, 0]},
                  {'t': 'clonewin', 'win': [S61 + SW - 5, 455900, S61 + 2 * SW + 5, 498000], 'd': [d2 + SW - SW, 0] if False else [SW * (k2 - 2), 0]}], 'cw')
    print([l for l in out.splitlines() if 'clonewin' in l or 'ERR' in l])
    # opalubka: drop the copied openings + their symbols, draw this level's openings; level mark; texts
    X = OX61 + d1
    ents = listwin(S61 + d1, S61 + d1 + SW)
    old = []
    for t, h, lay, e in ents:
        if e is None or t != 'LWPOLYLINE': continue
        for a, b, c, d in OLD_OPEN:
            if abs(e[0] - (X + a)) < 2 and abs(e[1] - (OY + b)) < 2 and abs(e[2] - (X + c)) < 2 and abs(e[3] - (OY + d)) < 2: old.append(h)
    lv = [h for t, h, lay, e in ents if t == 'SPDSLEVELMARK']
    ops = [{'t': 'erase', 'h': old}]
    def P(a, b): return [X + a, OY + b, 0]
    for i, (a, b, c, d) in enumerate(C['openings']):
        tg = 'OP%s_%d' % (C['tag'], i)
        ops.append({'t': 'clone', 'h': '2B43FE', 'tag': tg})
        ops.append({'t': 'plset', 'h': tg, 'p': [P(a, b), P(c, b), P(c, d), P(a, d)], 'closed': True})
        w, hh = c - a, d - b
        ops.append({'t': 'pl', 'p': [P(a, b), P(a + 0.15 * w, b + 0.89 * hh), P(c, d)], 'layer': '_0', 'lw': 20})
    for h in lv: ops.append({'t': 'levelval', 'h': h, 'old': '-0,100', 'value': C['lvl']})
    ops.append(texts(k1, '6.1', '6.%d' % k1, notes))
    ops.append(texts(k2, '6.2', '6.%d' % k2, notes))
    ops.append({'t': 'save'})
    out = gx.run(ops, 'cp')
    print(len(old), 'old openings', len(lv), 'levels', [l for l in out.splitlines() if 'ERR' in l or 'trepl' in l or 'done' in l])


if __name__ == '__main__':
    run()
