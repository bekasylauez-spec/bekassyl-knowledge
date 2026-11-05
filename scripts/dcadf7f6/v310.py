# -*- coding: utf-8 -*-
"""3.10 Выпуски из фундамента: эскизы + спецификация (copy of template sheet 1464F, stretched)."""
import sys, json
import lib
from lib import *
import ab

TX, TY = 249867, 271898
X0 = float(sys.argv[1]) if len(sys.argv) > 1 else 1460000.0
Y0 = 450000
DX, DY = X0 - TX, Y0 - TY
P = 'V310:'
R = lambda h: P + h
W = lambda x0, y0, x1, y1: [x0 + DX, y0 + DY, x1 + DX, y1 + DY]
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + 14860, Y0 + 10510])
op(t='copywin', win=[TX - 1, TY - 1, TX + 14851, TY + 10501], d=[DX, DY], pre=P)

# ---------- 1) Вп-1 section -> column B (x +3600)
op(t='movewin', win=W(250500, 275950, 253200, 278400), d=[3600, 0])
# ---------- 2) wall-dowel sketch: down 900 (title stays), slab 300->700, bars 1220 / 2810 (+ pos 3 = 3000)
op(t='erase', h=[R('14CB2')])                         # slab hatch (re-hatched below)
op(t='movewin', win=W(250400, 278550, 253300, 281400), d=[0, -900])
op(t='stretch', win=W(250400, 277300, 253300, 278200), d=[0, -400])       # slab bottom, prep, feet, bottom dims
op(t='stretch', win=W(250400, 279080, 253300, 279180), d=[0, 360])        # short bar top 860 -> 1220
op(t='stretch', win=W(250400, 280220, 253300, 280320), d=[0, 810])        # long bar top 2000 -> 2810
# bars: pos1 short x 252106 (foot left), pos2 long x 252226 (foot right), pos3 new x 252600 foot right
zt = 279170 - 900; zb = 278870 - 900 - 400
pl([(252600 + DX, zb + 30 + DY), (252600 + DX, zt + 3000 + DY)], layer='диам20', lw=40)
pl([(252600 + DX, zb + 30 + DY), (252850 + DX, zb + 30 + DY)], layer='диам20', lw=40)
hatch([[(251602 + DX, zb + DY), (252882 + DX, zb + DY), (252882 + DX, zt + DY), (251602 + DX, zt + DY)]], pat='ANSI36', sc=5, layer='Размеры')
dim((251602 + DX, zt + 3000 + DY), (251602 + DX, zt + DY), (250950 + DX, zt + DY), 1.5708, 25)
op(t='settext', h=R('16D88'), s='{\\LВыпуск из фундамента для стен (поз. 1;2;3)}')
# ---------- 3) Разрез 1-1 (column A): slab 300->700, 160|160 -> 210|210
op(t='stretch', win=W(250500, 272850, 253300, 273800), d=[0, -400])
op(t='stretch', win=W(252150, 272850, 253400, 275400), d=[40, 0])
op(t='stretch', win=W(250400, 272850, 252115, 275400), d=[-40, 0])
op(t='erase', h=[R('14F74')])
op(t='eraseregion', win=W(252700, 273200, 253200, 274200))
hatch([[(251601 + DX, 273340 + DY), (252637 + DX, 273340 + DY), (252637 + DX, 274040 + DY), (251601 + DX, 274040 + DY)]], pat='ANSI36', sc=5, layer='Размеры')
chain_v([v + DY for v in (273340, 273440, 273590, 273790, 273990, 274040)], 252637 + DX, 252950 + DX, 25)
op(t='move', h=[R('16E23')], d=[0, -50])
for zz in (273590, 273440):
    pl([(251894 + DX, zz + DY), (252371 + DX, zz + DY)], layer='диам8', lw=25)
# ---------- 4) Вп-1 plan section: 400 -> 500 column
cx, cy = 252183 + 3600, 277244
op(t='dimval', win=W(cx - 1300, cy - 1300, cx + 1300, cy + 1300), pairs=[[40, '50'], [50, '50'], [160, '200'], [200, '200']])
op(t='erase', h=[R('14EDF'), R('151BD')])
for yb, oy in ((277044, 276757), (277444, 277732)):
    note('4;5', '(∅25)', (252510 + 3600 + DX, oy + DY), None, sc=25) if False else op(t='note', l1='4;5', l2='(∅25)', origin=[252510 + 3600 + DX, oy + DY], targets=[[x + 3600 + DX, yb + DY] for x in (251983, 252183, 252383)], scale=25, ts=2.5, arrow='oblique', layer='Размеры', align='Center')
op(t='dimval', win=W(250300, 277000, 253300, 281500), pairs=[[650, '650'], [700, '700']])
op(t='settext', h=R('15258'), s='{\\LВыпуск Вп-1}')
# ---------- 5) texts
SW = [X0 - 5, Y0 - 5, X0 + 14855, Y0 + 10505]
for fr, to, l2 in (('1;2(∅10)', '1;2;3(∅20)', 'ш.100'), ('1(∅20)', '4(∅25)', ' '), ('2(∅20)', '5(∅25)', ' '),
                   ('1;2', '4;5', '(∅25)')):
    op(t='noteset', win=SW, **{'from': fr, 'to': to, 'l2': l2})
op(t='levelval', h=R('146F4'), old='-2.000', value='-4.000', tag='lv1')
op(t='levelval', h=R('14F6A'), old='-2.000', value='-4.000', tag='lv2')
op(t='settext', h=R('19528'), s='Выпуски из фундамента Фм-1.\\PСпецификация')
op(t='settext', h=R('1952A'), s='3.10')
# ведомость деталей X1 520x420 L1880, X2 402x302 L1408
for hh, v in (('17875', '420'), ('17876', '420'), ('17878', '520'), ('1787E', '520'), ('17884', '1880'),
              ('17890', '302'), ('17891', '302'), ('17893', '402'), ('17899', '402'), ('1789F', '1408')):
    op(t='settext', h=R(hh), s=v)
# ---------- 6) spec table
TB = R('178AB')
op(t='trows', h=TB, mode='ins', at=6, **{'from': 5}, n=1)
cells = [[2, 10, '13'],
         [4, 0, '1'], [4, 3, '20'], [4, 9, '2070'], [4, 10, '1023'],
         [5, 0, '2'], [5, 3, '20'], [5, 9, '3660'], [5, 10, '1014'],
         [6, 0, '3'], [6, 1, 'ГОСТ 34028-2016'], [6, 2, '%%C'], [6, 3, '20'], [6, 4, 'A'], [6, 5, '500С'], [6, 8, 'L='], [6, 9, '3850'], [6, 10, '2018'],
         [9, 0, '4'], [9, 3, '25'], [9, 9, '1550'], [9, 10, '4'],
         [10, 0, '5'], [10, 3, '25'], [10, 9, '2150'], [10, 10, '4'],
         [11, 9, '1880'], [11, 10, '4'], [12, 9, '1408'], [12, 10, '4']]
op(t='tset', h=TB, cells=cells)
op(t='trowfmt', h=TB, src=5, dst=[6])
op(t='tdump', h=TB)
op(t='save')
r = ab.run(lib.OPS, 'v310', 2400)
print('\n'.join(l for l in ab.log().splitlines() if 'err' in l.lower() or 'fail' in l.lower() or 'copywin' in l or 'stretch' in l or 'movewin' in l)[-3000:])
