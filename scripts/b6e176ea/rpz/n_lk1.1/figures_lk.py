# -*- coding: utf-8 -*-
"""Рисунки РПЗ «Навес над лестницей ЛК-1.1» по модели и результатам ЛИРА (CSV)."""
import re, math, json, collections, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from mpl_toolkits.mplot3d.art3d import Line3DCollection

R = "res/"
OUT = "fig/"
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 9


def rd(p):
    raw = open(p, "rb").read().decode("cp1251", errors="replace")
    raw = raw.replace("﻿", "").replace("п»ї", "")
    return [l.split(";") for l in raw.splitlines()]


co = {}
for r in rd(R + "tbl01.101.csv")[1:]:
    if len(r) > 5 and r[2].strip().isdigit():
        co[int(r[2])] = tuple(float(x) for x in r[3:6])
els = {}
for r in rd(R + "tbl02.102.csv")[1:]:
    if len(r) > 13 and r[2].strip().isdigit():
        els[int(r[2])] = (int(r[5]) if 2 <= int(r[5]) <= 6 else 1, [int(x) for x in r[13].split(",")])

ST = {1: ("Ст1", "Стойки", "#dc0000"), 2: ("ВП1, НП1", "Пояса ферм", "#0028c8"),
      3: ("Р1", "Решетка ферм", "#00bedc"), 4: ("Пр1", "Прогоны", "#e6be00"),
      5: ("СГ1", "Горизонтальные связи", "#009600"), 6: ("РС1, СВ1", "Распорки и связи", "#c800c8")}

FR = [0.0, 1.7, 3.4, 5.1, 6.8, 8.5]
AX_X = {str(i + 1): x for i, x in enumerate(FR)}
AX_Y = {"А": 0.0, "Б": 1.4}
Z_BOT = 2.03

supports = {n for n, c in co.items() if abs(c[2]) < 1e-6}
H_COL = max(c[2] for n, c in co.items() if abs(c[1]) < 1e-6 and abs(c[0]) < 1e-6)
Z_TOP = max(c[2] for c in co.values())


def segs(filter_=lambda e, st: True):
    out = []
    for e, (st, ns) in els.items():
        if filter_(e, st):
            out.append((e, st, co[ns[0]], co[ns[1]]))
    return out


def ax3d(fig, rect=(0, 0, 1, 1), elev=24, azim=-62):
    ax = fig.add_axes(rect, projection="3d")
    ax.set_box_aspect((9.0, 3.0, 2.8), zoom=0.95)
    ax.view_init(elev, azim)
    ax.set_axis_off()
    ax.set_xlim(-0.4, 8.9); ax.set_ylim(-1.0, 2.0); ax.set_zlim(0, 2.8)
    return ax


def axes_marks_3d(ax):
    for nm, x in AX_X.items():
        ax.plot([x, x], [-0.9, -0.4], [0, 0], color="#4a6fd1", lw=0.6, ls="-.")
        ax.text(x, -1.05, 0, nm, color="#1f3a93", ha="center", va="center", fontsize=8)
    for nm, y in AX_Y.items():
        ax.plot([-0.8, -0.3], [y, y], [0, 0], color="#4a6fd1", lw=0.6, ls="-.")
        ax.text(-1.0, y, 0, nm, color="#1f3a93", ha="center", va="center", fontsize=8)


def draw3d(ax, colorfn, lwfn=lambda st: 1.0, filter_=lambda e, st: True):
    data = segs(filter_)
    lc = Line3DCollection([(a, b) for e, st, a, b in data],
                          colors=[colorfn(e, st) for e, st, a, b in data],
                          linewidths=[lwfn(st) for e, st, a, b in data])
    ax.add_collection3d(lc)
    bx = [co[n] for n in supports]
    ax.scatter([p[0] for p in bx], [p[1] for p in bx], [p[2] for p in bx], marker="s", s=6, color="#1f3a93")


def legend_st(fig, sts, y=0.02):
    from matplotlib.lines import Line2D
    h = [Line2D([0], [0], color=ST[s][2], lw=2) for s in sts]
    fig.legend(h, ["%d. %s — %s" % (s, ST[s][0], ST[s][1]) for s in sts], loc="lower center",
               ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.5, y))


def save(fig, name):
    fig.savefig(OUT + name, dpi=220, facecolor="white")
    plt.close(fig)
    from PIL import Image, ImageChops
    im = Image.open(OUT + name).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if bb:
        pad = 25
        im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height))).save(OUT + name)


