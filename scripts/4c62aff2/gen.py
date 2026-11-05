# ФБС (2 ряда) и ПБ раскладка -> LISP для AutoCAD. Ақтау қыз (ул. Мереке 14/16)
import itertools, json, math, sys
sys.stdout.reconfigure(encoding='utf-8')
S = r"C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/4c62aff2-a55a-4637-9af2-523dd75c9ccb/scratchpad"

MOD = {2400: '1', 1200: '2', 900: '3'}          # модуль (блок + шов 20)
FBS = {'1': ('ФБС 24.4.6-т', 2380, 1300, 0.55), '2': ('ФБС 12.4.6-т', 1180, 640, 0.27), '3': ('ФБС 9.4.6-т', 880, 470, 0.20)}
COLS = [(8950, 0), (12650, 0), (8950, 5400), (12650, 5400), (8950, 7500), (12650, 7500), (8950, 12900), (12650, 12900)]
CZ = [(8750, 9150), (12450, 12850)]   # зоны колонн вдоль горизонтальных стен

def split_cols(a, b):
    segs, s = [], a
    for c0, c1 in CZ:
        if a < c0 < b:
            segs.append((s, c0)); s = c1
    segs.append((s, b)); return segs

# run: (orient, centre, w, s0, s1)  orient H: along u at v=centre ; V: along v at u=centre
def runs(row):
    R = []
    if row == 1:
        for v in (12900, 0, 7500, 5400):
            for s in split_cols(-200, 21800): R.append(('H', v, 400) + s)
        for u in (0, 21600):
            for s in ((7700, 12700), (5600, 7300), (200, 5200)): R.append(('V', u, 400) + s)
        R.append(('V', 21200, 400, 200, 5200))
        for u in (8950, 12650):
            for s in ((7700, 12700), (200, 5200)): R.append(('V', u, 400) + s)
    else:
        for v, e in ((12900, 21400), (7500, 21400), (5400, 21000), (0, 21000)):
            for s in split_cols(200, e): R.append(('H', v, 400) + s)
        for u in (0, 21600): R.append(('V', u, 400, -200, 13100))
        R.append(('V', 21200, 400, -200, 5600))
        for u in (8950, 12650):
            for s in ((7700, 12700), (200, 5200)): R.append(('V', u, 400) + s)
    return R

