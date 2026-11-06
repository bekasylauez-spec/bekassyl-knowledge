# Column table on schema sheet 4.1: clone of the Онкоцентр schema table «Спецификация элементов каркаса» (ONC:3D44EA),
# columns -> Марка | Сечение | Отм. низа/верха | Арматура | Кол-во, шт | Лист. usage: python gen_tab.py rows.json [--run]
#   rows.json: [["Км-1","800×1200","−1,200 / +7,000","10Ø28 А500С",10,"4.2"], ...]
import json, sys, os
import gx
ROWS = json.load(open(sys.argv[1], encoding='utf-8'))
X0, YT = 250300.0, 330298.0 - 1500                     # top-left of the table on sheet 4.1 (frame 180617..264717 x 271898..331298)
ops = []
def add(**k): ops.append(k)
TG = 'SCHT'
add(t='erase', h=[TG]) if TG in gx.tagmap() else None
add(t='clone', h='ONC:3D44EA', base=[0, 0], to=[0, 0], tag=TG)
n0 = 41
add(t='trows', h=TG, mode='del', at=2 + len(ROWS), n=n0 - 2 - len(ROWS))
for r in (range(2, 2 + len(ROWS))):
    add(t='tmerge', h=TG, mode='unmerge', r=[r, 2, r, 9])
add(t='tmerge', h=TG, mode='unmerge', r=[1, 2, 1, 9])
add(t='tcols', h=TG, mode='del', at=3, n=7)             # 0 Поз, 1 Обозн, 2 Наим, 3 Кол, 4 Масса, 5 Прим
add(t='tcols', h=TG, mode='ins', at=3, n=1, **{'from': 2})   # -> 0 Марка, 1 Сечение, 2 Отм, 3 Арматура, 4 Кол-во, 5 Лист, 6 (Прим) deleted below
add(t='tcols', h=TG, mode='del', at=6, n=1)
add(t='twidth', h=TG, cols=[[0, 1500], [1, 2000], [2, 3000], [3, 2800], [4, 1500], [5, 1500]])
cells = [[0, 0, 'Ведомость колонн'], [1, 0, 'Марка'], [1, 1, 'Сечение, мм'], [1, 2, 'Отм. низа / верха'], [1, 3, 'Арматура'], [1, 4, 'Кол-во, шт'], [1, 5, 'Лист']]
for i, row in enumerate(ROWS):
    for c, v in enumerate(row): cells.append([2 + i, c, str(v)])
add(t='tset', h=TG, cells=cells)
add(t='theight', h=TG, rows=[[1, 1500]] + [[2 + i, 800] for i in range(len(ROWS))])
add(t='movegrp', h=[TG], d=[X0 - 1456471.0, YT - (-300956.0)])   # clone sits where ONC:3D44EA was imported (top-left)
json.dump(ops, open(os.path.join(gx.S, 'ops', 'sch_tab.json'), 'w', encoding='utf-8'), ensure_ascii=False)
if '--run' in sys.argv:
    print(gx.run(ops + [{'t': 'tdump', 'h': TG}, {'t': 'save'}], 'sch_tab')[-2500:])
