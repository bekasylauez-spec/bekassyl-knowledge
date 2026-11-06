"""3.5 tables: spec 37FCCB (11 positions of fm2) and steel 37FCCC (all A500С: Ø10 Ø12 Ø16 Ø20 Ø28)."""
import sys, re, ab, fm2 as F
SPEC, STEEL = '37FCCB', '37FCCC'
def rc(h):
    o = ab.run([{'t': 'tdump', 'h': h}], 'td'); return tuple(map(int, re.findall(r'TABLE rows (\d+) cols (\d+)', o)[-1]))
O = []
nr, nc = rc(SPEC)
if nr == 17: O.append({'t': 'trows', 'h': SPEC, 'mode': 'ins', 'at': 13, 'from': 12, 'n': 1}); nr = 18
if nr == 18:
    O.append({'t': 'trows', 'h': SPEC, 'mode': 'ins', 'at': 14, 'from': 13, 'n': 2})
    O.append({'t': 'move', 'h': [STEEL], 'd': [0, -1700]})
cells, form = [], []
for k, p in enumerate(F.POS):
    r = 3 + k; pos, st, d, cls, L, n, _ = p
    unit, _ = F.mass(p)
    cells += [[r, 0, pos + st], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, cls], [r, 8, 'L='],
              [r, 9, 'пог.м.' if L is None else str(int(L))], [r, 10, ('%.1f' % n) if L is None else str(n)], [r, 11, '%.2f' % unit]]
    form.append([r, 12, 'K%d*L%d' % (r + 1, r + 1)])
NP_ = len(F.POS)
form.append([2, 12, 'Sum(M4:M%d)' % (3 + NP_)])
cells += [[3 + NP_ + 1, 12, '%.2f' % F.V_CONC], [3 + NP_ + 2, 12, '%.2f' % F.V_PODG]]
O += [{'t': 'tset', 'h': SPEC, 'cells': cells}, {'t': 'tformula', 'h': SPEC, 'cells': form, 'fmt': '%lu2%pr2'}]
nr2, nc2 = rc(STEEL)
if nc2 == 10:
    O += [{'t': 'tcols', 'h': STEEL, 'at': 3, 'n': 1}, {'t': 'tcols', 'h': STEEL, 'at': 1, 'n': 1}]   # -> mark, Ø10, Ø12, Ø16, Ø20, Ø28, Итого, Всего
by = {}
for p in F.POS:
    by[p[2]] = by.get(p[2], 0) + float('%.2f' % F.mass(p)[0]) * p[5]
sc = [[5, 1, '%%C10'], [5, 2, '%%C12'], [5, 3, '%%C16'], [5, 4, '%%C20'], [5, 5, '%%C28'], [5, 6, 'Итого'], [6, 0, 'Фундамент Фм-1']]
for c, d in zip(range(1, 6), (10, 12, 16, 20, 28)): sc.append([6, c, '%.2f' % by.get(d, 0)])
O += [{'t': 'tset', 'h': STEEL, 'cells': sc},
      {'t': 'tformula', 'h': STEEL, 'cells': [[6, 6, 'Sum(B7:F7)'], [6, 7, 'G7']], 'fmt': '%lu2%pr2'},
      {'t': 'tdump', 'h': SPEC}, {'t': 'tdump', 'h': STEEL}, {'t': 'list', 'win': [-750903, -1751172, -691503, -1709172]}, {'t': 'save'}]
print('total %.2f' % sum(by.values()))
if len(sys.argv) > 1:
    out = ab.run(O, 'g35t', 900); i = out.find('\ufeff'); print(out[i:][-4500:])
