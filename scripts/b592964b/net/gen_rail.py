# листы 8-10: ограждения по типу Байтурсынова на разрезах лестницы БЦ (разрез 1-1 листа 4, разрезы листа 5)
import ezdxf, json, sys, math
from ezdxf import bbox
S = sys.argv[1]
doc = ezdxf.readfile(S + '/km/live.dxf'); msp = doc.modelspace()
ops = []
def grab(x0, y0, x1, y1, skip_types=(), skip=()):
    hs = []
    for e in msp:
        if e.dxftype() in skip_types or e.dxf.handle in skip: continue
        try: b = bbox.extents([e])
        except Exception: continue
        if not b.has_data: continue
        cx, cy = (b.extmin.x + b.extmax.x) / 2, (b.extmin.y + b.extmax.y) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1: hs.append(e.dxf.handle)
    return hs
def P(p, **k): ops.append(dict({"t": "pl", "p": p, "layer": "Размеры", "color": 256, "lw": -1}, **k))

# ---- стереть чертежи аналога на листах 8-10 (заголовки разрезов остаются)
for win, keep in (([2725000, -1748500, 2754013, -1714651], ["67A415", "67A584"]),
                  ([2754700, -1748500, 2783713, -1714651], ["67ABCE", "67A955"]),
                  ([2784400, -1748500, 2813413, -1714651], ["67AF2B", "67AF22"])):
    ops.append({"t": "eraseregion", "win": win, "mode": "inside", "keep": keep})

# ---- ступени разреза 1-1 (лист 4): верх подступенков = носки
def noses(h):
    pts = [(p[0], p[1]) for p in doc.entitydb[h].get_points()]
    ns = []
    for a, b in zip(pts, pts[1:]):
        if abs(a[0] - b[0]) < 1 and abs(a[1] - b[1]) > 1: ns.append(max((a, b), key=lambda q: q[1]))
    return sorted(ns)
YA = ["6731F8", "6731F6", "6731F4"]; YB = ["6731F7", "6731F5", "6731F3"]; GR = "673174"
X0, Z0 = 2671607.0, -1739654.3          # левый край площадок, отм. 0.000 на листе 4

def rail(xa, ya, xb, yb, dx, dy, posts_mid=False):
    """ограждение в фасаде: база (носки/верх площадки) от (xa,ya) до (xb,yb); +dx,dy — перенос на лист"""
    A = (xa + dx, ya + dy); Bp = (xb + dx, yb + dy)
    k = (Bp[1] - A[1]) / (Bp[0] - A[0])
    yl = lambda x: A[1] + k * (x - A[0])
    xs = [A[0], Bp[0]]
    if posts_mid:
        n = max(1, math.ceil(abs(Bp[0] - A[0]) / 1500))
        xs = [A[0] + (Bp[0] - A[0]) * i / n for i in range(n + 1)]
    for x in xs:
        P([[x - 25, yl(x) - 250], [x + 25, yl(x) - 250], [x + 25, yl(x) + 1200], [x - 25, yl(x) + 1200]], closed=True)
    for lo, hi in ((1150, 1200), (150, 200)):
        P([[A[0], yl(A[0]) + lo], [Bp[0], yl(Bp[0]) + lo], [Bp[0], yl(Bp[0]) + hi], [A[0], yl(A[0]) + hi]], closed=True)
    x0, x1 = sorted((A[0], Bp[0])); x = x0 + 150
    while x < x1 - 60:
        if all(abs(x - p) > 60 for p in xs): P([[x, yl(x) + 200], [x, yl(x) + 1150]], lw=5)
        x += 150

def flight(h, dx, dy):
    ns = noses(h); a, b = ns[0], ns[-1]
    rail(a[0], a[1], b[0], b[1], dx, dy)

def section11(dx, dy, skip=(), shift_marks=0):
    hs = grab(2662000, -1745000, 2684000, -1716000, skip_types=("SPDSFORMAT", "SPDSNOTEKNOT"), skip=("671CC3",) + tuple(skip))
    for h in hs: ops.append({"t": "clone", "h": h, "base": [0, 0], "to": [dx, dy], "tag": f"S{dx:.0f}:{h}"})
    if shift_marks:
        mk = [h for h in hs if doc.entitydb[h].dxftype() == "SPDSLEVELMARK"]
        ops.append({"t": "movegrp", "h": [f"S{dx:.0f}:{h}" for h in mk], "d": [shift_marks, 0]})

lvl = lambda L: Z0 + 1000 * L
# ---- Р1-Р1 (лист 8): наружные ограждения — марши YA, нижний марш, площадки по Y=0
d1 = (62013.0, -1500.0)
section11(*d1)
for h in YA + [GR]: flight(h, *d1)
for L in (0, 3.8, 7.2, 10.7): rail(X0 + 3500, lvl(L), X0 + 5600, lvl(L), *d1, posts_mid=True)
for L in (1.8, 5.5, 8.95): rail(X0, lvl(L), X0 + 1400, lvl(L), *d1, posts_mid=True)
# ---- Р2-Р2 (лист 9 слева): внутренние ограждения маршей YA и нижнего марша
d2 = (87813.0, 0.0)
right_dims = ("673399", "673248", "673257", "673271", "673287", "673296", "673350")
section11(*d2, skip=right_dims)
for h in YA + [GR]: flight(h, *d2)
# ---- Р3-Р3 (лист 9 справа): внутренние ограждения маршей YB
d3 = (102613.0, 0.0)
section11(*d3, skip=right_dims + ("673174", "6731F9", "673370"), shift_marks=-2000)
for h in YB: flight(h, *d3)

# ---- Р4-Р4, Р5-Р5 (лист 10): торцевые ограждения площадок по разрезам листа 5
yB = lambda L: -1739092.2 + 1000 * L
def section5(x0, x1, dx):
    hs = grab(x0, -1745000, x1, -1716000, skip_types=("SPDSFORMAT", "SPDSNOTEKNOT", "MTEXT"))
    for h in hs: ops.append({"t": "clone", "h": h, "base": [0, 0], "to": [dx, 0], "tag": f"T{dx:.0f}:{h}"})
d4 = 85413.0; section5(2700300, 2714500, d4)          # этажные площадки (у стойки x=3870)
ya0 = 2708180.8                                        # ось стойки Y=0 на правом разрезе листа 5
rail(ya0 + 70 + 880 + 100, yB(0), ya0 + 1930, yB(0), d4, 0, posts_mid=True)   # на отм. 0.000 — только половина без нижнего марша
for L in (3.8, 7.2, 10.7): rail(ya0 + 70, yB(L), ya0 + 1930, yB(L), d4, 0, posts_mid=True)
d5 = 112213.0; section5(2687000, 2700300, d5)          # промежуточные площадки (у стойки x=1330)
ya0 = 2708180.8 - 12896.2
for L in (1.8, 5.5, 8.95): rail(ya0 + 70, yB(L), ya0 + 1930, yB(L), d5, 0, posts_mid=True)
json.dump(ops, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops))
