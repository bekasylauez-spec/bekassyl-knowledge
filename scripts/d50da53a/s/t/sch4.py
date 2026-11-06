# scheme 4.1 step 4: column table (cloned from analog spec header/body tables, x2 for 1:100), notes, cleanup of 2.1
import json, sys
import mb
from sch import F0

TYPES = json.load(open(mb.S + r'\types.json', encoding='utf-8'))
ops = []
def add(**k): ops.append(k); return k
TX, TY = F0[0] + 42000, F0[1] + 40600            # table top-left on the sheet
HB = (-671302.685, -1728422.151); BB = (-671302.685, -1729572.151)
add(t='clone', h='4E8D9D', base=list(HB), to=[TX, TY], s=2, tag='TH')
add(t='clone', h='4E8C66', base=list(BB), to=[TX, TY - 2 * (HB[1] - BB[1])], s=2, tag='TB')
# body: unmerge, keep 12 rows (11 types + total)
for r, a, b in ((0, 2, 9), (9, 2, 9), (10, 2, 9), (11, 2, 9), (12, 2, 9), (15, 0, 12)):
    add(t='tmerge', h='TB', r=[r, a, r, b], mode='unmerge')
add(t='trows', h='TB', mode='del', at=12, n=4)
add(t='tcols', h='TB', at=12, n=1)
add(t='tmerge', h='TH', r=[1, 2, 1, 9], mode='unmerge')
add(t='tmerge', h='TH', r=[0, 0, 0, 12], mode='unmerge')
add(t='tcols', h='TH', at=12, n=1)
add(t='tmerge', h='TH', r=[0, 0, 0, 11], mode='merge')
add(t='tmerge', h='TH', r=[1, 2, 1, 5], mode='merge')
add(t='tmerge', h='TH', r=[1, 6, 1, 9], mode='merge')
cells = [[0, 0, '{\\C256;Спецификация колонн}'], [1, 0, 'Марка'], [1, 1, 'Сечение, мм'], [1, 2, 'Отм. низа / верха'],
         [1, 6, 'Арматура'], [1, 10, 'Кол-во, шт'], [1, 11, 'Лист']]
add(t='tset', h='TH', cells=cells)
rows = []
for r in range(12):
    add(t='tmerge', h='TB', r=[r, 2, r, 5], mode='merge')
    add(t='tmerge', h='TB', r=[r, 6, r, 9], mode='merge')
    for c in range(12):
        rows.append([r, c, ''])
tot = 0
for r, ty in enumerate(TYPES):
    rows += [[r, 0, ty['mark']], [r, 1, ty['sec']], [r, 2, ty['lev']], [r, 6, ty['arm']], [r, 10, str(ty['n'])], [r, 11, ty['sheet']]]
    tot += ty['n']
rows += [[11, 0, 'Итого'], [11, 10, str(tot)]]
add(t='tset', h='TB', cells=rows)
add(t='save')
if 'run' in sys.argv:
    print(mb.run(ops, 'sch4', 1500))
