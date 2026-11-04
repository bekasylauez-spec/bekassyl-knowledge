# лист 3: план кровли (навеса) по модели ЛИРА v18 — стропила по Y у x=0/1.33/3.87/5.6, прогоны по X у Y=0/1.0/2.0, □100x4
import json, sys, math
S = sys.argv[1]; B = chr(92)
K = 2
bx, by = 2639500.0, -1747200.0
g = lambda X, Y: [bx + K * X, by + K * Y]
ops = [{"t": "import", "file": S + "/km/bait.dwg", "h": ["63F881", "63F870"], "base": [0, 0], "to": [0, -100000], "pre": "BR:"}]
def P(p, **k): ops.append(dict({"t": "pl", "p": p, "layer": "Размеры", "color": 256, "lw": 5}, **k))
def R(x0, y0, x1, y1, **k): P([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], closed=True, **k)
# прогоны Пр1 вдоль X (Y = 0 / 1000 / 2000), стропила Пр1 вдоль Y (X = 0 / 1330 / 3870 / 5600), полоса 100
for Y in (0, 1000, 2000):
    R(*g(-50, Y - 50), *g(5650, Y + 50))
for X in (0, 1330, 3870, 5600):
    R(*g(X - 50, -50), *g(X + 50, 2050), lw=30)
# стойки Ст1 под стропилами
for X in (1330, 3870):
    for Y in (0, 2000):
        ops.append({"t": "clone", "h": "6724EA", "base": [2717190.9, -1753895.0], "to": g(X, Y), "s": K, "tag": f"RF:st{X}_{Y}"})
# стена здания
R(*g(-500, 2300), *g(6100, 2600), layer="0", lw=-1)
ops.append({"t": "hatch", "loops": [[g(-500, 2300), g(6100, 2300), g(6100, 2600), g(-500, 2600)]], "pat": "ANSI36", "sc": 25 * K, "ang": math.pi / 2, "layer": "0", "color": 256})
# уклон 10 % к наружной стороне (Y=0 ниже)
P([g(4600, 1700), g(4600, 300)], lw=-1)
ops.append({"t": "hatch", "loops": [[g(4600, 300), g(4570, 420), g(4630, 420)]], "pat": "SOLID", "layer": "Размеры", "color": 256})
ops.append({"t": "mtext", "at": g(4700, 1000), "h": 350, "s": "i = 10 %", "style": "Isocpeur", "att": 4, "rot": math.pi / 2, "layer": "Размеры"})
# выноски по образцу аналога: Пр1 на линии, Ст1 с полкой
ops.append({"t": "clone", "h": "BR:63F881", "base": [2644291.88, -1734798.66 - 100000], "to": g(2600, 2050), "tag": "RF:n1"})
ops.append({"t": "mcset", "h": "RF:n1", "set": {"FirstLine": "Пр1", "SecondLine": ""}})
ops.append({"t": "clone", "h": "BR:63F881", "base": [2644291.88, -1734798.66 - 100000], "to": g(2600, 1050), "tag": "RF:n2"})
ops.append({"t": "mcset", "h": "RF:n2", "set": {"FirstLine": "Пр1", "SecondLine": ""}})
ops.append({"t": "clone", "h": "BR:63F870", "base": [2640454.39, -1736918.50 - 100000], "to": [g(3870, -70)[0] + 594, g(3870, -70)[1] - 655], "tag": "RF:n3"})
ops.append({"t": "sp_set", "h": "RF:n3", "pts": [[1, *g(3870, -70)]]})
# размеры
def dim(p1, p2, dl, rot=0):
    ops.append({"t": "dim", "h": "673132", "p1": g(*p1), "p2": g(*p2), "dl": g(*dl), "rot": rot, "lfac": 1.0 / K})
for a, b in ((0, 1330), (1330, 3870), (3870, 5600)): dim((a, -100), (b, -100), (b, -450))
dim((0, -100), (5600, -100), (5600, -750))
for a, b in ((0, 1000), (1000, 2000)): dim((5600, a), (5600, b), (5900, b), math.pi / 2)
# заголовок — копия заголовка плана
ops.append({"t": "clone", "h": "B:ttl", "base": [2645500.0, -1728000.0], "to": g(2800, 3000), "tag": "RF:ttl"})
ops.append({"t": "settext", "h": "RF:ttl", "s": "{" + B + "LПлан кровли (навеса)   М 1:50}", "w": 16000})
ops.append({"t": "erase", "h": ["BR:63F881", "BR:63F870"]})
json.dump(ops, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops))
