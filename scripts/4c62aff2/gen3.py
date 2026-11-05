# Фундаментный пояс ФП-1 400x200 (4d12 A500C, хомут d8 A240 ш.300) -> листы 3.11, 3.12
import ezdxf, sys, math
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
S = r"C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/4c62aff2-a55a-4637-9af2-523dd75c9ccb/scratchpad"
OUT = sys.argv[1]
Y0 = -992318
X35, XA, XB = -393823, -183823, -141823
d = ezdxf.readfile(S + '/kl4.dxf'); m = d.modelspace()
plan = []
X37 = -309823
ak = [e for e in m.query('INSERT[name=="AKSNO"]') if X37 < e.dxf.insert.x < X37 + 42000 and Y0 < e.dxf.insert.y < Y0 + 29700]
ymin = min(e.dxf.insert.y for e in ak); xmin = min(e.dxf.insert.x for e in ak)
ax1 = min(e.dxf.insert.x for e in ak if abs(e.dxf.insert.y - ymin) < 50)
axD = min(e.dxf.insert.y for e in ak if abs(e.dxf.insert.x - xmin) < 50) + 199
print('axis1', ax1 - X37, 'axisD', axD - Y0)
for e in m:
    if e.dxf.layer.startswith('КЖ_') or e.dxf.layer == 'О_Формат' or e.dxftype() in ('ACAD_PROXY_ENTITY', 'HATCH'): continue
    try: bb = bbox.extents([e])
    except Exception: continue
    if not bb.has_data: continue
    if not (bb.extmin.x >= X37 + 500 and bb.extmax.x <= X37 + 40000 and bb.extmin.y >= Y0 + 5000 and bb.extmax.y <= Y0 + 28000): continue
    if e.dxftype() == 'INSERT' and e.dxf.name == 'AKSNO' and (e.dxf.insert.x > ax1 + 22600 or e.dxf.insert.y > axD + 13900): continue
    if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'kolon': continue
    plan.append(e.dxf.handle)
print('plan', len(plan))

# ---- количества
def n(L): return int(L / 0.3) + 1
Lbar = (4 * 21.94 * 4) + (2 * 13.24 * 4) + (4 * 5.74 * 4)
laps = (16 + 8) * 0.86
L12 = round(Lbar + laps, 1); m12 = round(L12 * 0.888, 2)
g1 = 16 * 4; mg1 = round(g1 * 1.0 * 0.888, 2)
x2 = 4 * n(21.94) + 2 * (2 * n(5.0) + n(1.7)) + 4 * n(5.0)
x3 = 0
mx2u = round(1.11 * 0.395, 2); mx3u = round(1.91 * 0.395, 2)
mx2 = round(x2 * 1.11 * 0.395, 2); mx3 = round(x3 * 1.91 * 0.395, 2)
V = round(52.56 * 0.2, 2)
a240 = round(mx2 + mx3, 2); a500 = round(m12 + mg1, 2); tot = round(a240 + a500, 2)
print('L12', L12, m12, 'G1', g1, mg1, 'X2', x2, mx2, 'X3', x3, mx3, 'V', V, 'tot', tot)

L = []
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def P(p): return "'(%.1f %.1f)" % p
def tx(p, h, s, j='MC', lay='КЖ_Марки', rot=0.0): L.append('(tx %s %s %g %s %.6f %s)' % (q(lay), P(p), h, q(s), rot, q(j)))
def ln(a, b, lay='КЖ_Таблица'): L.append('(ln %s %s %s)' % (q(lay), P(a), P(b)))
def rc(a, b, lay): L.append('(rc %s %s %s)' % (q(lay), P(a), P(b)))
def pl(pts, lay, closed=False): L.append('(pl %s (list %s) %s)' % (q(lay), ' '.join(P(p) for p in pts), 'T' if closed else 'nil'))
def dim(a, b, c, lfac): L.append('(dl %s %s %s %g)' % (P(a), P(b), P(c), lfac))

L.append('(sheetk %g %s %s %s)' % (XA - (-309823), q('3.11'), q('Фундаментный пояс ФП-1 на отм. -0.200. Сечение 1-1'),
                                   q('{\\LСхема фундаментного пояса ФП-1 на отм. -0.200...0.000}')))
