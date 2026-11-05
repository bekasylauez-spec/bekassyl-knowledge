"""Column sheet tables (spec 18D93, steel 18DCA of the template copy) + stamp. Args: <mark> <PRE> <sheet no> [run]"""
import sys, ab, coldata as C
MARK, PRE, SNO = sys.argv[1], sys.argv[2], sys.argv[3]
sch = C.schedule(MARK); col = C.COLS[MARK]
P = {p[0]: p for p in sch['pos']}
SP, ST = PRE + '18D93', PRE + '18DCA'
m = ab.tagmap(); sph = m[SP]
O = [{'t': 'trows', 'h': SP, 'mode': 'ins', 'at': 15, 'from': 14, 'n': 1}]
rows = {1: 'Х1', 2: 'Х2', 3: 'Ск1', 4: 'Ск2', 5: '1', 6: '2', 7: 'Х3', 9: 'Н2'}
cells, form = [[0, 2, 'Колонна %s' % MARK]], []
for r, pos in rows.items():
    _, d, L, n, _ = P[pos]
    cells += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='], [r, 9, str(int(L))]]
    form += [[r, 10, '%d' % n], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % ((r + 1,) * 3)], [r, 12, 'L%d*K%d' % (r + 1, r + 1)]]
for r, (pos, d, L, n) in zip((14, 15), sch['mesh']):
    cells += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='], [r, 9, str(int(L))]]
    form += [[r, 10, '%d' % n], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % ((r + 1,) * 3)], [r, 12, 'L%d*K%d' % (r + 1, r + 1)]]
form += [[10, 10, '%d' % sch['n_mesh']], [10, 11, 'M15+M16'], [10, 12, 'L11*K11'], [0, 12, 'Sum(M2:M11)'],
         [12, 12, '%g*%g*%g' % (C.BX / 1000, C.BY / 1000, (col['top'] - col['bot']) / 1000)]]
form = [f + ([None, '%lu2%pr0'] if f[1] == 10 else []) for f in form]
O += [{'t': 'tset', 'h': SP, 'cells': cells}, {'t': 'tformula', 'h': SP, 'cells': form, 'fmt': '%lu2%pr2'}]
TT = 'Table({T:%s})' % sph
O += [{'t': 'tset', 'h': ST, 'cells': [[5, 6, '%%C28'], [6, 0, 'Колонна %s' % MARK]]},
      {'t': 'tformula', 'h': ST, 'fmt': '%lu2%pr2', 'cells': [[6, 1, '0'], [6, 2, '0'],
        [6, 4, '%s.M2+%s.M3+%s.M8+%s.M11' % (TT, TT, TT, TT)], [6, 5, '%s.M4+%s.M5' % (TT, TT)], [6, 6, '%s.M6+%s.M7+%s.M10' % (TT, TT, TT)], [6, 3, 'Sum(B7:C7)'], [6, 7, 'Sum(E7:G7)'], [6, 8, 'H7+D7']]},
      {'t': 'settext', 'h': PRE + '18C86', 's': 'Колонна %s' % MARK}, {'t': 'settext', 'h': PRE + '19531', 's': SNO},
      {'t': 'tdump', 'h': SP}, {'t': 'tdump', 'h': ST}, {'t': 'save'}]
if len(sys.argv) > 4:
    out = ab.run(O, 'g4t', 900)
    i = out.find('\ufeff'); print(out[i:][-5000:])
