# Sheet 6.8 «Спецификация плиты перекрытия Пм-1 на отм. -0.100» = analog 5.1/5.8 sheet (tables + ведомость деталей)
# filled from the design: pos 1 (пог.м incl. laps 61d), dop 2.., shear .., Ск1, Ф1, concrete; formulas as the analog
# (mass ed = D*D*π/4*0.00785*L/1000, total = L*K); table split in two parts (does not fit the A2 height).
import gx, json, os, math, collections
import gen62 as G
import slab_design as SD
import lev
C = lev.CUR
S = gx.S
SW = 59400.0
K = 6.8
X0 = 231579 + SW * (C['k0'] + 5)                     # slot of sheet 6.8
T8 = 4200000.0
GOST = {10: '(214-210-0501-0005)', 12: '(214-210-0502-0001)', 14: '(214-210-0502-0002)', 16: '(214-210-0502-0003)',
        18: '(214-210-0502-0004)'}
LAP = {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}
STOCK = 11700


def quantities():
    P = dict(Z=C['z'], rect=C['rect'], openings=C['openings'], rx=C['rx'], ry=C['ry'])
    Sl = SD.Slab(P['Z'], P['rect'], P['openings'], P['rx'], P['ry'])
    # pos 1: base bars @200 by the 6.2 chains, both directions, both layers, clipped at openings, + laps
    tot = 0.0
    for axis in ('x', 'y'):
        for a, b in Sl.base_lines(axis):
            p = a + 50
            while p <= b - 50 + 1:
                for r0, r1 in Sl.free_runs(axis, p):
                    L = r1 - r0
                    tot += L + max(0, math.ceil(L / STOCK) - 1) * LAP[12]
                p += 200
    pos1_m = round(2 * tot / 1000, 1)
    R = json.load(open(os.path.join(S, 'arm', C['tag'] + '_design.json')))
    pos = {tuple(map(int, k.split('_'))): v for k, v in json.load(open(os.path.join(S, 'arm', C['tag'] + '_pos.json'))).items()}
    dop = collections.Counter()
    for zs in R.values():
        for z in zs: dop[(z['d'], int(round(z['s1'] - z['s0'])))] += z['n']
    rows = [(1, 12, 'пог.м.', pos1_m)]
    for (d, L), v in sorted(pos.items(), key=lambda kv: kv[1]): rows.append((v, d, L, dop[(d, L)]))
    sh = json.load(open(os.path.join(S, 'arm', C['tag'] + '_shear.json')))
    cnt = collections.Counter()
    for z in sh['zones']: cnt[z['d']] += z['n']
    for d, v in sorted(sh['pos'].items(), key=lambda kv: kv[1]): rows.append((v, int(d), 230, cnt[int(d)]))
    # Ск1 @200 along every free edge (slab + openings), Ф1 per 0.4 m² (analog 5.8: 1048 per 405 m²)
    x0, y0, x1, y1 = P['rect']
    per = 2 * ((x1 - x0) + (y1 - y0)) + sum(2 * ((c - a) + (d - b)) for a, b, c, d in P['openings'])
    area = (x1 - x0) * (y1 - y0) / 1e6 - sum((c - a) * (d - b) for a, b, c, d in P['openings']) / 1e6
    rows.append(('Ск1', 12, 1540, int(math.ceil(per / 200))))
    rows.append(('Ф1', 12, 1180, int(math.ceil(area / 0.4))))
    rows += C.get('extra', [])
    return rows, round(area, 2)


def col(c): return 'ABCDEFGHIJKLM'[c]


