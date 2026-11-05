"""Column sheet (A2, 1:50) from the template sheet «Колонна Км-1» (Шаблон для Кж.dwg) imported with prefix PRE.
Elevation 1:50 (real size), sections 1:25 (x2, dims «СПДС М2» show real values). Run: python gen4x.py <mark> <x0> <y0> <PRE> <sheet no> [run]"""
import sys, json, math
import ab, coldata as C

MARK, X0, Y0, PRE, SNO = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
RUN = len(sys.argv) > 6 and sys.argv[6] == 'run'
col = C.COLS[MARK]; sch = C.schedule(MARK)
R = json.load(open('w/k41_list.json', encoding='utf-8'))
N2O = {r['h'].upper(): r['old'] for r in R}


def T(newh):                              # template object (handles of the 4.1 import) -> tag of this sheet's copy
    return PRE + N2O[newh.upper()]


O = []
_n = [0]


def add(**k):
    O.append(k); return k


def tag():
    _n[0] += 1; return '%s%s_%d' % ('g4_', MARK.replace('-', ''), _n[0])


def W(x, y): return [round(X0 + x, 1), round(Y0 + y, 1)]


# ---------------- layout of the elevation
bot, top = col['bot'], col['top']
CX = 4600.0; FL, FR = CX - C.BY / 2, CX + C.BY / 2
z_lo, z_hi = -1600, top + 1700
YB = 10600 - (z_lo + z_hi) / 2
def E(y, z): return W(CX + y, YB + z)          # y = along the column width (Y of the building), z = level (mm)


# ---------------- erase template content that is redrawn
ERASE_NEW = [r['h'] for r in R if (r['e'][2] < 7000 and r['e'][1] > 7700 and r['t'] != 'SPDSFORMAT')
             or (7300 < r['e'][0] and r['e'][2] < 15700 and r['e'][1] > 15500 and r['e'][3] < 20500)
             or (16500 < r['e'][0] < 20000 and r['e'][1] > 15700 and r['e'][3] < 20700 and r['t'] != 'ACAD_TABLE')
             or r['h'] in ('3E8EA8',) or r['old'] == '18E05']
REUSE = ('3E8739', '3E8737', '3E8738', '3E873B', '3E873A', '3E8EA3', '3E8E9A', '3E8E99', '3E8736', '3E8E9D')
ERASE_NEW = [PRE + N2O[h.upper()] for h in ERASE_NEW if h not in REUSE and N2O.get(h.upper())]
KEEP_TPL = ['3E8749', '3E879A', '3E878D', '3E878C', '3E879D', '3E8793', '3E8792', '3E874A', '3E8855', '3E8882', '3E8E9D',
            '3E8737', '3E8738', '3E873B', '3E873A', '3E8739', '3E8EA3', '3E8E9A', '3E8E99', '3E8736', '18CB9', '18CF8', '18CB6', '18E05']
NEWH = {r['old']: r['h'] for r in R}


def tpl(h):    # template handle given as new handle of 4.1 or old handle of the template file
    return T(h) if h.upper() in N2O else PRE + h


O.append({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
O.append({'t': 'eraseregion', 'win': [X0 - 1, Y0 - 1, X0 + 29701, Y0 + 21001]})
O.append({'t': 'import', 'file': r'D:\РАБОЧКА\Шаблон для Кж.dwg', 'wins': [[264700, 271880, 294430, 292910]], 'base': [264717, 271898], 'to': [X0, Y0], 'pre': PRE})
# detail A / ГОСТ block right, накладки table up, junk insert away
add(t='move', h=[tpl('18C89')], d=[4300, 0])
TBLN = [PRE + r['old'] for r in R if 15300 < r['e'][0] and r['e'][2] < 18600 and 3990 < r['e'][1] and r['e'][3] < 7000]
add(t='move', h=TBLN, d=[0, 3500])


def clone(h, layer=None, lw=None):
    t = tag(); d = dict(t='clone', h=tpl(h), tag=t)
    if layer: d['layer'] = layer
    if lw is not None: d['lw'] = lw
    add(**d); return t


def pl(h, pts, closed=False, layer=None, lw=None):
    t = clone(h, layer, lw); add(t='plset', h=t, p=pts, closed=closed); return t


def ln(pts, layer, lw, closed=False):
    t = tag(); add(t='pl', p=pts, layer=layer, lw=lw, closed=closed, tag=t); return t


def dot(c, r, layer='диам28'):
    add(t='circle', c=c, r=r, layer=layer)
    add(t='hatch', pat='SOLID', layer=layer, loops=[[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]])


def dim(h, p1, p2, dl, vertical=False, txt=None, tx=None):
    d = dict(t='dim', h=tpl(h), p1=p1, p2=p2, dl=dl, rot=math.pi / 2 if vertical else 0)
    d['txt'] = txt or ''
    if tx: d['tx'] = tx
    add(**d)


def note(l1, l2, tgt, org, arrow='Oblique'):
    h = clone('3E8E9D')
    add(t='moveto', h=h, idx=1, to=tgt)
    add(t='mcset', h=h, set={'FirstLine': l1, 'SecondLine': l2, 'Origin': org, 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow})


