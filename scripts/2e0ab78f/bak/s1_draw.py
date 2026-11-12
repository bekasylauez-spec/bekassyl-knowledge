# -*- coding: utf-8 -*-
"""Ортақ сызу бөліктері: резервуар қимасы, план шеңберлері, камера (45° бағытта)."""
import math
import s1_lib as L
from s1_geo import *

A45 = math.radians(45.0)
U0 = 11035.0                 # камераның резервуарға жақын қыры (осьтен)
CAM_L, CAM_W = 6600.0, 3600.0
AX = dict(layer=L.L_DIM, ltype='ГОСТ 2.303 5', ltscale=100, lw=9)


def uv(C, u, v, k=1.0):
    """камера координатасы (u — осьтен сыртқа 45°, v — көлденең) → парақ"""
    return (C[0] + k * (u * math.cos(A45) - v * math.sin(A45)), C[1] + k * (u * math.sin(A45) + v * math.cos(A45)))


def rect_uv(C, u0, u1, v0, v1, k=1.0):
    return [uv(C, u0, v0, k), uv(C, u1, v0, k), uv(C, u1, v1, k), uv(C, u0, v1, k)]


def fm_loop(S):
    return [S(r, z) for r, z in TOP] + [S(r, z) for r, z in BOT] + [S(-r, z) for r, z in reversed(BOT[:-1])] + [S(-r, z) for r, z in reversed(TOP[1:])]


def wall_half(S, sg, hatch=True, launder=True, console=True):
    w = [S(sg * R_WI, Z_JOINT), S(sg * R_WI, Z_TOPW), S(sg * (11000 if console else R_WO), Z_TOPW)]
    if console: w += [S(sg * 11000, Z_TOPW - 120), S(sg * R_WO, Z_TOPW - 120)]
    w += [S(sg * R_WO, Z_JOINT)]
    L.pl(w)
    if hatch: L.hatch([w])
    if launder:
        lt = [S(sg * R_WI, 1050), S(sg * 9300, 1050), S(sg * 9300, 1750), S(sg * 9500, 1750), S(sg * 9500, 1250), S(sg * R_WI, 1250)]
        L.pl(lt)
        if hatch: L.hatch([lt])


def column(S, hatch=True):
    for sg in (1, -1):
        c = [S(sg * R_COL_I, Z_PB), S(sg * R_COL_O, Z_PB), S(sg * R_COL_O, Z_TOPW), S(0, Z_TOPW), S(0, Z_TOPW - 262), S(sg * R_COL_I, Z_TOPW - 262)]
        L.pl(c)
        if hatch: L.hatch([c])


def tank_section(cx, y0, k=1.0, hatch=True, pod=True, fill=True):
    def S(r, z): return (cx + r * k, y0 + z * k)
    fm = fm_loop(S)
    L.pl(fm, closed=True)
    if hatch: L.hatch([fm])
    if pod:
        podl = [S(r, z) for r, z in POD] + [S(-r, z) for r, z in reversed(POD[:-1])]
        L.pl(podl, layer=L.L_THIN)
        edge = [S(R_OUT, Z_BOT)] + [S(r, z) for r, z in BOT] + [S(-r, z) for r, z in reversed(BOT[:-1])] + [S(-R_OUT, Z_BOT)]
        L.hatch([podl + list(reversed(edge))], pat='AR-CONC', sc=2)
    for sg in (1, -1): wall_half(S, sg, hatch)
    column(S, hatch)
    if fill:
        rf = R_PB + (R_PT - R_PB) * (752.0 / (Z_PT - Z_PB))
        for sg in (1, -1):
            f = [S(sg * R_COL_O, Z_PB), S(sg * R_PB, Z_PB), S(sg * rf, Z_PB + 752), S(sg * R_COL_O, Z_PB + 752)]
            L.pl([f[2], f[3]], layer=L.L_THIN); L.hatch([f], pat='AR-CONC', sc=4)
    L.line(S(0, Z_B3 - 600 / k), S(0, Z_TOPW + 600 / k), **AX)
    return S


def axes(C, rx=12700, ry=11900, bubbles=True):
    L.line((C[0] - rx, C[1]), (C[0] + rx - 800, C[1]), **AX)
    L.line((C[0], C[1] - ry), (C[0], C[1] + ry - 400), **AX)
    if bubbles:
        L.circle((C[0] - rx - 350, C[1]), 350, layer=L.L_DIM, lw=25)
        L.circle((C[0], C[1] - ry - 350), 350, layer=L.L_DIM, lw=25)


def camera_plan(C, slab=True, walls=True, hatch=True, cover=False, k=1.0):
    """камера планы: Фм-2 контуры, қабырғалар (штрихпен), жабын"""
    if slab: L.pl(rect_uv(C, U0, U0 + CAM_W + 500, -CAM_L / 2 - 500, CAM_L / 2 + 500, k), closed=True, layer=L.L_THIN if walls else L.L_CONT)
    if cover:
        L.pl(rect_uv(C, U0, U0 + CAM_W, -CAM_L / 2, CAM_L / 2, k), closed=True)
        for v0, v1 in ((-3000, -150), (150, 3000)):
            L.pl(rect_uv(C, U0 + 300, U0 + 3300, v0, v1, k), closed=True, layer=L.L_THIN, ltype='HIDDEN', ltscale=30)
        return
    if walls:
        outer = rect_uv(C, U0, U0 + CAM_W, -CAM_L / 2, CAM_L / 2, k)
        c1 = rect_uv(C, U0 + 300, U0 + 3300, -3000, -150, k); c2 = rect_uv(C, U0 + 300, U0 + 3300, 150, 3000, k)
        L.pl(outer, closed=True); L.pl(c1, closed=True); L.pl(c2, closed=True)
        if hatch: L.hatch([outer, c1, c2])


def pile_points():
    """[(x, y, 'Св1'|'Св2')] резервуар осіне қатысты, мм"""
    pts = []
    n = int(math.ceil(2 * math.pi * 10175 / 1000))
    for i in range(n):
        a = 2 * math.pi * i / n; pts.append((10175 * math.cos(a), 10175 * math.sin(a), 'Св1'))
    pts.append((0, 0, 'Св1'))
    for i in range(6):
        a = 2 * math.pi * i / 6; pts.append((950 * math.cos(a), 950 * math.sin(a), 'Св1'))
    cam = set()
    for i in range(8):
        cam.add((0, round(i * 6300 / 7.0))); cam.add((3300, round(i * 6300 / 7.0)))
    for j in (0, 3150, 6300):
        for i in range(1, 4): cam.add((round(i * 3300 / 4.0), j))
    for a, b in sorted(cam):
        x, y = uv((0, 0), U0 + 150 + a, -3150 + b); pts.append((x, y, 'Св1'))
    for a in range(-5, 6):
        for b in range(-5, 6):
            if 2700 < math.hypot(2000 * a, 2000 * b) < 9300: pts.append((2000 * a, 2000 * b, 'Св2'))
    return pts


def dot(p, r, layer='ф18_арм'):
    """арматура қимасы — толтырылған нүкте"""
    L.op(t='hatch', pat='SOLID', layer=layer, lw=0, loops=[[list(q) for q in L.ring_pts(p, r, 12)]])


def bar(pts, d=18, **k):
    return L.pl(pts, layer='ф%d_арм' % d, lw=40, **k)
