# Подошва Фм-1 (800x300) под ФБС по новому плану -> LISP для «для клауда»
import ezdxf, json, sys
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
S = r"C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/4c62aff2-a55a-4637-9af2-523dd75c9ccb/scratchpad"
OUT = sys.argv[1]
Y0 = -992318
X35, X36, X39 = -393823, -351823, -225823
def W(x0, u, v): return (x0 + 9500 + u, Y0 + 10500 + v)

# ---- план из листа 3.9 (оси, размеры, контуры стен, колонны) без КЖ_* и без верхних/правых марок осей
d = ezdxf.readfile(S + '/kl.dxf'); m = d.modelspace()
px0, py0, px1, py1 = -562500 + 339223, -494500 - 493878, -527000 + 339223, -469500 - 493878
ax6x = X39 + 9500 + 21600; axAy = Y0 + 10500 + 12900
plan = []
for e in m:
    if e.dxf.layer.startswith('КЖ_') or e.dxf.layer == 'О_Формат': continue
    try: b = bbox.extents([e])
    except Exception: continue
    if not b.has_data: continue
    if not (b.extmin.x >= px0 and b.extmax.x <= px1 and b.extmin.y >= py0 and b.extmax.y <= py1): continue
    if e.dxftype() == 'HATCH' and b.extmax.y - b.extmin.y > 1000: continue
    if e.dxftype() == 'INSERT' and e.dxf.name == 'AKSNO' and (e.dxf.insert.x > ax6x + 1000 or e.dxf.insert.y > axAy + 1000): continue
    plan.append(e.dxf.handle)
print('plan handles', len(plan))

# ---- подошва
outer = (-400, -400, 22000, 13300)
holes = [(400, 7900, 8550, 12500), (9350, 7900, 12250, 12500), (13050, 7900, 21200, 12500),
         (400, 5800, 21200, 7100),
         (400, 400, 8550, 5000), (9350, 400, 12250, 5000), (13050, 400, 20800, 5000)]
A = (outer[2] - outer[0]) * (outer[3] - outer[1]) - sum((h[2] - h[0]) * (h[3] - h[1]) for h in holes)
Ap = (outer[2] - outer[0] + 200) * (outer[3] - outer[1] + 200) - sum((h[2] - h[0] - 200) * (h[3] - h[1] - 200) for h in holes)
Vb25 = A / 1e6 * 0.3; Vb75 = Ap / 1e6 * 0.1
# ---- арматура
lay = 4 * 22.3 * 5 + 2 * 13.6 * 5 + 4 * 6.1 * 5 + 2 * 6.1      # один ряд (верх или низ), м
laps = (4 * 5 + 2 * 5) * 2 * 1.0                                   # нахлёсты 1000 мм для стержней > 11.7 м
L14 = round(lay * 2 + laps, 1)
m14 = round(L14 * 1.21, 2)
def npos(L): return int(round(L / 0.2)) + 1
x1 = 2 * (4 * npos(22.3) + 2 * (2 * npos(4.6) + npos(1.3)) + 4 * npos(4.6)) + npos(4.6)
mx1 = round(x1 * 0.66, 2)
ck = 16 * 5; mck = round(ck * 1.69, 2)
tot = round(mx1 + m14 + mck, 2)
print('A', A / 1e6, 'B25', Vb25, 'B7.5', Vb75, 'L14', L14, m14, 'X1', x1, mx1, 'Ck', ck, mck, 'tot', tot)
f2 = lambda v: '%.2f' % v
spec = {(2, 12): f2(tot), (3, 10): str(x1), (3, 11): '0.66', (3, 12): f2(mx1),
        (4, 10): '%.1f' % L14, (4, 11): '1.21', (4, 12): f2(m14),
        (5, 5): '500С', (5, 10): str(ck), (5, 11): '1.69', (5, 12): f2(mck),
        (7, 12): f2(Vb25), (8, 12): f2(Vb75)}
