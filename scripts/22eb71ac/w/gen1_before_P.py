# Резервуар КЖ: лист 2 (схемы расположения на отм. -3.700 и -0.900, 1:100) и лист 3 (разрезы 1-1, 2-2, 1:50)
# Local plan coords: x from axis 1, y from axis А (mm). Section coords: x along cut, y = elevation in mm (0.000 = 0).
import json, sys, math

ops = []
def add(**k): ops.append(k); return k

# ---- geometry (AR outline + LIRA elements, decisions 31.10) ----
AX = {'1': 0, '2': 8250, '3': 14750}
AY = {'А': 0, 'Б': 4100, 'В': 8400, 'Г': 12500, 'Д': 17750}
T = 250; h = T / 2
XO, XE = -h, 14750 + h          # outer faces x
YO, YE = -h, 17750 + h          # outer faces y
CON = 500                        # Фм-1 console beyond the walls (Bekassyl 31.10: as in LIRA)
FXO, FXE, FYO, FYE = XO - CON, XE + CON, YO - CON, YE + CON
pil = {  # pilasters 400x400 flush with outer face; columns 400x400; junction 500x500
    'П1Б': (-h, 3900, 275, 4300), 'П1В': (-h, 8200, 275, 8600),
    'П3Б': (14475, 3900, XE, 4300), 'П3В': (14475, 8200, XE, 8600), 'П3Г': (14475, 12300, XE, 12700),
    'ПА2': (8050, -h, 8450, 275)}
cols = {'К2Б': (8050, 3900, 8450, 4300), 'К2В': (8050, 8200, 8450, 8600)}
col3 = (8000, 12250, 8500, 12750)
walls1 = {  # outer walls См-1 split at pilasters
    'А': [(XO, YO, 8050, h), (8450, YO, XE, h)],
    'Д': [(XO, 17625, XE, YE)],
    '1': [(XO, h, h, 3900), (XO, 4300, h, 8200), (XO, 8600, h, 17625)],
    '3': [(14625, h, XE, 3900), (14625, 4300, XE, 8200), (14625, 8600, XE, 12300), (14625, 12700, XE, 17625)]}
walls2 = [(h, 12375, 8000, 12625), (8125, 12750, 8375, 17625)]   # partition См-2
necks = {'N1': (625, 10375, 2125, 11875), 'N2': (625, 13125, 2125, 14625), 'N3': (625, 15125, 2625, 17125)}
tn = 150   # neck wall (LIRA)
pit = (4625, 13125, 5625, 14125)   # приямок 1000x1000, depth 500 (assumed), base 400 under it
pitb = (4225, 12725, 6025, 14525)
beams1 = [(8075, 275, 8425, 12250), (8450, 3925, 14475, 4275), (8450, 8225, 14475, 8575), (8500, 12325, 14475, 12675)]  # Бм-1 350x500
beams2 = [(275, 3925, 8050, 4275), (275, 8225, 8050, 8575)]   # Бм-2 350x600
Z = dict(top=-900, slb=-1200, b1=-1400, b2=-1500, fnd=-3700, fbot=-4100, prep=-4200, pitb=-4200, pitbot=-4600, pitprep=-4700, neck=100, gr=-300)

# ---- template sources ----
SRC = dict(fr100='33C2', fr100o=(71667.3, 271897.8), fr50='244FB', fr50o=(556617.3, 271897.8),
           stampf=(190467.3, 271897.8), stamp=['19522'], sname='19523', snum='19525',
           axis='3201', dim='3203', lev='3227', levbase=(89797.3, 293016.1), lev0='-2,000',
           plev='239E1', plevbase=(501388, 307683), plev0='-0,080',
           bound='3262', boundbase=(88320.2, 292616.2), sec='238E8', secbase=(472785.1, 297378.5),
           title='3230', titlebase=(96393, 305204))

def rect(r): x0, y0, x1, y1 = r; return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