def build():
    rows, area = quantities()
    L = []
    for l in open(os.path.join(S, 'w', 't42.txt'), encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if len(r) > 3 and r[0] in 'LN' and r[2] not in ('108B',): L.append(r[2])
    dx = X0 - T8
    ops = [{'t': 'eraseregion', 'win': [X0 - 1, 455930, X0 + SW + 1, 497950]}]
    for h in L: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0], 'tag': 'SP_' + h})
    name = 'Спецификация плиты перекрытия %s на отм. %s' % (C['name'], C['mark'])
    ops.append({'t': 'settext', 'h': 'SP_2BDB0C', 's': '{\\C0;' + name + '}'})
    ops.append({'t': 'settext', 'h': 'SP_2BDB0E', 's': '7.%d' % (C['k0'] + 7)})
    # part 2 = copy of the main table and of its header, to the right
    ops.append({'t': 'clone', 'h': 'SP_2BDB7E', 'tag': 'SPB' + C['tag'], 'base': [0, 0], 'to': [19000, 0]})
    ops.append({'t': 'clone', 'h': 'SP_2BDE8B', 'tag': 'SPBH' + C['tag'], 'base': [0, 0], 'to': [19000, 0]})
    # ведомость деталей and ведомость расхода стали under part 2
    det = [h for h in L if h in ('2BDB13',) or ('2BDB55' <= h <= '2BDB7D')]
    ops.append({'t': 'movegrp', 'h': ['SP_' + h for h in det], 'd': [-5465, 2562]})
    ops.append({'t': 'movegrp', 'h': ['SP_2BDEA3'], 'd': [-7560, 177]})
    N1 = min(46, len(rows))                   # data rows of part 1 (rows 1..46), rest in part 2
    p1, p2 = rows[:N1], rows[N1:]
    # part 1: rows 0 header, 1..33 analog rows; need N1 data rows + nothing below
    A, B = 'SP_2BDB7E', 'SPB' + C['tag']
    if N1 > 28: ops.append({'t': 'trows', 'h': A, 'mode': 'ins', 'at': 3, 'from': 2, 'n': N1 - 28})   # rows 1..N1
    ops.append({'t': 'trows', 'h': A, 'mode': 'del', 'at': N1 + 1, 'n': 5 + max(0, 28 - N1)})       # tail of part 1
    # part 2: delete header row 0 and analog data rows, keep 2 template data rows then tail
    n2 = len(p2)
    ops.append({'t': 'trows', 'h': B, 'mode': 'del', 'at': 0, 'n': 1})                          # rows: 0..27 data, 28.. tail
    ops.append({'t': 'trows', 'h': B, 'mode': 'del', 'at': n2, 'n': 28 - n2})                    # keep n2 data rows
    cells1, form1, cells2, form2 = [], [], [], []

    def fill(cells, form, r, row):
        p, d, Ln, q = row
        R1 = r + 1
        cells += [[r, 0, str(p)], [r, 1, 'ГОСТ 34028-2016' + GOST.get(d, '')], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='], [r, 9, str(Ln)]]
        form += [[r, 10, '(%s)' % q, '%lu2%pr0' if p != 1 else '%lu2%pr1']]
        if p == 1: form += [[r, 11, '(D%d*D%d*3.1415926/4*0.00785*1)' % (R1, R1), '%lu2%pr2']]
        else: form += [[r, 11, '(D%d*D%d*3.1415926/4*0.00785*J%d/1000)' % (R1, R1, R1), '%lu2%pr2']]
        form += [[r, 12, '(L%d*K%d)' % (R1, R1), '%lu2%pr2']]
    cells1.append([0, 2, 'Плита ' + C['name']])
    for i, row in enumerate(p1): fill(cells1, form1, 1 + i, row)
    for i, row in enumerate(p2): fill(cells2, form2, i, row)
    cells2 += [[n2 + 3, 12, '']]
    form2 += [[n2 + 3, 12, '(%.2f*0.25)' % area, '%lu2%pr2']]
    form1 += [[0, 12, ('(Sum(M2:M%d)+Table({T:%s}).Evaluate(Sum(M1:M%d)))' % (N1 + 1, B, n2)) if n2 else '(Sum(M2:M%d))' % (N1 + 1), '%lu2%pr2']]
    ops += [{'t': 'tset', 'h': A, 'cells': cells1}, {'t': 'tformula', 'h': A, 'cells': form1},
            {'t': 'tset', 'h': B, 'cells': cells2}, {'t': 'tformula', 'h': B, 'cells': form2}]
    # ведомость расхода стали: Ø columns 4..10 (10,12,14,16,18,20,22), A240 empty
    byd = collections.defaultdict(list)
    for i, row in enumerate(p1): byd[row[1]].append(('A', 2 + i))
    for i, row in enumerate(p2): byd[row[1]].append(('B', 1 + i))
    vf = []
    for c, d in zip(range(4, 11), (10, 12, 14, 16, 18, 20, 22)):
        terms = ['Table({T:%s}).Evaluate(Sum(M%d:M%d))' % (A if t == 'A' else B, r, r) for t, r in byd.get(d, [])]
        vf.append([6, c, '(' + ('+'.join(terms) if terms else '0') + ')', '%lu2%pr2'])
    vf += [[6, 1, '(0)', '%lu2%pr2'], [6, 2, '(0)', '%lu2%pr2'], [6, 3, '(Sum(B7:C7))', '%lu2%pr2'],
           [6, 11, '(Sum(E7:K7))', '%lu2%pr2'], [6, 12, '(Sum(L7:L7)+Sum(D7:D7))', '%lu2%pr2']]
    ops.append({'t': 'tformula', 'h': 'SP_2BDEA3', 'cells': vf})
    ops.append({'t': 'tset', 'h': 'SP_2BDEA3', 'cells': [[6, 0, C['name']]]})
    ops.append({'t': 'trepl', 'win': [X0 - 5, 455900, X0 + SW + 5, 498000], 'pairs': [['КЖ-5.1... 5.8', 'КЖ-7.%d ... 7.%d' % (C['k0'], C['k0'] + 7)]]})
    ops += [{'t': 'evalf'}, {'t': 'save'}]
    return ops, rows, area


if __name__ == '__main__':
    ops, rows, area = build()
    for r in rows: print(r)
    print('area', area)
    out = gx.run(ops, 'spec')
    print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][:10])
