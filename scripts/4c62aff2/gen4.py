# Колонна Км-1 (400x400, 4d20, Х1 d8) лист 3.13 + Сейсмопояс СП-1 (400x300, 4d12, Х d8 ш.300) лист 3.14
import sys, math
sys.stdout.reconfigure(encoding='utf-8')
S = r"C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/4c62aff2-a55a-4637-9af2-523dd75c9ccb/scratchpad"
Y0 = -992318
XC, XS = -99823, -57823
LVL_SRC = '1E789F'
L = []; LV = []
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def P(p): return "'(%.1f %.1f)" % p
def tx(p, h, s, j='MC', lay='КЖ_Марки', rot=0.0): L.append('(tx %s %s %g %s %.6f %s)' % (q(lay), P(p), h, q(s), rot, q(j)))
def ln(a, b, lay='КЖ_Марки'): L.append('(ln %s %s %s)' % (q(lay), P(a), P(b)))
def rc(a, b, lay): L.append('(rc %s %s %s)' % (q(lay), P(a), P(b)))
def pl(pts, lay, closed=False): L.append('(pl %s (list %s) %s)' % (q(lay), ' '.join(P(p) for p in pts), 'T' if closed else 'nil'))
def dim(a, b, c, f, t=None): L.append('(dlt %s %s %s %g %s)' % (P(a), P(b), P(c), f, q(t) if t else 'nil'))
def dn(p, d, lay): L.append('(dn2 %s %g %s)' % (P(p), d, q(lay)))
def hatch_last(): L.append('(hl)')
def lvl(x, y, t): LV.append('%s;%.1f;%.1f;%s' % (LVL_SRC, x, y, t))
def leader(pts, shelf_to, text, text2=None):
    for a, b in zip(pts[:-1], pts[1:]): ln(a, b)
    x0, y0 = pts[-1]; ln((x0, y0), (shelf_to, y0))
    tx(((x0 + shelf_to) / 2, y0 + 200), 250, text)
    if text2: tx(((x0 + shelf_to) / 2, y0 - 250), 250, text2)

def table(x0, ytop, cws, header, rows, title):
    tx((x0 + sum(cws) / 2, ytop + 450), 350, title)
    xs = [x0]
    for c in cws: xs.append(xs[-1] + c)
    hh, rh = 1400, 800; tot = hh + rh * len(rows)
    for y in (ytop, ytop - hh, ytop - tot): ln((x0, y), (xs[-1], y), 'КЖ_Таблица_т')
    for x in xs: ln((x, ytop), (x, ytop - tot), 'КЖ_Таблица_т')
    for i, h in enumerate(header):
        cx = (xs[i] + xs[i + 1]) / 2
        if '|' in h:
            a, b = h.split('|'); tx((cx, ytop - 450), 250, a); tx((cx, ytop - 950), 250, b)
        else: tx((cx, ytop - 700), 250, h)
    y = ytop - hh
    for r in rows:
        ln((x0, y - rh), (xs[-1], y - rh), 'КЖ_Таблица')
        for i, s in enumerate(r):
            if s:
                if i in (1, 2): tx((xs[i] + 150, y - 400), 250, s, 'ML')
                else: tx(((xs[i] + xs[i + 1]) / 2, y - 400), 250, s)
        y -= rh
    return ytop - tot
SPEC_H = ['Поз.', 'Обозначение', 'Наименование', 'Кол.', 'Масса|ед., кг', 'Приме-|чание']

def detail_table(x0, ytop, items, title='Ведомость деталей'):
    tx((x0 + 2750, ytop + 450), 350, title)
    cw = [1500, 4000]; rh = [1000] + [2500] * len(items)
    ys = [ytop]
    for h in rh: ys.append(ys[-1] - h)
    for y in ys: ln((x0, y), (x0 + sum(cw), y), 'КЖ_Таблица_т')
    for x in (x0, x0 + cw[0], x0 + sum(cw)): ln((x, ytop), (x, ys[-1]), 'КЖ_Таблица_т')
    tx((x0 + 750, ytop - 500), 250, 'Поз.'); tx((x0 + 3500, ytop - 500), 250, 'Эскиз')
    for i, it in enumerate(items):
        yt = ys[i + 1]; cx = x0 + cw[0] + 2000; cy = yt - 1250
        tx((x0 + 750, cy), 250, it['pz'])
        it['draw'](cx, cy)
        tx((cx + 1100, yt - 2300), 200, it['L'])
    return ys[-1]

