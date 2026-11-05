# Км-1 sheet 4.1 — sections 1-1 (hoops) and 2-2 (top П elements) at 1:25 (x4 on the 1:100 sheet, dims lfac 0.25).
import json, math, sys, gx
X0, Y0 = 706779.0, 455939.0
K = 4.0; LF = 0.25
b = 500.0
BARS_C = [(56, 56), (444, 56), (56, 444), (444, 444)]          # Ø32
BARS_M = [(250, 50), (450, 250), (250, 450), (50, 250)]         # Ø20
CEN = {'1': (17725.0, 37240.0), '2': (25975.0, 37240.0)}
R = json.load(open('w/k41_list2.json'))
KEEP = {'10AFEB', '10B0E9', '10B5D7', '10B5D8', '10B79F', '10B7A0'}
TPL = {'10B107', '10B14B'}
OLD = [r['h'] for r in R if 13000 < r['x0'] and r['x1'] < 31500 and r['y0'] > 26000 and r['y1'] < 41000 and r['h'].upper() not in KEEP | TPL]
ops = []
def add(**k): ops.append(k); return k
NOTE = dict(scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')

def sec(n):
    cx, cy = CEN[n]; ox, oy = cx - K * b / 2, cy - K * b / 2
    f = lambda x, y: [X0 + ox + K * x, Y0 + oy + K * y]
    T = 'K41s%s_' % n
    add(t='pl', p=[f(0, 0), f(b, 0), f(b, b), f(0, b)], closed=True, layer='Размеры', tag=T + 'COL')
    for i, (x, y) in enumerate(BARS_C): add(t='circle', c=f(x, y) + [0], r=K * 16, layer='диам32', lw=40, tag=T + 'C%d' % i)
    for i, (x, y) in enumerate(BARS_M): add(t='circle', c=f(x, y) + [0], r=K * 10, layer='диам20', lw=40, tag=T + 'M%d' % i)
    # dims: bottom and left chains 40 | 210 | 210 | 40
    yb = -200.0; xl = -200.0
    for i, (a, c) in enumerate(((0, 40), (40, 250), (250, 460), (460, 500))):
        o = dict(t='dim', h='10B107', p1=f(a, 0), p2=f(c, 0), dl=f((a + c) / 2, yb), rot=0, lfac=LF, txt='', tag=T + 'DB%d' % i)
        if c - a < 100: o['tx'] = f(a - 70 if a == 0 else c + 70, yb)
        add(**o)
        o = dict(t='dim', h='10B14B', p1=f(0, a), p2=f(0, c), dl=f(xl, (a + c) / 2), rot=math.pi / 2, lfac=LF, txt='', tag=T + 'DL%d' % i)
        if c - a < 100: o['tx'] = f(xl, a - 70 if a == 0 else c + 70)
        add(**o)
    return f, T

# ---- 1-1: hoops Х1 (square) + Х2 (diamond), 135° hooks with 100 mm tails ----
f, T = sec('1')
c0, c1 = 36.0, b - 36.0; tl = 70.0
add(t='pl', p=[f(c0 + 16 + tl, c1 - tl), f(c0 + 16, c1), f(c1, c1), f(c1, c0), f(c0, c0), f(c0, c1 - 16), f(c0 + tl, c1 - 16 - tl)], layer='диам8', tag=T + 'X1')
mt = c1; add(t='pl', p=[f(b / 2 - 12, mt - 12 - tl), f(b / 2 - 12, mt - 12), f(b / 2, mt), f(c1, b / 2), f(b / 2, c0), f(c0, b / 2), f(b / 2, mt), f(b / 2 + 12, mt - 12), f(b / 2 + 12, mt - 12 - tl)], layer='диам8', tag=T + 'X2')
add(t='note', l1='1;2', l2='', origin=f(b + 230, b + 190), targets=[f(56, 444 + 16), f(250, 450 + 10), f(444, 444 + 16)], **NOTE)
add(t='note', l1='1;2', l2='', origin=f(b + 230, -230), targets=[f(56, 56 - 16), f(250, 50 - 10), f(444, 56 - 16)], **NOTE)
add(t='note', l1='2', l2='', origin=f(b + 230, 250), targets=[f(450 + 10, 250)], **NOTE)
add(t='note', l1='Х1;Х2', l2='', origin=f(-230, b + 190), targets=[f(c0, 360), f((c0 + b / 2) / 2, (b / 2 + mt) / 2)], **NOTE)

# ---- 2-2: top view, П elements Ск1 (corner diagonals) and Ск2 (mid bars) ----
f, T = sec('2')
add(t='pl', p=[f(56, 56), f(444, 444)], layer='диам16', lw=40, tag=T + 'K1a')
add(t='pl', p=[f(56, 444), f(444, 56)], layer='диам16', lw=40, tag=T + 'K1b')
add(t='pl', p=[f(250, 50), f(250, 450)], layer='диам16', lw=40, tag=T + 'K2a')
add(t='pl', p=[f(50, 250), f(450, 250)], layer='диам16', lw=40, tag=T + 'K2b')
add(t='note', l1='Ск1', l2='', origin=f(b + 230, b + 190), targets=[f(380, 380)], **NOTE)
add(t='note', l1='Ск2', l2='', origin=f(b + 230, -230), targets=[f(330, 250), f(250, 120)], **NOTE)

ops.insert(0, dict(t='erase', h=OLD))
ops.append(dict(t='erase', h=sorted(TPL)))
ops.append(dict(t='save'))
json.dump(ops, open('ops/k41s.json', 'w'), ensure_ascii=False)
print(len(ops), 'erase', len(OLD))
if '--run' in sys.argv: print(gx.run(ops, 'k41s')[-1500:])