L.append('(sheetk %g %s %s nil)' % (XB - (-309823), q('3.12'), q('Спецификация фундаментного пояса ФП-1')))
L.append('(plancp2 (list %s) %g %g)' % (' '.join(q(h) for h in plan), XA + 9500 - ax1, Y0 + 10500 - axD))
def W(u, v): return (XA + 9500 + u, Y0 + 10500 + v)
for a, b in [((-200, -200), (21800, 13100)), ((200, 7700), (8750, 12700)), ((9150, 7700), (12450, 12700)), ((12850, 7700), (21400, 12700)),
             ((200, 5600), (21400, 7300)), ((200, 200), (8750, 5200)), ((9150, 200), (12450, 5200)), ((12850, 200), (21400, 5200))]:
    rc(W(*a), W(*b), 'КЖ_Фундамент')

# ---- сечение пояса М1:10 (x10) на 3.11 справа
sx, sy = XA + 34600, Y0 + 16500
k = 10.0
rc((sx, sy), (sx + 400 * k, sy + 200 * k), 'КЖ_Фундамент')
for x in (sx, sx + 4000):  # блок ФБС под поясом (обрыв)
    ln((x, sy), (x, sy - 900), 'КЖ_ФБС')
pl([(sx - 300, sy - 900), (sx + 1700, sy - 900), (sx + 1850, sy - 750), (sx + 2150, sy - 1050), (sx + 2300, sy - 900), (sx + 4300, sy - 900)], 'КЖ_Штрих')
tx((sx + 2000, sy - 500), 250, 'ФБС')
# хомут Х2 (по оси стержня d8, защитный слой 30) + крюки
c = 34 * k
pl([(sx + c, sy + c), (sx + 4000 - c, sy + c), (sx + 4000 - c, sy + 2000 - c), (sx + c, sy + 2000 - c)], 'КЖ_Арматура', True)
pl([(sx + c, sy + 2000 - c - 150), (sx + c + 450, sy + 2000 - c - 600)], 'КЖ_Арматура')
pl([(sx + c + 150, sy + 2000 - c), (sx + c + 600, sy + 2000 - c - 450)], 'КЖ_Арматура')
bars = [(sx + 440, sy + 440), (sx + 3560, sy + 440), (sx + 440, sy + 1560), (sx + 3560, sy + 1560)]
for p in bars: L.append('(dn %s 120.0)' % P(p))
# размеры (DIMLFAC 0.1)
dim((sx, sy), (sx + 440, sy), (sx + 220, sy - 1500), 0.1)
dim((sx + 440, sy), (sx + 3560, sy), (sx + 2000, sy - 1500), 0.1)
dim((sx + 3560, sy), (sx + 4000, sy), (sx + 3780, sy - 1500), 0.1)
dim((sx, sy), (sx + 4000, sy), (sx + 2000, sy - 2500), 0.1)
dim((sx + 4000, sy), (sx + 4000, sy + 440), (sx + 4900, sy + 220), 0.1)
dim((sx + 4000, sy + 440), (sx + 4000, sy + 1560), (sx + 4900, sy + 1000), 0.1)
dim((sx + 4000, sy + 1560), (sx + 4000, sy + 2000), (sx + 4900, sy + 1780), 0.1)
dim((sx + 4000, sy), (sx + 4000, sy + 2000), (sx + 6300, sy + 1000), 0.1)
# выноски: позиции
ln((sx + 440, sy + 1560), (sx - 600, sy + 3000), 'КЖ_Марки'); ln((sx + 3560, sy + 1560), (sx - 600, sy + 3000), 'КЖ_Марки')
ln((sx - 600, sy + 3000), (sx - 2400, sy + 3000), 'КЖ_Марки'); tx((sx - 1500, sy + 3200), 250, '1 (2%%c12)')
ln((sx + 440, sy + 440), (sx - 600, sy - 300), 'КЖ_Марки'); ln((sx + 3560, sy + 440), (sx - 600, sy - 300), 'КЖ_Марки')
ln((sx - 600, sy - 300), (sx - 2400, sy - 300), 'КЖ_Марки'); tx((sx - 1500, sy - 100), 250, '1 (2%%c12)')
ln((sx + c, sy + 1000), (sx - 600, sy + 1300), 'КЖ_Марки'); ln((sx - 600, sy + 1300), (sx - 2400, sy + 1300), 'КЖ_Марки')
tx((sx - 1500, sy + 1500), 250, 'Х2 (%%c8)'); tx((sx - 1500, sy + 1050), 250, 'ш.300')
tx((sx + 2000, sy + 4400), 350, 'Сечение 1-1 (М 1:10)')
ln((sx + 300, sy + 4150), (sx + 3700, sy + 4150), 'КЖ_Марки')
tx((sx + 2000, sy + 3700), 250, 'верх пояса - отм. 0.000')
# примечания 3.11
bx, by = XA + 2500, Y0 + 4800
for i, s in enumerate(['Примечания:',
        '1. Пояс ФП-1 сечением 400х200 мм по всем стенам из ФБС (отм. -0.200...0.000), бетон В25.',
        '2. Армирование: 4%%c12 А500С (поз. 1), хомуты Х2 %%c8 А240 с шагом 300 мм.',
        '3. В углах и примыканиях - Г-образные стержни Г1 %%c12 (4 шт. на узел); нахлёст %%c12 - 860 мм вразбежку.',
        '4. Сечение 1-1 действует для всех стен; спецификация - лист 3.12.']):
    tx((bx, by - i * 450), 250, s, 'ML')