class Sheet:
    def __init__(s, ox, oy, sc): s.ox, s.oy, s.sc = ox, oy, sc; s.avoid_x = list(AX.values()); s.avoid_y = list(AY.values())
    def P(s, x, y): return [round(s.ox + x, 2), round(s.oy + y, 2)]
    def pl(s, pts, layer='Несущие колонны', closed=True, **k):
        return add(t='pl', p=[s.P(*p) for p in pts], closed=closed, layer=layer, **k)
    def hatch(s, loops, pat='ANSI36', sc=20, layer='Размеры', **k):
        # concrete as in the template (Bekassyl 31.10): ANSI36, scale 20 on any sheet scale, layer Размеры, 0.05 mm
        return add(t='hatch', loops=[[s.P(*p) for p in lp] for lp in loops], pat=pat, sc=sc, layer=layer, lw=5, **k)
    def solid(s, r, pat='ANSI36', **k):
        s.pl(rect(r)); s.hatch([rect(r)], pat=pat, **k)
    def hid(s, pts, closed=False):
        return add(t='pl', p=[s.P(*p) for p in pts], closed=closed, layer='Тонкая', ltype='HIDDEN2', ltscale=s.sc / 4)
    def thin(s, pts, closed=False):
        return add(t='pl', p=[s.P(*p) for p in pts], closed=closed, layer='Тонкая')
    def dim(s, a, b, off, vert=False, tx=None, txt=None):
        # chain dimension between coordinates a,b along axis; off = dim line position on the other axis
        # tx = (along, perp) text centre in local coords along the dim / across it
        if vert: p1, p2, dl, rot = s.P(off[0], a), s.P(off[0], b), s.P(off[1], a), math.pi / 2
        else: p1, p2, dl, rot = s.P(a, off[0]), s.P(b, off[0]), s.P(a, off[1]), 0
        if tx is None:                                    # №32: no axis/level line through the text
            av = getattr(s, 'avoid_y' if vert else 'avoid_x', [])
            th = 2.5 * s.sc; lo, hi = min(a, b), max(a, b); mid = (a + b) / 2
            w = len(txt or str(int(round(hi - lo)))) * 0.72 * th
            hit = [v for v in av if abs(v - mid) < w / 2 + 0.3 * th]
            if hit and hi - lo >= 7 * s.sc:
                v = hit[0]; right = (hi - v) >= (v - lo)
                along = v + (w / 2 + 0.5 * th) if right else v - (w / 2 + 0.5 * th)
                tx = (along, off[1] - 0.9 * th if vert else off[1] + 0.9 * th)
        k = dict(t='dim', h=SRC['dim'], p1=p1, p2=p2, dl=dl, rot=rot, dscale=s.sc)
        if tx: k['tx'] = s.P(tx[1], tx[0]) if vert else s.P(tx[0], tx[1])
        if txt: k['txt'] = txt
        return add(**k)
    def chain(s, pts, base, line, vert=False, inside=False):
        # short dims (< 7 mm on paper), Bekassyl 31.10: text beside the chain on its outer (text) side, near the end,
        # tied by the dim leader - not continued along the line past the extension line
        th = 2.5 * s.sc; n = len(pts) - 1
        out = 1 if line >= base else -1                     # away from the element the chain measures
        side = line + out * 2.8 * th
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            L = abs(b - a); tx = None
            if L < 7 * s.sc and n > 1:
                lo, hi = min(a, b), max(a, b)
                if i == 0: tx = (lo - 1.0 * th, side)
                elif i == n - 1: tx = (hi + 1.0 * th, side)
                elif inside: tx = ((a + b) / 2, line - out * 0.9 * th)
                else: tx = ((a + b) / 2, line + out * 1.6 * th)   # between this row and the next (rows 10 mm)
            s.dim(a, b, (base, line), vert, tx)
    def axis(s, tag, val, st, en):
        add(t='clone', h=SRC['axis'], tag=tag)
        add(t='axis', h=tag, s=s.P(*st), e=s.P(*en), val=val, scale=s.sc)
    def level(s, tag, val, x, y, down=False, right=False, ax=None):
        b = SRC['levbase']
        add(t='clone', h=SRC['lev'], base=list(b), to=s.P(x, y), tag=tag)
        add(t='levbase', h=tag, old=295016.137, new=s.oy, tol=0.5, tag=tag)   # zero level of this drawing
        add(t='levelval', h=tag, old=SRC['lev0'], value=val, tag=tag)
        if s.sc != 100: add(t='mcscale', h=tag, v=s.sc)
        f = s.sc / 100   # x = contour face; arrow 1800 (at 1:50) left of it, shelf like the template
        add(t='moveto', h=tag, idx=0, to=s.P(x, y))
        # close marks must not overlap (Bekassyl 31.10): lower one turned down (shelf below, arrow up) or put on the right
        k = 1 if right else -1; up = -1 if down else 1
        axp = ax if ax is not None else x + k * 36 * s.sc
        add(t='sp_set', h=tag, pts=[[2] + s.P(axp, y), [1] + s.P(axp + k * 1254 * f, y + up * 600 * f)])
    def plevel(s, tag, val, x, y):
        add(t='clone', h=SRC['plev'], base=list(SRC['plevbase']), to=s.P(x, y), tag=tag)
        add(t='levelval', h=tag, old=SRC['plev0'], value=val, tag=tag)
    def note(s, l1, org, tgts, l2='', arrow='arrow'):
        # shelf on the side opposite the arrow (Bekassyl 31.10): target to the right -> shelf to the left (Angle = pi)
        ang = math.pi if sum(q[0] for q in tgts) / len(tgts) > org[0] else 0
        add(t='note', l1=l1, l2=l2, origin=s.P(*org), targets=[s.P(*q) for q in tgts], scale=s.sc, arrow=arrow, layer='Размеры', angle=ang)
    def mark(s, l1, r, face=None, at=None, d=400, dx=None, dy=None, l2=''):
        # Bekassyl 31.10: arrow on the element edge facing the drawing centre (s.cx, s.cy), shelf start 300..600 from it
        # towards the centre, shelf opposite the arrow (note()).
        x0, y0, x1, y1 = r; cx, cy = s.cx, s.cy
        dxc = cx - min(max(cx, x0), x1); dyc = cy - min(max(cy, y0), y1)
        if face is None: face = ('x1' if dxc > 0 else 'x0') if abs(dxc) > abs(dyc) else ('y1' if dyc > 0 else 'y0')
        if face in ('x0', 'x1'):
            tx = x0 if face == 'x0' else x1; ty = at if at is not None else min(max(cy, y0), y1)
        else:
            ty = y0 if face == 'y0' else y1; tx = at if at is not None else min(max(cx, x0), x1)
        sx = 1 if cx >= tx else -1; sy = 1 if cy >= ty else -1
        if face == 'x1': sx = 1
        if face == 'x0': sx = -1
        if face == 'y1': sy = 1
        if face == 'y0': sy = -1
        # Bekassyl 31.10 (См-1 sample): clearance element edge -> top of the text 400 (4 mm at 1:100); a note BELOW
        # the element therefore drops its shelf by the text band (another 4 mm on paper): 400 + 400 at 1:100
        band = 4 * s.sc if face == 'y0' and dy is None else 0
        ox = tx + sx * (dx if dx is not None else d); oy = ty + sy * ((dy if dy is not None else d) + band)
        s.note(l1, (ox, oy), [(tx, ty)], l2=l2)
    def title(s, text, x, y, cx=None):
        # Bekassyl 31.10 sample: one line, underlined, layer 0, Standard, 3 mm on paper, centred (MText middle-centre)
        h = 3.0 * s.sc; w = len(text) * 0.75 * h + 2 * h
        c = cx if cx is not None else x + w / 2
        add(t='mtext', at=s.P(c, y - h / 2), h=h, w=w, att=5, style='Standard', layer='0', s='{\\L' + text + '}')
    def section(s, tag, word, a, b, d=-1):
        add(t='clone', h=SRC['sec'], base=list(SRC['secbase']), to=s.P(*a), tag=tag)
        add(t='sp_set', h=tag, pts=[[0] + s.P(*a), [1] + s.P(*b)])
        add(t='mcset', h=tag, set={'Word': word, 'Dir': d})
    def bound(s, tag, a, b):
        add(t='clone', h=SRC['bound'], base=list(SRC['boundbase']), to=s.P(*a), tag=tag)
        add(t='sp_set', h=tag, pts=[[0] + s.P(*a), [1] + s.P(*b)])
        if s.sc != 100: add(t='mcscale', h=tag, v=s.sc)

