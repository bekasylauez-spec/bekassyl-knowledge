import json, math, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
S = r"C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/4c62aff2-a55a-4637-9af2-523dd75c9ccb/scratchpad"
D = json.load(open(S + '/layout.json', encoding='utf-8'))
OUT = sys.argv[1] if len(sys.argv) > 1 else S + '/res.dwg'

X31, Y0, FW = -561823, -992318, 42000
def x0(k): return X31 + FW * k
def W(k, u, v): return (x0(k) + 9500 + u, Y0 + 10500 + v)
L = []
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def P(p): return "'(%.1f %.1f)" % p
def rect(lay, a, b): L.append('(rc %s %s %s)' % (q(lay), P(a), P(b)))
def line(lay, a, b): L.append('(ln %s %s %s)' % (q(lay), P(a), P(b)))
def text(lay, p, h, s, rot=0, just='MC'):
    L.append('(tx %s %s %g %s %.6f %s)' % (q(lay), P(p), h, q(s.replace('³', '\\U+00B3')), rot, q(just)))
def hatch_last(): L.append('(hl)')

FBSN = {'1': 'ФБС 24.4.6-т', '2': 'ФБС 12.4.6-т', '3': 'ФБС 9.4.6-т'}
PHYS = {'1': 2380, '2': 1180, '3': 880}
COLS = [(8950, 0), (12650, 0), (8950, 5400), (12650, 5400), (8950, 7500), (12650, 7500), (8950, 12900), (12650, 12900)]

SHEETS = {6: ('3.7', 'Схема раскладки фундаментных блоков. 1-й ряд (отм. -1.400...-0.800)'),
          7: ('3.8', 'Схема раскладки фундаментных блоков. 2-й ряд (отм. -0.800...-0.200)'),
          8: ('3.9', 'Схема раскладки плит перекрытия над 1-м этажом'),
          9: ('3.10', 'Спецификация сборных элементов. Разрез 1-1')}
for k, (num, name) in SHEETS.items():
    L.append('(sheet %d %s %s %s)' % (k, q(num), q(name), q('{\\L' + name + '}')))

# ---------- ФБС
for row, k in ((1, 6), (2, 7)):
    L.append('(plancopy %d T)' % k)
    for R in D['layout'][str(row)]:
        o, c, w = R['o'], R['c'], R['w']
        for t, a, b in R['P']:
            e = b if t == 'M' else a + PHYS[t]
            if o == 'H':
                p1, p2 = W(k, a, c - w / 2), W(k, e, c + w / 2); rot = 0
            else:
                p1, p2 = W(k, c - w / 2, a), W(k, c + w / 2, e); rot = math.pi / 2
            if t == 'M':
                rect('КЖ_Монолит', p1, p2); hatch_last()
            else:
                rect('КЖ_ФБС', p1, p2)
                text('КЖ_Марки', ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), 250, t, rot)
    for u, v in COLS:
        rect('КЖ_Монолит', W(k, u - 200, v - 200), W(k, u + 200, v + 200)); hatch_last()
    # условные обозначения под планом слева
    bx, by = x0(k) + 2500, Y0 + 3600
    rect('КЖ_Монолит', (bx, by), (bx + 800, by + 400)); hatch_last()
    text('КЖ_Марки', (bx + 1100, by + 200), 250, '- монолитный участок (бетон кл. В15; под колоннами В20)', 0, 'ML')
    text('КЖ_Марки', (bx + 400, by - 500), 250, '1', 0)
    text('КЖ_Марки', (bx + 1100, by - 500), 250, '- позиция блока по спецификации (лист 3.10)', 0, 'ML')

# ---------- Плиты
k = 8
L.append('(plancopy %d nil)' % k)
MK = {'ПБ 54.15-8-30': 'П1', 'ПБ 54.12-8-30': 'П2', 'ПБ 54.10-8-25': 'П3', 'ПБ 20.15-8-30': 'П4', 'ПБ 20.12-8-30': 'П5', 'ПБ 20.10-8-25': 'П6'}
for s in D['slabs']:
    p1, p2 = W(k, s['u0'], s['v0']), W(k, s['u1'], s['v1'])
    rect('КЖ_Плиты', p1, p2)
    line('КЖ_Плиты_т', p1, p2)
    cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    text('КЖ_Марки', (cx - 220, cy + (600 if s['v1'] - s['v0'] > 3000 else 0)), 250, MK[s['mark']], math.pi / 2)
MU = [(8750, 9150), (12450, 12850)]
for a, b in MU:
    p1, p2 = W(k, a, 5460), W(k, b, 7440)
    rect('КЖ_Монолит', p1, p2); hatch_last()
bx, by = x0(k) + 2500, Y0 + 3600
rect('КЖ_Монолит', (bx, by), (bx + 800, by + 400)); hatch_last()
text('КЖ_Марки', (bx + 1100, by + 200), 250, '- монолитный участок Му-1 (бетон кл. В20, h=220)', 0, 'ML')
text('КЖ_Марки', (bx, by - 500), 250, 'Стены и пояс под плитами показаны штриховой линией. Низ плит - по АР.', 0, 'ML')

# ---------- Лист 3.10: таблица + разрез
k = 9
L.append('(seccopy %d)' % k)
cnt = D['cnt']
def n(row, t): return cnt[row].get(t, 0)
mono = D['mono']; colV = D['colV']
sc = Counter(s['mark'] for s in D['slabs']); sv = {s['mark']: s['vol'] for s in D['slabs']}
rows = [('', '', 'Фундаментные блоки', '', '', '', 'H')]
for i, t in enumerate(('1', '2', '3'), 1):
    rows.append((str(i), 'ГОСТ 13579-2018', FBSN[t], str(n('1', t) + n('2', t)), {'1': '1300', '2': '640', '3': '470'}[t], '%d+%d' % (n('1', t), n('2', t)), ''))