# ---- лист 3.12: ведомость деталей + спецификация + ведомость стали
x0 = XB
# ведомость деталей
vx, vy = x0 + 3500, Y0 + 27500
tx((vx + 2750, vy + 450), 350, 'Ведомость деталей')
cw = [1500, 4000]; rh = [1000] + [2500] * 2
ys = [vy]
for h in rh: ys.append(ys[-1] - h)
for y in ys: ln((vx, y), (vx + sum(cw), y), 'КЖ_Таблица_т')
for x in (vx, vx + cw[0], vx + sum(cw)): ln((x, vy), (x, ys[-1]), 'КЖ_Таблица_т')
tx((vx + 750, vy - 500), 250, 'Поз.'); tx((vx + 3500, vy - 500), 250, 'Эскиз')
det = [('Х2', 340, 140, 'L=1110'), ('Г1', None, None, 'L=1000')]
for i, (pz, w, h, Ltxt) in enumerate(det):
    yt = ys[i + 1]; cx = vx + cw[0] + 2000; cy = yt - 1250
    tx((vx + 750, cy), 250, pz)
    if w:
        sw = 2400 * w / 740; sh = 600
        pl([(cx - sw / 2, cy - sh / 2), (cx + sw / 2, cy - sh / 2), (cx + sw / 2, cy + sh / 2), (cx - sw / 2, cy + sh / 2)], 'КЖ_Арматура', True)
        pl([(cx - sw / 2, cy + sh / 2 - 120), (cx - sw / 2 + 200, cy + sh / 2 - 320)], 'КЖ_Арматура')
        tx((cx, cy + sh / 2 + 220), 200, str(w)); tx((cx - sw / 2 - 250, cy), 200, str(h), 'MC', 'КЖ_Марки', math.pi / 2)
    else:
        pl([(cx - 900, cy + 500), (cx - 900, cy - 400), (cx + 900, cy - 400)], 'КЖ_Арматура')
        tx((cx - 1150, cy + 50), 200, '500', 'MC', 'КЖ_Марки', math.pi / 2); tx((cx, cy - 180), 200, '500')
    tx((cx + 1100, yt - 2300), 200, Ltxt)
# спецификация
sx0, sy0 = x0 + 21500, Y0 + 27800
cws = [1500, 5000, 6000, 1300, 1500, 2700]
tx((sx0 + sum(cws) / 2, sy0 + 450), 350, 'Спецификация элементов')
rows = [('', '', 'Фундаментный пояс ФП-1', '', '', '%.2f' % tot, 'H'),
        ('1', 'ГОСТ 34028-2016', '%%c12 А500С  L= пог.м', '%.1f' % L12, '0.888', '%.2f' % m12, ''),
        ('Г1', 'ГОСТ 34028-2016', '%%c12 А500С  L=1000', str(g1), '0.89', '%.2f' % mg1, ''),
        ('Х2', 'ГОСТ 34028-2016', '%%c8 А240  L=1110', str(x2), '%.2f' % mx2u, '%.2f' % mx2, ''),
        ('', '', 'Материалы:', '', '', '', 'H'),
        ('', '', 'Бетон кл. В25, м\\U+00B3', '', '', '%.2f' % V, '')]