def frame(fx, fy, sc, name, num, fmt='A2'):
    if fmt == 'A3': src, so = '1A0B3', (294417.3, 271897.8)        # A3 1:100 frame of the template
    else: src, so = (SRC['fr100'], SRC['fr100o']) if sc == 100 else (SRC['fr50'], SRC['fr50o'])
    add(t='clone', h=src, base=list(so), to=[fx, fy], tag='frame' + num)
    if fmt == 'A3' and sc != 100: add(t='mcscale', h='frame' + num, v=sc)
    f = sc / 100
    sb = list(SRC['stampf'])
    if fmt == 'A3': sb[0] += 59400 - 42000                           # stamp to the right edge of the narrower sheet
    for hh in SRC['stamp']:
        add(t='clone', h=hh, base=sb, to=[fx, fy], s=f, tag='stamp' + num)
    add(t='clone', h=SRC['sname'], base=sb, to=[fx, fy], s=f, text=name, tag='sname' + num)
    add(t='clone', h=SRC['snum'], base=sb, to=[fx, fy], s=f, text=num, tag='snum' + num)

def spec(fx, fy, tag, title, rows):
    # clone the template scheme spec 11BF4 (18 rows) to the right column of an A3 sheet, above the stamp
    add(t='clone', h='11BF4', base=[49980, 305086], to=[fx + 23000, fy + 28700], tag=tag)
    n = 2 + len(rows)
    if n < 18: add(t='trows', h=tag, mode='del', at=n, n=18 - n)
    cells = [[0, 0, '{\C256;' + title + '}']]
    for i, r in enumerate(rows):
        k = 2 + i
        if len(r) == 1: cells += [[k, 0, ''], [k, 1, ''], [k, 2, r[0]], [k, 10, ''], [k, 11, ''], [k, 12, '']]
        else: cells += [[k, 0, r[0]], [k, 1, r[1]], [k, 2, r[2]], [k, 10, r[3]], [k, 11, ''], [k, 12, r[4] if len(r) > 4 else '']]
    add(t='tset', h=tag, cells=cells)

