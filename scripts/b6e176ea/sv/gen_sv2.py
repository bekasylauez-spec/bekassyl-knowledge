# -*- coding: utf-8 -*-
# СВ2 (vertical cross bracing between the columns of each row, middle bay) for the ЛК-1.1 / ЛК-1.2 / ЛК-2 albums.
# Writes sv/ops_con_<a>.json (accoreconsole, net/sc2.cs: tables, texts) and sv/ops_live_<a>.json (own AutoCAD, mc/rn.cs: SPDS).
# Sheet 6 (1:40): СВ2 in section 2-2, scheme «Связь вертикальная СВ2» and nodes 7, 8 drawn ×4 (1:10, dimlfac 0.25).
# Sheet 4: СВ2 on the columns plan + ведомость. Sheet 2: spec formula + «Расчёт массы металла» table. Sheet 1: ОД, ведомость листов.
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(HERE)
SRC11 = os.path.join(HERE, "c1.1.dwg")          # template source (unchanged copy of ЛК-1.1)

# templates in ЛК-1.1 (imported into every album as "T:<handle>", erased at the end)
T_KNOT, T_BREAK = "57E788", "5819C5"
T_WELD, T_J1, T_J2 = "581B2D", "581B33", "581B35"          # weld seam + its two end marks (node 6, top-right branch)
W_A, W_B = (2481623.5, -1755689.42), (2481688.1, -1755689.42)  # seam on the chord edge, branch on the +y side
T_TITLE = ("5819E4", "5819E2", "5819E3")                   # node title circle (block) + number + sheet
TITLE_C = (2481607.5, -1755369.5)
T_HEAD = "57C675"                                          # «Разрез 2 - 2» title MText (sheet 6)
T_DIM = "57C85D"                                           # sheet 6 linear dimension (clone)
TEMPL = [T_KNOT, T_BREAK, T_WELD, T_J1, T_J2] + list(T_TITLE)

GEO = {"1.1": dict(B=1700), "1.2": dict(B=1700), "2": dict(B=1830)}
CALC = {"1.1": ("587340", "587490"), "1.2": ("587490", "5875E0"), "2": ("589B42", "589C92")}


def V(x, y): return (float(x), float(y))
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def L(p): return [round(p[0], 2), round(p[1], 2)]


def isect(p, d, q, e):
    """intersection of lines p + s d and q + t e -> point"""
    den = d[0] * e[1] - d[1] * e[0]
    s = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return add(p, mul(d, s))


class Ops:
    def __init__(self):
        self.o = []
        self.n = 0

    def tag(self, p):
        self.n += 1
        return "%s%d" % (p, self.n)

    def pl(self, pts, layer, closed=False, lw=None, color=None, ltype=None, ltscale=None, w=None):
        m = {"t": "pl", "p": [L(p) for p in pts], "closed": closed, "layer": layer}
        if lw is not None: m["lw"] = lw
        if color is not None: m["color"] = color
        if ltype: m["ltype"] = ltype
        if ltscale: m["ltscale"] = ltscale
        if w: m["w"] = w
        self.o.append(m)

    def note(self, l1, origin, target, scale, arrow="open", l2=""):
        self.o.append({"t": "note", "l1": l1, "l2": l2, "origin": L(origin), "scale": scale, "arrow": arrow,
                       "ts": 2.5, "style": "ГОСТ 2.304", "layer": "Размеры", "targets": [L(target)]})

    def dim(self, p1, p2, dl, rot=0.0, lfac=None):
        m = {"t": "dim", "h": T_DIM, "p1": L(p1), "p2": L(p2), "dl": L(dl), "rot": rot}
        if lfac: m["lfac"] = lfac
        self.o.append(m)

    def clone(self, h, base, to, s=None, ang=None, text=None):
        tg = self.tag("c")
        m = {"t": "clone", "h": "T:" + h, "base": L(base), "to": L(to), "tag": tg}
        if s: m["s"] = s
        if text is not None: m["text"] = text
        self.o.append(m)
        if ang:
            self.o.append({"t": "xform", "h": tg, "base": L(to), "to": L(to), "ang": ang})
        return tg

    def mcset(self, tg, d):
        self.o.append({"t": "mcset", "h": tg, "set": d})