def hoop_sketch(w, h, lay):
    def f(cx, cy):
        sw = 1800 * w / max(w, h); sh = 1800 * h / max(w, h) * 0.55
        pl([(cx - sw / 2, cy - sh / 2), (cx + sw / 2, cy - sh / 2), (cx + sw / 2, cy + sh / 2), (cx - sw / 2, cy + sh / 2)], lay, True)
        pl([(cx - sw / 2, cy + sh / 2 - 120), (cx - sw / 2 + 200, cy + sh / 2 - 320)], lay)
        tx((cx, cy + sh / 2 + 220), 200, str(w)); tx((cx - sw / 2 - 250, cy), 200, str(h), 'MC', 'КЖ_Марки', math.pi / 2)
    return f
def L_sketch(a, b, lay):
    def f(cx, cy):
        pl([(cx - 900, cy + 500), (cx - 900, cy - 400), (cx + 900, cy - 400)], lay)
        tx((cx - 1150, cy + 50), 200, str(a), 'MC', 'КЖ_Марки', math.pi / 2); tx((cx, cy - 180), 200, str(b))
    return f
def bar_sketch(a, b, c, lay):
    def f(cx, cy):
        pl([(cx - 1500, cy - 300), (cx - 1100, cy - 300), (cx - 1100, cy + 500), (cx - 500, cy + 500)], lay)
        tx((cx - 1300, cy - 520), 200, str(a)); tx((cx - 1350, cy + 100), 200, str(b), 'MC', 'КЖ_Марки', math.pi / 2); tx((cx - 800, cy + 700), 200, str(c))
    return f

# ======================= 3.13 КОЛОННА Км-1 =======================
L.append('(sheetk %g %s %s %s)' % (XC - (-309823), q('3.13'), q('Колонна Км-1'), 'nil'))
cx = XC + 8000
def Yz(z): return Y0 + 8500 + (z + 1700) * 2
tx((cx, Yz(3030) + 2300), 350, 'Колонна Км-1 (8 шт.)'); ln((cx - 2200, Yz(3030) + 2050), (cx + 2200, Yz(3030) + 2050))
rc((cx - 800, Yz(-1700)), (cx + 800, Yz(-1400)), 'КЖ_Фундамент'); hatch_last()
rc((cx - 400, Yz(-1400)), (cx + 400, Yz(2730)), 'КЖ_Фундамент')
rc((cx - 1400, Yz(2730)), (cx + 1400, Yz(3030)), 'КЖ_Фундамент')
tx((cx, Yz(-1700) - 400), 250, 'Подошва Фм-1'); tx((cx, Yz(3030) + 450), 250, 'Сейсмопояс СП-1')
# стержни поз.1 (d20): низ - отгиб 200 наружу, верх - отгиб 300 внутрь пояса
for s in (-1, 1):
    xb = cx + s * 300
    pl([(xb + s * 400, Yz(-1650)), (xb, Yz(-1650)), (xb, Yz(3000)), (xb - s * 600, Yz(3000))], 'диам20')
# хомуты Х1: 50 | 100x10 | 200x9 | 230 | 100x10 | 50
zs = [-1350 + 100 * i for i in range(11)] + [-350 + 200 * i for i in range(1, 10)] + [1680 + 100 * i for i in range(11)]
for z in zs: ln((cx - 332, Yz(z)), (cx + 332, Yz(z)), 'диам8')
print('hoops', len(zs))
dx1, dx2 = cx + 2300, cx + 3100
chain = [(-1350, -350, '100х10=1000'), (-350, 1450, '200х9=1800'), (1450, 1680, '230'), (1680, 2680, '100х10=1000')]
for a, b, t in chain: dim((cx + 400, Yz(a)), (cx + 400, Yz(b)), (dx1, (Yz(a) + Yz(b)) / 2), 0.5, t)
dim((cx + 400, Yz(-1400)), (cx + 400, Yz(2730)), (dx2, Yz(600)), 0.5)
dim((cx - 800, Yz(-1700)), (cx - 800, Yz(-1400)), (cx - 1300, Yz(-1550)), 0.5)
# отметки (СПДС, копии) + выносные линии
for z, t, edge in ((-1700, '-1.700', cx - 800), (-1400, '-1.400', cx - 800), (0, '0.000', cx - 400), (2730, '+2.730', cx - 1400), (3030, '+3.030', cx - 1400)):
    xt = cx - 1900
    ln((xt, Yz(z)), (edge, Yz(z)))
    lvl(xt, Yz(z), t)
