# лист 7: новые узлы 6 (кронштейн К1 [12П к стене здания) и 7 (прогон кровли □100x4 на стойке Ст1)
import ezdxf, json, sys, os, math
from ezdxf import bbox
S = sys.argv[1]
doc = ezdxf.readfile(os.path.join(S, 'km', 'live.dxf')); msp = doc.modelspace()
def grab(x0, y0, x1, y1):
    hs = []
    for e in msp:
        try: b = bbox.extents([e])
        except Exception: continue
        if not b.has_data: continue
        cx, cy = (b.extmin.x + b.extmax.x) / 2, (b.extmin.y + b.extmax.y) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1: hs.append(e.dxf.handle)
    return hs
ops = []
sw = lambda win, d: ops.append({"t": "stretchwin", "win": win, "d": d})
def pl(p, **k): ops.append(dict({"t": "pl", "p": p, "layer": "Размеры", "color": 256, "lw": -1}, **k))
def vbrk(x, top, h):           # вертикальный разрыв на конце горизонтального элемента
    m = top - h / 2
    pl([[x, top - h], [x, m - 25], [x + 50, m - 12.5], [x - 50, m + 12.5], [x, m + 25], [x, top]])
def hbrk(y, x0, x1):           # горизонтальный разрыв
    m = (x0 + x1) / 2
    pl([[x0, y], [m - 25, y], [m - 12.5, y + 50], [m + 12.5, y - 50], [m + 25, y], [x1, y]])
def txt(src, at_src, at, s): ops.append({"t": "clone", "h": src, "base": at_src, "to": at, "text": s})
def lead(p0, p1, x2): pl([p0, p1, [x2, p1[1]]])

# ================= узел 6: копия узла 4 со сдвигом
V = (-1302.0, -1260.0)
src = grab(2722400, -1754620, 2723420, -1753350)
for h in src: ops.append({"t": "clone", "h": h, "base": [0, 0], "to": list(V), "tag": "N6:" + h})
T = lambda h: "N6:" + h
ops.append({"t": "erase", "h": [T(h) for h in ("672ADB", "672B90", "672B91", "672B92", "672B93", "672B94", "672B95", "672B96",
                                             "672B84", "672B85", "672B86", "672B87", "672AF7", "672AF8", "673B1F")]})
X6 = 2722759.0 + V[0]; Yt = -1753868.3 + V[1]
# Б1 □140 -> К1 [12П: низ вверх на 20
sw([X6 - 20, -1755560, X6 + 700, -1755262], [0, 20])
Yb = Yt - 120; Ym = Yt - 60
Xw = X6 + 230                                                     # торец кронштейна = закладная
sw([2723176.2 + V[0] - 15, -1755700, 2723365.3 + V[0] + 20, -1754900], [Xw - (2723176.2 + V[0]), 0])
ops.append({"t": "settext", "h": T("672B4F"), "s": "К1"})
for h, s in ((T("672ADC"), "6"), (T("672ADD"), "3")): ops.append({"t": "settext", "h": h, "s": s})
# закладная -t10 250 и стена
pl([[Xw, Ym + 125], [Xw + 10, Ym + 125], [Xw + 10, Ym - 125], [Xw, Ym - 125]], closed=True)
Wt, Wb, Wr = Ym + 380, Ym - 380, Xw + 10 + 220
pl([[Xw + 10, Wt], [Xw + 10, Wb]])
hbrk(Wt, Xw + 10, Wr); hbrk(Wb, Xw + 10, Wr); vbrk(Wr, Wt, Wt - Wb)
ops.append({"t": "hatch", "loops": [[[Xw + 10, Wt], [Wr, Wt], [Wr, Wb], [Xw + 10, Wb]]], "pat": "ANSI31", "sc": 20, "layer": "Размеры", "color": 8})
for ya in (Ym + 90, Ym - 90):                                     # анкеры М12
    pl([[Xw - 25, ya], [Xw + 160, ya]], w=12)
# сварной шов кронштейна к закладной (как у стойки)
for i in range(6):
    y = Yt - 10 - i * 20
    pl([[Xw, y], [Xw - 10, y - 10]]); pl([[Xw, y - 10], [Xw - 10, y]])
