"""Sheet 3.2 tables: spec 37FCCB (10 positions, formulas) and steel 37FCCC (A240 Ø8/Ø10, A500С Ø12/16/20/28)."""
import sys, os, re
import ab, fm_data as FD

X0, Y0 = -750903.0, -1749172.0
SPEC, STEEL = '37FCCB', '37FCCC'


def rows(h):
    out = ab.run([{'t': 'tdump', 'h': h}], 'td')
    m = re.findall(r'TABLE rows (\d+) cols (\d+)', out)
    return tuple(map(int, m[-1]))


O = []
nr, nc = rows(SPEC)
if nr == 15: O.append({'t': 'trows', 'h': SPEC, 'mode': 'ins', 'at': 11, 'from': 10, 'n': 2})
cells, form = [], []
order = ['1', '2', '3', '4', '5', '6', 'Ск1', 'Вп1', 'Х1', 'Х2']
P = {p[0]: p for p in FD.POS}
for k, pos in enumerate(order):
    r = 3 + k
    _, st, d, cls, L, n, _ = P[pos]
    unit, _ = FD.mass(P[pos])
    cells += [[r, 0, pos + st], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, cls], [r, 8, 'L='],
              [r, 9, 'пог.м.' if L is None else str(int(L))], [r, 10, ('%.1f' % n) if L is None else str(n)], [r, 11, '%.2f' % unit]]
    form.append([r, 12, 'K%d*L%d' % (r + 1, r + 1)])
form.append([2, 12, 'Sum(M4:M13)'])
cells += [[14, 2, '\A1;Класс бетона C 20/25 (B25) м³'], [15, 2, '\A1;Класс бетона C 8/10 (B7.5) м³'], [14, 12, '%.2f' % FD.V_CONC], [15, 12, '%.2f' % FD.V_PODG]]
O += [{'t': 'tset', 'h': SPEC, 'cells': cells}, {'t': 'tformula', 'h': SPEC, 'cells': form, 'fmt': '%lu2%pr2'}]

# steel table
nr2, nc2 = rows(STEEL)
if nc2 == 7:
    O += [{'t': 'tcolins', 'h': STEEL, 'at': 2, 'from': 1, 'n': 1}, {'t': 'tcolins', 'h': STEEL, 'at': 6, 'from': 5, 'n': 2}]
by = {}
for p in FD.POS:
    by[(p[3], p[2])] = by.get((p[3], p[2]), 0) + float('%.2f' % FD.mass(p)[0]) * p[5]
vals = [by.get(('240', 8), 0), by.get(('240', 10), 0), None, by.get(('500С', 12), 0), by.get(('500С', 16), 0), by.get(('500С', 20), 0), by.get(('500С', 28), 0)]
sc = [[5, 1, '%%C8'], [5, 2, '%%C10'], [5, 3, 'Итого'], [5, 4, '%%C12'], [5, 5, '%%C16'], [5, 6, '%%C20'], [5, 7, '%%C28'], [5, 8, 'Итого'],
      [6, 0, 'Фундамент Фм-1']]
for c, v in zip((1, 2, 4, 5, 6, 7), [vals[0], vals[1], vals[3], vals[4], vals[5], vals[6]]):
    sc.append([6, c, '%.2f' % v])
O += [{'t': 'tset', 'h': STEEL, 'cells': sc},
      {'t': 'tformula', 'h': STEEL, 'cells': [[6, 3, 'B7+C7'], [6, 8, 'Sum(E7:H7)'], [6, 9, 'D7+I7']], 'fmt': '%lu2%pr2'},
      {'t': 'tcolw', 'h': STEEL, 'cols': [[0, 3000]] + [[c, 1550] for c in range(1, 10)]},
      {'t': 'tdump', 'h': SPEC}, {'t': 'tdump', 'h': STEEL}, {'t': 'list', 'win': [X0, Y0 - 2000, X0 + 70000, Y0 + 45000]}, {'t': 'save'}]
print('total kg %.2f' % sum(v for v in vals if v))
if len(sys.argv) > 1:
    out = ab.run(O, 'g32t', 600)
    print(out[out.rfind('TABLE rows 1') - 10:][-6000:])