def notes(fx, fy, top, lines, sc=100):
    txt = '\pxi-3.3333,l3.3333,ql,t3.3333;' + '\P'.join('%d.	%s' % (i + 1, l) for i, l in enumerate(lines))
    # Bekassyl 31.10: notes sit right above the stamp (bottom-left anchored at stamp top + 250)
    f = sc / 100.0
    add(t='mtext', at=[fx + 23000 * f, fy + (500 + 5712 + 250) * f], h=250 * f, w=18500 * f, att=7, style='Isocpeur', layer='О_Формат', s=txt)

def plan_axes(s, pre, ext=(XO, YO, XE, YE), row=1):
    x0, y0, x1, y1 = ext; R0 = 10 * s.sc * (row - 1)
    for k, x in AX.items(): s.axis(pre + 'ax' + k, k, (x, y1 + 700), (x, y0 - R0 - 2500))
    for k, y in AY.items(): s.axis(pre + 'ay' + k, k, (x1 + 700, y), (x0 - R0 - 2500, y))
    xs = [x0] + list(AX.values()) + [x1]; ys = [y0] + list(AY.values()) + [y1]
    # outer dimension = between the extreme axes, not the whole element (Bekassyl 31.10)
    R = 10 * s.sc                                         # №28/30: first row 10 mm from the contour, next +10 mm
    s.chain(xs, y0, y0 - R0 - R); s.dim(AX['1'], AX['3'], (y0, y0 - R0 - 2 * R))
    s.chain(ys, x0, x0 - R0 - R, vert=True); s.dim(AY['А'], AY['Д'], (x0, x0 - R0 - 2 * R), vert=True)

# ================= LIST 2: plans 1:100 =================
F1 = (0.0, 340000.0)
frame(*F1, 100, 'Схема расположения элементов\Pна отм. -3.700', '2.1', 'A3')   # Bekassyl 31.10: plans on A3, one per sheet
A = Sheet(F1[0] + 6600, F1[1] + 6100, 100); A.cx, A.cy = 7375, 8875
A.title('Схема расположения элементов на отм. -3.700', 1200, FYE + 2600, cx=7375)
A.pl(rect((FXO, FYO, FXE, FYE)))                                 # Фм-1 contour with the 500 console
A.thin(rect((FXO - 100, FYO - 100, FXE + 100, FYE + 100)), closed=True)   # подбетонка C8/10 t=100 (Bekassyl 31.10)
for side, rs in walls1.items():
    for r in rs: A.solid(r)
