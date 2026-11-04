# -*- coding: utf-8 -*-
# КМ ЛК без СВ2: columns Ст1 □60×4 -> □70×4. Builds sc2 ops for one drawing from its DXF dump:
# node 1 elevation + section a-a, node 2 (widen column outlines and move dimension points by 5 mm each side),
# texts (ОД, labels), spec tables (section text, mass 7.97 kg/m), sheet-3 load table (forces of the 70×4 calc).
# Usage: python -X utf8 gen70.py <id> <dxf> <task> <out.dwg>
import json, sys
import ezdxf

ID, DXF, TASK, OUT = sys.argv[1:5]
d = ezdxf.readfile(DXF); msp = d.modelspace(); db = d.entitydb
ops = []
W, W2 = 60.0, 70.0
dd = (W2 - W) / 2


def xs(e):
    return [p[0] for p in e.get_points()]


def ys(e):
    return [p[1] for p in e.get_points()]


# --- column outlines in nodes 1 and 2: open 4-point verticals, outer 60 wide, inner 52/55 wide
cols = []
for e in msp.query("LWPOLYLINE"):
    if len(e) != 4 or e.closed:
        continue
    x, y = xs(e), ys(e)
    w, h = max(x) - min(x), max(y) - min(y)
    if h > 100 and abs(w - 60) < 0.05 or (h > 100 and (abs(w - 52) < 0.05 or abs(w - 55) < 0.05)):
        cols.append((e, w))
for e, w in cols:
    x = xs(e); cx = (min(x) + max(x)) / 2
    for i, p in enumerate(e.get_points()):
        nx = p[0] + (dd if p[0] > cx else -dd)
        ops.append({"t": "plset", "h": e.dxf.handle, "i": i, "p": [nx, p[1]]})
print(ID, "column outlines", [(e.dxf.handle, round(w, 2)) for e, w in cols])

# --- section a-a: profile block + chained dims 70/60/70 both ways
blk = [e for e in msp.query("INSERT") if "60x60x4" in e.dxf.name]
for b in blk:
    ops.append({"t": "bscale", "h": b.dxf.handle, "s": [W2 / W, W2 / W, 1]})
print(ID, "profile blocks", [b.dxf.handle for b in blk])
assert len(blk) == 1
bx, by = blk[0].dxf.insert.x, blk[0].dxf.insert.y
lo_x, hi_x, lo_y, hi_y = bx - 30, bx + 30, by - 30, by + 30


def moved(p):
    x, y = p.x, p.y
    if abs(x - lo_x) < 0.2: x -= dd
    elif abs(x - hi_x) < 0.2: x += dd
    if abs(y - lo_y) < 0.2: y -= dd
    elif abs(y - hi_y) < 0.2: y += dd
    return x, y


ndim = 0
for e in msp.query("DIMENSION"):
    p2, p3 = e.dxf.defpoint2, e.dxf.defpoint3
    near = abs(p2.x - bx) < 400 and abs(p2.y - by) < 400
    meas = e.get_measurement()
    if near and (abs(meas - 60) < 0.05 or abs(meas - 69.92) < 0.2):
        n2, n3 = moved(p2), moved(p3)
        if (n2 != (p2.x, p2.y)) or (n3 != (p3.x, p3.y)):
            ops.append({"t": "dimpts", "h": e.dxf.handle, "p1": [n2[0], n2[1]], "p2": [n3[0], n3[1]]}); ndim += 1
# node 2 width dim (60) at the column foot
for e, w in cols:
    if abs(w - 60) > 0.05:
        continue
    x = xs(e); y0 = min(ys(e))
    for dm in msp.query("DIMENSION"):
        p2, p3 = dm.dxf.defpoint2, dm.dxf.defpoint3
        if abs(dm.get_measurement() - 60) < 0.05 and abs(p2.y - y0) < 0.2 and abs(p3.y - y0) < 0.2 \
                and {round(p2.x, 1), round(p3.x, 1)} == {round(min(x), 1), round(max(x), 1)}:
            f = lambda px: px - dd if abs(px - min(x)) < 0.2 else px + dd
            ops.append({"t": "dimpts", "h": dm.dxf.handle, "p1": [f(p2.x), p2.y], "p2": [f(p3.x), p3.y]}); ndim += 1