# ---------------------------------------------------------------- styles (as the user's node 6 / sheet 6)
MET = "_АР_Металл"
def outline(o, pts, color=1): o.pl(pts, MET, lw=30, color=color, ltscale=1)
def hidden(o, pts): o.pl(pts, MET, lw=5, color=1, ltype="HIDDEN", ltscale=160)
def center(o, a, b): o.pl([a, b], "КОНТУР", color=1, ltype="CENTER2", ltscale=4)


def brk(o, a, b, scale=40):
    tg = o.clone(T_BREAK, (0, 0), (0, 0))
    o.mcset(tg, {"Scale": scale, "StartPoint": L(a), "EndPoint": L(b), "ClipZonePoint": L(b)})


def weld(o, a, b, rot, k):
    """weld seam + end marks of node 6 mapped onto segment a->b (model), branch side = left of a->b"""
    s = math.hypot(b[0] - a[0], b[1] - a[1]) / (W_B[0] - W_A[0])
    for h in (T_WELD, T_J1, T_J2):
        o.clone(h, W_A, a, s=s, ang=rot)


def title(o, c, num, sheet, k=4):
    for h, txt in zip(T_TITLE, (None, num, sheet)):
        o.clone(h, TITLE_C, c, s=k, text=txt)


def knot(o, c, rack, knot_no, sheet, rx=230, ry=150, scale=40):
    tg = o.clone(T_KNOT, (0, 0), (0, 0))
    o.mcset(tg, {"Scale": scale, "Center": L(c), "Rack": L(rack), "XRadius": rx, "YRadius": ry, "Knot": knot_no, "Note": sheet})


def tube_between(x_left, x_right, p, u, h):
    """outline of a tube along u through p, cut by the vertical faces x_left / x_right -> 4 corners"""
    n = (-u[1], u[0])
    pts = []
    for x, sgn in ((x_left, 1), (x_right, 1), (x_right, -1), (x_left, -1)):
        q = add(p, mul(n, sgn * h))
        pts.append(isect(q, u, (x, 0), (0, 1)))
    return pts


