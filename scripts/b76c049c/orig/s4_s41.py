# -*- coding: utf-8 -*-
"""Лист 4.1: Опалубочный чертеж стены См-1 + Разрез 1-1 (опалубка). М 1:50, A2 (аналог an10).
Разрез 1-1 — через стену на 180° (труба Ø350, углублённый лоток); стрелки вверх: слева — наружу, справа — к оси."""
import math
import s4_lib as L
from s4_lib import op, pl, dim, lev, section, Sheet
from s4_geo import *
import s4_draw as D
SC = 50
X0, Y0 = 339000.0, -300000.0
W, H = 29700.0, 21000.0
op(t='ltload', names=['CENTER2', 'HIDDEN2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + W + 10, Y0 + H + 10])
sh = Sheet('4.1', 'Опалубочный чертеж стены См-1', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT; V = math.pi / 2
HID = dict(layer=T, ltype='HIDDEN2', ltscale=10)
# ================= план =================
cx, cy = X0 + 8600.0, Y0 + 10600.0
R = D.R_CON
sh.text(L.title_u('Опалубочный чертеж стены См-1'), cx, cy + R + 1250, 175, att=8, layer='0')
D.circ(cx, cy, R, C)
D.circ(cx, cy, R_OUT, C); D.circ(cx, cy, R_IN, C)
D.ring_hatch(cx, cy, R_OUT, R_IN)
D.circ(cx, cy, D.R_LT_O, C); D.circ(cx, cy, D.R_LT_I, C)
D.ring_hatch(cx, cy, D.R_LT_O, D.R_LT_I)
for s in (1, -1):
    pl([(cx - D.R_LT_O * math.cos(math.asin(400 / D.R_LT_O)), cy + s * 400), (cx - R_IN * math.cos(math.asin(400 / R_IN)), cy + s * 400)], layer=T)
    pl([(cx - R_IN, cy + s * D.D_PIPE / 2), (cx - R_OUT, cy + s * D.D_PIPE / 2)], **HID)      # отверстие Ø350 (под консолью)
D.axes(cx, cy, R)
for r, a in ((R, 108), (R_OUT, 120), (R_IN, 132), (D.R_LT_O, 144), (D.R_LT_I, 156)):
    D.diam(cx, cy, r, a, SC, trad=3500)
a = math.radians(40)
dim((cx + R_OUT * math.cos(a), cy + R_OUT * math.sin(a)), (cx + R * math.cos(a), cy + R * math.sin(a)), (cx + R_OUT * math.cos(a), cy + R_OUT * math.sin(a)), rot=a, sc=SC)
dim((cx - 4750, cy - 400), (cx - 4750, cy + 400), (cx - 4600, cy), V, SC, tx=(cx - 4600 + 2, cy + 230))
D.note('Отв. %%c350', '', (cx - 3800, cy + 900), (cx - (R_IN + R_OUT) / 2, cy + D.D_PIPE / 2), sc=SC, arrow='arrow')
section('1', (cx - D.R_LT_I + 700, cy), (cx - R - 700, cy), sc=SC)
# ================= Разрез 1-1 =================
OX, zy = X0 + 27400.0, Y0 + 13300.0          # P(x, z): x — координата левой половины разреза (x<0)
P = lambda x, z: (OX + x, zy + z)
XB = -3900.0                                   # обрыв днища
sh.text(L.title_u('Разрез 1-1 (опалубка)'), OX - 5150, zy + Z_TOP + 1450, 175, att=8, layer='0')
CUT = (-R - 10, Z_FBOT - 300, XB, Z_TOP + 10)
g = D.clip_geom(D.section_geom(dict(deep=1, pipe=1), dict()), *CUT)
D.draw_section(P, g, cut=CUT)
D.break_line(P, XB, Z_FBOT - (R_BOT1 + XB) / 12.0, Z_F15 + (-XB - R_SUMP_T) / 12.0)
# ось отверстия
pl([P(-R_OUT - 300, D.Z_PIPE), P(-R_IN + 250, D.Z_PIPE)], layer=T, ltype='CENTER2', ltscale=10)
# --- горизонтальные размеры: верх ---
zt = Z_TOP
pts = [(-R, zt), (-R_OUT, zt), (-R_IN, zt), (-D.R_LT_O, D.Z_LT_TOP), (-D.R_LT_I, D.Z_LT_TOP)]
for (a0, b0), (a1, b1) in zip(pts[:-1], pts[1:]):
    dim(P(a0, b0), P(a1, b1), P(-R, zt + 500), 0.0, SC)
dim(P(-R, zt), P(-R_IN, zt), P(-R, zt + 900), 0.0, SC)
# --- низ: выступ днища ---
dim(P(-R_FM, Z_FBOT), P(-R_OUT, Z_FBOT), P(-R_FM, Z_FBOT - 500), 0.0, SC)
dim(P(-R_OUT, Z_FBOT), P(-R_IN, Z_FBOT), P(-R_FM, Z_FBOT - 500), 0.0, SC)
# --- вертикальные слева ---
x1, x2 = -R - 450, -R - 900
ch = [(-R_FM, Z_FBOT), (-R_FM, Z_WBOT), (-R_OUT, D.Z_CON_ROOT), (-R, Z_TOP)]
for (a0, b0), (a1, b1) in zip(ch[:-1], ch[1:]):
    dim(P(a0, b0), P(a1, b1), P(x1, b0), V, SC)
for (a0, b0), (a1, b1) in (((-R_FM, Z_FBOT), (-R_FM, Z_WBOT)), ((-R_FM, Z_WBOT), (-R, Z_TOP))):
    dim(P(a0, b0), P(a1, b1), P(x2, b0), V, SC)
dim(P(-R, D.Z_CON_TIP), P(-R, Z_TOP), P(-R - 200, D.Z_CON_TIP), V, SC, tx=P(-R - 200 + 2, Z_TOP + 230))   # 90 — торец консоли
# отверстие: от -2.500 до оси, диаметр
dim(P(-R_OUT, Z_WBOT), P(-R_OUT, D.Z_PIPE), P(-R_OUT - 350, Z_WBOT), V, SC)
dim(P(-R_OUT, D.Z_PIPE - D.D_PIPE / 2), P(-R_OUT, D.Z_PIPE + D.D_PIPE / 2), P(-R_OUT - 700, D.Z_PIPE), V, SC, txt='%%c350')
# --- вертикальные: лоток (в канале) ---
xl = -(R_IN + D.R_LT_O) / 2
chd = [(-D.R_LT_I, D.Z_LT_D[0]), (-D.R_LT_O, D.Z_LT_D[1]), (-D.R_LT_O, D.Z_LT_TOP), (-R_IN, Z_TOP)]
for (a0, b0), (a1, b1) in zip(chd[:-1], chd[1:]):
    dim(P(a0, b0), P(a1, b1), P(xl, b0), V, SC, tx=P(xl + 2, b0 - 250) if b1 - b0 < 200 else None)
# --- отметки ---
xm = -R - 1350
lev(zy, P(-R, Z_TOP), SC, side='L', ext=-R - xm)
lev(zy, P(-R_FM, Z_WBOT), SC, side='L', ext=-R_FM - xm)
lev(zy, P(-R_FM, Z_FBOT), SC, side='L', ext=-R_FM - xm)
lev(zy, P(-D.R_LT_I, D.Z_LT_TOP), SC, side='R', ext=300)
lev(zy, P(-D.R_LT_O, D.Z_LT_D[1]), SC, side='R', ext=450)
sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 4.2, 4.3.',
          'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки не менее 3 шт. на стык. Длина нахлеста 61d. Стыки располагать вразбежку, чтобы площадь рабочей арматуры, стыкуемой в одном сечении, не превышала 50%.',
          'Расход арматуры в погонных метрах приведен с учетом нахлеста.',
          'Стержни, указанные в "Ведомости деталей", должны гнуться механическим способом в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня.'], w=8900)
L.dump(r'D:\_claude_work\otst\s4\ops\s41.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's41')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
