p = 'gen1.py'; s = open(p, encoding='utf-8').read()
R = [
 # plan_axes: optional first row index (element chain may take row 1)
 ("def plan_axes(s, pre, ext=(XO, YO, XE, YE)):\n    x0, y0, x1, y1 = ext\n    for k, x in AX.items(): s.axis(pre + 'ax' + k, k, (x, y1 + 700), (x, y0 - 2500))\n    for k, y in AY.items(): s.axis(pre + 'ay' + k, k, (x1 + 700, y), (x0 - 2500, y))",
  "def plan_axes(s, pre, ext=(XO, YO, XE, YE), row=1):\n    x0, y0, x1, y1 = ext; R0 = 10 * s.sc * (row - 1)\n    for k, x in AX.items(): s.axis(pre + 'ax' + k, k, (x, y1 + 700), (x, y0 - R0 - 2500))\n    for k, y in AY.items(): s.axis(pre + 'ay' + k, k, (x1 + 700, y), (x0 - R0 - 2500, y))"),
 ("    s.chain(xs, y0, y0 - R); s.dim(AX['1'], AX['3'], (y0, y0 - 2 * R))\n    s.chain(ys, x0, x0 - R, vert=True); s.dim(AY['А'], AY['Д'], (x0, x0 - 2 * R), vert=True)",
  "    s.chain(xs, y0, y0 - R0 - R); s.dim(AX['1'], AX['3'], (y0, y0 - R0 - 2 * R))\n    s.chain(ys, x0, x0 - R0 - R, vert=True); s.dim(AY['А'], AY['Д'], (x0, x0 - R0 - 2 * R), vert=True)"),
 ("A.chain([XO, 0, 275], 4300, 5000)                              # Км-2 at wall 1", "A.chain([0, 275], 4300, 5000)                                  # Км-2 at wall 1 (inner face from the axis)"),
 ("A.chain([YO, 0, 275], 8450, 9200, vert=True)                   # Км-2 at А/2", "A.chain([0, 275], 8450, 9200, vert=True)                       # Км-2 at А/2"),
 ("A.plevel('Apl3', '-4,200', 5900, 13400)", "A.plevel('Apl3', '-4,200', 6200, 13400)"),
 ("plan_axes(B, 'B')", "plan_axes(B, 'B', row=2)                                       # neck chain takes row 1"),
 ("B.chain([0, 625, 2125, 2625], 17125, YE + 400)", "B.chain([0, 625, 2125, 2625], 17125, YE + 1000)"),
 ("B.chain([8400, 10375, 11875, 13125, 14625, 15125, 17125], XO, -700, vert=True, inside=True)",
  "B.chain([8400, 10375, 11875, 13125, 14625, 15125, 17125], XO, XO - 1000, vert=True, inside=True)"),
 # sections: rows 10 mm / 20 mm on paper (500/1000 at 1:50), level lines avoided by dim texts
 ("    s.chain([Z['prep'], Z['fbot'], Z['fnd'], Z['slb'], Z['top'], Z['gr'], Z['neck']], L, L - 650, vert=True)\n    s.dim(Z['fbot'], Z['top'], (L, L - 1300), vert=True)",
  "    s.avoid_y = [Z[k] for k in ('neck', 'gr', 'top', 'slb', 'fnd', 'fbot', 'prep')]\n    s.chain([Z['prep'], Z['fbot'], Z['fnd'], Z['slb'], Z['top'], Z['gr'], Z['neck']], L, L - 10 * s.sc, vert=True)\n    s.dim(Z['fbot'], Z['top'], (L, L - 20 * s.sc), vert=True)"),
 ("S1.bound('b1a', (XO - 2600, Z['gr']), (x0n, Z['gr']))", "S1.bound('b1a', (FXO - 200, Z['gr']), (x0n, Z['gr']))"),
 ("S1.chain([FXO, 0, 8250, 14750, FXE], Z['prep'], Z['prep'] - 650)\nS1.dim(AX['1'], AX['3'], (Z['prep'], Z['prep'] - 1150))",
  "S1.chain([FXO, 0, 8250, 14750, FXE], Z['prep'], Z['prep'] - 500)\nS1.dim(AX['1'], AX['3'], (Z['prep'], Z['prep'] - 1000))"),
 ("S2.bound('b2a', (YO - 2600, Z['gr']), (YE + 1500, Z['gr']))", "S2.bound('b2a', (FYO - 200, Z['gr']), (YE + 1500, Z['gr']))"),
 ("S2.note('Пр-1', (13225, -3600), [(13625, Z['pitb'])])", "S2.note('Пр-1', (pit[3] + 400, -3550), [(pit[3], -3950)])"),
 ("S2.note('Гр-1', (11475, -500), [(11875, -100)])", "S2.note('Гр-1', (12275, -500), [(11875, -100)])"),
 ("S1 = Sheet(F2[0] + 5200, F2[1] + 9400, 50); S1.cx, S1.cy = 7375, -2400", "S1 = Sheet(F2[0] + 5200, F2[1] + 9400, 50); S1.cx, S1.cy = 7375, -2400; S1.avoid_x = list(AX.values())"),
 ("S2 = Sheet(F2[0] + 5200, F2[1] + 18200, 50); S2.cx, S2.cy = 8875, -2400", "S2 = Sheet(F2[0] + 5200, F2[1] + 18200, 50); S2.cx, S2.cy = 8875, -2400; S2.avoid_x = list(AY.values())"),
]
for a, b in R:
    assert a in s, a[:80]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