def live_ops(a, pr):
    g = GEO[a]
    B = g["B"]
    o = Ops()
    o.o.append({"t": "maprst"})
    o.o.append({"t": "import", "file": SRC11, "h": TEMPL, "base": [0, 0], "to": [0, 0], "pre": "T:"})
    th = math.atan2(1800.0, B - 60.0)
    u, v = (math.cos(th), math.sin(th)), (-math.cos(th), math.sin(th))
    n = (-u[1], u[0])

    # ---------------- 1. section 2-2 (sheet 6, real size): СВ2 in the middle bay as a bracing symbol (like СВ1 in 3-3)
    cols = pr["s22cols"]
    c3, c4 = cols[2][0], cols[3][0]
    yb, yt = cols[2][1], cols[2][2]
    P1, P2 = V(c3 + 30, yb + 100), V(c4 - 30, yt - 100)
    P3, P4 = V(c4 - 30, yb + 100), V(c3 + 30, yt - 100)
    for A, Bp in ((P1, P2), (P3, P4)):
        o.pl([A, Bp], "0", lw=15, color=1, ltype="ACAD_ISO03W100", ltscale=2.0)
        d = sub(Bp, A); ln = math.hypot(*d); e = mul(d, 1 / ln)
        o.pl([add(A, mul(e, 100)), sub(Bp, mul(e, 100))], "Размеры", w=40)
    xm = (c3 + c4) / 2
    o.note("СВ2", V(xm - 140, yb + 330), add(P1, mul(sub(P2, P1), 0.22)), 40, arrow="none")
    knot(o, V(c3 + 30, yb + 100), V(c3 - 520, yb + 330), "7", "6", rx=200, ry=130)

    # ---------------- 2. columns plan (sheet 4): СВ2 along both rows in the middle bay
    pc = pr["plancols"][:12]
    rows = sorted(set(p[1] for p in pc), reverse=True)[:2]
    for i, y in enumerate(rows):
        xs = sorted(p[0] for p in pc if p[1] == y)
        x3, x4 = xs[2], xs[3]
        o.pl([V(x3 + 150, y), V(x4 - 150, y)], "Размеры", w=50)
        xm = (x3 + x4) / 2
        dy = -380 if i == 0 else 380
        o.note("СВ2", V(xm + 60, y + dy), V(xm - 160, y), 50, arrow="none")

    # ---------------- 3. scheme «Связь вертикальная СВ2» (sheet 6, 1:40, real size)
    X0, Yb = 2470150.0, -1753700.0
    Yt = Yb + 2000
    title_at = V(X0 + B / 2, Yt + 380)
    tg = o.clone(T_HEAD, (0, 0), (0, 0))
    o.o[-1]["h"] = T_HEAD                              # the title MText exists in every album: clone it directly
    o.o.append({"t": "xform", "h": tg, "base": pr["head22"], "to": L(title_at)})
    o.o.append({"t": "settext", "h": tg, "s": "{\\LСвязь вертикальная СВ2}", "w": 1900})
    for xc in (X0, X0 + B):
        outline(o, [V(xc - 30, Yb), V(xc + 30, Yb), V(xc + 30, Yt), V(xc - 30, Yt)] + [V(xc - 30, Yb)], color=0)
    WA = V(X0 + 30, Yb + 100)                         # lower-left work point
    WB = V(X0 + B - 30, Yb + 100)                     # lower-right
    O = isect(WA, u, WB, v)                           # crossing
    pa = tube_between(X0 + 30, X0 + B - 30, WA, u, 20)
    outline(o, pa + [pa[0]], color=5)
    # second diagonal: two pieces cut by the continuous one
    for sgn in (1, -1):
        edge_p = add(O, mul(n, sgn * 20))             # edge of the continuous tube on this side
        m = (-v[1], v[0])
        far_x = X0 + 30 if sgn > 0 else X0 + B - 30
        pts = []
        for k in (1, -1):
            q = add(O, mul(m, k * 20))
            pts.append((isect(q, v, (far_x, 0), (0, 1)), isect(q, v, edge_p, u)))
        outline(o, [pts[0][0], pts[0][1], pts[1][1], pts[1][0], pts[0][0]], color=5)
    o.pl([WA, add(WA, mul(u, math.hypot(B - 60, 1800)))], "0", lw=15, color=1, ltype="ACAD_ISO03W100", ltscale=2.0)
    o.pl([WB, add(WB, mul(v, math.hypot(B - 60, 1800)))], "0", lw=15, color=1, ltype="ACAD_ISO03W100", ltscale=2.0)
    # dims: axes B below, chain 100 / 1800 / 100 on the right, 30 / face-to-face / 30 under the axes dim
    o.dim(V(X0, Yb), V(X0 + B, Yb), V(X0, Yb - 520))
    o.dim(V(X0 + 30, Yb + 100), V(X0 + B - 30, Yb + 100), V(X0, Yb - 260))
    xr = X0 + B + 330
    for y1, y2 in ((Yb, Yb + 100), (Yb + 100, Yt - 100), (Yt - 100, Yt)):
        o.dim(V(X0 + B + 30, y1), V(X0 + B + 30, y2), V(xr, y1), rot=math.pi / 2)
    # labels and node marks
    o.note("40х2.5", add(O, V(-120, 520)), add(O, mul(u, 330)), 40, arrow="none", l2="СВ2")
    o.note("Ст1", V(X0 - 330, Yb + 1150), V(X0 - 30, Yb + 1000), 40)
    knot(o, V(X0 + 60, Yb + 120), V(X0 - 420, Yb + 560), "7", "6", rx=190, ry=130)
    knot(o, O, add(O, V(560, 470)), "8", "6", rx=170, ry=170)

    # ---------------- 4. node 7 (×4): СВ2 welded to the face of Ст1 near the base; same at the top
    K = 4.0
    N7 = V(2474700.0, -1753330.0)
    R = lambda p: add(N7, mul(p, K))
    hc, hb = 330.0, 300.0
    outline(o, [R((-30, 0)), R((-30, hc))]); outline(o, [R((30, 0)), R((30, hc))])
    hidden(o, [R((-26, 0)), R((-26, hc))]); hidden(o, [R((26, 0)), R((26, hc))])
    center(o, R((0, -40)), R((0, hc + 30)))
    brk(o, R((-30, hc)), R((30, hc)))
    outline(o, [R((-100, -10)), R((100, -10)), R((100, 0)), R((-100, 0)), R((-100, -10))])
    W7 = (30.0, 100.0)
    cu, cd = (30.0, 100 + 20 / math.cos(th)), (30.0, 100 - 20 / math.cos(th))
    fu, fd = add(add(W7, mul(u, hb)), mul(n, 20)), add(add(W7, mul(u, hb)), mul(n, -20))
    outline(o, [R(fu), R(cu), R(cd), R(fd)], color=6)
    iu, idn = (30.0, 100 + 17.5 / math.cos(th)), (30.0, 100 - 17.5 / math.cos(th))
    hidden(o, [R(add(add(W7, mul(u, hb)), mul(n, 17.5))), R(iu), R(idn), R(add(add(W7, mul(u, hb)), mul(n, -17.5)))])
    center(o, R((0, 100 - 30 * math.tan(th))), R(add(W7, mul(u, hb + 25))))
    brk(o, R(fu), R(fd))
    weld(o, R(cu), R(cd), -math.pi / 2, K)
    o.dim(R((-30, 0)), R((30, 100)), R((-95, 0)), rot=math.pi / 2, lfac=0.25)
    o.dim(R((-30, hc - 40)), R((30, hc - 40)), R((-30, hc + 45)), lfac=0.25)
    q = add(W7, mul(u, hb - 45))
    o.dim(R(add(q, mul(n, 20))), R(add(q, mul(n, -20))), R(add(add(q, mul(n, 20)), mul(u, 60))), rot=th + math.pi / 2, lfac=0.25)
    o.note("Ст1", R((-150, 250)), R((-30, 215)), 40)
    o.note("СВ2", R(add(add(W7, mul(u, 170)), (-95, 140))), R(add(add(W7, mul(u, 170)), mul(n, 20))), 40)
    o.note("Зд-1", R((-230, -30)), R((-80, -10)), 40)
    title(o, R((-165, hc + 60)), "7", "6")

    # ---------------- 5. node 8 (×4): crossing — one diagonal continuous, the other cut and welded to it
    N8 = V(2478050.0, -1752520.0)
    R8 = lambda p: add(N8, mul(p, K))
    LA, LB = 230.0, 210.0
    for s in (1, -1):
        outline(o, [R8(add(mul(u, -LA), mul(n, s * 20))), R8(add(mul(u, LA), mul(n, s * 20)))])
        hidden(o, [R8(add(mul(u, -LA), mul(n, s * 17.5))), R8(add(mul(u, LA), mul(n, s * 17.5)))])
    center(o, R8(mul(u, -LA - 20)), R8(mul(u, LA + 20)))
    brk(o, R8(add(mul(u, LA), mul(n, 20))), R8(add(mul(u, LA), mul(n, -20))))
    brk(o, R8(add(mul(u, -LA), mul(n, 20))), R8(add(mul(u, -LA), mul(n, -20))))
    m = (-v[1], v[0])
    for sgn in (1, -1):
        dv = mul(v, sgn)
        edge = mul(n, sgn * 20)
        outer, inner = [], []
        for k in (1, -1):
            q = mul(m, k * 20); qi = mul(m, k * 17.5)
            outer.append((add(mul(dv, LB), q), isect(q, dv, edge, u)))
            inner.append((add(mul(dv, LB), qi), isect(qi, dv, edge, u)))
        outline(o, [R8(outer[0][0]), R8(outer[0][1]), R8(outer[1][1]), R8(outer[1][0])], color=6)
        hidden(o, [R8(inner[0][0]), R8(inner[0][1]), R8(inner[1][1]), R8(inner[1][0])])
        center(o, R8((0, 0)), R8(mul(dv, LB + 25)))
        brk(o, R8(outer[0][0]), R8(outer[1][0]))
        c1, c2 = outer[0][1], outer[1][1]
        # seam along the continuous tube edge; branch on the left of a->b
        a_, b_ = (c1, c2) if (sgn > 0) == ((c2[0] - c1[0]) * u[0] + (c2[1] - c1[1]) * u[1] > 0) else (c2, c1)
        ang = th if sgn > 0 else th + math.pi
        weld(o, R8(a_), R8(b_), ang, K)
    q = mul(u, LA - 55)
    o.dim(R8(add(q, mul(n, 20))), R8(add(q, mul(n, -20))), R8(add(add(q, mul(n, 20)), mul(u, 70))), rot=th + math.pi / 2, lfac=0.25)
    q = mul(v, LB - 50)
    o.dim(R8(add(q, mul(m, 20))), R8(add(q, mul(m, -20))), R8(add(add(q, mul(m, 20)), mul(v, 70))), rot=math.atan2(m[1], m[0]), lfac=0.25)
    o.note("СВ2", R8(add(mul(u, 140), (60, -120))), R8(add(mul(u, 140), mul(n, -20))), 40)
    o.note("СВ2", R8(add(mul(v, 150), (-160, 30))), R8(add(mul(v, 150), mul(m, 20))), 40)
    title(o, R8((0, 300)), "8", "6")

    # ведомость элементов (sheet 4): the СВ1 row becomes «СВ1, СВ2», narrowed to fit the cell
    o.o.append({"t": "erase", "h": ["578B83"]})
    o.o.append({"t": "mtext", "at": [2445088.5, -1752951.0], "h": 150, "att": 5, "style": "Ариал", "layer": "KOHTYP",
                "s": "{\\W0.8;СВ1, СВ2}"})
    o.o.append({"t": "erase", "h": ["T:" + h for h in TEMPL]})
    o.o.append({"t": "regen"})
    return o.o