# сечение (СПДС 1-1) через колонну на отм. +0.700
L.append('(seccp %s)' % P((cx, Yz(700))))
# выноски на фасаде
leader([(cx - 300, Yz(1000)), (cx - 900, Yz(1300))], cx - 2300, '1 (%%c20)')
leader([(cx - 332, Yz(1900)), (cx - 900, Yz(2150))], cx - 2300, 'Х1 (%%c8)')
# ---- разрез 1-1 М1:20 (x5)
sxc, syc = XC + 15500, Y0 + 17500
tx((sxc, syc + 2400), 350, 'Разрез 1 - 1 (М 1:20)'); ln((sxc - 1800, syc + 2150), (sxc + 1800, syc + 2150))
rc((sxc - 1000, syc - 1000), (sxc + 1000, syc + 1000), 'КЖ_Фундамент')
h = 830
pl([(sxc - h, syc - h), (sxc + h, syc - h), (sxc + h, syc + h), (sxc - h, syc + h)], 'диам8', True)
pl([(sxc - h, syc + h - 150), (sxc - h + 300, syc + h - 450)], 'диам8'); pl([(sxc - h + 150, syc + h), (sxc - h + 450, syc + h - 300)], 'диам8')
for px, py in ((-750, -750), (750, -750), (-750, 750), (750, 750)): dn((sxc + px, syc + py), 100, 'диам20')
for a, b in ((-1000, -750), (-750, 750), (750, 1000)):
    dim((sxc + a, syc - 1000), (sxc + b, syc - 1000), ((2 * sxc + a + b) / 2, syc - 1600), 0.2)
    dim((sxc + 1000, syc + a), (sxc + 1000, syc + b), (sxc + 1600, (2 * syc + a + b) / 2), 0.2)
dim((sxc - 1000, syc - 1000), (sxc + 1000, syc - 1000), (sxc, syc - 2700), 0.2)
dim((sxc + 1000, syc - 1000), (sxc + 1000, syc + 1000), (sxc + 2700, syc), 0.2)
leader([(sxc - 750, syc + 750), (sxc - 1500, syc + 1500)], sxc - 3300, '1 (4%%c20)')
leader([(sxc - h, syc), (sxc - 1500, syc - 300)], sxc - 3300, 'Х1 (%%c8)', 'шаг по фасаду')
# ---- таблицы 3.13
n1, L1 = 4, 5150; m1u = round(L1 / 1000 * 2.466, 2)
nx = len(zs); Lx = 1510; mxu = round(Lx / 1000 * 0.395, 2)
m1 = round(n1 * m1u, 2); mx = round(nx * mxu, 2); totc = round(m1 + mx, 2); Vc = round(0.4 * 0.4 * 4.13, 2)
detail_table(XC + 19000, Y0 + 27500, [dict(pz='1', L='L=5150', draw=bar_sketch(200, 4650, 300, 'диам20')),
                                      dict(pz='Х1', L='L=1510', draw=hoop_sketch(340, 340, 'диам8'))])
rows = [('', '', 'Колонна Км-1 (на 1 шт.)', '', '', '%.2f' % totc),
        ('1', 'ГОСТ 34028-2016', '%%c20 А500С  L=5150', str(n1), '%.2f' % m1u, '%.2f' % m1),
        ('Х1', 'ГОСТ 34028-2016', '%%c8 А240  L=1510', str(nx), '%.2f' % mxu, '%.2f' % mx),
        ('', '', 'Материалы:', '', '', ''),
        ('', '', 'Бетон кл. В25, м\\U+00B3', '', '', '%.2f' % Vc)]
