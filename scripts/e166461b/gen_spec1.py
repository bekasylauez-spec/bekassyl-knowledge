import json, sys, gx, os
SP, ST = '10B8E8', '10BBD8'
ops = []
def add(**k): ops.append(k)
for at, n in ((28, 2), (23, 1), (19, 3), (12, 6), (9, 2), (3, 4)): add(t='trows', h=SP, at=at, n=n)
F = '%lu2%pr0'
G = 'ГОСТ 34028-2016(214-210-%s)'
rows = [  # r, mark, code, d, class, L, qty-formula
    (1, 'Х1*', '0101-0002', 8, '240', 1910, '65'),
    (2, 'Х2*', '0101-0002', 8, '240', 1410, '65'),
    (3, 'Ск1*', '0502-0003', 16, '500С', 1190, '2'),
    (4, 'Ск2*', '0502-0003', 16, '500С', 800, '2'),
    (5, '1', '0502-0009', 32, '500С', 9230, '4'),
    (6, '2', '0502-0005', 20, '500С', 9230, '4'),
    (11, '3', '0501-0005', 10, '500С', 460, '2*6')]
cells = [[0, 2, 'Колонна Км-1'], [7, 0, 'С1'], [7, 2, 'Сетка С1'], [10, 2, 'Сетка С1']]
nums = []; fml = [[0, 12, 'Sum(M2:M8)'], [7, 10, '(2*5)'], [7, 11, '(M12)'], [7, 12, '(L8*K8)'], [9, 12, '(0.5*0.5*8.6)']]
for r, mk, code, d, cl, L, q in rows:
    cells += [[r, 0, mk], [r, 1, G % code], [r, 5, cl]]
    nums += [[r, 3, d, F], [r, 9, L, F]]
    n = r + 1
    fml += [[r, 10, '(%s)' % q], [r, 11, '(D%d*D%d*3.1415926/4*0.00785*J%d/1000)' % (n, n, n)], [r, 12, '(L%d*K%d)' % (n, n)]]
add(t='tset', h=SP, cells=cells)
add(t='tnum', h=SP, cells=nums)
add(t='tformula', h=SP, cells=fml)
# steel table: drop Ø6 (c1) and Ø25, Ø28 (c8, c9)
add(t='tcols', h=ST, at=8, n=2)
add(t='tcols', h=ST, at=1, n=1)
add(t='tset', h=ST, cells=[[5, 6, '%%C32'], [6, 0, 'Колонна Км-1']])
T = '{T:%s}' % SP
ev = lambda s: 'Table(%s).Evaluate(%s)' % (T, s)
add(t='tformula', h=ST, cells=[[6, 1, ev('Sum(M2:M3)')], [6, 2, 'B7'], [6, 3, ev('M8')], [6, 4, ev('Sum(M4:M5)')],
                                [6, 5, ev('M7')], [6, 6, ev('M6')], [6, 7, 'Sum(D7:G7)'], [6, 8, 'C7+H7']])
add(t='evalf'); add(t='tdump', h=SP); add(t='tdump', h=ST); add(t='save')
json.dump(ops, open('ops/k41sp.json', 'w'), ensure_ascii=False)
if '--run' in sys.argv:
    print(gx.run(ops, 'k41sp')[-200:])
    print(open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read()[-5000:])