# размеры
ops.append({"t": "dim", "h": "672B1F", "p1": [X6, Yt], "p2": [Xw, Yt], "dl": [X6, Yt + 160]})
ops.append({"t": "dim", "h": "672B12", "p1": [Xw + 10, Ym - 125], "p2": [Xw + 10, Ym + 125], "dl": [Wr + 120, Ym], "rot": math.pi / 2})
# подписи
txt("672B49", [2722856.6, -1754239.9], [Xw + 60, Wt + 120], "-t10")
txt("672B4B", [2722851.5, -1754284.9], [Xw + 55, Wt + 75], "С245")
lead([Xw + 5, Ym + 115], [Xw + 50, Wt + 70], Xw + 150)
txt("6727EC", [2718038.1, -1753846.9], [Xw + 40, Wb - 90], "Анкер М12, L=150")
lead([Xw + 120, Ym - 90], [Xw + 30, Wb - 100], Xw + 300)
txt("67264C", [2720140.0, -1754030.6], [Wr + 70, Wt - 60], "Стена здания")
ops.append({"t": "settext", "h": "672A8F", "s": "Узлы 3 - 7"})
for h in ("672ADD", "672B63"): ops.append({"t": "settext", "h": h, "s": "4"})

# ================= узел 7: стойка Ст1 + оголовок -t16 + прогон Пр1 □100x4
Xc, Ypt = 2724183.0, -1754756.0
bs = [2718359.3, -1753989.9]
for h in ["6727E3", "6727F6", "6727F7", "6727F8", "6727EA", "6727F0", "6727FD", "6727F1", "6727F2", "6727F3", "6727F4",
          "6727F9", "6727FA", "6727FB", "6727FC"] + ["%X" % k for k in range(0x6727FF, 0x67280D)]:
    ops.append({"t": "clone", "h": h, "base": bs, "to": [Xc, Ypt], "tag": "N7:" + h})
    ops.append({"t": "xform", "h": "N7:" + h, "base": [Xc, Ypt], "to": [Xc, Ypt], "ang": math.pi, "mirror": True})
# оголовок 320 -> 240
sw([Xc - 165, Ypt - 5, Xc - 155, Ypt + 25], [40, 0]); sw([Xc + 155, Ypt - 5, Xc + 165, Ypt + 25], [-40, 0])
Yp = Ypt + 16
pl([[Xc - 420, Yp], [Xc + 420, Yp]]); pl([[Xc - 420, Yp + 100], [Xc + 420, Yp + 100]])
vbrk(Xc - 420, Yp + 100, 100); vbrk(Xc + 420, Yp + 100, 100)
for i in range(6):                                                 # шов прогона к оголовку
    x = Xc - 55 + i * 20
    pl([[x, Yp], [x + 10, Yp + 10]]); pl([[x, Yp + 10], [x + 10, Yp]])
ops.append({"t": "dim", "h": "672B12", "p1": [Xc + 420, Yp], "p2": [Xc + 420, Yp + 100], "dl": [Xc + 560, Yp], "rot": math.pi / 2})
ops.append({"t": "dim", "h": "672B12", "p1": [Xc + 120, Ypt], "p2": [Xc + 120, Yp], "dl": [Xc + 560, Ypt], "rot": math.pi / 2})
ops.append({"t": "dim", "h": "672B1F", "p1": [Xc - 70, Ypt - 300], "p2": [Xc + 70, Ypt - 300], "dl": [Xc - 70, Ypt - 400]})
ops.append({"t": "dim", "h": "672B1F", "p1": [Xc - 120, Ypt], "p2": [Xc + 120, Ypt], "dl": [Xc - 120, Yp + 200]})
txt("672B4F", [2723128.8, -1753779.0], [Xc + 250, Yp + 140], "Пр1")
lead([Xc + 200, Yp + 100], [Xc + 240, Yp + 130], Xc + 320)
txt("672B53", [2722459.9, -1753882.0], [Xc - 330, Ypt - 190], "Ст1")
lead([Xc - 70, Ypt - 150], [Xc - 250, Ypt - 200], Xc - 340)
txt("672B49", [2722856.6, -1754239.9], [Xc + 230, Ypt - 70], "-t16")
txt("672B4B", [2722851.5, -1754284.9], [Xc + 225, Ypt - 115], "С245")
lead([Xc + 110, Ypt + 8], [Xc + 210, Ypt - 120], Xc + 330)
for h in ("672B62", "672B63", "672B64"):
    ops.append({"t": "clone", "h": h, "base": [0, 0], "to": [Xc - 2724145, -1754300 - (-1753437)], "tag": "M7:" + h})
ops.append({"t": "settext", "h": "M7:672B62", "s": "7"}); ops.append({"t": "settext", "h": "M7:672B63", "s": "4"})
json.dump(ops, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops), len(src))
