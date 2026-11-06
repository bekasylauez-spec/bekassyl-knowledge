# 4.1 Block 3 scheme, step A: A1 frame, axes, columns, outer + binding dims, title (clones of Block 2 scheme objects)
import json, math, sys
sys.path.insert(0, r'..\t'); import mb
from b3plan import AXX, AXY, C
HP = math.pi / 2
F0 = (-1636903.1, -1749172.3)               # A1 frame origin (right edge stays at -1552803.1)
OLD = (-1612203.1, -1749172.3, -1552803.1, -1707172.3)
PX0, PY0 = F0[0] + 9000, F0[1] + 9300
X14 = AXX['14']
def P(x, y): return [PX0 + x - X14, PY0 + y]
ALL = [l.rstrip('\n').split('|') for l in open(mb.S + r'\w\all.txt', encoding='utf-8-sig')]
def old(t, lay=None):
    out = []
    for p in ALL:
        if len(p) < 7 or p[1] != t or not p[3]: continue
        if lay and p[2] != lay: continue
        a, b, c, d = map(float, p[3:7])
        if a >= OLD[0] - 1 and c <= OLD[2] + 1 and b >= OLD[1] - 1 and d <= OLD[3] + 1: out.append(p[0])
    return out
ops = []
def add(**k): ops.append(k); return k
# ---- frame A1 ----
add(t='mcset', h='37EA1B', set={'Format': 'A1', 'Origin': [F0[0], F0[1], 0]})
# ---- axes ----
xs, ys = list(AXX.items()), list(AXY.items())
xh = ['3444AD', '3444AE', '3444AF', '3444B0', '3444B1']
yh = ['34467D', '344687', '3446D3', '522422', '522423']
TOP = AXY['М'] + 1900
for i, (v, x) in enumerate(xs):
    h = xh[i] if i < len(xh) else 'B3AX_' + v
    if i >= len(xh): add(t='clone', h=xh[0], tag=h)
    add(t='axis', h=h, s=P(x, TOP), e=P(x, -5200), val=v)
for i, (v, y) in enumerate(ys):
    h = yh[i] if i < len(yh) else 'B3AY_' + v
    if i >= len(yh): add(t='clone', h=yh[0], tag=h)
    add(t='axis', h=h, s=P(AXX['22'] + 1400, y), e=P(X14 - 4700, y), val=v)
# ---- columns (rect + hatch) ----
oldr, oldh = old('LWPOLYLINE', 'О_Формат'), old('HATCH', '.')
for i, c in enumerate(C):
    if c['top_of']: continue
    x0, y0, x1, y1 = c['x'] - c['bx'] / 2, c['y'] - c['by'] / 2, c['x'] + c['bx'] / 2, c['y'] + c['by'] / 2
    pts = [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]
    hr, hh = 'B3R_' + c['id'], 'B3H_' + c['id']
    add(t='clone', h='3E166F', tag=hr); add(t='clone', h='3E1670', tag=hh)
    add(t='plset', h=hr, p=pts, closed=True)
    add(t='hatchset', h=hh, loops=[[p + [0] for p in pts]])
# ---- outer dims (proto DXB0, СПДС) ----
xv = [x for _, x in xs]; yv = [y for _, y in ys]
for i, (a, b) in enumerate(zip(xv, xv[1:])):
    add(t='dim', h='DXB0', p1=P(a, 0), p2=P(b, 0), dl=P(a, -2700), rot=0, tag='B3DX%d' % i)
add(t='dim', h='DXB0', p1=P(xv[0], 0), p2=P(xv[-1], 0), dl=P(xv[0], -3700), rot=0, tag='B3DX_ALL')
for i, (a, b) in enumerate(zip(yv, yv[1:])):
    add(t='dim', h='DXB0', p1=P(X14, a), p2=P(X14, b), dl=P(X14 - 2700, a), rot=HP, tag='B3DY%d' % i)
add(t='dim', h='DXB0', p1=P(X14, yv[0]), p2=P(X14, yv[-1]), dl=P(X14 - 3700, yv[0]), rot=HP, tag='B3DY_ALL')
# ---- binding dims (proto BD1, 0_ANNOT_Dimensions) ----
n = [0]
def dh(x1, x2, yr, yd, short=None):
    n[0] += 1; o = add(t='dim', h='BD1', p1=P(x1, yr), p2=P(x2, yr), dl=P(x1, yd), rot=0, tag='B3BD%d' % n[0])
    if short is not None: o['tx'] = P(short, yd + (450 if yd > yr else -350))
def dv(y1, y2, xr, xd, short=None):
    n[0] += 1; o = add(t='dim', h='BD1', p1=P(xr, y1), p2=P(xr, y2), dl=P(xd, y1), rot=HP, tag='B3BD%d' % n[0])
    if short is not None: o['tx'] = P(xd - 450 if xd < xr else xd + 450, short)
YA = -250 - 700                                   # below row А
dh(87050, 87700, -250, YA); dh(87700, 87950, -250, YA, short=87950 + 450)
dh(93850, 94300, -250, YA, short=93850 - 500); dh(94300, 94750, -250, YA, short=94750 + 500)
dh(130300, 133300, -250, YA)                      # А/21-22 centre
dh(135650, 136300, -250, YA); dh(136300, 136550, -250, YA, short=136550 + 450)
YL = 34350 + 700                                  # above row Л (700x700)
dh(87050, 87700, 34350, YL); dh(87700, 87750, 34350, YL, short=87750 + 400)
dh(129950, 130300, 34350, YL, short=129950 - 500); dh(130300, 130650, 34350, YL, short=130650 + 500)
dh(135850, 136300, 34350, YL, short=135850 - 500); dh(136300, 136550, 34350, YL, short=136550 + 450)
XL = 87050 - 700                                  # left of axis-14 columns
dv(-250, 0, 87050, XL, short=-125 - 300); dv(0, 850, 87050, XL)
dv(10300, 10500, 87050, XL, short=10300 - 400); dv(10500, 11400, 87050, XL)
dv(15150, 15500, 87050, XL, short=15150 - 450); dv(15500, 15850, 87050, XL, short=15850 + 450)
dv(38650, 39500, 87050, XL); dv(39500, 39750, 87050, XL, short=39750 + 400)
XR = 136550 + 900                                 # right of axis 22: stair columns, В/21-22
dv(0, 3150, 136300, XR); dv(3150, 5800, 136300, XR)
dv(10500, 10650, 133550, 133550 + 700, short=10650 + 450)
for ax in ('18',):                                # upper columns on beams: 2500 from В / Е
    x = AXX[ax]
    dv(10500, 13000, x, x + 1100); dv(21000, 23500, x, x + 1100)
# ---- title over plan centre ----
add(t='move', h=['TITLE'], d=[P((xv[0] + xv[-1]) / 2, 0)[0] - (OLD[0] + 25298.5), (PY0 + TOP + 1400) - (OLD[1] + 40605)])
# ---- erase Block 2 plan objects ----
add(t='erase', h=oldr + oldh + old('DIMENSION'))
add(t='save')
if __name__ == '__main__':
    json.dump(ops, open(mb.S + r'\ops\sch_a.json', 'w', encoding='utf-8'), ensure_ascii=False)
    if 'run' in sys.argv:
        out = mb.run(ops, 'sch_a', 900); print(out[-2500:])