def fig_3d():
    fig = plt.figure(figsize=(9, 5))
    ax = ax3d(fig, (0, 0.08, 1, 0.92))
    draw3d(ax, lambda e, st: ST[st][2], lambda st: 1.6 if st == 1 else 0.9)
    axes_marks_3d(ax)
    legend_st(fig, range(1, 7))
    save(fig, "f_3d.png")
    fig = plt.figure(figsize=(9, 5))
    ax = ax3d(fig, (0, 0.05, 1, 0.95), elev=18, azim=-118)
    draw3d(ax, lambda e, st: ST[st][2], lambda st: 1.6 if st == 1 else 0.9)
    axes_marks_3d(ax)
    save(fig, "f_3d_2.png")


def plan_axes(ax):
    for nm, x in AX_X.items():
        ax.plot([x, x], [-0.6, 2.0], color="#4a6fd1", lw=0.5, ls="-.", zorder=0)
        ax.add_patch(plt.Circle((x, -0.85), 0.18, fill=False, color="#1f3a93", lw=0.7))
        ax.text(x, -0.85, nm, ha="center", va="center", fontsize=7, color="#1f3a93")
    for nm, y in AX_Y.items():
        ax.plot([-0.5, 9.0], [y, y], color="#4a6fd1", lw=0.5, ls="-.", zorder=0)
        ax.add_patch(plt.Circle((-0.75, y), 0.18, fill=False, color="#1f3a93", lw=0.7))
        ax.text(-0.75, y, nm, ha="center", va="center", fontsize=7, color="#1f3a93")
    ax.set_xlim(-1.1, 9.2); ax.set_ylim(-1.2, 2.1)
    ax.set_aspect("equal"); ax.axis("off")
    ax.invert_yaxis()


def is_bottom(p):
    return abs(p[2] - Z_BOT) < 0.005


def fig_plans():
    fig = plt.figure(figsize=(9, 3.6)); ax = fig.add_axes((0, 0.12, 1, 0.88))
    for e, st, a, b in segs():
        if st in (2, 5, 6) and is_bottom(a) and is_bottom(b):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=ST[st][2], lw=1.6 if st == 2 else 1.2)
    plan_axes(ax)
    legend_st(fig, (2, 5, 6), y=0.0)
    save(fig, "f_plan_bot.png")
    fig = plt.figure(figsize=(9, 3.6)); ax = fig.add_axes((0, 0.12, 1, 0.88))
    for e, st, a, b in segs():
        if st == 4 or (st == 2 and a[0] == b[0] and not (is_bottom(a) and is_bottom(b))):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=ST[st][2], lw=1.0 if st == 4 else 1.6)
    plan_axes(ax)
    legend_st(fig, (2, 4), y=0.0)
    save(fig, "f_plan_top.png")


def fig_rows():
    for nm, y0, fn in (("А", 0.0, "f_row_A.png"), ("Б", 1.4, "f_row_B.png"), ("по середине пролета", 0.7, "f_row_mid.png")):
        fig = plt.figure(figsize=(9, 2.8)); ax = fig.add_axes((0, 0.05, 1, 0.95))
        for e, st, a, b in segs():
            if abs(a[1] - y0) < 1e-6 and abs(b[1] - y0) < 1e-6 and not (st in (2, 3) and a[0] == b[0]):
                ax.plot([a[0], b[0]], [a[2], b[2]], color=ST[st][2], lw=1.6 if st == 1 else 1.0)
        for x in FR:
            if y0 in (0.0, 1.4):
                ax.plot([x - 0.08, x + 0.08], [0, 0], color="k", lw=1.2)
        for an, x in AX_X.items():
            ax.plot([x, x], [-0.3, 2.8], color="#4a6fd1", lw=0.5, ls="-.", zorder=0)
            ax.add_patch(plt.Circle((x, -0.5), 0.17, fill=False, color="#1f3a93", lw=0.7))
            ax.text(x, -0.5, an, ha="center", va="center", fontsize=7, color="#1f3a93")
        ax.set_xlim(-0.5, 9.0); ax.set_ylim(-0.8, 2.9); ax.set_aspect("equal"); ax.axis("off")
        save(fig, fn)


