p = 'gen6.py'; s = open(p, encoding='utf-8').read()
a = s.index("e = 100                                                            # first/last bar from the slab edge")
b = s.index("# ===================== 5.3–5.6 доп.")
new32 = r'''# analog 3.2: bars 50 from the edge, ONE position «1» for all base bars (пог.м.), one «1/ш.200» note with two leaders,
# «Ск1» (no step) on short leaders at the bar ends, chains «50 | 200xN=… | rest» along the top and the right side
e = 50
nX = int((FYE - FYO - 2 * e) / 200); nY = int((FXE - FXO - 2 * e) / 200)
YB, XB = 1700, 7600                                                   # horizontal bar near the bottom, vertical one through the middle
add(t='pl', p=[S.P(FXO + e, YB), S.P(FXE - e, YB)], closed=False, layer='диам14')
add(t='pl', p=[S.P(XB, FYO + e), S.P(XB, FYE - e)], closed=False, layer='диам14')
S.note('1', (XB + 800, YB + 2100), [(XB, YB + 2100), (XB + 400, YB)], l2='ш.200', arrow='oblique')
for org, tgt in [((FXO - 900, YB - 500), (FXO + e, YB)), ((FXE + 300, YB - 500), (FXE - e, YB)),
                 ((XB + 450, FYE + 300), (XB, FYE - e)), ((XB + 450, FYO - 500), (XB, FYO + e))]:
    S.note('Ск1', org, [tgt], arrow='oblique')
for a_, b_ in ((FXO, FXO + e), (FXO + e + 200 * nY, FXE)): S.dim(a_, b_, (FYE, FYE + 600))
dimtxt(S, FXO + e, FXO + e + 200 * nY, (FYE, FYE + 600), '200x%d=%d' % (nY, 200 * nY))
for a_, b_ in ((FYO, FYO + e), (FYO + e + 200 * nX, FYE)): S.dim(a_, b_, (FXE, FXE + 600), vert=True)
dimtxt(S, FYO + e, FYO + e + 200 * nX, (FXE, FXE + 600), '200x%d=%d' % (nX, 200 * nX), vert=True)
S.section('a21', '1', (2500, FYO - 2600), (2500, 2300))
# --- Разрез 1-1 (армирование), М 1:25 at the slab edge (axis А), as analog 3.2 «Разрез 1-1 (Армирование)»
K = SheetK(FX['3.2'] + 30400, 340000.0 + 30000, 4)
K.title('Разрез 1-1 (Армирование) М 1:25', -700, -2850)
XR = 1500                                                              # cut end of the drawn piece
K.pl([(XR, -4100), (-625, -4100), (-625, -3700), (XR, -3700)], closed=False)
K.thin([(XR, -4100), (XR + 60, -3990), (XR - 60, -3810), (XR, -3700)])           # break line
K.thin([(-125, -3700), (-125, -3350)]); K.thin([(125, -3700), (125, -3350)])     # wall stub, not shown
K.thin([(-200, -3350), (-30, -3350), (0, -3290), (30, -3410), (60, -3350), (200, -3350)])
K.hatch([[(-125, -3700), (125, -3700), (125, -3350), (-125, -3350)]])
K.thin([(-725, -4200), (XR, -4200)]); K.thin([(-725, -4200), (-725, -4100)])
yb1, yt1 = -4100 + CB + 7, -3700 - CT - 7                              # bars along the cut (lines)
x_first = -625 + e
add(t='pl', p=[K.P(x_first, yb1), K.P(XR, yb1)], closed=False, layer='диам14')
add(t='pl', p=[K.P(x_first, yt1), K.P(XR, yt1)], closed=False, layer='диам14')
for i in range(int((XR - x_first) / 200) + 1):
    xx = x_first + 200 * i
    for yy in (yb1 + 14, yt1 - 14): add(t='clone', h='24323', base=[534291, 275556], to=K.P(xx, yy), s=14 * 4 / 32.0)
sk = [(x_first + SK_LEG[D0], yb1 - 14), (x_first - 7, yb1 - 14), (x_first - 7, yt1 + 14), (x_first + SK_LEG[D0], yt1 + 14)]
add(t='pl', p=[K.P(*q) for q in sk], closed=False, layer='диам14', color=3)
f1 = [(150, yb1 + 28), (450, yb1 + 28), (450, yt1 - 28), (750, yt1 - 28), (750, yb1 + 28), (1050, yb1 + 28)]
add(t='pl', p=[K.P(*q) for q in f1], closed=False, layer='диам12')
K.chain([-4100, -4100 + CB, -3700 - CT, -3700], -625, -1000, vert=True)
K.dim(-4100, -3700, (-625, -1350), vert=True)
K.chain([-625, -125, 0, 125], -3350, -3150)                           # wall binding 125|125 and console
K.dim(-625, x_first, (-4200, -4450))
nn = int((XR - 100 - x_first) / 200)
dimtxt(K, x_first, x_first + 200 * nn, (-4200, -4450), '200x%d=%d' % (nn, 200 * nn))
K.note('1', (XR + 250, -4450), [(XR + 50, -4450)], l2='ш.200', arrow='arrow')
K.note('1', (900, -3450), [(700, yt1)], l2='ш.200', arrow='oblique')
K.note('1', (300, -4450), [(100, yb1 + 14), (500, yb1 + 14)], l2='ш.200', arrow='none')
K.note('Ск1', (-950, -3450), [(x_first - 7, -3900)], arrow='oblique')
K.note('Ф1', (1300, -3450), [(750, -3850)], l2='ш.400х400', arrow='oblique')
K.note('Стена', (450, -3250), [(125, -3500)], l2='условно не показана', arrow='arrow')
K.axis('k21a', 'А', (0, -3200), (0, -4800))
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,100', -4100, 1)]): K.level('k21l%d' % i, v, -625, z, down=dn)

'''
s = s[:a] + new32 + s[b:]
R = [
 ("pos = [dict(n='1', d=D0, L='пог.м.', cnt=None, note='низ+верх, вдоль осей 1-3'), dict(n='2', d=D0, L='пог.м.', cnt=None, note='низ+верх, вдоль осей А-Д')]\nnxt = [3]",
  "pos = [dict(n='1', d=D0, L='пог.м.', cnt=None, note='основная, низ+верх, оба направления')]\nnxt = [2]"),
 ("gx = lambda v: FXO + 100 + 200 * round((v - FXO - 100) / 200.0)           # base bar lines",
  "gx = lambda v: FXO + 50 + 200 * round((v - FXO - 50) / 200.0)             # base bar lines (50 from the edge)"),
 ("            S.chain(sorted({xa, xb} | set(ax[:1])), p0, p0 - 450)                  # length bound to an axis, under the first bar",
  "            S.chain(sorted({xa, xb} | set(ax[:1])), p1, p1 + 300)                  # length bound to an axis, right above the bar"),
 ("            tgt = ((xa + xb) / 2 + 300, p1)",
  "            xc = (xa + xb) / 2 + 400; tg = [(xc, p0), (xc, p1)] if n > 1 else [(xc, p0)]\n            org = (xc, (p0 + p1) / 2) if n > 1 else (xc + 300, p0 - 700)"),
 ("            S.chain(sorted({ya, yb} | set(ay[:1])), p0, p0 - 450, vert=True)",
  "            S.chain(sorted({ya, yb} | set(ay[:1])), p0, p0 - 300, vert=True)"),
 ("            tgt = (p1, (ya + yb) / 2 + 300)",
  "            yc = (ya + yb) / 2 + 400; tg = [(p0, yc), (p1, yc)] if n > 1 else [(p0, yc)]\n            org = ((p0 + p1) / 2, yc) if n > 1 else (p0 + 400, yc + 400)"),
 ("note=('низ' if key.startswith('bot') else 'верх') + ', между поз.' + ('1' if dr == 'x' else '2'), key=(d, L)))",
  "note=('низ' if key.startswith('bot') else 'верх') + ', между поз.1', key=(d, L)))"),
 ("        S.note(pn, (tgt[0] + 400, tgt[1] + 400), [tgt], l2='ш.200', arrow='oblique')",
  "        S.note(pn, org, tg, l2='ш.200', arrow='oblique')                    # analog: note on the line linking first and last bar"),
 ("    'Поз. 1, 2 - %%C14 A500C шаг 200 в нижней и верхней сетке (основная арматура по толщине плиты 400 мм).',",
  "    'Поз. 1 - %%C14 A500C шаг 200 в нижней и верхней сетке в обоих направлениях (основная арматура по толщине плиты 400 мм).',"),
]
for x, y in R:
    assert x in s, x
    s = s.replace(x, y)
open(p, 'w', encoding='utf-8').write(s)
print('patched')