for r in walls2: A.solid(r)
for r in list(pil.values()) + list(cols.values()) + [col3]: A.solid(r)
A.pl(rect(pit), layer='Несущие колонны')
A.hid(rect(pitb), closed=True)
plan_axes(A, 'A', (FXO, FYO, FXE, FYE))
# bindings
A.chain([0, 4625, 5625], 14125, 15400)                        # pit x from axis 1
A.chain([13125, 14125, 17750], 4625, 4100, vert=True)          # pit y from axis Д (no short end dim)
A.chain([8050, 8250, 8450], 3900, 3200)                        # Км-1
A.chain([3900, 4100, 4300], 8450, 9900, vert=True)
A.chain([8000, 8250, 8500], 12250, 11000)                      # Км-3
A.chain([12250, 12500, 12750], 8500, 9900, vert=True)
A.chain([0, 275], 4300, 5000)                                  # Км-2 at wall 1 (inner face from the axis)
A.chain([0, 275], 8450, 9200, vert=True)                       # Км-2 at А/2
A.plevel('Apl1', '-3,700', 3000, 2800)
A.plevel('Apl2', '-3,700', 1200, 16700)
A.plevel('Apl3', '-4,200', 6200, 13400)
# marks
A.note('Фм-1', (4400, 6900), [(4000, 6500)])
A.mark('См-1', walls1['1'][1], at=6000)
A.mark('См-1', walls1['3'][3], at=15000)
A.mark('См-1', walls1['А'][1], at=11500)
A.mark('См-1', walls1['Д'][0], at=11500)
A.mark('См-2', walls2[0], at=1500)
A.mark('См-2', walls2[1], face='x0', at=15500)
A.mark('Км-1', cols['К2Б'], face='y1', at=8250)
A.mark('Км-1', cols['К2В'], face='x0', at=8400)
for k in ('П1Б', 'П1В', 'П3Б', 'П3В', 'П3Г'): A.mark('Км-2', pil[k], at=(pil[k][1] + pil[k][3]) / 2)
A.mark('Км-2', pil['ПА2'], at=8250)
A.mark('Км-3', col3, face='y0', at=8250)
A.mark('Пр-1', pit, face='y1', at=5125, d=500)
A.section('s1a', '1', (FXO - 2600, 11125), (FXE + 600, 11125))
A.section('s2a', '2', (5125, FYO - 2600), (5125, FYE + 1000))
spec(*F1, 'spec2', 'Спецификация элементов на отм. -3.700', [
    ('Плита днища:',), ('Фм-1', 'лист 3.1', 'Плита днища Фм-1', '1'), ('Пр-1', 'лист 3.1', 'Приямок Пр-1', '1'),
    ('Стены:',), ('См-1', 'лист 5.1', 'Стена наружная См-1', '1'), ('См-2', 'лист 5.1', 'Стена внутренняя См-2', '1'),
    ('Колонны:',), ('Км-1', 'лист 4.1', 'Колонна Км-1', '2'), ('Км-2', 'лист 4.1', 'Пилястра Км-2', '6'), ('Км-3', 'лист 4.1', 'Колонна Км-3', '1')])
notes(*F1, 16000, [
    'Общие указания см. лист 1.',
    'Данный лист читать совместно с листами 2.2, 2.3.',
    'За относительную отметку 0.000 принят уровень чистого пола здания котельной (по АР).',
    'Размеры даны в мм, отметки - в м.',
    'Плита днища Фм-1 выполняется с консолью 500 мм за наружную грань стен.',
    'Под плитой днища Фм-1 выполнить бетонную подготовку из бетона класса C8/10 толщиной 100 мм.',
    'Приямок Пр-1 бетонировать совместно с плитой днища Фм-1.',
    'Рабочий шов бетонирования между плитой днища и стенами выполнить с гидрошпонкой.',
    'Наружные поверхности, соприкасающиеся с грунтом, обмазать горячим битумом за 2 раза.'])

F1b = (42000.0, 340000.0)   # sheets edge to edge (Bekassyl 31.10)
frame(*F1b, 100, 'Схема расположения элементов\Pна отм. -0.900', '2.2', 'A3')
B = Sheet(F1b[0] + 6600, F1b[1] + 6100, 100); B.cx, B.cy = 7375, 8875
B.title('Схема расположения элементов на отм. -0.900', 1200, YE + 2600, cx=7375)
B.pl(rect((XO, YO, XE, YE)))
# elements under the slab (walls, partition, columns, pilasters, beams) as ONE outline: every hidden line once,
# beams stop at column faces, nothing runs through columns (Bekassyl 31.10)
from shapely.geometry import box
from shapely.ops import unary_union
under = unary_union([box(*r) for rs in walls1.values() for r in rs] + [box(*r) for r in walls2] +
                    [box(*r) for r in list(pil.values()) + list(cols.values()) + [col3] + beams1 + beams2]).simplify(0.5)
def on_edge(p, q):   # segment on the slab outline (already drawn solid)
    return (abs(p[0] - q[0]) < 1 and min(abs(p[0] - XO), abs(p[0] - XE)) < 1) or (abs(p[1] - q[1]) < 1 and min(abs(p[1] - YO), abs(p[1] - YE)) < 1)
geoms = getattr(under, 'geoms', [under])
for g in geoms:
    for ring in [g.exterior] + list(g.interiors):
        c = [(round(x, 1), round(y, 1)) for x, y in ring.coords]
        runs, cur = [], []
        for p0, p1 in zip(c, c[1:]):
            if on_edge(p0, p1):
                if cur: runs.append(cur); cur = []
            else:
                if not cur: cur = [p0]
                cur.append(p1)
        if cur: runs.append(cur)
        if len(runs) > 1 and runs[0][0] == runs[-1][-1]: runs[0] = runs[-1][:-1] + runs[0]; runs.pop()
        for rr in runs: B.hid(rr, closed=(rr[0] == rr[-1]))