def fig_frame():
    fig = plt.figure(figsize=(6, 4.6)); ax = fig.add_axes((0.03, 0.12, 0.94, 0.86))
    for e, st, a, b in segs():
        if abs(a[0]) < 1e-6 and abs(b[0]) < 1e-6:
            ax.plot([a[1], b[1]], [a[2], b[2]], color=ST[st][2], lw=1.8 if st in (1, 2) else 1.1)
    for y in (0.0, 1.4):
        ax.plot([y - 0.12, y + 0.12], [0, 0], color="k", lw=1.5)
    for nm, y in AX_Y.items():
        ax.plot([y, y], [-0.35, 0], color="#4a6fd1", lw=0.5, ls="-.")
        ax.add_patch(plt.Circle((y, -0.5), 0.13, fill=False, color="#1f3a93", lw=0.7))
        ax.text(y, -0.5, nm, ha="center", va="center", fontsize=8, color="#1f3a93")

    def dim(x1, x2, yy, t):
        ax.annotate("", (x1, yy), (x2, yy), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text((x1 + x2) / 2, yy + 0.05, t, ha="center", fontsize=8)
    dim(-0.3, 0, -0.18, "300"); dim(0, 1.4, -0.18, "1400"); dim(1.4, 1.7, -0.18, "300")
    for y, z in ((0.0, Z_BOT), (0.7, Z_TOP)):
        ax.text(y + 0.04, z + 0.04, "+%.3f" % z, fontsize=7)
    ax.set_xlim(-0.6, 2.0); ax.set_ylim(-0.75, 2.75); ax.set_aspect("equal"); ax.axis("off")
    legend_st(fig, (1, 2, 3, 4), y=0.0)
    save(fig, "f_frame.png")


RO = {1: 0.00797, 2: 0.00282, 3: 0.00282, 4: 0.00282, 5: 0.00282, 6: 0.00282}
LOADQ = {2: (0.010, 0.015), 3: (0.010, 0.020), 4: (0.025, 0.050)}


def fig_loads():
    for case in (1, 2, 3, 4):
        fig = plt.figure(figsize=(9, 4.6))
        ax = ax3d(fig, (0, 0.08, 1, 0.92))
        if case == 1:
            vals = sorted(set(RO.values()))
            cm = plt.get_cmap("viridis", len(vals))
            draw3d(ax, lambda e, st: cm(vals.index(RO[st])), lambda st: 1.4)
            from matplotlib.lines import Line2D
            h = [Line2D([0], [0], color=cm(i), lw=2.5) for i in range(len(vals))]
            fig.legend(h, ["q = %.5f т/м" % v for v in vals], loc="lower center", ncol=4, frameon=False, fontsize=8)
        else:
            draw3d(ax, lambda e, st: ("#d62728" if st == 4 else "#b8b8b8"), lambda st: 1.6 if st == 4 else 0.6)
            for e, st, a, b in segs(lambda e, st: st == 4):
                xm, ym, zm = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
                ax.plot([xm, xm], [ym, ym], [zm, zm + 0.25], color="#d62728", lw=0.5)
            q1, q2 = LOADQ[case]
            fig.text(0.5, 0.03, "q = %.3f т/м на крайние прогоны, %.3f т/м на средние; направление — вниз (глобальная ось Z)"
                     % (q1, q2), ha="center", fontsize=9, color="#d62728")
        axes_marks_3d(ax)
        save(fig, "f_load%d.png" % case)


def scale_bar(fig, bounds, cmap, label, fmt="%.0f"):
    cax = fig.add_axes((0.08, 0.93, 0.84, 0.03))
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal",
                      ticks=bounds, spacing="uniform")
    cb.ax.set_xticklabels([fmt % b for b in bounds], fontsize=7)
    cb.ax.set_title(label, fontsize=8, loc="left")
    return norm


def metal():
    res = collections.defaultdict(lambda: {"I": 0.0, "II": 0.0, "MU": 0.0})
    for f in ("tbl09.49_1.csv", "tbl09.49_2.csv", "tbl09.49_3.csv"):
        rows = rd(R + f); hdr = rows[0]
        pc = [i for i, h in enumerate(hdr) if h.endswith("%")]
        for r in rows[1:]:
            if len(r) < len(hdr) - 1 or "-S" in r[1] or not r[4].strip().isdigit():
                continue
            e = int(r[4]); g = res[e]
            for i in pc:
                v = float(r[i]) if r[i] not in ("", "-") else 0.0
                h = hdr[i]
                if h == "Прог %":
                    g["II"] = max(g["II"], v)
                elif h == "М.У. %":
                    g["MU"] = max(g["MU"], v)
                elif h != "ЭПС %":
                    g["I"] = max(g["I"], v)
    return res


