"""Лист 3.5 «Фундамент Фм-1. Разрезы, спецификация» (A2 1:100 frame of the АБК analog, sections 1:50 / 1:25)."""
import sys, math, re
import ab, fm2 as F

X0, Y0 = -750903.0, -1749172.0
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
TP = ['37FC02', '37FCBB', '37FB36', '37FB09', '37FB38']
SPEC, STEEL = '37FCCB', '37FCCC'
m = ab.tagmap()
O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1}]
if 'T35:37FC02' not in m:
    O.append({'t': 'import', 'file': ABK, 'h': TP, 'base': [0, 0], 'to': [0, -80000], 'pre': 'T35:'})
T_BAR, T_THIN, T_NOTE, T_DIM, T_TTL = ['T35:' + h for h in TP]
LV_T = {'-1,500': 'g31b_6', '-0,500': 'g31b_4'}      # 1:100 level marks of sheet 3.1 (values set there)
O.append({'t': 'eraseregion', 'win': [X0 - 5000, Y0 - 2000, X0 + 59400, Y0 + 40000],
          'keep': ['37FB3A', '37FC4A', '37FC4B', '37FC4D', SPEC, STEEL]})
_n = [0]


def tag():
    _n[0] += 1; return 'g35_%d' % _n[0]


class V:
    def __init__(s, ox, oy, k): s.ox, s.oy, s.k = X0 + ox, Y0 + oy, k
    def P(s, x, z): return [round(s.ox + s.k * x, 1), round(s.oy + s.k * z, 1)]


def pl(v, pts, layer=None, lw=None, closed=False, tmpl=None):
    if tmpl:
        t = tag(); O.append({'t': 'clone', 'h': tmpl, 'tag': t}); O.append({'t': 'plset', 'h': t, 'p': [v.P(*p) for p in pts], 'closed': closed})
    else:
        O.append({'t': 'pl', 'p': [v.P(*p) for p in pts], 'layer': layer, 'lw': lw, 'closed': closed, 'tag': tag()})


def rect(v, x0, z0, x1, z1, layer='Размеры', lw=30):
    pl(v, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], layer, lw, True)


def dot(v, x, z, d):
    c = v.P(x, z); r = v.k * d / 2
    lay = 'диам%d' % d
    O.append({'t': 'circle', 'c': c, 'r': r, 'layer': lay})
    O.append({'t': 'hatch', 'pat': 'SOLID', 'layer': lay, 'loops': [[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]]})


def dim(v, p1, p2, at, vertical=False, txt=None, tx=None):
    a, b = v.P(*p1), v.P(*p2)
    d = {'t': 'dim', 'h': T_DIM, 'p1': a, 'p2': b, 'rot': math.pi / 2 if vertical else 0, 'lfac': 1 / v.k, 'txt': txt or '',
         'dl': [v.ox + v.k * at, a[1]] if vertical else [a[0], v.oy + v.k * at]}
    if tx: d['tx'] = v.P(*tx)
    O.append(d)