for k, r in necks.items():
    x0, y0, x1, y1 = r; ri = (x0 + tn, y0 + tn, x1 - tn, y1 - tn)
    B.pl(rect(r)); B.pl(rect(ri)); B.hatch([rect(r), rect(ri)])
    B.thin([(ri[0], ri[1]), (ri[2], ri[3])])   # opening: one diagonal lower-left -> upper-right
plan_axes(B, 'B', row=2)                                       # neck chain takes row 1
B.chain([0, 625, 2125, 2625], 17125, YE + 1000)
B.chain([8400, 10375, 11875, 13125, 14625, 15125, 17125], XO, XO - 1000, vert=True)   # short text on the outer side (analog)
B.chain([8075, 8250, 8425], 4275, 6200)
B.chain([3925, 4100, 4275], 11000, 11900, vert=True)
B.chain([3925, 4100, 4275], 5000, 5900, vert=True)
B.note('Пм-1', (5200, 15600), [(4800, 15200)])
B.mark('Бм-1', beams1[0], face='x0', at=2000)
for r in beams1[1:]: B.mark('Бм-1', r, at=11500)
for r in beams2: B.mark('Бм-2', r, at=3300)
B.mark('Гр-1', necks['N1'], face='x1', at=11125)
B.mark('Гр-1', necks['N2'], face='x1', at=13875)
B.mark('Гр-2', necks['N3'], face='x1', at=16100)
B.section('s1b', '1', (-3100, 11125), (XE + 1000, 11125))
B.section('s2b', '2', (5125, -3100), (5125, YE + 1300))
spec(*F1b, 'spec3', 'Спецификация элементов на отм. -0.900', [
    ('Плита покрытия:',), ('Пм-1', 'лист 7.1', 'Плита покрытия Пм-1', '1'),
    ('Балки:',), ('Бм-1', 'лист 6.1', 'Балка Бм-1', '4'), ('Бм-2', 'лист 6.1', 'Балка Бм-2', '2'),
    ('Горловины:',), ('Гр-1', 'лист 8.1', 'Горловина Гр-1', '2'), ('Гр-2', 'лист 8.1', 'Горловина Гр-2', '1')])
notes(*F1b, 20600, [
    'Общие указания см. лист 1.',
    'Данный лист читать совместно с листами 2.1, 2.3.',
    'Размеры даны в мм, отметки - в м.',
    'Плиту покрытия Пм-1 и балки Бм-1, Бм-2 бетонировать совместно.',
    'Высота балок Бм-1 (500 мм) и Бм-2 (600 мм) дана с учётом толщины плиты покрытия.',
    'Горловины Гр-1, Гр-2 бетонировать по выпускам из плиты покрытия; рабочий шов выполнить с гидрошпонкой.',
    'Отверстия в плите покрытия под горловинами: 1200x1200 (Гр-1), 1700x1700 (Гр-2). Верх горловин на отм. +0.100.'])

# ================= LIST 3: sections 1:50 =================
F2 = (84000.0, 340000.0)
frame(*F2, 50, 'Разрезы 1-1, 2-2', '2.3')

def sec_common(s, pre, L, ax, prepx, Rf):
    # left level marks + vertical chains on the left face x=XO-ish (L = left outer face)
    # Bekassyl 31.10: a dimension between every pair of neighbouring level marks
    s.avoid_y = [Z[k] for k in ('neck', 'gr', 'top', 'slb', 'fnd', 'fbot', 'prep')]
    zs = [Z['prep'], Z['fbot'], Z['fnd'], Z['slb'], Z['top'], Z['gr'], Z['neck']]; line = L - 10 * s.sc; th = 2.5 * s.sc
    for i, (a, b) in enumerate(zip(zs, zs[1:])):          # short dim whose text fits between the level lines: centred beside it
        Lg = b - a; w = len(str(int(round(Lg)))) * 0.72 * th; tx = None
        if Lg < 7 * s.sc:
            if Lg >= w + 0.1 * th: tx = ((a + b) / 2, line - 0.9 * th)
            elif i == 0: tx = (a - 1.0 * th, line - 2.8 * th)
            else: tx = (b + 1.0 * th, line - 2.8 * th)
        s.dim(a, b, (L, line), True, tx)
    s.dim(Z['fbot'], Z['top'], (L, L - 20 * s.sc), vert=True)
    for i, (v, z, dn, rt) in enumerate([('+0,100', Z['neck'], 0, 0), ('-0,300', Z['gr'], 0, 1), ('-0,900', Z['top'], 0, 0),
                                        ('-1,200', Z['slb'], 1, 0), ('-3,700', Z['fnd'], 0, 0), ('-4,100', Z['fbot'], 1, 0)]):
        s.level(pre + 'lv%d' % i, v, Rf if rt else L, z, down=dn, right=rt)