hh, rhh = 1400, 800
xs = [sx0]
for c_ in cws: xs.append(xs[-1] + c_)
tot_h = hh + rhh * len(rows)
for y in (sy0, sy0 - hh, sy0 - tot_h): ln((sx0, y), (xs[-1], y), 'КЖ_Таблица_т')
for x in xs: ln((x, sy0), (x, sy0 - tot_h), 'КЖ_Таблица_т')
for i, h in enumerate(['Поз.', 'Обозначение', 'Наименование', 'Кол.', 'Масса ед., кг', 'Примечание']):
    if h == 'Масса ед., кг':
        tx(((xs[i] + xs[i + 1]) / 2, sy0 - 450), 250, 'Масса'); tx(((xs[i] + xs[i + 1]) / 2, sy0 - 950), 250, 'ед., кг')
    else: tx(((xs[i] + xs[i + 1]) / 2, sy0 - 700), 250, h)
y = sy0 - hh
for r in rows:
    ln((sx0, y - rhh), (xs[-1], y - rhh), 'КЖ_Таблица')
    for i in range(6):
        if r[i]:
            if i in (1, 2): tx((xs[i] + 150, y - 400), 250, r[i], 'ML')
            else: tx(((xs[i] + xs[i + 1]) / 2, y - 400), 250, r[i])
    y -= rhh
# ведомость расхода стали
wx, wy = x0 + 21500, Y0 + 18500
cwv = [4000, 1500, 1500, 1500, 1500, 2000]
tx((wx + sum(cwv) / 2, wy + 450), 350, 'Ведомость расхода стали, кг')
xv = [wx]
for c_ in cwv: xv.append(xv[-1] + c_)
yv = [wy, wy - 700, wy - 1400, wy - 2100, wy - 2900]
for yy in (yv[0], yv[-1]): ln((wx, yy), (xv[-1], yy), 'КЖ_Таблица_т')
for yy in yv[1:4]: ln((xv[1], yy), (xv[5], yy), 'КЖ_Таблица_т')
ln((xv[0], yv[3]), (xv[1], yv[3]), 'КЖ_Таблица_т'); ln((xv[5], yv[3]), (xv[6], yv[3]), 'КЖ_Таблица_т')
for x in (xv[0], xv[1], xv[5], xv[6]): ln((x, yv[0]), (x, yv[-1]), 'КЖ_Таблица_т')
ln((xv[3], yv[1]), (xv[3], yv[-1]), 'КЖ_Таблица_т')
for x in (xv[2], xv[4]): ln((x, yv[2]), (x, yv[-1]), 'КЖ_Таблица_т')
tx((wx + 2000, (yv[0] + yv[3]) / 2), 250, 'Марка элемента')
tx(((xv[1] + xv[5]) / 2, wy - 350), 250, 'Изделия арматурные')
tx(((xv[1] + xv[3]) / 2, yv[1] - 350), 250, 'А240'); tx(((xv[3] + xv[5]) / 2, yv[1] - 350), 250, 'А500С')
for i, h in enumerate(['%%c8', 'Итого', '%%c12', 'Итого']):
    tx(((xv[1 + i] + xv[2 + i]) / 2, yv[2] - 350), 250, h)
tx(((xv[5] + xv[6]) / 2, (yv[0] + yv[3]) / 2), 250, 'Всего')
vals = ['Пояс ФП-1', '%.2f' % a240, '%.2f' % a240, '%.2f' % a500, '%.2f' % a500, '%.2f' % tot]
for i, s in enumerate(vals):
    if s: tx(((xv[i] + xv[i + 1]) / 2, yv[3] - 400), 250, s)

core = open(S + '/p3_core.lsp', encoding='utf-8').read()
out = core.replace(';;BODY', '(defun p3_body ()\n' + '\n'.join(L) + '\n)\n').replace('%OUT%', OUT)
open(S + '/p3.lsp', 'w', encoding='cp1251').write(out)
print('ops', len(L))