def note(v, l1, l2, tgt, org, arrow='Oblique'):
    h = tag(); O.append({'t': 'clone', 'h': T_NOTE, 'tag': h})
    O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': v.P(*tgt)})
    O.append({'t': 'mcset', 'h': h, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': v.P(*org), 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow}})


def title(v, text, xa, xb, z):
    x = (xa + xb) / 2 - len(text) * 240 / 2 / v.k
    h = tag(); O.append({'t': 'clone', 'h': T_TTL, 'tag': h})
    O.append({'t': 'settext', 'h': h, 's': '{\\L' + text + '}'})
    O.append({'t': 'moveto', 'h': h, 'idx': 0, 'to': v.P(x, z)})


def level(v, x, z, value):
    src = LV_T['-1,500']
    t = tag(); O.append({'t': 'clone', 'h': src, 'tag': t})
    q = v.P(x, z)
    O.append({'t': 'move', 'h': [t], 'd': [q[0] - (-1107303 + 6800), q[1] - (Y0 + 8800)]})
    if value != '-1,500': O.append({'t': 'levelval', 'h': t, 'old': '-1,500', 'value': value})


def pad_section(v, L, along_y, name):
    """z = level in mm (-1600 ... +900); x from 0 to L across the pad"""
    rect(v, 0, -1500, L, -500)
    rect(v, -100, -1600, L + 100, -1500, 'Размеры', 5)
    for a, b in ((-350, 0), (L, L + 350)):                      # beam stubs (axis -1.000)
        pl(v, [(a, -1300), (b, -1300)], 'Размеры', 30); pl(v, [(a, -700), (b, -700)], 'Размеры', 30)
    cw = 450 if along_y else 350
    pl(v, [(L / 2 - cw, -500), (L / 2 - cw, 900)], 'Размеры', 5); pl(v, [(L / 2 + cw, -500), (L / 2 + cw, 900)], 'Размеры', 5)
    line_b, dots_b = (F.P1, F.P2) if along_y else (F.P2, F.P1)
    # bottom: pos 1 lower layer (-1440), pos 2 upper (-1420); top: pos 3 upper (-558), pos 4 lower (-574)
    if along_y:
        pl(v, [(50, -1440), (L - 50, -1440)], 'диам20', 40)
        for p in F.P2: dot(v, p, -1420, 20)
        pl(v, [(125, -558), (L - 125, -558)], 'диам16', 40)
        for p in F.P4: dot(v, p, -574, 16)
    else:
        for p in F.P1: dot(v, p, -1440, 20)
        pl(v, [(50, -1420), (L - 50, -1420)], 'диам20', 40)
        for p in F.P3: dot(v, p, -558, 16)
        pl(v, [(125, -574), (L - 125, -574)], 'диам16', 40)
    for e, s in ((40, 1), (L - 40, -1)):                       # Ск1
        pl(v, [(e + s * 1000, -1460), (e, -1460), (e, -540), (e + s * 1000, -540)], 'диам16', 40)
    # beam bars: own direction = lines (z -1220/-780), crossing beam = dots (z -1240/-760)
    pl(v, [(-350, -1220), (L + 350, -1220)], 'диам20', 40); pl(v, [(-350, -780), (L + 350, -780)], 'диам20', 40)
    for b in F.BAR_B:
        dot(v, L / 2 + b, -1240, 20); dot(v, L / 2 + b, -760, 20)
    offs = F.COLY if along_y else F.COLX
    zb = -1500 + 50 + 40
    for d in offs:
        x = L / 2 + d; s = 1 if d > 0 else -1
        top = -500 + (600 if d in (offs[0], offs[-1]) else 1200)
        pl(v, [(x + s * 200, zb), (x, zb), (x, top)], 'диам28', 40)
    w = (F.X2[1] if along_y else F.X2[0]) / 2
    for z in (-700, -950, -1200):
        pl(v, [(L / 2 - w, z), (L / 2 + w, z)], 'диам10', 30)
    # dims
    dim(v, (0, -1600), (L / 2, -1600), -2000); dim(v, (L / 2, -1600), (L, -1600), -2000)
    dim(v, (-100, -1600), (L + 100, -1600), -2400)
    xr = L + 350
    dim(v, (xr, -1600), (xr, -1500), xr + 500, True, None, (xr + 500 + 170, -1760))
    dim(v, (xr, -1500), (xr, -500), xr + 500, True)
    dim(v, (xr, -500), (xr, 100), xr + 500, True); dim(v, (xr, 100), (xr, 700), xr + 500, True)
    for p, q in ((-1500, -1300), (-1300, -700), (-700, -500)):
        dim(v, (xr, p), (xr, q), xr + 1100, True, None, (xr + 1100 + 170, p - 150) if q - p < 300 and p < -1000 else ((xr + 1100 + 170, q + 150) if q - p < 300 else None))
    level(v, -900, -500, '-0,500'); level(v, -900, -1500, '-1,500')
    p_line, p_dots = ('1(%%C20)', '2(%%C20)') if along_y else ('2(%%C20)', '1(%%C20)')
    t_line, t_dots = ('3(%%C16)', '4(%%C16)') if along_y else ('4(%%C16)', '3(%%C16)')
    note(v, p_line, '', (L * 0.2, -1440 + (0 if along_y else 20)), (-900, -1150))
    note(v, p_dots, '', (dots_b[2], -1430), (-900, -1900), 'None')
    note(v, t_line, '', (L * 0.2, -566), (-900, -250))
    note(v, 'Ск1(%%C16)', '', (40, -1000), (-900, -700))
    note(v, '5(%%C20)', '', (L * 0.75, -780), (L * 0.75 + 400, 300))
    note(v, 'Вп1(%%C28)', '', (L / 2 + offs[-1], 400), (L / 2 + offs[-1] + 600, 1000))
    note(v, 'Вп2(%%C28)', '', (L / 2 + offs[1], 200), (L / 2 + offs[0] - 600, 600))
    if along_y:                                                # КР-1 at both ends of the pad (clear of the dowels)
        for a0 in (200, L - 900):
            pl(v, [(a0, -1410), (a0, -590), (a0 + 700, -590), (a0 + 700, -1410), (a0, -1410)], 'диам12', 40)
        note(v, 'КР-1(%%C12)', '', (200, -1250), (-900, -1525))
    note(v, 'Х2(%%C10)', '', (L / 2 - w, -1200), (-900, -2350))
    title(v, name, 0, L, 1500)


v1 = V(8700, 33500, 2); pad_section(v1, F.PY, True, 'Разрез 1 - 1')
v2 = V(25000, 33500, 2); pad_section(v2, F.PX, False, 'Разрез 2 - 2')

# beam section 3-3, 1:25
v3 = V(9000, 19000, 4)
rect(v3, -175, 0, 175, 600)
rect(v3, -275, -100, 275, 0, 'Размеры', 5)
for b in F.BAR_B: dot(v3, b, 60, 20); dot(v3, b, 540, 20)
for s in (-1, 1): dot(v3, s * 117, 300, 12)
a, b = F.X1
pl(v3, [(-a / 2, 300 - b / 2), (a / 2, 300 - b / 2), (a / 2, 300 + b / 2), (-a / 2, 300 + b / 2)], 'диам10', 30, True)
pl(v3, [(-a / 2, 300 + b / 2), (-a / 2 + 50, 300 + b / 2 - 50)], 'диам10', 30)
dim(v3, (-175, -100), (0, -100), -300); dim(v3, (0, -100), (175, -100), -300); dim(v3, (-275, -100), (275, -100), -450)
dim(v3, (-175, 0), (-175, 600), -420, True); dim(v3, (275, -100), (275, 0), 420, True, None, (560, -150))
level(v3, -750, 600, '-0,700'); level(v3, -750, 0, '-1,300')
note(v3, '5(%%C20)', '3+3', (117, 540), (600, 760), 'None')
note(v3, '6(%%C12)', '', (117, 300), (600, 380), 'None')
note(v3, 'Х1(%%C10)', 'см. лист 3.4', (a / 2, 150), (600, 40))
pl(v3, [(-92, 328), (-130, 300), (130, 300), (92, 272)], 'диам10', 30)
note(v3, 'Шп1(%%C10)', 'шаг хомутов', (-60, 300), (-600, 420))
title(v3, 'Разрез 3 - 3', -175, 175, 900)

# ---------------- ведомость деталей
TX0, TY1, CW0, CW, RH = X0 + 33900, Y0 + 38200, 1300, 5000, 2000
DET = ['Ск1', 'Х1', 'Х2', 'Вп1', 'Вп2', 'Шп1', 'КР-1']
TY0 = TY1 - 800 - RH * len(DET)


def ln(pts, layer='0', lw=30, closed=False):
    O.append({'t': 'pl', 'p': [[round(p, 1), round(q, 1)] for p, q in pts], 'layer': layer, 'lw': lw, 'closed': closed, 'tag': tag()})


def tx(x, y, s, att=5, rot=None):
    d = {'t': 'mtext', 'at': [round(x, 1), round(y, 1)], 'h': 250, 'layer': 'Размеры', 's': s, 'att': att}
    if rot is not None: d['rot'] = rot
    O.append(d)


tx(TX0 + (CW0 + CW) / 2, TY1 + 450, 'Ведомость деталей')
ln([(TX0, TY0), (TX0 + CW0 + CW, TY0), (TX0 + CW0 + CW, TY1), (TX0, TY1)], closed=True)
ln([(TX0 + CW0, TY0), (TX0 + CW0, TY1)]); ln([(TX0, TY1 - 800), (TX0 + CW0 + CW, TY1 - 800)])
tx(TX0 + CW0 / 2, TY1 - 400, 'Поз.'); tx(TX0 + CW0 + CW / 2, TY1 - 400, 'Эскиз')
PP = {p[0]: p for p in F.POS}
for k, pos in enumerate(DET):
    yt = TY1 - 800 - RH * k; yb = yt - RH
    if k: ln([(TX0, yt), (TX0 + CW0 + CW, yt)])
    tx(TX0 + CW0 / 2, (yt + yb) / 2, pos)
    _, _, d, cls, L, n, _ = PP[pos]
    tx(TX0 + CW0 + CW / 2, yb + 260, '%%%%C%d A%s  L=%d' % (d, cls, L))
    sx, sy = TX0 + CW0 + 900, yb + 650
    lay = 'диам%d' % d
    if pos == 'Ск1':
        ln([(sx + 2800, sy + 1000), (sx, sy + 1000), (sx, sy), (sx + 2800, sy)], lay, 40)
        tx(sx + 1400, sy + 1170, '1000'); tx(sx - 180, sy + 500, '%d' % (F.PH - 80), rot=math.pi / 2)
    elif pos.startswith('Х'):
        a, b = F.X1 if pos == 'Х1' else F.X2
        h = 950; w = h * a / b
        ln([(sx, sy), (sx + w, sy), (sx + w, sy + h), (sx, sy + h)], lay, 30, True)
        ln([(sx, sy + h), (sx + 90, sy + h - 90)], lay, 30)
        tx(sx + w / 2, sy + h + 170, '%d' % a); tx(sx - 180, sy + h / 2, '%d' % b, rot=math.pi / 2)
        tx(sx + w + 400, sy + h / 2, 'крюки 2х100', att=4)
    elif pos == 'Шп1':
        ln([(sx + 400, sy + 750), (sx + 150, sy + 500), (sx + 2900, sy + 500), (sx + 2650, sy + 250)], lay, 30)
        tx(sx + 1500, sy + 680, '%d' % (2 * 117 + 10)); tx(sx + 1500, sy + 50, 'крюки 135° 2х100')
    elif pos == 'КР-1':
        ln([(sx, sy + 100), (sx, sy + 800), (sx + 700, sy + 800), (sx + 700, sy + 100), (sx, sy + 100)], lay, 40)
        ln([(sx + 700, sy + 800), (sx + 1000, sy + 1000), (sx + 300, sy + 1000), (sx, sy + 800)], lay, 25)
        tx(sx + 650, sy + 1180, '700х700'); tx(sx - 180, sy + 450, '%d' % F.KR_H, rot=math.pi / 2)
        tx(sx + 1500, sy + 450, 'шахматно', att=4)
    else:
        up = L - 200 - F.DOW_IN
        ln([(sx, sy + 900), (sx + 3200, sy + 900), (sx + 3200, sy + 600)], lay, 40)
        tx(sx + 1600, sy + 1080, '%d' % (L - 200)); tx(sx + 3400, sy + 750, '200', rot=math.pi / 2)

# ---------------- notes
O.append({'t': 'mtext', 'at': [X0 + 2300, Y0 + 7800], 'h': 250, 'w': 30000, 'layer': 'Размеры',
          's': '1. Подушки 2000х3000х1000 (верх -0.500, низ -1.500) и балки 350х600 (ось -1.000) - как в расчете ЛИРА. Бетон С20/25 (B25) W6 F150, подготовка С8/10 t=100.\\P'
               '2. Защитный слой: низ подушки 50, верх и боковые грани 40-50; балки - 50 до оси продольных стержней.\\P'
               '3. Стыки продольной арматуры балок внахлест: %%C20 - 1220, %%C12 - 730, в пределах подушек, вразбежку (не более 50% в одном сечении).\\P'
               '4. Схемы раскладки: по буквенным осям - лист 3.2, по цифровым - 3.3, хомуты - 3.4, выпуски - 3.6.'})
O += [{'t': 'settext', 'h': '37FC4B', 's': 'Фундамент Фм-1. Разрезы. Спецификация'}, {'t': 'settext', 'h': '37FC4D', 's': '3.5'},
      {'t': 'vpset2', 'layout': '3.5', 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [X0, Y0 - 2000, X0 + 59400, Y0 + 40000], 'scale': 100},
      {'t': 'save'}]
if len(sys.argv) > 1:
    out = ab.run(O, 'g35', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'import' in l)[-2500:])