# --- 1-1 (cut at y=11125, looking north) ---
S1 = Sheet(F2[0] + 5200, F2[1] + 9400, 50); S1.cx, S1.cy = 7375, -2400; S1.avoid_x = list(AX.values())
S1.title('Разрез 1 - 1', 6000, 1500, cx=7375)
x0n, x1n = 625, 2125
S1.solid((FXO, Z['fbot'], FXE, Z['fnd']))                                   # Фм-1 with console
S1.solid((XO, Z['fnd'], h, Z['slb'])); S1.solid((14625, Z['fnd'], XE, Z['slb']))   # walls
slab = [(XO, Z['slb']), (8075, Z['slb']), (8075, Z['b1']), (8425, Z['b1']), (8425, Z['slb']), (XE, Z['slb']), (XE, Z['top']),
        (x1n - tn, Z['top']), (x1n - tn, Z['slb']), (x0n + tn, Z['slb']), (x0n + tn, Z['top']), (XO, Z['top'])]
S1.pl(slab); S1.hatch([slab])
S1.solid((x0n, Z['top'], x0n + tn, Z['neck'])); S1.solid((x1n - tn, Z['top'], x1n, Z['neck']))
S1.pl(rect((FXO - 100, Z['prep'], FXE + 100, Z['fbot'])), layer='Тонкая')
S1.hatch([rect((FXO - 100, Z['prep'], FXE + 100, Z['fbot']))], pat='AR-CONC', sc=3, layer='Бетон штриховка')
S1.thin([(8425, Z['b1']), (14475, Z['b1'])])                   # beam on Г (2-3) beyond
S1.thin([(8000, Z['fnd']), (8000, Z['b1'])]); S1.thin([(8500, Z['fnd']), (8500, Z['b1'])])   # Км-3 beyond
S1.thin([(h, Z['fnd']), (h, Z['slb'])])
S1.bound('b1a', (FXO - 200, Z['gr']), (x0n, Z['gr'])); S1.bound('b1b', (x1n, Z['gr']), (XE + 1500, Z['gr']))
for k, x in AX.items(): S1.axis('S1x' + k, k, (x, Z['neck'] + 300), (x, Z['prep'] - 1400))
S1.chain([FXO, 0, 8250, 14750, FXE], Z['prep'], Z['prep'] - 500)
S1.dim(AX['1'], AX['3'], (Z['prep'], Z['prep'] - 1000))
S1.chain([0, x0n, x0n + tn, x1n - tn, x1n], Z['neck'], Z['neck'] + 600)
S1.chain([Z['b1'], Z['slb'], Z['top']], 8425, 9100, vert=True)
sec_common(S1, 'S1', FXO, AX, 0, XE)
S1.mark('Фм-1', (FXO, Z['fbot'], FXE, Z['fnd']), face='y1', at=2600)
S1.mark('Бетонная подготовка', (FXO - 100, Z['prep'], FXE + 100, Z['fbot']), face='x1', at=Z['prep'] + 50, l2='C8/10 t=100')
S1.mark('См-1', (XO, Z['fnd'], h, Z['slb']), face='x1', at=-2600)
S1.mark('Пм-1', (XO, Z['slb'], XE, Z['top']), face='y0', at=3600)
S1.mark('Бм-1', (8075, Z['b1'], 8425, Z['slb']), face='y0', at=8250)
S1.mark('Гр-1', (x1n - tn, Z['top'], x1n, Z['neck']), face='x1', at=-400)

# --- 2-2 (cut at x=5125, looking west) ---
S2 = Sheet(F2[0] + 5200, F2[1] + 18200, 50); S2.cx, S2.cy = 8875, -2400; S2.avoid_x = list(AY.values())
S2.title('Разрез 2 - 2', 7500, 1500, cx=8875)
fnd = [(FYO, Z['fbot']), (pitb[1], Z['fbot']), (pitb[1], Z['pitbot']), (pitb[3], Z['pitbot']), (pitb[3], Z['fbot']), (FYE, Z['fbot']),
       (FYE, Z['fnd']), (pit[3], Z['fnd']), (pit[3], Z['pitb']), (pit[1], Z['pitb']), (pit[1], Z['fnd']), (FYO, Z['fnd'])]
