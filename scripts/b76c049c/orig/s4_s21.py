# -*- coding: utf-8 -*-
"""Лист 2.1: Схема расположения элементов на отм. -2.500 + Спецификация элементов. М 1:50, A2 (аналог an03)."""
import math
import s4_lib as L
from s4_lib import op, pl, note, section, Sheet
from s4_geo import *
import s4_draw as D
SC = 50
X0, Y0 = 131100.0, -300000.0
W, H = 29700.0, 21000.0
op(t='ltload', names=['CENTER2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + W + 10, Y0 + H + 10])
sh = Sheet('2.1', 'Схема расположения элементов на отм. -2.500', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT
cx, cy = X0 + 9300.0, Y0 + 10300.0
sh.text(L.title_u('Схема расположения элементов на отм. -2.500'), cx, cy + R_FM + 1250, 175, att=8, layer='0')
# --- план ---
D.circ(cx, cy, R_FM, C)
D.circ(cx, cy, R_OUT, C); D.circ(cx, cy, R_IN, C)
D.ring_hatch(cx, cy, R_OUT, R_IN)
D.circ(cx, cy, R_VUT, T)
D.circ(cx, cy, R_SUMP_T, C); D.circ(cx, cy, R_SUMP_B, C)
D.circ(cx, cy, R_COLB, T)
D.circ(cx, cy, R_COL, C); D.circ(cx, cy, R_HOLE, C)
D.ring_hatch(cx, cy, R_COL, R_HOLE)
D.axes(cx, cy, R_FM)
# диаметры
D.diam(cx, cy, R_FM, 128, SC, trad=3900)
D.diam(cx, cy, R_OUT, 142, SC, trad=3900)
D.diam(cx, cy, R_IN, 156, SC, trad=3900)
# марки элементов (КЖ: без стрелки)
def mark(txt, r, ang, dx, dy):
    b = math.radians(ang); tp = (cx + r * math.cos(b), cy + r * math.sin(b))
    note(txt, '', (tp[0] + dx, tp[1] + dy), tp, sc=SC, arrow='none')
mark('Фм-1', (R_OUT + R_FM) / 2, 40, 650, 500)
mark('См-1', (R_IN + R_OUT) / 2, 22, 1100, 400)
mark('Км-1', (R_COL + R_HOLE) / 2, 45, 990, 990)
# разрезы
section('1', (cx + R_FM + 600, cy), (cx - R_FM - 600, cy), sc=SC)   # стрелки вверх: слева 180°
section('2', (cx, cy + R_FM + 600), (cx, cy - R_FM - 600), sc=SC)
# --- спецификация элементов ---
colw = [w * SC for w in (15, 60, 65, 10, 15, 20)]
x0 = X0 + W - 250 - 250 - sum(colw)          # рамкаға тимейді
ytop = Y0 + 250 + 2750 + 600 + 750 + 3 * 400
sh.text('Спецификация элементов', x0 + sum(colw) / 2, ytop + 250, 175, att=7, layer='0')
D.table(x0, ytop, colw,
        [['Фм-1', 'лист 3.1...3.4', 'Фундамент Фм-1', '1', '', ''],
         ['См-1', 'лист 4.1...4.3', 'Стена См-1', '1', '', ''],
         ['Км-1', 'лист 5.1', 'Колонна Км-1', '1', '', '']],
        hdr=['Поз.', 'Обозначение', 'Наименование', 'Кол.', 'Масса ед., кг', 'Примечание'])
L.dump(r'D:\_claude_work\otst\s4\ops\s21.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's21')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
