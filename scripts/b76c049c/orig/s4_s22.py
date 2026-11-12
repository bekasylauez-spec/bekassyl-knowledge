# -*- coding: utf-8 -*-
"""Лист 2.2: Схема расположения элементов на отм. +1.500. М 1:50, A2 (аналог an04)."""
import math
import s4_lib as L
from s4_lib import op, pl, note, section, dim, Sheet
from s4_geo import *
import s4_draw as D
SC = 50
X0, Y0 = 160800.0, -300000.0
W, H = 29700.0, 21000.0
op(t='ltload', names=['CENTER2', 'HIDDEN2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + W + 10, Y0 + H + 10])
sh = Sheet('2.2', 'Схема расположения элементов на отм. +1.500', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT
HID = dict(layer=T, ltype='HIDDEN2', ltscale=10)
cx, cy = X0 + 10300.0, Y0 + 10300.0
R = D.R_CON
sh.text(L.title_u('Схема расположения элементов на отм. +1.500'), cx, cy + R + 1250, 175, att=8, layer='0')
# --- план (вид сверху) ---
D.circ(cx, cy, R, C)                                   # консоль
D.circ(cx, cy, R_OUT, C); D.circ(cx, cy, R_IN, C)
D.ring_hatch(cx, cy, R_OUT, R_IN)                      # стена
D.circ(cx, cy, D.R_LT_O, C); D.circ(cx, cy, D.R_LT_I, C)
D.ring_hatch(cx, cy, D.R_LT_O, D.R_LT_I)               # стенка лотка
# углублённый участок лотка (180°, ширина 800)
for s in (1, -1):
    pl([(cx - D.R_LT_O * math.cos(math.asin(400 / D.R_LT_O)), cy + s * 400), (cx - R_IN * math.cos(math.asin(400 / R_IN)), cy + s * 400)], layer=T)
# труба Ø350 через стену (под стеной и консолью — невидимая)
for s in (1, -1):
    pl([(cx - R_IN, cy + s * D.D_PIPE / 2), (cx - R_OUT - D.PIPE_OUT, cy + s * D.D_PIPE / 2)], **HID)
pl([(cx - R_OUT - D.PIPE_OUT, cy - D.D_PIPE / 2), (cx - R_OUT - D.PIPE_OUT, cy + D.D_PIPE / 2)], **HID)
# оголовок и колонна
D.circ(cx, cy, D.R_PLATE, C)
D.circ(cx, cy, R_COL, T, ltype='HIDDEN2', ltscale=10)
D.circ(cx, cy, R_HOLE, T, ltype='HIDDEN2', ltscale=10)
D.axes(cx, cy, R)
# диаметры
for r, a in ((R, 108), (R_OUT, 120), (R_IN, 132), (D.R_LT_O, 144), (D.R_LT_I, 156)):
    D.diam(cx, cy, r, a, SC, trad=3500)
D.diam(cx, cy, D.R_PLATE, 225, SC, trad=900)
# 900 — вылет консоли; 800 — углублённый участок
a = math.radians(40)
p1 = (cx + R_OUT * math.cos(a), cy + R_OUT * math.sin(a)); p2 = (cx + R * math.cos(a), cy + R * math.sin(a))
dim(p1, p2, p1, rot=a, sc=SC)
xl = cx - (R_IN + D.R_LT_O) / 2
dim((xl, cy - 400), (xl, cy + 400), (cx - 4600, cy), math.pi / 2, SC, tx=(cx - 4600 + 2, cy + 230))
# марки
def mark(txt, r, ang, dx, dy):
    b = math.radians(ang); tp = (cx + r * math.cos(b), cy + r * math.sin(b))
    note(txt, '', (tp[0] + dx, tp[1] + dy), tp, sc=SC, arrow='none')
mark('См-1', (R_IN + R_OUT) / 2, 22, 1600, 500)
mark('Км-1', 1200, 50, 900, 900)
# разрезы
section('1', (cx + R + 600, cy), (cx - R - 600, cy), sc=SC)
section('2', (cx, cy + R + 600), (cx, cy - R - 600), sc=SC)
L.dump(r'D:\_claude_work\otst\s4\ops\s22.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's22')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
