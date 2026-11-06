# scheme 4.1 step 2: dims, marks, stamp, title (all cloned from analog 2.1 objects)
import json, math, sys
import mb
from sch import F0, PX0, PY0, AXX, AXY, P, COLS

ops = []
def add(**k): ops.append(k); return k
HP = math.pi / 2
# ---- outer dims: interaxis + overall (proto 3444D8 = СПДС, dsc 100) ----
xs = list(AXX.values()); ys = list(AXY.values())
R1, R2 = -2700, -3700
for i, (a, b) in enumerate(zip(xs, xs[1:])):
    add(t='dim', h='3444D8', p1=P(a, 0), p2=P(b, 0), dl=P(a, R1), rot=0, tag='DXB%d' % i)
add(t='dim', h='3444D8', p1=P(xs[0], 0), p2=P(xs[-1], 0), dl=P(xs[0], R2), rot=0, tag='DXB_ALL')
L1, L2 = 55050 - 2700, 55050 - 3700
for i, (a, b) in enumerate(zip(ys, ys[1:])):
    add(t='dim', h='3444D8', p1=P(55050, a), p2=P(55050, b), dl=P(L1, a), rot=HP, tag='DYL%d' % i)
add(t='dim', h='3444D8', p1=P(55050, ys[0]), p2=P(55050, ys[-1]), dl=P(L2, ys[0]), rot=HP, tag='DYL_ALL')

# ---- binding dims (proto 3E14B8, 0_ANNOT_Dimensions) ----
def near(v, axes):
    return min(axes.items(), key=lambda kv: abs(kv[1] - v))
seenx, seeny = set(), set()
k = 0
for c in sorted(COLS, key=lambda c: (c['y'], c['x'])):
    an, ax = near(c['x'], AXX); bn, by = near(c['y'], AXY)
    x0, x1 = c['x'] - c['bx'] / 2, c['x'] + c['bx'] / 2
    y0, y1 = c['y'] - c['by'] / 2, c['y'] + c['by'] / 2
    onx = x0 - 1 < ax < x1 + 1; ony = y0 - 1 < by < y1 + 1
    # x binding: below the column (row А columns: below them), else above
    kx = (an, round(x0 - ax), round(x1 - ax)) if onx else (an, round(c['x'] - ax), 'c')
    if kx not in seenx:
        seenx.add(kx)
        yd = y0 - 700 if c['y'] < 3000 else y1 + 700
        yr = y0 if c['y'] < 3000 else y1
        if onx:
            add(t='dim', h='3E14B8', p1=P(x0, yr), p2=P(ax, yr), dl=P(x0, yd), rot=0, tag='BX%da' % k)
            add(t='dim', h='3E14B8', p1=P(ax, yr), p2=P(x1, yr), dl=P(x0, yd), rot=0, tag='BX%db' % k)
        else:
            add(t='dim', h='3E14B8', p1=P(ax, c['y']), p2=P(c['x'], c['y']), dl=P(ax, yd), rot=0, tag='BX%dc' % k)
    ky = (bn, round(y0 - by), round(y1 - by)) if ony else (bn, round(c['y'] - by), 'c', round(c['x']))
    if ky not in seeny:
        seeny.add(ky)
        xd = x0 - 700 if c['x'] < 60000 else x1 + 700
        xr = x0 if c['x'] < 60000 else x1
        if ony:
            add(t='dim', h='3E14B8', p1=P(xr, y0), p2=P(xr, by), dl=P(xd, y0), rot=HP, tag='BY%da' % k)
            add(t='dim', h='3E14B8', p1=P(xr, by), p2=P(xr, y1), dl=P(xd, y0), rot=HP, tag='BY%db' % k)
        else:
            add(t='dim', h='3E14B8', p1=P(c['x'], by), p2=P(c['x'], c['y']), dl=P(xd, by), rot=HP, tag='BY%dc' % k)
    k += 1

# ---- marks: SPDS note with arrow at the column corner facing the plan centre ----
CX, CY = (55050 + 86250) / 2, 14500
MOVE = json.load(open(mb.S + r'\w\markfix.json', encoding='utf-8')) if __import__('os').path.exists(mb.S + r'\w\markfix.json') else {}
for i, c in enumerate(COLS):
    sx = 1 if c['x'] < CX else -1; sy = 1 if c['y'] < CY else -1
    f = MOVE.get(c['id'], {})
    sx = f.get('sx', sx); sy = f.get('sy', sy); d = f.get('d', 1300)
    tx, ty = c['x'] + sx * c['bx'] / 2, c['y'] + sy * c['by'] / 2
    ox, oy = tx + sx * d, ty + sy * d
    tag = 'MK_' + c['id']
    add(t='clone', h='3E14F4', tag=tag)
    add(t='sp_set', h=tag, pts=[[0] + P(ox, oy), [1] + P(tx, ty)])
    add(t='notetxt', h=tag, l1=c['mark'], angle=0 if sx > 0 else math.pi)

# ---- stamp (2.1 -> A2 frame), title ----
dx = -42000
for h, tg in (('3E2B5F', 'ST_BLK'), ('3E2B60', 'ST_NAME'), ('3E2B62', 'ST_NO')):
    add(t='clone', h=h, base=[0, 0], to=[dx, 0], tag=tg)
add(t='settext', h='ST_NAME', s='Схема расположения колонн')
add(t='settext', h='ST_NO', s='4.1')
add(t='clone', h='344830', tag='TITLE', base=[-1546078, -1720272], to=[PX0 + 15600 - 3600, PY0 + 29000 + 2500])
add(t='settext', h='TITLE', s='{\\LСхема расположения колонн}')
add(t='save')
if 'run' in sys.argv:
    print(mb.run(ops, 'sch2', 1500))
