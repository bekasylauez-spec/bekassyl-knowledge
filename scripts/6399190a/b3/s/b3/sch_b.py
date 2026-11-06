# 4.1 Block 3 scheme, step B: marks (SPDS notes cloned from Block 2 marks), spec table, notes, stair dims moved right
import json, math, sys
sys.path.insert(0, r'..\t'); import mb
from b3plan import AXX, AXY, C
from sch_a import P, F0, OLD, old, HP
TY = json.load(open('types_b3.json', encoding='utf-8'))
AS = json.load(open('assign.json', encoding='utf-8'))
ops = []
def add(**k): ops.append(k); return k
# ---- stair dims further right (clear of marks at axis 22) ----
add(t='erase', h=['B3BD22', 'B3BD23'])
XR = 139300
add(t='dim', h='BD1', p1=P(136300, 0), p2=P(136300, 3150), dl=P(XR, 0), rot=HP, tag='B3BS1')
add(t='dim', h='BD1', p1=P(136300, 3150), p2=P(136300, 5800), dl=P(XR, 0), rot=HP, tag='B3BS2')
# ---- marks ----
lv = {T['mark']: T for T in TY}
def lvtxt(v): return '+%d.%03d' % (v // 1000, v % 1000)
over = {c['top_of']: c for c in C if c['top_of']}
oldmk = old('SPDSNOTEPOSITION', 'Размеры')
D = 1000
for c in C:
    if c['top_of']: continue
    sx, sy = 1, 1
    if c['id'].startswith('Л/'): sy = -1
    tx, ty = c['x'] + sx * c['bx'] / 2, c['y'] + sy * c['by'] / 2
    ox, oy = tx + sx * D, ty + sy * D
    tag = 'B3MK_' + c['id']
    add(t='clone', h='522B5A', tag=tag)
    add(t='sp_set', h=tag, pts=[[0] + P(ox, oy), [1] + P(tx, ty)])
    mk = AS[c['id']]; l2 = ''
    T = lv[mk]
    if T['base'] > 0: l2 = '(отм. %s)' % lvtxt(T['base'])
    if c['id'] in over:
        u = AS[over[c['id']]['id']]; l2 = '%s (отм. %s)' % (u, lvtxt(lv[u]['base']))
    add(t='notetxt', h=tag, l1=mk, l2=l2, angle=0 if sx > 0 else math.pi)
add(t='erase', h=oldmk)
# ---- spec table: move to the right of the plan, rows = types + Итого ----
dx, dy = (F0[0] + 63500) - (OLD[0] + 42000), (F0[1] + 56500) - (OLD[1] + 40600)
add(t='move', h=['TH', 'TB'], d=[dx, dy])
add(t='trows', h='TB', mode='ins', at=1, **{'from': 1}, n=len(TY) - 7)
cells = []
def lvl(v): return '±0.000' if v == 0 else lvtxt(v)
for i, T in enumerate(TY):
    top = T['base'] + T['levels'][-1] - T['beams'][-1]
    cells += [[i, 0, T['mark']], [i, 1, '%dх%d' % (T['b'], T['h'])], [i, 2, '%s / %s' % (lvl(T['base']), lvl(top))],
              [i, 3, '%d%%%%C28 А500С' % T['ns']], [i, 4, str(T['n'])], [i, 5, '4.%d' % (i + 2)]]
cells += [[len(TY), 0, 'Итого'], [len(TY), 4, str(sum(T['n'] for T in TY))]]
add(t='tset', h='TB', cells=cells)
# ---- notes ----
up = [T['mark'] for T in TY if T['base'] > 0]
st = [T['mark'] for T in TY if T['b'] == 500 and T['base'] == 0]
txt = ('1. Отметка ±0.000 соответствует отметке чистого пола 1-го этажа (по АР).\P'
       '2. Колонны Км-1...Км-%d - от верха фундамента (отм. ±0.000) до низа ригелей; колонны %s - на отм. +7.000 '
       '(на ригелях и над колоннами по осям Г, Е в осях 18, 19).\P'
       '3. Колонны %s - колонны лестницы и площадок в осях 21-22.\P'
       '4. Армирование колонн - по расчёту ЛИРА-САПР "массаподготовка блок 3 униф".\P'
       '5. Бетон колонн С20/25 (B25), арматура А500С по ГОСТ 34028-2016.\P'
       '6. Привязка колонн, не указанная на схеме, - по однотипным колоннам той же оси.') % (
           len(TY) - len(up), ', '.join(up), ', '.join(st))
add(t='settext', h='NOTES', s=txt)
add(t='move', h=['NOTES'], d=[dx, dy - 800 * (len(TY) - 7) - 1500])
add(t='save')
if __name__ == '__main__':
    json.dump(ops, open(mb.S + r'\ops\sch_b.json', 'w', encoding='utf-8'), ensure_ascii=False)
    if 'run' in sys.argv: print(mb.run(ops, 'sch_b', 900)[-2500:])
    else: print(len(ops))