table(XC + 25300, Y0 + 27800, [1200, 3800, 5500, 1000, 1500, 2700], SPEC_H, rows, 'Спецификация элементов')
wx, wy = XC + 25300, Y0 + 20500
cwv = [4000, 1500, 1500, 1500, 1500, 2000]
tx((wx + sum(cwv) / 2, wy + 450), 350, 'Ведомость расхода стали, кг')
xv = [wx]
for c in cwv: xv.append(xv[-1] + c)
yv = [wy, wy - 700, wy - 1400, wy - 2100, wy - 2900, wy - 3700]
for yy in (yv[0], yv[-1]): ln((wx, yy), (xv[-1], yy), 'КЖ_Таблица_т')
for yy in yv[1:4]: ln((xv[1], yy), (xv[5], yy), 'КЖ_Таблица_т')
ln((xv[0], yv[3]), (xv[1], yv[3]), 'КЖ_Таблица_т'); ln((xv[5], yv[3]), (xv[6], yv[3]), 'КЖ_Таблица_т'); ln((wx, yv[4]), (xv[-1], yv[4]), 'КЖ_Таблица')
for x in (xv[0], xv[1], xv[5], xv[6]): ln((x, yv[0]), (x, yv[-1]), 'КЖ_Таблица_т')
ln((xv[3], yv[1]), (xv[3], yv[-1]), 'КЖ_Таблица_т')
for x in (xv[2], xv[4]): ln((x, yv[2]), (x, yv[-1]), 'КЖ_Таблица_т')
tx((wx + 2000, (yv[0] + yv[3]) / 2), 250, 'Марка элемента'); tx(((xv[1] + xv[5]) / 2, wy - 350), 250, 'Изделия арматурные')
tx(((xv[1] + xv[3]) / 2, yv[1] - 350), 250, 'А240'); tx(((xv[3] + xv[5]) / 2, yv[1] - 350), 250, 'А500С')
for i, hd in enumerate(['%%c8', 'Итого', '%%c20', 'Итого']): tx(((xv[1 + i] + xv[2 + i]) / 2, yv[2] - 350), 250, hd)
tx(((xv[5] + xv[6]) / 2, (yv[0] + yv[3]) / 2), 250, 'Всего')
for k, (nm, f) in enumerate((('Км-1 (1 шт.)', 1), ('Км-1 (8 шт.)', 8))):
    vals = [nm, '%.2f' % (mx * f), '%.2f' % (mx * f), '%.2f' % (m1 * f), '%.2f' % (m1 * f), '%.2f' % (totc * f)]
    for i, s in enumerate(vals): tx(((xv[i] + xv[i + 1]) / 2, yv[3 + k] - 400), 250, s)
notes = ['Примечания:',
    '1. Колонны Км-1 - 8 шт. по осям 3, 4 / A, B, C, D; сечение 400х400, бетон В25.',
    '2. Низ колонны - на подошве Фм-1 (отм. -1.400); стержни поз.1 ставить до бетонирования',
    '    подошвы с отгибом 200 мм на нижнюю сетку.',
    '3. В пределах ФБС (отм. -1.400...-0.200) колонна бетонируется как монолитный участок Мк.',
    '4. Верх стержней поз.1 заанкерить в сейсмопояс СП-1 отгибом 300 мм (лист 3.14).',
    '5. Хомуты Х1: шаг 100 мм на 1000 мм у низа и верха колонны, в средней части - 200 мм.',
    '6. Защитный слой бетона до хомутов - 30 мм.']
for i, s in enumerate(notes): tx((XC + 19000, Y0 + 14500 - i * 450), 250, s, 'ML')

