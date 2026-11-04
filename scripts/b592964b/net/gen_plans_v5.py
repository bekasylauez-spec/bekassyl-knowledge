# лист 3: три плана лестницы по типу плана пользователя/Байтурсынова, геометрия — разрез 1-1 и модель v18
import json, sys, math
S = sys.argv[1]
B = chr(92)
ops = [{"t": "import", "file": S + "/km/bait.dwg", "h": ["63F844", "63F845", "63F846", "63F847"], "base": [0, 0], "to": [0, -100000], "pre": "SEC:"}]
HOLD = (0, -100000)                       # временная площадка для шаблонов
T = ["B:arYA", "B:arYAc", "B:brk", "B:ax1", "B:axB", "B:axV", "B:st3870_0", "B:ttl"]
for h in T: ops.append({"t": "clone", "h": h, "base": [0, 0], "to": list(HOLD), "tag": "T:" + h})
ops.append({"t": "eraseregion", "win": [2615500, -1755500, 2656500, -1727000], "mode": "inside", "keep": ["671846", "671848", "671849"]})
TM = {"6730F6": "B:arYA", "6730F7": "B:arYAc", "673107": "B:brk", "672FF1": "B:ax1", "672FF2": "B:axB", "672FF3": "B:axV", "67308D": "B:st3870_0", "671828": "B:ttl"}
th = lambda h: "T:" + TM.get(h, h)
def P(p, **k): ops.append(dict({"t": "pl", "p": p, "layer": "Размеры", "color": 256, "lw": 5}, **k))
def R(x0, y0, x1, y1, **k): P([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], closed=True, **k)