rows.append(('', '', 'Монолитные участки', '', '', '', 'H'))
rows.append(('Мн', '', 'Вставки, бетон кл. В15', ('%.2f' % (mono['1'] + mono['2'])).replace('.', ','), '', 'м³', ''))
rows.append(('Мк', '', 'Под колонны (8 шт.), бетон В20', ('%.2f' % colV).replace('.', ','), '', 'м³', ''))
rows.append(('Му-1', '', 'Перекрытие (2 шт.), бетон В20', ('%.2f' % (2 * 0.4 * 1.98 * 0.22)).replace('.', ','), '', 'м³', ''))
rows.append(('', '', 'Плиты перекрытия', '', '', '', 'H'))
for mk in ('ПБ 54.15-8-30', 'ПБ 54.12-8-30', 'ПБ 54.10-8-25', 'ПБ 20.15-8-30', 'ПБ 20.12-8-30', 'ПБ 20.10-8-25'):
    if sc[mk]:
        rows.append((MK[mk], 'ГОСТ 9561-2016', mk, str(sc[mk]), '%d' % round(sv[mk] * 2500, -1), '', ''))
cw = [1500, 6000, 6500, 1000, 1500, 2000]
tx0, ty0 = x0(k) + 2500, Y0 + 28400
text('КЖ_Марки', (tx0 + sum(cw) / 2, ty0 + 500), 350, 'Спецификация сборных элементов', 0)
hh, rh = 1500, 800
H = ['Поз.', 'Обозначение', 'Наименование', 'Кол.', 'Масса ед., кг', 'Приме-чание']
total = hh + rh * len(rows)
xs = [tx0]
for c in cw: xs.append(xs[-1] + c)
line('КЖ_Таблица_т', (tx0, ty0), (xs[-1], ty0)); line('КЖ_Таблица_т', (tx0, ty0 - hh), (xs[-1], ty0 - hh))
line('КЖ_Таблица_т', (tx0, ty0 - total), (xs[-1], ty0 - total))
for x in xs: line('КЖ_Таблица_т', (x, ty0), (x, ty0 - total))
for i, h in enumerate(H):
    cx = (xs[i] + xs[i + 1]) / 2
    if h == 'Масса ед., кг':
        text('КЖ_Марки', (cx, ty0 - 500), 250, 'Масса', 0); text('КЖ_Марки', (cx, ty0 - 1000), 250, 'ед., кг', 0)
    elif h == 'Приме-чание':
        text('КЖ_Марки', (cx, ty0 - 500), 250, 'Приме-', 0); text('КЖ_Марки', (cx, ty0 - 1000), 250, 'чание', 0)
    else:
        text('КЖ_Марки', (cx, ty0 - 750), 250, h, 0)
y = ty0 - hh
for r in rows:
    y2 = y - rh
    line('КЖ_Таблица', (tx0, y2), (xs[-1], y2))
    if r[6] == 'H':
        text('КЖ_Марки', ((xs[2] + xs[3]) / 2, y - 400), 250, r[2], 0)
    else:
        for i in range(6):
            if not r[i]: continue
            if i in (1, 2):
                text('КЖ_Марки', (xs[i] + 150, y - 400), 250, r[i], 0, 'ML')
            else:
                text('КЖ_Марки', ((xs[i] + xs[i + 1]) / 2, y - 400), 250, r[i], 0)
    y = y2
notes = ['Примечания:',
         '1. Блоки ФБС по ГОСТ 13579-2018 (ТОО "КИС-Актау"), ширина 400 мм, высота ряда 600 мм.',
         '2. Блоки укладывать на растворе М100 слоем 20 мм, вертикальные швы 20 мм заполнить раствором.',
         '3. Перевязка вертикальных швов смежных рядов - не менее 300 мм (обеспечена раскладкой).',
         '4. 1-й ряд - на подошву Фм-1 (отм. -1.400), 2-й ряд -0.800...-0.200, выше - пояс 200 мм до 0.000.',
         '5. Монолитные вставки - бетон кл. В15 W6 F150; под колоннами (Мк) - бетон В20 с выпусками колонн.',
         '6. Планировочная отм. земли -0.800, дно котлована -2.000, подушка ПГС 200, подбетонка 100 (лист 2).',
         '7. Боковые поверхности блоков, соприкасающиеся с грунтом, обмазать битумной мастикой за 2 раза.',
         '8. Плиты ПБ по ГОСТ 9561-2016 (КИС-Актау), опирание на стены А-Г 140...190 мм (не менее 120 мм).',
         '9. Швы между плитами замоноличить раствором М150, плиты заанкерить в монолитный пояс.',
         '10. В графе "Примечание" для блоков ФБС: количество 1-го ряда + 2-го ряда.']
ny = ty0 - total - 900
for i, s in enumerate(notes):
    text('КЖ_Марки', (tx0, ny - i * 550), 250, s, 0, 'ML')

lsp = open(S + '/fjob_core.lsp', encoding='utf-8').read()
H = json.load(open(S + '/handles.json'))
def hl_(n, l): return '(setq %s (list %s))\n' % (n, ' '.join(q(x) for x in l))
body = hl_('*PLAN*', H['plan']) + hl_('*PLANF*', H['planf']) + hl_('*SEC*', H['sec']) + '(defun fjob_body ()\n' + '\n'.join(L) + '\n)\n'
out = lsp.replace(';;BODY', body).replace('%OUT%', OUT.replace('\\', '/'))
open(S + '/fjob.lsp', 'w', encoding='cp1251').write(out)
print('ops', len(L), 'rows', len(rows), 'table bottom', ty0 - total, 'notes bottom', ny - len(notes) * 550, 'y0', Y0)
