# scheme 4.1: apply renumbered types (Км-7 removed; Км-8->Км-7, Км-9->Км-8; Б/11, Б/12 carry Км-8 above +7.000)
import json, sys
import mb
COLS = json.load(open(mb.S + r'\colplan.json', encoding='utf-8'))
TYPES = json.load(open(mb.S + r'\types.json', encoding='utf-8'))
ops = []
def add(**k): ops.append(k); return k
for c in COLS:
    o = add(t='notetxt', h='MK_' + c['id'], l1=c['mark'])
    if c.get('upper'): o['l2'] = '%s (отм. +7.000)' % c['upper']
add(t='trows', h='TB', mode='del', at=10, n=1)
cells = []
tot = 0
for r, ty in enumerate(TYPES):
    cells += [[r, 0, ty['mark']], [r, 1, ty['sec']], [r, 2, ty['lev']], [r, 3, ty['arm']], [r, 4, str(ty['n'])], [r, 5, ty['sheet']]]
    tot += ty['n']
r = len(TYPES)
cells += [[r, 0, 'Итого'], [r, 1, ''], [r, 2, ''], [r, 3, ''], [r, 4, str(tot)], [r, 5, '']]
add(t='tset', h='TB', cells=cells)
add(t='tfix', h='TB', widths=[1600, 3200, 3600, 4200, 1500, 1400], rowh=800, vborders=30)
txt = ('1. Отметка ±0.000 соответствует отметке чистого пола 1-го этажа (по АР).\\P'
       '2. Колонны Км-1...Км-7 - от верха фундамента (отм. ±0.000) до низа ригелей; колонны Км-8 - на отм. +7.000 '
       '(на ригелях и над колоннами по оси Б в осях 11, 12).\\P'
       '3. Армирование колонн - по расчёту ЛИРА-САПР "массаподготовка блок 2 униф".\\P'
       '4. Бетон колонн С20/25 (B25), арматура А500С по ГОСТ 34028-2016.\\P'
       '5. Привязка колонн, не указанная на схеме, - по однотипным колоннам той же оси.')
add(t='settext', h='NOTES', s=txt, w=15500)
add(t='save')
if 'run' in sys.argv:
    print(mb.run(ops, 'sch5', 1200)[-800:])
