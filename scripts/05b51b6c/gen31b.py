"""Sheet 3.1 -> A2: plan of Фм-1 without column hatches / column bindings, plus formwork sections 1-1, 2-2 (pads), 3-3 (beam, axis -1.000 as in LIRA)."""
import sys, json, math, ezdxf
import ab

X0, Y0 = -1107303.0, -1749172.0
A2 = ['3E425D', '3E425E', '3E425F', '3E4261']; A2X0 = -1701303.0
E = json.load(open('w/e31.json', encoding='utf-8'))
d = ezdxf.readfile('w/live.dxf')
meas = {e['h']: round(d.entitydb.get(e['h']).get_measurement()) for e in E if e['t'] == 'DIMENSION'}
frame = [e['h'] for e in E if e['t'] == 'SPDSFORMAT' or (e['t'] == 'INSERT' and e['e'][1] < Y0 + 1000) or (e['t'] == 'MTEXT' and e['lay'] == 'О_Формат')]
cols = [e['h'] for e in E if (e['t'] == 'HATCH' and e['lay'] == '.') or (e['t'] == 'LWPOLYLINE' and e['lay'] == 'О_Формат')]
binds = [h for h, m in meas.items() if m in (350, 450)]
T_DIM = next(h for h, m in meas.items() if m == 1000)
mt = [e for e in E if e['t'] == 'MTEXT' and e['lay'] == 'Размеры']
T_TTL = max(mt, key=lambda e: e['e'][3])['h']          # plan title (top)
NOTES = min(mt, key=lambda e: e['e'][3])['h']
T_OUT, T_HAT, T_LM = '3D9E56', '3D9E57', '3D9F9C'
LM_ARROW, LM_ZERO = (-1146453.0, -1738572.0), -1737072.0
skip = set(frame + cols + binds + [NOTES])
C = [e for e in E if e['h'] not in skip]
bx0 = min(e['e'][0] for e in C); by0 = min(e['e'][1] for e in C); bx1 = max(e['e'][2] for e in C); by1 = max(e['e'][3] for e in C)
dx = X0 + 2000 + (57400 - (bx1 - bx0)) / 2 - bx0
dy = Y0 + 42000 - 700 - by1
print('content %.0f x %.0f, move %.0f %.0f; erase cols %d binds %d' % (bx1 - bx0, by1 - by0, dx, dy, len(cols), len(binds)))

O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1},
     {'t': 'movewin', 'win': [bx0 - 1, by0 - 1, bx1 + 1, by1 + 1], 'd': [dx, dy], 'skip': list(skip)},
     {'t': 'clonexf', 'hs': A2, 'd': [X0 - A2X0, 0], 'pre': 'a2_31_'},
     {'t': 'erase', 'h': frame + cols + binds},
     {'t': 'settext', 'h': 'a2_31_3E4261', 's': 'Опалубочный чертеж фундамента Фм-1'},
     {'t': 'settext', 'h': 'a2_31_3E425F', 's': '3.1'}]
_n = [0]


def tag():
    _n[0] += 1; return 'g31b_%d' % _n[0]


def W(x, y): return [round(X0 + x, 1), round(Y0 + y, 1)]


def rect(x0, y0, x1, y1, cut):
    p = [W(x0, y0), W(x1, y0), W(x1, y1), W(x0, y1)]
    t = tag(); O.append({'t': 'clone', 'h': T_OUT, 'tag': t}); O.append({'t': 'plset', 'h': t, 'p': p, 'closed': True})
    if cut:
        th = tag(); O.append({'t': 'clone', 'h': T_HAT, 'tag': th}); O.append({'t': 'hatchset', 'h': th, 'loops': [p]})


def thin(x0, y0, x1, y1):
    t = tag(); O.append({'t': 'pl', 'p': [W(x0, y0), W(x1, y0), W(x1, y1), W(x0, y1)], 'closed': True, 'layer': 'Размеры', 'tag': t})


def dim(p1, p2, at, vertical=False, txt=None, tx=None):
    o = {'t': 'dim', 'h': T_DIM, 'p1': W(*p1), 'p2': W(*p2), 'dl': W(at, 0) if vertical else W(0, at), 'rot': math.pi / 2 if vertical else 0, 'txt': txt or ''}
    if tx: o['tx'] = W(*tx)
    O.append(o)