print(ID, "dims moved", ndim)

# --- texts
for e in msp.query("MTEXT"):
    t = e.text
    if "квадратная 60х4" in t:
        ops.append({"t": "mtrepl", "h": e.dxf.handle, "pairs": [["квадратная 60х4", "квадратная 70х4"]]})
    elif t.rstrip().endswith("60×4") and len(t) < 80:
        ops.append({"t": "mtrepl", "h": e.dxf.handle, "pairs": [["60×4", "70×4"]]})
    elif t.startswith("Сбор нагрузок, расчетные сочетания"):
        loadnote = e.dxf.handle
print(ID, "text ops", [o["h"] for o in ops if o["t"] == "mtrepl"])

# --- tables: find by raw strings (ezdxf does not parse ACAD_TABLE cells) -> handles from the DXF text
raw = open(DXF, encoding="utf-8", errors="replace").read().splitlines()
tabs = {}
typ = h = None
for i in range(0, len(raw) - 1, 2):
    c, v = raw[i].strip(), raw[i + 1]
    if c == "0": typ = v.strip(); h = None
    elif c == "5": h = v.strip()
    elif typ == "ACAD_TABLE" and c == "1":
        if v.startswith("Расчёт массы металла"): tabs["calc"] = h
        if "Масса металла по элементам" in v: tabs["spec"] = h
print(ID, "tables", tabs)
fmt = "%lu2%pr3"
ops.append({"t": "cell", "h": tabs["calc"], "c": [[2, 2, "Тр. {\\fBankGothic Md BT|b0|i0|c0|p34;0}70×4"]]})
ops.append({"t": "formula", "h": tabs["calc"], "fmt": "%lu2%pr2", "c": [[2, 6, "7.97"]]})
ops.append({"t": "cell", "h": tabs["spec"], "c": [[3, 2, "Тр. {\\fBankGothic Md BT|b0|i0|c0|p34;0}70×4"]]})
ops.append({"t": "formula", "h": tabs["spec"], "fmt": fmt, "c": [[3, 4, "7.97*12*2.0*0.001"]]})
ops += [{"t": "evalfields"}, {"t": "recompute", "h": tabs["calc"]}, {"t": "recompute", "h": tabs["spec"]},
        {"t": "dumptable", "h": tabs["calc"]}, {"t": "dumptable", "h": tabs["spec"]}]

# --- sheet-3 load table: same clones as the НТП pass (template text 5785EB-equivalent from ops3 of this id)
zd = json.load(open("../nt/zd.json", encoding="utf-8"))[TASK]


def f(x):
    s = "%.2f" % x
    return ("0.00" if s == "-0.00" else s).replace(".", ",")


vals = []
for k in ("N max", "N min", "M max", "M min", "Q max", "Q min"):
    r = zd[k]; vals += [f(r["N"]), f(r["Mx"]), f(r["Qy"]), f(r["My"]), f(r["Qx"]), "_".join(r["rsn"].split("_")[:2])]
src = json.load(open("ops3_%s.json" % ID, encoding="utf-8"))
i = 0
for x in src:
    if x["t"] == "clone":
        y = dict(x); y["s"] = vals[i]; i += 1; ops.append(y)
    elif x["t"] == "mtrepl":
        ops.append(x)
ops.append({"t": "save", "file": OUT})
json.dump(ops, open("ops70_%s.json" % ID, "w", encoding="utf-8"), ensure_ascii=False)
print(ID, "loads", vals)
print(ID, "ops", len(ops))
