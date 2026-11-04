# ограждения на разрезах Р1..Р5 — по образцу аналога: база = верх косоура/обвязки, низ пояса +150, поручень +1150..+1200,
# стойки 50 от -150 до +1200, балясины 20 с шагом <=150; контуры замкнутые, слой 0, цвет 1, вес 0.30 (как блоки аналога)
import ezdxf, json, sys, math, os
from ezdxf import bbox
S = sys.argv[1]
doc = ezdxf.readfile(S + '/km/live.dxf'); msp = doc.modelspace()
m = json.load(open(os.environ['TEMP'] + '/bc_map.json', encoding='utf-8-sig'))
keep = {v for k, v in m.items() if k.split(':')[0] in ('S62013', 'S87813', 'S102613', 'T85413', 'T112213')}
ops = []
# --- стереть прежние ограждения (полилинии без тега клона в зонах разрезов)
wins = [(2733400, -1742500, 2741200, -1722500), (2759200, -1742500, 2766800, -1722500), (2774000, -1742500, 2781000, -1722500),
        (2793500, -1741000, 2795700, -1725000), (2807400, -1741000, 2809600, -1725000)]
er = []
for e in msp:
    if e.dxftype() != 'LWPOLYLINE' or e.dxf.handle in keep: continue
    try: b = bbox.extents([e])
    except Exception: continue
    for x0, y0, x1, y1 in wins:
        if b.extmin.x >= x0 and b.extmax.x <= x1 and b.extmin.y >= y0 and b.extmax.y <= y1:
            er.append(e.dxf.handle); break
ops.append({"t": "erase", "h": er})
print('erase', len(er))

def P(p): ops.append({"t": "pl", "p": p, "closed": True, "layer": "0", "color": 1, "lw": 30})
def rail(xa, ya, xb, yb, dx=0.0, dy=0.0, mid_posts=False):
    A = (xa + dx, ya + dy); Bq = (xb + dx, yb + dy)
    if A[0] > Bq[0]: A, Bq = Bq, A
    k = (Bq[1] - A[1]) / (Bq[0] - A[0])
    yl = lambda x: A[1] + k * (x - A[0])
    x0, x1 = A[0] + 25, Bq[0] - 25                       # оси крайних стоек — внутри концов
    posts = [x0, x1]
    if mid_posts:
        n = max(1, math.ceil((x1 - x0) / 1500)); posts = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for x in posts:
        P([[x - 25, yl(x) - 150], [x + 25, yl(x) - 150], [x + 25, yl(x) + 1200], [x - 25, yl(x) + 1200]])
    for lo, hi in ((150, 200), (1150, 1200)):
        P([[x0 + 25, yl(x0 + 25) + lo], [x1 - 25, yl(x1 - 25) + lo], [x1 - 25, yl(x1 - 25) + hi], [x0 + 25, yl(x0 + 25) + hi]])
    # балясины между стойками, шаг <=150, 20 мм
    for a, b in zip(posts, posts[1:]):
        L = b - a - 50; n = max(1, math.ceil(L / 150)); st = L / n
        for i in range(1, n):
            x = a + 25 + st * i
            P([[x - 10, yl(x - 10) + 200], [x + 10, yl(x + 10) + 200], [x + 10, yl(x + 10) + 1150], [x - 10, yl(x - 10) + 1150]])

# верх косоура = верхняя наклонная грань контура косоура на разрезе пользователя (лист 4 в исходном положении)
def top_edge(h):
    pts = [(p[0], p[1]) for p in doc.entitydb[h].get_points()]
    best = None
    for a, b in zip(pts, pts[1:] + pts[:1]):
        if abs(a[0] - b[0]) > 100 and abs(a[1] - b[1]) > 100:
            if best is None or (a[1] + b[1]) > (best[0][1] + best[1][1]): best = (a, b)
    return best
# контуры косоуров на листе 4 сдвинуты пользователем/перестановкой — берём их клоны на листе 9 (S87813 = 2-2 YA, S102613 = YB)
def src_of(tag_prefix, h):
    return m.get(f"{tag_prefix}:{h}")
YA = ["673213", "673212", "673211"]; YB = ["673216", "673215", "673214"]; GR = "6731F9"
X0, Z0 = 2671607.0, -1739654.3
lvl = lambda L: Z0 + 1000 * L

def flights(prefix, hs, dx_src, dx_dst):
    for h in hs:
        hh = src_of(prefix, h)
        if not hh: print('no clone', prefix, h); continue
        a, b = top_edge(hh)
        rail(a[0] - dx_src, a[1], b[0] - dx_src, b[1], dx_dst, 0)
# Р2 (лист 9 слева) — клоны S87813 с YA и нижним маршем; Р3 — клоны S102613 с YB
flights('S87813', YA + [GR], 87813.0, 87813.0)
flights('S102613', YB, 102613.0, 102613.0)
# Р1 (лист 8) — наружные: марши YA, нижний марш, площадки по Y=0
flights('S62013', YA + [GR], 62013.0, 62013.0)
d1 = (62013.0, -1500.0)
for L in (0, 3.8, 7.2, 10.7): rail(X0 + 3800, lvl(L), X0 + 5600, lvl(L), *d1, mid_posts=True)
for L in (1.8, 5.5, 8.95): rail(X0, lvl(L), X0 + 1450, lvl(L), *d1, mid_posts=True)
# Р4, Р5 (лист 10) — торцевые ограждения площадок
yB = lambda L: -1739092.2 + 1000 * L
ya4 = 2708180.8 + 85413.0
rail(ya4 + 1050, yB(0), ya4 + 1930, yB(0), mid_posts=True)
for L in (3.8, 7.2, 10.7): rail(ya4 + 70, yB(L), ya4 + 1930, yB(L), mid_posts=True)
ya5 = 2708180.8 - 12896.2 + 112213.0
for L in (1.8, 5.5, 8.95): rail(ya5 + 70, yB(L), ya5 + 1930, yB(L), mid_posts=True)
json.dump(ops, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops))
