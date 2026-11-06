# scheme 4.1 step 3: replace binding dims with an explicit, uncluttered set; fix crowded marks
import json, math, sys
import mb
from sch import P, COLS

HP = math.pi / 2
m = mb.tagmap()
ops = [{'t': 'erase', 'h': [v for k, v in m.items() if k.startswith('BX') or k.startswith('BY') or k.startswith('BD')]}]
def add(**k): ops.append(k); return k
n = [0]
def dh(p1, p2, yd, short=None):
    """horizontal dim between scheme points p1,p2 (same y used for ext origins), dim line at yd"""
    n[0] += 1; tg = 'BD%d' % n[0]
    o = add(t='dim', h='DXB0', p1=P(*p1), p2=P(*p2), dl=P(p1[0], yd), rot=0, tag=tg, layer='0_ANNOT_Dimensions')
    if short:
        o['tx'] = P(short, yd + (450 if yd > p1[1] else -350))
def dv(p1, p2, xd, short=None):
    n[0] += 1; tg = 'BD%d' % n[0]
    o = add(t='dim', h='DXB0', p1=P(*p1), p2=P(*p2), dl=P(xd, p1[1]), rot=HP, tag=tg, layer='0_ANNOT_Dimensions')
    if short:
        o['tx'] = P(xd - 450 if xd < p1[0] else xd + 450, short)

# --- X bindings below row А (dim line 700 under the column bottom -250) ---
Y = -250 - 700
dh((54399, -250), (55050, -250), Y)                     # 651
dh((55050, -250), (55299, -250), Y, short=55299 + 450)  # 249
dh((63700, -250), (64150, -250), Y, short=63700 - 500)  # 450
dh((64150, -250), (64600, -250), Y, short=64600 + 500)  # 450
dh((86000, -250), (86250, -250), Y, short=86000 - 450)  # 250
dh((86250, -250), (86900, -250), Y, short=86900 + 500)  # 650
# --- X bindings above row Д interior columns (dim line 700 over column top 16850) ---
Y = 16850 + 700
dh((54400, 16850), (55050, 16850), Y)                   # 650
dh((55050, 16850), (55100, 16850), Y, short=55100 + 400)  # 50
dh((63800, 16850), (64150, 16850), Y, short=63800 - 500)  # 350
dh((64150, 16850), (64500, 16850), Y, short=64500 + 500)  # 350
dh((86200, 16850), (86250, 16850), Y, short=86200 - 400)  # 50
dh((86250, 16850), (86900, 16850), Y, short=86900 + 500)  # 650
dh((79650, 16850), (83650, 16850), Y)                   # 4000 axis 12 -> column Д/12-13 centre
# --- Y bindings left of axis-9 columns ---
X = 54399 - 700
dv((54399, -250), (54399, 0), X, short=-125 - 300)      # 250
dv((54399, 0), (54399, 1050), X)                        # 1050
dv((54399, 27975), (54399, 29000), X)                   # 1025
dv((54399, 29000), (54399, 29275), X, short=29137 + 300)  # 275
X = 54400 - 700
dv((54400, 6650), (54400, 7000), X, short=6650 - 500)  # 350
dv((54400, 7000), (54400, 7350), X, short=7350 + 500)  # 350
# --- off-axis columns: centre to axis ---
dh((70650, 10000), (73650, 10000), 10000 + 950)        # Км-8: 3000 from axis 11
dv((71000, 7000), (71000, 10000), 71000 + 900)           # 3000 from axis Б
dv((74000, 7000), (74000, 11750), 74000 + 900)           # Км-8 on axis 11: 4750 from Б
dv((86900, 7000), (86900, 10500), 86900 + 900)           # В/13: 3500 from Б
dv((73925, 0), (73925, 1850), 73925 + 700)               # Км-9: 1850 from А
dh((79650, 1850), (83900, 1850), 1850 + 900)            # Км-9: 4250 from axis 12
# --- marks: move crowded ones ---
def mark(cid, sx, sy, d):
    c = [q for q in COLS if q['id'] == cid][0]
    tx, ty = c['x'] + sx * c['bx'] / 2, c['y'] + sy * c['by'] / 2
    ox, oy = tx + sx * d, ty + sy * d
    add(t='sp_set', h='MK_' + cid, pts=[[0] + P(ox, oy), [1] + P(tx, ty)])
    add(t='notetxt', h='MK_' + cid, angle=0 if sx > 0 else math.pi)
mark('А/13', 1, 1, 1100)
mark('Б/11', -1, -1, 1300)
mark('Б/12', -1, -1, 1300)
mark('А-Б/12-13', 1, 1, 1100)
mark('Б/12-13', -1, 1, 1300)
mark('А-Б/11', -1, 1, 1100)
mark('А-Б/12', -1, 1, 1100)
add(t='save')
if 'run' in sys.argv:
    print(mb.run(ops, 'sch3', 1500))
