# Разрез лестницы КМ Чертеж БЦ: ступени 300 x <=230 (равные в марше), косоуры по линии носков.
# Координаты относительно грани левой колонны (X0, Y0 = земля). Конвенции чертежа пользователя:
# излом косоура у этажной площадки x=4870, косоур 160, площадки от x=70 (левая колонна) до 6825 (правая).
import json, math, sys

X0, Y0 = 2686878, -1671080
XF, XL, XR, XOUT = 4870, 70, 6825, 6965
T, D = 300, 160
LEV = [980, 2780, 4780, 6480, 8180, 9930, 11680]
# (ручка косоура, ручка ступеней, нижний уровень, верхний уровень, 'dep' = от этажа вверх влево / 'arr' = к этажу)
FL = [("66CB9A", "66CB96", 0, 1, "dep"), ("66C642", "66CB95", 1, 2, "arr"),
      ("66CB99", "66CB94", 2, 3, "dep"), ("66C63F", "66CB93", 3, 4, "arr"),
      ("66CB01", "66CB92", 4, 5, "dep"), ("66C049", "66CB91", 5, 6, "arr")]


def nris(rise):
    return math.ceil(rise / 230 - 1e-9)


def A(p):
    return [round(X0 + p[0], 3), round(Y0 + p[1], 3)]


ops, info = [], []
for hs, hst, i, j, kind in FL:
    zl, zu = LEV[i], LEV[j]
    n = nris(zu - zl); h = (zu - zl) / n; s = h / T
    xm = XF - n * T                       # излом у промежуточной площадки
    ang = math.atan(s); dv = D / math.cos(ang)
    if kind == "dep":                     # этаж справа внизу -> промежуточная слева вверху
        top = [(XR, zl), (XF, zl), (xm, zu), (XL, zu)]
        # низ: наклон = верх - dv; пересечения с zl-D и zu-D
        xb1 = XF - (dv - D) / s
        xb2 = xm - (dv - D) / s
        bot = [(XL, zu - D), (xb2, zu - D), (xb1, zl - D), (XR, zl - D)]
        st = [(XF - T, zl)]
        for k in range(1, n + 1):
            x = XF - k * T
            st += [(x, zl + (k - 1) * h), (x, zl + k * h)]
            if k < n:
                st.append((x - T, zl + k * h))
        st = st[1:]
        st.insert(0, (XF - T, zl))
    else:                                 # промежуточная слева внизу -> этаж справа вверху
        top = [(XL, zl), (xm, zl), (XF, zu), (XR, zu)]
        xb1 = xm + (dv - D) / s
        xb2 = XF + (dv - D) / s
        bot = [(XR, zu - D), (xb2, zu - D), (xb1, zl - D), (XL, zl - D)]
        st = []
        for k in range(1, n + 1):
            x = xm + k * T
            if k > 1:
                st.append((x, zl + (k - 1) * h))
            else:
                st.append((x, zl))
            st.append((x, zl + k * h))
        # x последнего подступенка = xm + n*T = XF
    poly = top + bot
    # порядок как у пользователя: начать с правой точки верха
    ops.append({"h": hs, "op": "pts", "closed": True, "pts": [A(p) for p in poly]})
    ops.append({"h": hst, "op": "pts", "closed": False, "pts": [A(p) for p in st]})
    info.append((f"{zl}->{zu}", n, round(h, 1), n - 1, xm))

# нижний марш: от +0.980 у наружной грани правой колонны вниз вправо к земле
zl0 = LEV[0]; n = nris(zl0); h = zl0 / n; s = h / T; ang = math.atan(s); dv = D / math.cos(ang)
xg = XOUT + zl0 / s                       # верх косоура (линия носков) у земли
xgb = XOUT + (zl0 - dv) / s
ops.append({"h": "66D428", "op": "pts", "closed": True,
            "pts": [A(p) for p in [(xg, 0), (XOUT, zl0), (XOUT, zl0 - dv), (xgb, 0)]]})
st = [(XOUT, zl0)]
for k in range(1, n + 1):
    x = XOUT + (k - 1) * T
    st += [(x, zl0 - k * h)] if k == 1 else [(x, zl0 - (k - 1) * h), (x, zl0 - k * h)]
    if k < n:
        st.append((x + T, zl0 - k * h))
# упростить: убрать повторы
cl = []
for p in st:
    if not cl or (abs(cl[-1][0] - p[0]) > 1e-6 or abs(cl[-1][1] - p[1]) > 1e-6):
        cl.append(p)
ops.append({"h": "66B2F0", "op": "pts", "closed": False, "pts": [A(p) for p in cl]})
info.append((f"0->{zl0}", n, round(h, 1), n - 1, xg))

# размеры над верхним маршем: изломы косоура верхнего марша
xm_top = XF - nris(LEV[6] - LEV[5]) * T
ops += [{"h": "66B747", "op": "dim", "p1": A((XL, 11680)), "p2": A((xm_top, 11680))},
        {"h": "66B775", "op": "dim", "p1": A((xm_top, 11680)), "p2": A((XF, 11680))}]
json.dump(ops, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
for r in info:
    print(r)