def plan(bx, by, kind, title):
    g = lambda X, Y: [bx + K * X, by + K * Y]          # план в М 1:50 на листе М 1:100
    xend = 6800 if kind == "A" else 5600
    # --- стена здания и ось 1
    R(*g(-700, 2300), *g(xend + 700, 2600), layer="0", lw=-1)
    ops.append({"t": "hatch", "loops": [[g(-700, 2300), g(xend + 700, 2300), g(xend + 700, 2600), g(-700, 2600)]],
                "pat": "ANSI36", "sc": 25 * K, "ang": math.pi / 2, "layer": "0", "color": 256})
    def ax(src, p0, p1, tag):
        ops.append({"t": "clone", "h": th(src), "base": [0, 0], "to": [0, 0], "tag": tag})
        ops.append({"t": "sp_set", "h": tag, "pts": [[0, *p0], [1, *p1]]})
    ax("672FF1", g(-1000, 2450), g(xend + 1600, 2450), kind + ":ax1")
    ax("672FF3", g(3400, 2900), g(3400, -2200), kind + ":axV")
    ax("672FF2", g(5600, 2900), g(5600, -2200), kind + ":axB")
    # --- что видно в плане
    if kind == "A":
        land = [(3800, 5600)]; mids = []; beams = [3870]; brk_at = 2600
        ya = [(x, x + 300) for x in range(2600, 3500, 300)]            # нижняя часть марша до разрыва
        yb = []
        gr = [(x, x + 300) for x in range(5600, 6800, 300)]
        brk = [3870]
    else:
        land = [(3800, 5600)]; mids = [(0, 1400)]; beams = [1330, 3870]; gr = []
        ya = [(x, x + 300) for x in range(1400, 3500, 300)]
        yb = [(x, x + 300) for x in range(1700, 3800, 300)]
        brk_at = 2600 if kind == "B" else None
        brk = [1330, 3870] + ([5600] if kind == "C" else [])
    for x0, x1 in land + mids: R(*g(x0, 70), *g(x1, 1930))
    for x0, x1 in ya + gr: R(*g(x0, 95), *g(x1, 925))
    for x0, x1 in yb: R(*g(x0, 1075), *g(x1, 1905))
    if kind == "A":
        for y in (95, 925): P([g(2450, y), g(6800, y)], w=50 * K)
        P([g(6775, 70), g(6775, 950)], w=50 * K)
        for y in (1075, 1905): P([g(3800, y), g(5600, y)], w=50 * K)
        P([g(5575, 950), g(5575, 1930)], w=50 * K)
    else:
        for y in (95, 925, 1075, 1905): P([g(0, y), g(5600, y)], w=50 * K)
        for x in (25, 5575): P([g(x, 70), g(x, 1930)], w=50 * K)
    # балки Б1 (□140) по осям стоек, стойки Ст1, кронштейны К1
    for x in beams: R(*g(x - 70, 70), *g(x + 70, 1930), color=244, lw=30)
    for x in (1330, 3870):
        for y in (0, 2000):
            tg = f"{kind}:st{x}_{y}"
            ops.append({"t": "clone", "h": th("67308D"), "base": [0, 0], "to": [0, 0], "tag": tg})
            ops.append({"t": "xform", "h": tg, "base": [2670579.84, -1725799.92 + HOLD[1]], "to": g(x, y), "s": 0.875 * K / 3.5})
    for x in brk:
        y0 = 1930 if x == 5600 else 2070
        R(*g(x - 30, y0), *g(x + 30, 2300), color=244, lw=30)
    # разрыв марша
    if brk_at:
        tg = kind + ":brk"
        ops.append({"t": "clone", "h": th("673107"), "base": [0, 0], "to": [0, 0], "tag": tg})
        ops.append({"t": "mcset", "h": tg, "set": {"StartPoint": g(brk_at - 150, 1000), "EndPoint": g(brk_at + 250, 0), "ClipZonePoint": g(brk_at + 250, 0)}})
    # стрелки подъёма
    def arrow(xs, xe, y, tag):
        d = 1 if xe > xs else -1
        ops.append({"t": "clone", "h": th("6730F7"), "base": [2658449.95, -1729069.95 + HOLD[1]], "to": g(xs, y), "tag": tag + "c"})
        ops.append({"t": "clone", "h": th("6730F6"), "base": [0, 0], "to": [0, 0], "tag": tag})
        ops.append({"t": "sp_set", "h": tag, "pts": [[0, *g(xs + 150 * d, y)], [1, *g(xe, y)]]})
    if kind == "A":
        arrow(3650, 2750, 510, "A:arYA"); arrow(6650, 5750, 510, "A:arGR")
    else:
        arrow(3650, 1550 if kind == "C" else 2750, 510, kind + ":arYA"); arrow(1550, 3650, 1490, kind + ":arYB")
    # размеры
    def dim(p1, p2, dl, rot=0):
        ops.append({"t": "dim", "h": "673132", "p1": g(*p1), "p2": g(*p2), "dl": g(*dl), "rot": rot, "lfac": 1.0 / K})
    xs = [0, 1400, 3800, 5600] + ([6800] if kind == "A" else [])
    for a, b in zip(xs, xs[1:]): dim((a, -100), (b, -100), (b, -800))
    dim((0, -100), (xend, -100), (xend, -1150))
    dim((3400, -1600), (5600, -1600), (5600, -1600))
    ys = [70, 950, 1050, 1930, 2300]
    for a, b in zip(ys, ys[1:]): dim((xend, a), (xend, b), (xend + 500, b), math.pi / 2)
    # выноски
    def note(s, org, tgt): ops.append({"t": "note", "l1": s, "origin": g(*org), "target": g(*tgt), "scale": 100})
    if kind != "A": note("Ст1", (1900, -500), (1370, -40))
    note("Ст1", (4800, -500), (3910, -40))
    note("Б1", (4450, 1350), (3940, 1200))
    if kind != "A": note("Б1", (750, 1350), (1260, 1200))
    note("Л", (5000, 400), (4900, 95))
    note("Л", (5000, 1650), (4900, 1905))
    note("К1", (4900, 3250), (3900, 2200))
    if kind == "A": note("Л", (6300, 1400), (6400, 925))
    if kind == "C": note("К1", (6300, 3250), (5630, 2200))
    # разрезы: 1-1 вдоль лестницы (взгляд к зданию), 2-2 у стойки x=3870, 3-3 у стойки x=1330
    def cut(a, b, view, num):
        # знак разреза СПДС (SPDSSECTION из альбома Байтурсынова): концы a, b; Dir=1 — взгляд влево от направления a->b
        ab = [b[0] - a[0], b[1] - a[1]]
        left = [-ab[1], ab[0]]
        d = 1 if left[0] * view[0] + left[1] * view[1] > 0 else -1
        tg = f"{kind}:sec{num}"
        ops.append({"t": "clone", "h": "SEC:63F844", "base": [0, 0], "to": [0, 0], "tag": tg})
        ops.append({"t": "sp_set", "h": tg, "pts": [[0, *g(*a)], [1, *g(*b)]]})
        ops.append({"t": "mcset", "h": tg, "set": {"Word": num, "Dir": d}})
    cut((-700, 500), (xend + 1000, 500), (0, 1), "1")
    cut((3700, -350), (3700, 2850), (1, 0), "2")
    if kind != "A": cut((1150, -350), (1150, 2850), (-1, 0), "3")
    # заголовок
    tg = kind + ":ttl"
    ops.append({"t": "clone", "h": th("671828"), "base": [2655900.0, -1720100.0 + HOLD[1]], "to": g(xend / 2, 3700), "tag": tg})
    ops.append({"t": "settext", "h": tg, "s": "{" + B + "L" + title + "}", "w": 16000})

K = 2
plan(2619800, -1735400, "A", "План на отм. 0.000 (между отм. -0,980 и +1,800)   М 1:50")
plan(2639900, -1735400, "B", "План на отм. +3,800; +7,200   М 1:50")
plan(2619800, -1749000, "C", "План на отм. +10,700   М 1:50")
ops.append({"t": "erase", "h": [th(h) for h in T] + ["SEC:63F844", "SEC:63F845", "SEC:63F846", "SEC:63F847"]})
ops.append({"t": "settext", "h": "671846", "s": "Планы лестницы"})
json.dump(ops, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops))