def level(x, y, zero_y, value):
    t = tag(); O.append({'t': 'clone', 'h': T_LM, 'tag': t})
    O.append({'t': 'move', 'h': [t], 'd': [X0 + x - LM_ARROW[0], Y0 + y - LM_ARROW[1]]})
    if value != '-1,500': O.append({'t': 'levelval', 'h': t, 'old': '-1,500', 'value': value})


def title(text, xc, y):
    t = tag(); O.append({'t': 'clone', 'h': T_TTL, 'tag': t})
    O.append({'t': 'settext', 'h': t, 's': '{\\L%s}' % text})
    O.append({'t': 'moveto', 'h': t, 'idx': 0, 'to': W(xc - len(text) * 240 / 2, y)})


TOP = 9800                      # y of the top of pads / beam reference on the sheet


def pad_section(xc, w, name):
    z0 = TOP + 500              # ±0.000
    rect(xc - w / 2, TOP - 1000, xc + w / 2, TOP, True)
    thin(xc - w / 2 - 100, TOP - 1100, xc + w / 2 + 100, TOP - 1000)
    dim((xc - w / 2, TOP - 1100), (xc, TOP - 1100), TOP - 1700)
    dim((xc, TOP - 1100), (xc + w / 2, TOP - 1100), TOP - 1700)
    dim((xc - w / 2, TOP - 1100), (xc + w / 2, TOP - 1100), TOP - 2300)
    dim((xc + w / 2, TOP), (xc + w / 2, TOP - 1000), xc + w / 2 + 700, True)
    dim((xc + w / 2 + 100, TOP - 1000), (xc + w / 2 + 100, TOP - 1100), xc + w / 2 + 700, True, None, (xc + w / 2 + 1000, TOP - 1400))
    level(xc - w / 2 - 200, TOP, z0, '-0,500'); level(xc - w / 2 - 200, TOP - 1000, z0, '-1,500')
    title(name, xc, TOP + 1500)


def beam_section(xc, name):
    bt = TOP - 200              # beam top -0.700 drawn 200 below the pad top line
    z0 = bt + 700
    rect(xc - 175, bt - 600, xc + 175, bt, True)
    thin(xc - 275, bt - 700, xc + 275, bt - 600)
    dim((xc - 175, bt - 700), (xc, bt - 700), bt - 1300, False, None, (xc - 500, bt - 1300))
    dim((xc, bt - 700), (xc + 175, bt - 700), bt - 1300, False, None, (xc + 500, bt - 1300))
    dim((xc - 275, bt - 700), (xc + 275, bt - 700), bt - 1900)
    dim((xc + 175, bt), (xc + 175, bt - 600), xc + 900, True)
    dim((xc + 275, bt - 600), (xc + 275, bt - 700), xc + 900, True, None, (xc + 1200, bt - 1000))
    level(xc - 400, bt, z0, '-0,700'); level(xc - 400, bt - 600, z0, '-1,300')
    title(name, xc, TOP + 1500)


pad_section(8500, 3000, 'Разрез 1 - 1')
pad_section(19500, 2000, 'Разрез 2 - 2')
beam_section(28500, 'Разрез 3 - 3')
O += [{'t': 'moveto', 'h': NOTES, 'idx': 0, 'to': W(2300, 4200)},
      {'t': 'settext', 'h': NOTES, 's': '1. Фундамент Фм-1 монолитный (как в расчете ЛИРА): подушки 2000х3000х1000 под колоннами, верх -0.500, низ -1.500; '
       'фундаментные балки 350х600 по всем осям, ось балок -1.000 (верх -0.700, низ -1.300). Бетон С20/25 (B25) W6 F150.\\P'
       '2. Под подушками и балками - бетонная подготовка С8/10 t=100. Основание - подушка из уплотненного суглинка t=1000 и раскатные сваи - см. листы 1.3, 1.4.\\P'
       '3. Армирование - см. листы 3.2...3.6.'},
     {'t': 'vpset2', 'layout': '3.1', 'media': 'ISO_full_bleed_A2_(594.00_x_420.00_MM)', 'win': [X0, Y0, X0 + 59400, Y0 + 42000], 'scale': 100},
     {'t': 'save'}]
if len(sys.argv) > 1:
    out = ab.run(O, 'g31b', 1500)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'movewin' in l or 'levbase' in l or 'levelval' in l)[-2500:])
