# -*- coding: utf-8 -*-
"""Лист 3.1: Опалубочный чертеж фундамента Фм-1, Разрез 1-1 (опалубка). М 1:50, A2."""
import math, sys
import s4_lib as L
import s4_draw as D
from s4_lib import op, pl, dim, hatch, lev, section, note, Sheet
from s4_geo import *
SC = 50; k = SC / 100.0
X0, Y0 = 220200.0, -300000.0
op(t='ltload', names=['CENTER2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + 29710, Y0 + 21010])
op(t='eraseregion', win=[173100 - 10, Y0 - 10, 202800 + 10, Y0 + 21010])   # ескі пилот слоты
sh = Sheet('3.1', 'Опалубочный чертеж фундамента Фм-1. Разрез 1-1', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT
# ---------- план ----------
cx, cy = X0 + 8060.0, Y0 + 10300.0
sh.text(L.title_u('Опалубочный чертеж фундамента Фм-1'), cx, cy + R_FM + 1250, 175, att=8, layer='0')
def circ(r, layer, **kw):
    d = dict(t='circle', c=[cx, cy], r=r, layer=layer); d.update(kw); op(**d)
circ(R_FM, C)
for r in (R_OUT, R_IN, R_VUT): circ(r, T)
circ(R_SUMP_T, C); circ(R_SUMP_B, C)
for r in (R_COLB, R_COL, R_HOLE): circ(r, T)
AX = dict(layer=T, ltype='CENTER2', ltscale=20)
pl([(cx - R_FM - 500, cy), (cx + R_FM + 500, cy)], **AX)
pl([(cx, cy - R_FM - 500), (cx, cy + R_FM + 500)], **AX)
a = math.radians(145)
p1 = (cx + R_FM * math.cos(a), cy + R_FM * math.sin(a)); p2 = (cx - R_FM * math.cos(a), cy - R_FM * math.sin(a))
dim(p1, p2, p1, rot=a - math.pi, sc=SC, txt='%%c11600', tx=(cx + 3300 * math.cos(a) - 110 * math.sin(a), cy + 3300 * math.sin(a) + 110 * math.cos(a)))
def rnote(txt, r, ang, dx, dy):
    b = math.radians(ang); tp = (cx + r * math.cos(b), cy + r * math.sin(b))
    D.note(txt, '', (tp[0] + dx, tp[1] + dy), tp, sc=SC, arrow='arrow')
rnote('%%c3000', R_SUMP_T, 40, 900, 700)
rnote('%%c2400', R_SUMP_B, -40, 1100, -800)
rnote('%%c10600', R_OUT, 60, 500, 600)
rnote('%%c10000', R_IN, 30, -900, -500)
section('1', (cx + R_FM + 600, cy), (cx - R_FM - 600, cy), sc=SC)   # стрелки вверх: слева 180°
# ---------- разрез 1-1 ----------
sx, zy = X0 + 22545.0, Y0 + 10300.0 + 2534.0      # zy = Y отметки 0.000
P = lambda r, z: (sx + r, zy + z)
sh.text(L.title_u('Разрез 1-1 (опалубка)'), sx, zy + Z_WBOT + 2700, 175, att=8, layer='0')
ZB = -1500.0                                       # обрыв стены
TOP2 = [(0, Z_HOLE), (R_HOLE, Z_HOLE), (R_HOLE, Z_SUMP)] + TOP[1:]      # углубление Ø500 (дно -3.793)
NT = len(TOP2) + 1
right = TOP2 + [(R_IN, ZB), (R_OUT, ZB), (R_OUT, Z_WBOT), (R_FM, Z_WBOT)] + BOT
full = [P(r, z) for r, z in right] + [P(-r, z) for r, z in reversed(right[:-1])][:-1]
up = [P(-r, z) for r, z in reversed(right[:NT])] + [P(r, z) for r, z in right[1:NT]]
low = [P(r, z) for r, z in right[NT:]] + [P(-r, z) for r, z in reversed(right[NT:-1])]
pl(up, layer=C); pl(low, layer=C)
hatch([full], pat='ANSI36', sc=10, layer='Бетон штриховка')
podr = [(R_FM, Z_FBOT)] + POD + [(r, z) for r, z in reversed(BOT[1:])]
for s in (1, -1):
    pp = [P(s * r, z) for r, z in podr]
    pl(pp, layer=T, closed=True)
    hatch([pp], pat='AR-CONC', sc=0.4, layer='Бетон штриховка')
    # обрыв стены, шов стена/вут, низ колонны
    xm = s * (R_IN + R_OUT) / 2
    pl([P(s * R_IN - s * 80, ZB), P(xm - 40, ZB), P(xm - 15, ZB + 60), P(xm + 15, ZB - 60), P(xm + 40, ZB), P(s * R_OUT + s * 80, ZB)], layer=T)
    pl([P(s * R_COL, -2900), P(s * R_COL, Z_COLB), P(s * R_COLB, Z_SUMP)], layer=T)
    # уклон
    r0, r1 = 3900.0, 2500.0; zf = lambda r: Z_F15 + (r - R_SUMP_T) / 12.0
    pl([P(s * r0, zf(r0) + 230), P(s * r1, zf(r1) + 230)], layer=T)
    pl([P(s * (r1 + 160), zf(r1 + 160) + 262), P(s * r1, zf(r1) + 230), P(s * (r1 + 165), zf(r1 + 165) + 212)], layer=T)
    sh.text('i=1:12', sx + s * 3200, zy + zf(3200) + 300, 125, att=8, layer=L.L_DIM, rot=math.atan(1 / 12.0) * s)
pl([P(-R_COL, -2900), P(R_COL, -2900)], layer=T)
pl([P(0, Z_SBOT - 500), P(0, -1900)], layer=T, ltype='CENTER2', ltscale=20)
# размеры: низ
yb = zy + Z_SBOT - 100
xs = [-R_FM, -R_OUT, -R_IN, -R_BOT2, -R_BOT3, 0, R_BOT3, R_BOT2, R_IN, R_OUT, R_FM]
tx = [None, None, '3156', None, None, None, None, '3156', None, None]
zs = [Z_FBOT, Z_FBOT, Z_FBOT, Z_B2, Z_SBOT, Z_SBOT, Z_SBOT, Z_B2, Z_FBOT, Z_FBOT, Z_FBOT]
for i in range(len(xs) - 1):
    dim(P(xs[i], zs[i]), P(xs[i + 1], zs[i + 1]), (sx, yb - 500), 0.0, SC, txt=tx[i])
dim(P(-R_FM, Z_FBOT), P(R_FM, Z_FBOT), (sx, yb - 900), 0.0, SC)
# размеры: верх (вут, уклон, приямок)
yt = zy - 1850
xs2 = [-R_IN, -R_VUT, -R_SUMP_T, -R_SUMP_B, -R_HOLE, R_HOLE, R_SUMP_B, R_SUMP_T, R_VUT, R_IN]
zs2 = [Z_VUT, Z_F45, Z_F15, Z_SUMP, Z_SUMP, Z_SUMP, Z_SUMP, Z_F15, Z_F45, Z_VUT]
for i in range(len(xs2) - 1):
    dim(P(xs2[i], zs2[i]), P(xs2[i + 1], zs2[i + 1]), (sx, yt), 0.0, SC)
# вертикальные
V = math.pi / 2
for z0, z1 in ((Z_SBOT, Z_FBOT), (Z_FBOT, Z_WBOT), (Z_WBOT, Z_VUT)):
    dim(P(R_FM, z0), P(R_FM, z1), (sx + R_FM + 450, zy + z0), V, SC)
for z0, z1 in ((Z_FBOT, Z_WBOT), (Z_WBOT, Z_VUT)):
    dim(P(-R_FM, z0), P(-R_FM, z1), (sx - R_FM - 450, zy + z0), V, SC)
for z0, z1 in ((Z_SBOT, Z_SUMP), (Z_SUMP, Z_F15)):
    dim(P(950, z0), P(950, z1), (sx + 950, zy + z0), V, SC)
dim(P(R_HOLE, Z_SBOT), P(R_HOLE, Z_HOLE), (sx + 430, zy + Z_SBOT), V, SC)
dim(P(R_HOLE, Z_HOLE), P(R_HOLE, Z_SUMP), (sx + 430, zy + Z_SBOT), V, SC, tx=(sx + 432, zy + (Z_HOLE + Z_SUMP) / 2))
# толщина днища по нормали
rr = 3300.0; zt = Z_F15 + (rr - R_SUMP_T) / 12.0; n = math.hypot(1, 1 / 12.0)
q1 = P(-rr, zt); q2 = P(-rr - 500 / 12.0 / n, zt - 500 / n)
op(t='adim', h=L.A_DIM, p1=list(q1), p2=list(q2), dl=list(q1), dscale=SC)
# отметки
lev(zy, P(-R_FM, Z_WBOT), SC, side='L', ext=1000)
lev(zy, P(-R_FM, Z_FBOT), SC, side='L', ext=1000)
lev(zy, P(-R_BOT3, Z_SBOT), SC, side='L', ext=R_FM - R_BOT3 + 1000)
lev(zy, P(-R_OUT, Z_VUT), SC, side='L', ext=500 + 1000)
t_ = lev(zy, P(-950, Z_SUMP), SC, side='L', ext=0)        # выноска вверх: полка над приямком
op(t='sp_set', h=t_, pts=[[2, sx - 950, zy + Z_SUMP + 1050], [1, sx - 950 - 627, zy + Z_SUMP + 1350]])
pl([P(-R_OUT, Z_VUT), P(-R_IN, Z_VUT)], layer=T)
pl([P(R_OUT, Z_VUT), P(R_IN, Z_VUT)], layer=T)
D.note('Подготовка, бетон С8/10, t=100', '', P(-1950, Z_SBOT - 250), P(-1676, -3800), sc=SC, arrow='arrow')   # полка между выносными -5000 и -1844
sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.2, 3.3.',
          'Под фундаментом выполнить бетонную подготовку толщиной 100 мм, выступающую за грань фундамента на 100 мм.',
          'Фундамент Фм-1 бетонировать совместно с приямком и вутом, без рабочих швов.'], w=8900)
L.dump(r'D:\_claude_work\otst\s4\ops\s31.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's31')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