S2.pl(fnd); S2.hatch([fnd])
S2.solid((YO, Z['fnd'], h, Z['slb'])); S2.solid((17625, Z['fnd'], YE, Z['slb']))
S2.solid((12375, Z['fnd'], 12625, Z['slb']))                  # См-2 cut
slab2 = [(YO, Z['slb'])]
for y0, y1 in ((3925, 4275), (8225, 8575)): slab2 += [(y0, Z['slb']), (y0, Z['b2']), (y1, Z['b2']), (y1, Z['slb'])]
slab2 += [(YE, Z['slb']), (YE, Z['top']), (YO, Z['top'])]
S2.pl(slab2); S2.hatch([slab2])
prep2 = [(FYO - 100, Z['prep']), (pitb[1] - 100, Z['prep']), (pitb[1] - 100, Z['pitprep']), (pitb[3] + 100, Z['pitprep']),
         (pitb[3] + 100, Z['prep']), (FYE + 100, Z['prep']), (FYE + 100, Z['fbot']), (pitb[3], Z['fbot']), (pitb[3], Z['pitbot']),
         (pitb[1], Z['pitbot']), (pitb[1], Z['fbot']), (FYO - 100, Z['fbot'])]
S2.pl(prep2, layer='Тонкая'); S2.hatch([prep2], pat='AR-CONC', sc=3, layer='Бетон штриховка')
for k, r in necks.items():   # necks beyond the cut, visible above ground
    S2.thin([(r[1], Z['gr']), (r[1], Z['neck']), (r[3], Z['neck']), (r[3], Z['gr'])])
for r in (pil['П1Б'], pil['П1В']):
    S2.thin([(r[1], Z['fnd']), (r[1], Z['slb'])]); S2.thin([(r[3], Z['fnd']), (r[3], Z['slb'])])
S2.bound('b2a', (FYO - 200, Z['gr']), (YE + 1500, Z['gr']))
for k, y in AY.items(): S2.axis('S2y' + k, k, (y, Z['neck'] + 300), (y, Z['pitprep'] - 1200))
S2.chain([FYO] + list(AY.values()) + [FYE], Z['pitprep'], Z['pitprep'] - 500)
S2.dim(AY['А'], AY['Д'], (Z['pitprep'], Z['pitprep'] - 1000))
S2.chain([12500, pit[1], pit[3]], Z['fnd'], Z['fnd'] + 600)
S2.chain([Z['pitbot'], Z['pitb'], Z['fnd']], pitb[3], pitb[3] + 700, vert=True)
S2.level('S2lp1', '-4,200', pit[3], Z['pitb'], down=True, right=True, ax=pitb[3] + 1800)     # pit bottom
S2.level('S2lp2', '-4,600', pitb[3], Z['pitbot'], down=True, right=True, ax=pitb[3] + 1800)  # pit base
S2.chain([Z['b2'], Z['slb'], Z['top']], 8575, 9300, vert=True)
sec_common(S2, 'S2', FYO, AY, 0, YE)
S2.mark('Фм-1', (FYO, Z['fbot'], FYE, Z['fnd']), face='y1', at=2000)
S2.mark('Бетонная подготовка', (FYO - 100, Z['prep'], FYE + 100, Z['fbot']), face='x1', at=Z['prep'] + 50, l2='C8/10 t=100')
S2.note('Пр-1', (pit[3] + 400, -3550), [(pit[3], -3950)])
S2.mark('См-1', (YO, Z['fnd'], h, Z['slb']), face='x1', at=-2600)
S2.mark('См-2', (12375, Z['fnd'], 12625, Z['slb']), face='x0', at=-2600)
S2.mark('Пм-1', (YO, Z['slb'], YE, Z['top']), face='y0', at=6000)
S2.mark('Бм-2', (3925, Z['b2'], 4275, Z['slb']), face='y0', at=4100)
S2.note('Гр-1', (12575, -700), [(11875, -100)])

ONLY = sys.argv[2] if len(sys.argv) > 2 else None
if ONLY == 'dimfix':
    ops = [{'t': 'dimfix', 'items': [{'p1': o['p1'], 'p2': o['p2'], 'tx': o['tx']} for o in ops if o.get('t') == 'dim' and 'tx' in o]}, {'t': 'regen'}]
SAVE = 'nosave' not in sys.argv
if ONLY == 'all': ops = [{'t': 'eraseregion', 'win': [-1000, 339500, 121000, 383000], 'mode': 'intersect'}, {'t': 'maprst'}] + ops + [{'t': 'eraseregion', 'win': [195000, 353000, 216000, 362000], 'mode': 'intersect'}, {'t': 'regen'}] + ([{'t': 'save'}] if SAVE else [])
if ONLY == 'levels':
    ops = [{'t': 'erase', 'h': [o['tag'] for o in ops if o.get('t') == 'clone' and o.get('h') == SRC['lev']]}] + [o for o in ops if 'lv' in str(o.get('tag', '')) or ('lv' in str(o.get('h', '')))]
json.dump(ops, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(ops), 'ops')