# ======================= 3.14 СЕЙСМОПОЯС СП-1 =======================
L.append('(sheetk %g %s %s %s)' % (XS - (-309823), q('3.14'), q('Сейсмопояс СП-1 на отм. +2.730...+3.030'), 'nil'))
sx, sy = XS + 9500, Y0 + 15000
k = 10.0
tx((sx + 2000, sy + 3000 + 4200), 350, 'Сечение 1-1 сейсмопояса СП-1 (М 1:10)'); ln((sx - 2000, sy + 6950), (sx + 6000, sy + 6950))
rc((sx, sy), (sx + 4000, sy + 3000), 'КЖ_Фундамент')
for x in (sx, sx + 4000): ln((x, sy), (x, sy - 1200), 'КЖ_ФБС')
pl([(sx - 300, sy - 1200), (sx + 1700, sy - 1200), (sx + 1850, sy - 1050), (sx + 2150, sy - 1350), (sx + 2300, sy - 1200), (sx + 4300, sy - 1200)], 'КЖ_Штрих')
tx((sx + 2000, sy - 700), 250, 'Стена 1-го этажа')
ln((sx + 2000, sy + 3000), (sx + 5800, sy + 3000), 'КЖ_ФБС'); ln((sx + 2000, sy + 5200), (sx + 5800, sy + 5200), 'КЖ_ФБС')
ln((sx + 2000, sy + 3000), (sx + 2000, sy + 5200), 'КЖ_ФБС')
tx((sx + 3900, sy + 4100), 250, 'Плита ПБ (h=220)')
c = 340
pl([(sx + c, sy + c), (sx + 4000 - c, sy + c), (sx + 4000 - c, sy + 3000 - c), (sx + c, sy + 3000 - c)], 'диам8', True)
pl([(sx + c, sy + 3000 - c - 150), (sx + c + 450, sy + 3000 - c - 600)], 'диам8'); pl([(sx + c + 150, sy + 3000 - c), (sx + c + 600, sy + 3000 - c - 450)], 'диам8')
for p in ((sx + 440, sy + 440), (sx + 3560, sy + 440), (sx + 440, sy + 2560), (sx + 3560, sy + 2560)): dn(p, 120, 'диам12')
for a, b in ((0, 440), (440, 3560), (3560, 4000)): dim((sx + a, sy), (sx + b, sy), (sx + (a + b) / 2, sy - 1900), 0.1)
dim((sx, sy), (sx + 4000, sy), (sx + 2000, sy - 3000), 0.1)
for a, b in ((0, 440), (440, 2560), (2560, 3000)): dim((sx + 4000, sy + a), (sx + 4000, sy + b), (sx + 6600, sy + (a + b) / 2), 0.1)
dim((sx + 4000, sy), (sx + 4000, sy + 3000), (sx + 7700, sy + 1500), 0.1)
for z, t in ((0, '+2.730'), (3000, '+3.030')):
    ln((sx - 1500, sy + z), (sx, sy + z)); lvl(sx - 1500, sy + z, t)
leader([(sx + 440, sy + 2560), (sx - 600, sy + 3900)], sx - 2600, '1 (2%%c12)')
leader([(sx + 440, sy + 440), (sx - 600, sy - 300)], sx - 2600, '1 (2%%c12)')
leader([(sx + c, sy + 1500), (sx - 600, sy + 1800)], sx - 2600, 'Х1 (%%c8)', 'ш.300')
# количества (как ФП-1: те же стены)
L12 = 569.4; m12 = round(L12 * 0.888, 2); g = 64; mg = round(g * 0.888, 2)
nxh = 444; Lh = 1310; mhu = round(Lh / 1000 * 0.395, 2); mh = round(nxh * Lh / 1000 * 0.395, 2)
Vb = round(52.56 * 0.3, 2); a500 = round(m12 + mg, 2); tot = round(a500 + mh, 2)
detail_table(XS + 19000, Y0 + 27500, [dict(pz='Х1', L='L=1310', draw=hoop_sketch(340, 240, 'диам8')),
                                      dict(pz='Г1', L='L=1000', draw=L_sketch(500, 500, 'диам12'))])
rows = [('', '', 'Сейсмопояс СП-1', '', '', '%.2f' % tot),
        ('1', 'ГОСТ 34028-2016', '%%c12 А500С  L= пог.м', '%.1f' % L12, '0.888', '%.2f' % m12),
        ('Г1', 'ГОСТ 34028-2016', '%%c12 А500С  L=1000', str(g), '0.89', '%.2f' % mg),
        ('Х1', 'ГОСТ 34028-2016', '%%c8 А240  L=1310', str(nxh), '%.2f' % mhu, '%.2f' % mh),
        ('', '', 'Материалы:', '', '', ''),
        ('', '', 'Бетон кл. В25, м\\U+00B3', '', '', '%.2f' % Vb)]
