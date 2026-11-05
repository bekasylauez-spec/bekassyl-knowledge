"""Column sheet tables (spec 18D93, steel 18DCA of the template copy) + stamp. Args: <mark> <PRE> <sheet no> [run]
Run right after gen4x (fresh template import)."""
import sys, ab, coldata as C
MARK, PRE, SNO = sys.argv[1], sys.argv[2], sys.argv[3]
sch = C.schedule(MARK); col = C.COLS[MARK]
POS = sch['pos']; Np = len(POS)
SP, ST = PRE + '18D93', PRE + '18DCA'
m = ab.tagmap(); sph = m[SP]
O = []
if Np > 9: O.append({'t': 'trows', 'h': SP, 'mode': 'ins', 'at': 8, 'from': 7, 'n': Np - 9})
if Np < 9: O.append({'t': 'trows', 'h': SP, 'mode': 'del', 'at': 8, 'n': 9 - Np})
rC1, rMesh = Np + 1, Np + 5
O.append({'t': 'trows', 'h': SP, 'mode': 'ins', 'at': rMesh + 1, 'from': rMesh, 'n': 1})
cells = [[0, 2, 'Колонна %s' % MARK]]
form = []
unit = lambda r: 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % ((r + 1,) * 3)
for r, p in zip(range(1, Np + 1), POS):
    pos, d, L, n, _ = p
    cells += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'], [r, 6, ''], [r, 7, ''], [r, 8, 'L='], [r, 9, str(int(L))]]
    form += [[r, 10, '%d' % n, None, '%lu2%pr0'], [r, 11, unit(r)], [r, 12, 'L%d*K%d' % (r + 1, r + 1)]]
for r, (pos, d, L, n) in zip((rMesh, rMesh + 1), sch['mesh']):
    cells += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='], [r, 9, str(int(L))]]
    form += [[r, 10, '%d' % n, None, '%lu2%pr0'], [r, 11, unit(r)], [r, 12, 'L%d*K%d' % (r + 1, r + 1)]]
form += [[rC1, 10, '%d' % sch['n_mesh'], None, '%lu2%pr0'], [rC1, 11, 'M%d+M%d' % (rMesh + 1, rMesh + 2)], [rC1, 12, 'L%d*K%d' % (rC1 + 1, rC1 + 1)],
         [0, 12, 'Sum(M2:M%d)' % (rC1 + 1)], [Np + 3, 12, '%.3f' % sch['conc']]]
O += [{'t': 'move', 'h': [ST], 'd': [0, -400 * (Np - 9 + 1)]}, {'t': 'tset', 'h': SP, 'cells': cells}, {'t': 'tformula', 'h': SP, 'cells': form, 'fmt': '%lu2%pr2'}]
TT = 'Table({T:%s})' % sph
grp = {10: [], 16: [], 28: []}
for r, p in zip(range(1, Np + 1), POS): grp[p[1]].append('%s.M%d' % (TT, r + 1))
grp[10].append('%s.M%d' % (TT, rC1 + 1))
O += [{'t': 'tset', 'h': ST, 'cells': [[5, 6, '%%C28'], [6, 0, 'Колонна %s' % MARK]]},
      {'t': 'tformula', 'h': ST, 'fmt': '%lu2%pr2', 'cells': [[6, 1, '0'], [6, 2, '0'], [6, 4, '+'.join(grp[10])], [6, 5, '+'.join(grp[16])],
                                                            [6, 6, '+'.join(grp[28])], [6, 3, 'Sum(B7:C7)'], [6, 7, 'Sum(E7:G7)'], [6, 8, 'H7+D7']]},
      {'t': 'settext', 'h': PRE + '18C86', 's': 'Колонна %s' % MARK}, {'t': 'settext', 'h': PRE + '19531', 's': SNO},
      {'t': 'settext', 'h': PRE + '18CB3', 's': '1. Схема колонн - листы 2.1...2.4; выпуски из фундамента - лист 3.6.\P'
       '2. Бетонировать узлы после установки арматуры ригелей, плит и сеток С1.\P'
       '3. Сварка ручная дуговая, электроды Э-42А (ГОСТ 9467-75).\P'
       '4. Защитный слой - 42 мм до наружной грани продольной арматуры.\P'
       '5. Стыки продольной арматуры - накладки Н2 (ГОСТ 14098-2014, С21-Рн), вразбежку.\P'
       '6. Сетки С1 (поз. 10, 11) - сварные, К1-Кт.'},
      {'t': 'tdump', 'h': SP}, {'t': 'tdump', 'h': ST}, {'t': 'save'}]
if len(sys.argv) > 4:
    out = ab.run(O, 'g4t', 900)
    i = out.find('﻿'); o2 = out[i:]
    print('\n'.join(l[:160] for l in o2.splitlines() if l.startswith(('R0 ', 'R6 h4', 'ERR')) or 'errors' in l))