ved = {(6, 1): '%.1f' % mx1, (6, 2): f2(mx1), (6, 3): '0.0', (6, 4): '0.0', (6, 5): '%.1f' % (m14 + mck),
       (6, 6): '0.0', (6, 7): f2(m14 + mck), (6, 8): f2(tot)}

L = []
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def P(p): return "'(%.1f %.1f)" % p
L.append('(sheetk -84000.0 %s %s %s)' % (q('3.5'), q('Опалубочный чертеж подошвы фундамента Фм-1 на отм. -1.700'),
                                        q('{\\LОпалубочный чертеж подошвы фундамента Фм-1 на отм. -1.700}')))
L.append('(sheetk -42000.0 %s %s nil)' % (q('3.6'), q('Спецификация фундамента Фм-1. Разрез 1-1')))
L.append('(plancp (list %s) -168000.0)' % ' '.join(q(h) for h in plan))
L.append('(rc "КЖ_Фундамент" %s %s)' % (P(W(X35, outer[0], outer[1])), P(W(X35, outer[2], outer[3]))))
for h in holes:
    L.append('(rc "КЖ_Фундамент" %s %s)' % (P(W(X35, h[0], h[1])), P(W(X35, h[2], h[3]))))
for u, v in [(8950, 0), (12650, 0), (8950, 5400), (12650, 5400), (8950, 7500), (12650, 7500), (8950, 12900), (12650, 12900)]:
    pass
# размеры 400 (привязка граней подошвы к осям)
dims = [((-400, 13300), (0, 13300), (-200, 14300)),         # слева сверху: грань - ось 1
        ((21600, 13300), (22000, 13300), (21800, 14300)),   # справа сверху: ось 6 - грань
        ((-1200, 12900), (-1200, 13300), (-1500, 13100)),   # ось A - грань (вертикально)
        ((-1200, -400), (-1200, 0), (-1500, -200)),         # ось D - грань
        ((8550, 10200), (9350, 10200), (8950, 10700)),      # подошва по оси 3: 800
        ((20800, 2700), (21600, 2700), (21200, 3200)),      # ось 6 C-D: 800 | 400 (b=1200)
        ((21600, 2700), (22000, 2700), (21800, 3200)),
        ((7300, 5000), (7300, 5800), (7800, 5400))]         # подошва по оси C: 800
for a, b, c in dims:
    L.append('(dl %s %s %s)' % (P(W(X35, *a)), P(W(X35, *b)), P(W(X35, *c))))
bx, by = X35 + 2500, Y0 + 3600
for i, s in enumerate(['Примечания:',
    '1. Подошва Фм-1 b=800 мм, h=300 мм (отм. -1.700...-1.400), бетон В25, по подбетонке 100 мм из бетона В7.5.',
    '2. По оси 6 в осях C-D подошва b=1200 мм под двойную стену из ФБС;',
    '    армирование - по разрезу 1-1, 7 стержней %%c14 ш.200 в каждом ряду.',
    '3. Разрез 1-1, спецификацию и узел нахлёста см. лист 3.6. Раскладку ФБС см. листы 3.7, 3.8.']):
    L.append('(tx "КЖ_Марки" %s 250 %s 0.0 "ML")' % (P((bx, by + 1100 - i * 450)), q(s)))
L.append('(analog)')
L.append('(tables (list %s) (list %s))' % (
    ' '.join('(list %d %d %s)' % (r, c, q(v)) for (r, c), v in spec.items()),
    ' '.join('(list %d %d %s)' % (r, c, q(v)) for (r, c), v in ved.items())))
core = open(S + '/p2_core.lsp', encoding='utf-8').read()
out = core.replace(';;BODY', '(defun p2_body ()\n' + '\n'.join(L) + '\n)\n').replace('%OUT%', OUT)
open(S + '/p2.lsp', 'w', encoding='cp1251').write(out)
json.dump(dict(spec=spec and {str(k): v for k, v in spec.items()}, ved={str(k): v for k, v in ved.items()}), open(S + '/p2_vals.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ops', len(L))
