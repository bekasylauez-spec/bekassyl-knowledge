# -*- coding: utf-8 -*-
# Node 14 (truss end at the cantilever, caps -t4) on sheet 12 + cap in node 7 + marks on sections 1-1 / 2-2
import json, math

T = (88713.7, -9797.8)                       # section 1-1 -> sheet 12 (1:1 mm, node at 1:10)
def tr(p): return [p[0] + T[0], p[1] + T[1]]

ARCS = {  # handle: (cx, cy, r, kind)
    "586FCF": (2524258.232854624, -1729437.412930117, 17558.8951572387, "o"),   # ВП1 top
    "586FD0": (2524262.691213211, -1729422.642280145, 17503.34781463939, "a"),  # ВП1 axis
    "586FD1": (2524256.808544759, -1729437.553495195, 17479.0240689983, "o"),   # ВП1 bottom
    "586FD2": (2524189.970336332, -1729536.512507896, 17075.60866260418, "o"),  # НП1 bottom
    "586FD3": (2524194.475675427, -1729525.986052502, 17104.50770028968, "a"),  # НП1 axis
    "586FD4": (2524191.378351185, -1729536.709770437, 17155.82373175895, "o"),  # НП1 top
}
XPOST_L, XPOST_R, XPOST_AX = 2523846.3, 2523896.4, 2523872.5
XCAP = XPOST_R + 4.0          # chord end face behind the cap
XCUT = 2524136.0              # break of the chords (240 mm from the post)

def ang(a, x): cx, cy, r, _ = a; return math.degrees(math.acos((x - cx) / r))
def yat(a, x): cx, cy, r, _ = a; return cy + math.sqrt(r * r - (x - cx) ** 2)

ops = [{"t": "eraseregion", "win": [2612250, -1722420, 2612862, -1721400]}, {"t": "maprst"}]
for h, a in ARCS.items():
    tag = "n14_" + h
    ops.append({"t": "clone", "h": h, "base": [0, 0], "to": [T[0], T[1]], "tag": tag})
    xa = XPOST_AX if a[3] == "a" else XCAP
    ops.append({"t": "arcang", "h": tag, "sa": ang(a, XCUT), "ea": ang(a, xa)})

# end post Р1 and its axis
ops.append({"t": "clone", "h": "586FF0", "base": [0, 0], "to": [T[0], T[1]], "tag": "n14_post", "color": 5})
ops.append({"t": "clone", "h": "587090", "base": [0, 0], "to": [T[0], T[1]], "tag": "n14_postax"})

# caps -t4 at the chord ends (closed polylines like plate 58BC7E: layer 0, colour 0, lw 30)
xm = XPOST_R + 2.0
vp = (yat(ARCS["586FCF"], xm), yat(ARCS["586FD1"], xm))
np_ = (yat(ARCS["586FD4"], xm), yat(ARCS["586FD2"], xm))
for nm, (ytop, ybot) in (("cap_top", vp), ("cap_bot", np_)):
    ops.append({"t": "pl", "p": [tr((XPOST_R, ytop)), tr((XCAP, ytop)), tr((XCAP, ybot)), tr((XPOST_R, ybot))],
                "closed": True, "layer": "0", "color": 0, "lw": 30, "tag": "n14_" + nm})

# first diagonal Р1 (from the post foot to the top node over К1), 50 wide, cut by a break
A = (2523873.5, -1712424.5); B = (2524526.1, -1711922.3)
L = math.dist(A, B); u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L); n = (-u[1], u[0])
def lp(s, off): return (A[0] + u[0] * s + n[0] * off, A[1] + u[1] * s + n[1] * off)
s_end = (2524050.0 - A[0]) / u[0]
up_s = (XPOST_R - (A[0] + n[0] * 25)) / u[0]                         # upper face meets the post face
ytopNP = yat(ARCS["586FD4"], 2523960)
lo_s = (ytopNP - (A[1] + n[1] * -25)) / u[1]                         # lower face meets НП1 top
ops.append({"t": "pl", "p": [tr(lp(up_s, 25)), tr(lp(s_end, 25))], "layer": "0", "color": 5, "lw": 30})
ops.append({"t": "pl", "p": [tr(lp(lo_s, -25)), tr(lp(s_end, -25))], "layer": "0", "color": 5, "lw": 30})
ops.append({"t": "pl", "p": [tr(A), tr(lp(s_end + 25, 0))], "layer": "0", "color": 1, "lw": 15, "ltype": "ACAD_ISO03W100", "ltscale": 2})

