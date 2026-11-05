# Wall См-1 — sheet 5.3 «Горизонтальное армирование» by the analog sheet 4.3 (См-1 Тип С):
#  * horizontal bars are U-bars wrapping the free end: long leg + 170 + return leg (= lap 61d); two mirrored bars per row (one per face)
#  * per storey and piece: bottom bar (slab top + 50) and top bar (last row) drawn; note «pos / (Ød)» with leaders to both bars (analog)
#  * one Ø/step per storey for the whole wall (max As of the pieces, LIRA via wall_zones H); step chain on the right as in the analog
import json, math, sys
import gx, colsheet as C
sys.path.insert(0, 'arm'); import wall_zones as WZ

SX, SY = 948800.0, 455939.0
def W(x, y): return [SX + x, SY + y]
AX1 = 9810.0
L = [v - 347 for v in (15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497)]   # 5.3 block is 347 lower than 5.2
SLAB = 250.0
PIECES = [(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)]
LIRA = [(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)]
ENDS = [(False, True), (True, True), (True, True), (True, False)]
D = WZ.design('y', 0, LIRA, ENDS)
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)
# bar extents (sheet x): into the cross wall at axes 1/4 (analog 9705 / 29965), 20 mm cover at free ends
EXT = [(AX1 - 110, AX1 + 1225 - 25), (AX1 + 5875 + 20, AX1 + 7725 - 20), (AX1 + 12325 + 20, AX1 + 14175 - 20), (AX1 + 18825 + 25, AX1 + 20050 + 110)]
KIND = ['end', 'mid', 'mid', 'end']
NOTEX = [AX1 + 125 + 313, AX1 + 6800, AX1 + 13250, AX1 + 19925 - 312]   # analog: P1 a+313, P2/P3 on the axis, P4 b-312

def hor(s):
    """one (Ø, step) per storey: the piece with the largest As/m governs"""
    best = None
    for z in D:
        d, st = z['H'][s]; a = math.pi * d * d / 4 / st
        if best is None or a > best[0] + 1e-9: best = (a, d, st)
    return best[1], best[2]

vert = json.load(open('w/sm1_vert.json'))
P0 = max(int(k) for k in vert['POS'].values()) if vert['POS'] else 0
POS = {}; BARS = []
def pos_of(kind, d):
    k = (kind, d)
    if k not in POS: POS[k] = P0 + len(POS) + 1
    return POS[k]

ops = []
def add(**k): ops.append(k); return k
R = C.listwin(SX, SY, 59400, 42000)
EL = lambda r: 9000 < r['x0'] < 31500 and r['y0'] > 14000
er = [r['h'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and EL(r) and r['lay'].lower().startswith('диам')]
notes = [r['h'] for r in R if r['t'] == 'SPDSNOTEPOSITION' and EL(r)]
er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['x0'] > 29000 and r['y0'] > 14000]
add(t='clone', h=notes[0], base=[0, 0], to=[0, -200000], tag='HN_T')       # analog note kept as the template
add(t='erase', h=er + notes)
print('erase', len(er), 'notes', len(notes))

XD = 31130.0; XE = EXT[3][1]                                             # chain line (analog), ext. lines from the bar end
NOTE_LAY = 'Размеры'
k = 0
for s in range(7):
    yb, yt = L[s], L[s + 1]
    d, st = hor(s)
    y0 = yb + 50
    n = int((yt - SLAB - 50 - y0) // st)
    y1 = y0 + n * st
    rows = n + 1
    for i in range(4):
        x0, x1 = EXT[i]
        p = pos_of(KIND[i], d)
        BARS.append(dict(pos=p, d=d, long=int(round(x1 - x0)), ret=LAP(d), L=int(round(x1 - x0)) + 170 + LAP(d), n=2 * rows))
        for y in (y0, y1):
            add(t='pl', p=[W(x0, y), W(x1, y)], layer='диам%d' % d, lw=40)
        xn = NOTEX[i]; ym = (y0 + y1) / 2
        add(t='clone', h='HN_T', base=[0, 0], to=[0, 0], tag='HN%d' % k)
        add(t='spmove', h='HN%d' % k, items=[[0, SX + xn, SY + ym], [1, SX + xn, SY + y0], [2, SX + xn, SY + y1]])
        add(t='mcset', h='HN%d' % k, set={'FirstLine': str(p), 'SecondLine': '(%%%%C%d)' % d})
        k += 1
    # step chain on the right
    ch = []
    if s == 0: ch.append((yb, y0, ''))
    ch.append((y0, y1, '%dх%d' % (st, n)))
    nxt = (L[s + 1] + 50) if s < 6 else L[7]
    ch.append((y1, nxt, ''))
    for a, b, txt in ch:
        kw = dict(t='dim', h='WT_DV', p1=W(XE, a), p2=W(XE, b), dl=W(XD, (a + b) / 2), rot=math.pi / 2, txt=txt)
        if b - a < 450: kw['tx'] = W(XD + 330, (a + b) / 2)              # short: text beside the chain (analog)
        add(**kw)
add(t='erase', h=['HN_T'])
# texts
add(t='settext', h='11CB31', s='{\\LГоризонтальное армирование монолитной стены по оси А/1 стена См-1 (тол.250мм)}')
add(t='settext', h='11CB2C', s='5.3')
add(t='settext', h='11CB33', s='Горизонтальное армирование монолитной стены по оси А/1 стена См-1 (тол.250мм)')
add(t='settext', h='11CB2F', s='1. Общие указания см. л. - 1.1\\P2. Данный лист читать совместно с л. КЖ-5.1 ... 5.4\\P3. Горизонтальные стержни - П-образные, огибают свободный торец стены; стыки внахлестку без сварки, длина нахлеста 61d, вразбежку (не более 50% в одном сечении).\\P4. Первый ряд - 50 мм от верха плиты.\\P5. Расход арматуры в погонных метрах приведен с учетом нахлеста.\\P6. Стержни, указанные в "Ведомости деталей", гнуть механическим способом в холодном состоянии, радиус гиба 3d - 5d.')
add(t='save')
json.dump(dict(POS={'%s_%d' % k_: v for k_, v in POS.items()}, BARS=BARS), open('w/sm1_hor.json', 'w'), ensure_ascii=False)
json.dump(ops, open('ops/w53.json', 'w'), ensure_ascii=False)
print(len(ops), 'positions', POS)
for s in range(7): print(s, hor(s))
if '--run' in sys.argv: print(gx.run(ops, 'w53')[-400:])