def calc_table_ops(a, L_sv2):
    """«Расчёт массы металла по элементам» from gen_lkcalc.py with an СВ2 row added"""
    src = open(os.path.join(SP, "gen_lkcalc.py"), encoding="utf-8-sig").read()
    src = src[:src.index("for al in A:")]
    row = ('        ("Связи вертикальные", "СВ1 пояс", SQ + "40×2.5", 1, "%.2f" % a["svh"], "=(1*%.2f)" % a["svh"], 2.82, "m", "лист 5"),\n')
    assert row in src
    src = src.replace(row, row + '        ("Связи вертикальные", "СВ2", SQ + "40×2.5", 4, "%.2f" % a["sv2"], "=(4*%.2f)" % a["sv2"], 2.82, "m", "лист 6, по рядам стоек"),\n')
    src = src.replace('"lk/ops_calc%s.json"', '"_unused%s.json"')
    ns = {}
    exec(compile(src, "gen_lkcalc_sv2", "exec"), ns)
    ns["A"][a]["sv2"] = L_sv2
    ops = [x for x in ns["build"](a) if x["t"] in ("newtable", "rect", "evalfields")]
    return ops


def con_ops(a, pr):
    B = GEO[a]["B"]
    Lsv = round(math.hypot(B - 60, 1800) / 1000.0, 2)
    old = {"1.1": "2*0.98+1.66", "1.2": "2*0.98+1.66", "2": "2*1.03+1.79"}[a]
    tbl, rect = CALC[a]
    ops = [{"t": "formula", "h": "5771E3", "th": 187.5, "c": [[4, 6, "=(2.82*(%s+4*%.2f)*0.001)" % (old, Lsv)]]},
           {"t": "erase", "h": [tbl, rect]}]
    ops += calc_table_ops(a, Lsv)
    newt = "Разрезы 2-2; 3-3. Связь вертикальная СВ2. Узлы 7, 8"
    ops += [{"t": "cell", "h": "5771F4", "c": [[7, 1, newt]]},
            {"t": "mtrepl", "h": "57CD37", "pairs": [["Разрезы 2-2; 3-3", newt]]},
            {"t": "mtrepl", "h": "577515", "pairs": [
                ["в продольном - распорками РС1, горизонтальными связями СГ1 по нижним поясам ферм и вертикальной связью СВ1 между фермами в среднем пролете.",
                 "в продольном - вертикальными крестовыми связями СВ2 по продольным рядам стоек в среднем пролете (лист 6), распорками РС1, горизонтальными связями СГ1 по нижним поясам ферм и вертикальной связью СВ1 между фермами в среднем пролете."],
                ["распорки РС1, связи СГ1, СВ1 - труба 40х2,5;", "распорки РС1, связи СГ1, СВ1, СВ2 - труба 40х2,5;"]]},
            {"t": "mtrepl", "h": "578B85", "pairs": [["см. лист 5", "см. листы 5, 6"]]},
            {"t": "mtrepl", "h": "57D087", "pairs": [["на листе 4", "на листе 4\\P3.\tКрепление СВ2 у верха стойки - по узлу 7. Швы сплошные, катет 3 мм."]]},
            {"t": "evalfields"}, {"t": "save", "file": os.path.join(HERE, "k%s.dwg" % a)}]
    return ops, Lsv


if __name__ == "__main__":
    for a in sys.argv[1:]:
        pr = json.load(open(os.path.join(HERE, "c%s.probe.json" % ("1.1" if a == "1.2" else a)), encoding="utf-8"))
        pr["head22"] = pr["t_22"][0][1]
        lo = live_ops(a, pr)
        co, Lsv = con_ops(a, pr)
        json.dump(lo, open(os.path.join(HERE, "ops_live_%s.json" % a), "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(co, open(os.path.join(HERE, "ops_con_%s.json" % a), "w", encoding="utf-8"), ensure_ascii=False)
        print(a, "live", len(lo), "con", len(co), "Lsv", Lsv)
