# Разрез лестницы КМ Чертеж БЦ: подступенки по 230, последний (верхний) — остаток; проступь 300.
# Изломы косоуров у площадок прежние (число подступенков то же). Косоур идёт по линии носков:
# площадка -> носок 0 -> носок n-1 (уклон 230/300) -> носок n (остаток) -> площадка.
import json, math, sys

X0, Y0 = 2686878, -1671080
XF, XL, XR, XOUT = 4870, 70, 6825, 6965
T, D, HS = 300, 160, 230
LEV = [980, 2780, 4780, 6480, 8180, 9930, 11680]
FL = [("66CB9A", "66CB96", 0, 1, "dep"), ("66C642", "66CB95", 1, 2, "arr"),
      ("66CB99", "66CB94", 2, 3, "dep"), ("66C63F", "66CB93", 3, 4, "arr"),
      ("66CB01", "66CB92", 4, 5, "dep"), ("66C049", "66CB91", 5, 6, "arr")]


def A(p):
    return [round(X0 + p[0], 3), round(Y0 + p[1], 3)]


def heights(H):
    n = math.ceil(H / HS - 1e-9)
    return n, [min(HS * k, H) for k in range(n + 1)]


def offset_poly(top):
    """смещение ломаной вниз на D: возвращает точки нижней линии в том же порядке"""
    lines = []
    for (x1, z1), (x2, z2) in zip(top, top[1:]):
        dx, dz = x2 - x1, z2 - z1
        L = math.hypot(dx, dz)
        nx, nz = dz / L, -dx / L
        if nz > 0:
            nx, nz = -nx, -nz
        lines.append(((x1 + D * nx, z1 + D * nz), (x2 + D * nx, z2 + D * nz)))
    out = [lines[0][0]]
    for (a1, a2), (b1, b2) in zip(lines, lines[1:]):
        out.append(inter(a1, a2, b1, b2))
    out.append(lines[-1][1])
    return out, lines


def inter(a1, a2, b1, b2):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a1, a2, b1, b2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < 1e-9:
        return a2
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def dedup(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    return out


def steps_pts(B, s, zl, hs):
    n = len(hs) - 1
    st = []
    for k in range(1, n + 1):
        x = B + s * k * T
        st += [(x, zl + hs[k - 1]), (x, zl + hs[k])]
    return dedup(st)


ops, info = [], []
for hs_, hst, i, j, kind in FL:
    zl, zu = LEV[i], LEV[j]
    n, hs = heights(zu - zl)
    if kind == "dep":
        B, s, lowfar, upfar = XF, -1, XR, XL
    else:
        B, s, lowfar, upfar = XF - n * T, 1, XL, XR
    nos = [(B + s * k * T, zl + hs[k]) for k in range(n + 1)]
    top = dedup([(lowfar, zl), nos[0], nos[n - 1], nos[n], (upfar, zu)])
    bot, _ = offset_poly(top)
    ops.append({"h": hs_, "op": "pts", "closed": True, "pts": [A(p) for p in top + bot[::-1]]})
    ops.append({"h": hst, "op": "pts", "closed": False, "pts": [A(p) for p in steps_pts(B, s, zl, hs)]})
    info.append((f"{zl}->{zu}", n, [hs[k] - hs[k - 1] for k in range(1, n + 1)]))

# нижний марш: от земли (носок 0 у земли) влево вверх к площадке +0.980 у наружной грани колонны
zl0 = LEV[0]
n, hs = heights(zl0)
B, s = XOUT + n * T, -1
nos = [(B + s * k * T, hs[k]) for k in range(n + 1)]
top = dedup([nos[0], nos[n - 1], nos[n]])
_, lines = offset_poly(top)
b_end = inter(lines[-1][0], lines[-1][1], (XOUT, 0), (XOUT, 1000))
b_mid = inter(lines[0][0], lines[0][1], lines[-1][0], lines[-1][1]) if len(lines) > 1 else None
b_gnd = inter(lines[0][0], lines[0][1], (0, 0), (10000, 0))
poly = top[::-1] + [b_gnd] + ([b_mid] if b_mid else []) + [b_end]
ops.append({"h": "66D428", "op": "pts", "closed": True, "pts": [A(p) for p in poly]})
st = steps_pts(B, s, 0, hs)[::-1]
ops.append({"h": "66B2F0", "op": "pts", "closed": False, "pts": [A(p) for p in st]})
info.append((f"0->{zl0}", n, [hs[k] - hs[k - 1] for k in range(1, n + 1)]))

# размеры ступени на марше +8.180 -> +9.930 (dep): 5-й подступенок
zr0, zr1 = 8180 + 4 * HS, 8180 + 5 * HS
xr = XF - 5 * T
ops += [{"h": "66EE32", "op": "dim", "p1": A((xr - T, zr1)), "p2": A((xr, zr1)), "dl": A((xr - T / 2, zr1 + 450))},
        {"h": "66EE23", "op": "dim", "p1": A((xr, zr0)), "p2": A((xr, zr1)), "dl": A((xr + 700, zr0))}]
json.dump(ops, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
for r in info:
    print(r)