# SPDS breaks (clone of node 7 break 58B49F: start->end direction -120.12 deg, mid point)
BS, BE = (2612922.80930193, -1721607.34326663), (2612882.31222206, -1721677.15486089)
BM = ((BS[0] + BE[0]) / 2, (BS[1] + BE[1]) / 2); bdir = math.degrees(math.atan2(BE[1] - BS[1], BE[0] - BS[0]))
def brk(tag, mid, dirdeg):
    ops.append({"t": "clone", "h": "58B49F", "base": list(BM), "to": list(mid), "tag": tag})
    ops.append({"t": "xform", "h": tag, "base": list(mid), "to": list(mid), "ang": math.radians(dirdeg - bdir)})
brk("n14_bvp", tr((XCUT, yat(ARCS["586FD0"], XCUT))), -90)
brk("n14_bnp", tr((XCUT, yat(ARCS["586FD3"], XCUT))), -90)
dd = math.degrees(math.atan2(u[1], u[0]))
brk("n14_bdg", tr(lp(s_end, 0)), dd - 90)

# dimensions (clone of СПДС dim 58B4C0): post width 50, height 580
pbl, pbr, ptl = (XPOST_L, -1712463.7), (2523896.9, -1712463.4), (XPOST_L, -1711883.5)
ops.append({"t": "dim", "h": "58B4C0", "p1": tr(pbl), "p2": tr(pbr), "dl": tr((XPOST_L, -1712463.7 - 104)), "rot": 0, "txt": "50"})
ops.append({"t": "dim", "h": "58B4C0", "p1": tr(ptl), "p2": tr(pbl), "dl": tr((XPOST_L - 104, -1712173)), "rot": math.pi / 2})

# callouts in the style of node 7 (scale 10, 2.5, ГОСТ 2.304, open arrow)
def note(l1, l2, origin, targets):
    o = {"t": "note", "l1": l1, "l2": l2, "origin": origin, "scale": 10, "arrow": "open", "ts": 2.5, "style": "ГОСТ 2.304", "layer": "Размеры"}
    o["targets"] = targets
    ops.append(o)
X = lambda xs: xs + T[0]
note("Р1", "", [2612480, -1721560], [[2612585, -1721700]])
note("ВП1", "", [2612760, -1721600], [tr((2524060, yat(ARCS["586FCF"], 2524060)))])
note("НП1", "", [2612790, -1722340], [tr((2524070, yat(ARCS["586FD2"], 2524070)))])
note("Р1", "", [2612800, -1722030], [tr(lp(s_end - 50, 0))])
note("-t4", "С245", [2612700, -1721850], [tr((XPOST_R + 2, (vp[0] + vp[1]) / 2))])
note("-t4", "С245", [2612650, -1722335], [tr((XPOST_R + 2, (np_[0] + np_[1]) / 2))])

# node bubble: clone of node 7 bubble (block + 2 texts), «14 / 7»
dB = -486.6
for h, tg in (("580E18", "n14_bub"), ("580E19", "n14_bt"), ("580E1A", "n14_bb")):
    ops.append({"t": "clone", "h": h, "base": [0, 0], "to": [dB, 0], "tag": tg})
ops.append({"t": "settext", "h": "n14_bt", "s": "14"})
ops.append({"t": "move", "h": ["n14_bt"], "d": [-13, 0]})

ops.append({"t": "regen"})
json.dump(ops, open("mc/ops_node2.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops), "ops; caps", [round(v, 1) for v in vp + np_], "diag s", round(up_s, 1), round(lo_s, 1), round(s_end, 1))