table(XS + 25300, Y0 + 27800, [1200, 3800, 5500, 1000, 1500, 2700], SPEC_H, rows, 'Спецификация элементов')
wx, wy = XS + 25300, Y0 + 19800
xv = [wx]
for cc in cwv: xv.append(xv[-1] + cc)
yv = [wy, wy - 700, wy - 1400, wy - 2100, wy - 2900]
tx((wx + sum(cwv) / 2, wy + 450), 350, 'Ведомость расхода стали, кг')
for yy in (yv[0], yv[-1]): ln((wx, yy), (xv[-1], yy), 'КЖ_Таблица_т')
for yy in yv[1:4]: ln((xv[1], yy), (xv[5], yy), 'КЖ_Таблица_т')
ln((xv[0], yv[3]), (xv[1], yv[3]), 'КЖ_Таблица_т'); ln((xv[5], yv[3]), (xv[6], yv[3]), 'КЖ_Таблица_т')
for x in (xv[0], xv[1], xv[5], xv[6]): ln((x, yv[0]), (x, yv[-1]), 'КЖ_Таблица_т')
ln((xv[3], yv[1]), (xv[3], yv[-1]), 'КЖ_Таблица_т')
for x in (xv[2], xv[4]): ln((x, yv[2]), (x, yv[-1]), 'КЖ_Таблица_т')
tx((wx + 2000, (yv[0] + yv[3]) / 2), 250, 'Марка элемента'); tx(((xv[1] + xv[5]) / 2, wy - 350), 250, 'Изделия арматурные')
tx(((xv[1] + xv[3]) / 2, yv[1] - 350), 250, 'А240'); tx(((xv[3] + xv[5]) / 2, yv[1] - 350), 250, 'А500С')
for i, hd in enumerate(['%%c8', 'Итого', '%%c12', 'Итого']): tx(((xv[1 + i] + xv[2 + i]) / 2, yv[2] - 350), 250, hd)
tx(((xv[5] + xv[6]) / 2, (yv[0] + yv[3]) / 2), 250, 'Всего')
for i, s in enumerate(['СП-1', '%.2f' % mh, '%.2f' % mh, '%.2f' % a500, '%.2f' % a500, '%.2f' % tot]): tx(((xv[i] + xv[i + 1]) / 2, yv[3] - 400), 250, s)
notes = ['Примечания:',
    '1. Сейсмопояс СП-1 сечением 400х300 мм по всем несущим стенам 1-го этажа (схема - как ФП-1,',
    '    лист 3.11), отм. -/+2.730...+3.030, бетон В25.',
    '2. Армирование: 4%%c12 А500С (поз. 1), хомуты Х1 %%c8 А240 с шагом 300 мм.',
    '3. В углах и примыканиях - Г-образные стержни Г1 %%c12 (4 шт. на узел); нахлёст %%c12 - 860 мм.',
    '4. Стержни колонн Км-1 заводятся в пояс с отгибом 300 мм (лист 3.13).',
    '5. На пояс опираются плиты ПБ (лист 3.9), опирание не менее 120 мм; плиты заанкерить в пояс.']
notes[2] = '    лист 3.11), отм. +2.730...+3.030, бетон В25.'
for i, s in enumerate(notes): tx((XS + 2500, Y0 + 9000 - i * 450), 250, s, 'ML')

core = open(S + '/p4_core.lsp', encoding='utf-8').read()
open(S + '/p4.lsp', 'w', encoding='cp1251').write(core.replace(';;BODY', '(defun p4_body ()\n' + '\n'.join(L) + '\n)\n'))
open(S + '/lvl_copy.txt', 'w', encoding='utf-8').write('\n'.join(LV) + '\n')
print('ops', len(L), 'levels', len(LV), 'col', m1, mx, totc, Vc, 'belt', m12, mg, mh, tot, Vb)