def fig_checks():
    res = metal()
    bounds = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    cmap = mcolors.ListedColormap(["#1f3a93", "#2a62c9", "#2c8fd6", "#20b3c4", "#2ca02c",
                                   "#9acd32", "#e6c200", "#ff9f1a", "#ff6a00", "#d62728"])
    for key, fn, lab in (("I", "f_chk_I.png", "Проверка назначенных сечений по 1 ПС, % использования"),
                         ("II", "f_chk_II.png", "Проверка назначенных сечений по 2 ПС (прогибы), % использования"),
                         ("MU", "f_chk_MU.png", "Проверка назначенных сечений по местной устойчивости, % использования")):
        fig = plt.figure(figsize=(9, 5.2))
        norm = scale_bar(fig, bounds, cmap, lab)
        ax = ax3d(fig, (0, 0.0, 1, 0.9))
        draw3d(ax, lambda e, st: cmap(norm(min(res[e][key], 99.9))) if e in res else "#cccccc",
               lambda st: 1.4 if st in (1, 2) else 1.0)
        mx = max(res.items(), key=lambda kv: kv[1][key])
        st = els[mx[0]][0]
        fig.text(0.5, 0.02, "Максимум: %.1f %% — элемент %d (%s, %s)" % (mx[1][key], mx[0], ST[st][0], ST[st][1]),
                 ha="center", fontsize=8)
        axes_marks_3d(ax)
        save(fig, fn)
    return res


def nodal_mosaic(vals, fn, label, bounds, cmap, fmt="%.1f", note=""):
    fig = plt.figure(figsize=(9, 5.2))
    norm = scale_bar(fig, bounds, cmap, label, fmt)
    ax = ax3d(fig, (0, 0.0, 1, 0.9))
    draw3d(ax, lambda e, st: "#9a9a9a", lambda st: 0.6)
    ns = list(vals)
    ax.scatter([co[n][0] for n in ns], [co[n][1] for n in ns], [co[n][2] for n in ns],
               c=[cmap(norm(min(max(vals[n], bounds[0]), bounds[-1] - 1e-9))) for n in ns], s=9, depthshade=False)
    if note:
        fig.text(0.5, 0.02, note, ha="center", fontsize=8)
    axes_marks_3d(ax)
    save(fig, fn)


def rsn_disp():
    res = collections.defaultdict(dict)
    for r in rd(R + "rsn_disp.csv")[1:]:
        if len(r) < 11 or not r[4].strip().isdigit():
            continue
        k = int(re.search(r"(\d+)", r[2]).group(1))
        res[k][int(r[4])] = tuple(float(x) for x in r[5:8])
    return res


def modal_srss():
    modal = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rd(R + "tbl03.5_1.csv")[1:]:
        if len(r) < 11 or "-S" in r[1] or not r[4].strip().isdigit():
            continue
        m = re.match(r"\s*(\d+)\s*-\s*(\d+)", r[2])
        if m:
            modal[int(m.group(1))][int(r[4])].append(tuple(float(x) for x in r[5:8]))
    return {L: {n: [math.sqrt(sum(v[i] ** 2 for v in lst)) for i in range(3)] for n, lst in d.items()}
            for L, d in modal.items()}


RSN_IV = (10, 11)


def drift_calc():
    sr = modal_srss()
    q = 4.0
    drift = {}
    for L, i, lab in ((5, 0, "X"), (6, 1, "Y")):
        for row, y in (("А", 0.0), ("Б", 1.4)):
            ns = [n for n, c in co.items() if abs(c[1] - y) < 1e-6 and abs(c[2] - H_COL) < 0.005]
            n = max(ns, key=lambda n: sr[L][n][i]); de = sr[L][n][i]
            drift["%s_%s" % (lab, row)] = dict(row=row, node=n, h=H_COL, de=de, dr=q * de, drnu=q * de * 0.5)
    json.dump(drift, open("drift.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return drift


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    fig_3d(); fig_plans(); fig_rows(); fig_frame(); fig_loads()
    fig_checks(); fig_disp()
    print("ok")