def fills(L):
    out = []
    for a in range(L // 2400 + 1):
        for b in range(4):
            for c in range(4):
                s = 2400 * a + 1200 * b + 900 * c; r = L - s
                if r < 0 or (40 < r < 200) or r > 900: continue
                cost = a + 1.3 * b + 1.6 * c + (2.0 + r / 300 if r > 40 else 0)
                out.append((cost, a, b, c, r))
    out.sort(); return out

def pieces_of(seq, s0):
    P, x = [], s0
    for t in seq:
        if t == 'M': P.append(('M', x, x + mono)); x += mono
        elif isinstance(t, tuple): P.append(('M', x, x + t[1])); x += t[1]
        else: P.append((MOD_INV[t], x, x + t)); x += t
    return P

MOD_INV = {2400: '1', 1200: '2', 900: '3'}

def arrangements(L, s0, limit=4):
    res = []
    for cost, a, b, c, r in fills(L)[:limit]:
        base = [2400] * a + [1200] * b + [900] * c
        items = base + ([('M', r)] if r > 40 else [])
        seen = set()
        for perm in itertools.permutations(items):
            key = tuple(x if not isinstance(x, tuple) else 'M' for x in perm)
            if key in seen: continue
            seen.add(key)
            res.append((cost, list(perm), r if r <= 40 else 0))
            if len(seen) > 400: break
    return res

def joints(P):
    return [p[1] for p in P[1:]]

layout = {1: [], 2: []}
line_joints = {}
for row in (1, 2):
    for (o, c, w, s0, s1) in runs(row):
        L = s1 - s0
        arr = arrangements(L, s0)
        best = None
        for cost, seq, gap in arr:
            P = pieces_of(seq, s0)
            J = joints(P)
            if row == 1:
                # монолит у торца (у колонны/узла), крупные блоки первыми
                mono_pos = [i for i, t in enumerate(seq) if isinstance(t, tuple)]
                pen = 0 if (not mono_pos or mono_pos[0] in (0, len(seq) - 1)) else 1
                order_pen = sum(1 for i in range(len(seq) - 1) if not isinstance(seq[i], tuple) and not isinstance(seq[i + 1], tuple) and seq[i] < seq[i + 1])
                sc = (cost + pen + 0.1 * order_pen,)
            else:
                J1 = [j for j in line_joints.get((o, c), []) if s0 < j < s1]
                dmin = min([abs(a - b) for a in J for b in J1], default=9999)
                sc = (0 if dmin >= 300 else 1, cost, -dmin)
            if best is None or sc < best[0]: best = (sc, P, J, gap)
        sc, P, J, gap = best
        if row == 1:
            line_joints.setdefault((o, c), []).extend(J + [s0, s1])
        else:
            J1 = [j for j in line_joints.get((o, c), []) if s0 < j < s1]
            dmin = min([abs(a - b) for a in J for b in J1], default=9999)
            if dmin < 300: print('WARN перевязка', row, o, c, s0, s1, dmin)
        layout[row].append(dict(o=o, c=c, w=w, s0=s0, s1=s1, P=P, gap=gap))

# --- сводка
cnt = {1: {}, 2: {}}; mono = {1: 0.0, 2: 0.0}
for row in (1, 2):
    for R in layout[row]:
        for t, a, b in R['P']:
            if t == 'M': mono[row] += (b - a) / 1000 * 0.4 * 0.6
            else: cnt[row][t] = cnt[row].get(t, 0) + 1
        print(row, R['o'], R['c'], R['s0'], R['s1'], [(t, b - a) for t, a, b in R['P']], 'gap', R['gap'])
colV = len(COLS) * 0.4 * 0.4 * 1.2
print('cnt', cnt, 'mono', mono, 'cols', colV)

# --- плиты
SL = {1500: ('15', 1.06, 0.395, '30'), 1200: ('12', 0.83, 0.31, '30'), 1000: ('10', 0.70, 0.26, '25')}
def wfill(W):
    best = None
    for a in range(7):
        for b in range(8):
            for c in range(4):
                s = 1500 * a + 1200 * b + 1000 * c; r = W - s
                if r < 0 or r > 120: continue
                sc = (a + b + c, r, b + c)
                if best is None or sc < best[0]: best = (sc, [1500] * a + [1200] * b + [1000] * c, r)
    return best[1], best[2]
spans = {'AB': (7510, 12890, '54'), 'BC': (5460, 7440, '20'), 'CD': (10, 5390, '54')}
zones = [('AB', 200, 8750), ('AB', 9150, 12450), ('AB', 12850, 21400),
         ('BC', 200, 8750), ('BC', 9150, 12450), ('BC', 12850, 21400),
         ('CD', 200, 8750), ('CD', 9150, 12450), ('CD', 12850, 21000)]
slabs = []
for sp, u0, u1 in zones:
    ws, r = wfill(u1 - u0)
    x = u0 + r / 2
    v0, v1, ln = spans[sp]
    for wd in ws:
        slabs.append(dict(mark='ПБ %s.%s-8-%s' % (ln, SL[wd][0], SL[wd][3]), u0=x + 5, u1=x + wd - 5, v0=v0, v1=v1,
                          vol=SL[wd][1] if ln == '54' else SL[wd][2]))
        x += wd
    print('zone', sp, u0, u1, ws, 'r', r)
from collections import Counter
sc = Counter(s['mark'] for s in slabs); print(sc)
json.dump(dict(layout=layout, slabs=slabs, cnt=cnt, mono=mono, colV=colV), open(S + '/layout.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
