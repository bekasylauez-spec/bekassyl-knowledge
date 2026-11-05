# Км-1 sheet 4.1 (template sheet 1:50) — sections 1-1 / 2-2 at 1:25 (x2), from the template's own objects.
import json, math, sys, gx
X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
ops = []
def add(**k): ops.append(k); return k
K = 2.0; b = 500.0; e = 56.0                       # bars Ø32 at 56 from the faces
HS = (420.0 + 0) / 320.0                            # hoop size ratio vs the template (400 column: 320 envelope)
NOTE0 = dict(scale=50, ts=2.5, style='ГОСТ 2.304', layer='Размеры')

def bars(ox, oy):
    v = [e, b / 2, b - e]
    return [(ox + K * x, oy + K * y) for x in v for y in v if not (x == b / 2 and y == b / 2)]

def common(ox, oy, oldcol, oldbars, barT, dims, axes, tag):
    # outline
    add(t='spmove', h=oldcol, items=[[0, X0 + ox + K * b, Y0 + oy], [1, X0 + ox + K * b, Y0 + oy + K * b], [2, X0 + ox, Y0 + oy + K * b], [3, X0 + ox, Y0 + oy]])
    # bars: clone the template bar symbol (Ø32 = 64 at 1:25) to every bar centre, drop the old ones
    bx, by, bc = barT
    for i, (x, y) in enumerate(bars(ox, oy)):
        add(t='clone', h=bc, base=W(bx, by), to=W(x, y), tag=tag + 'B%d' % i)
    add(t='erase', h=oldbars)
    # dims: bottom row 40 | 210 | 210 | 40, second row 250 | 250; left the same
    (b40l, b210l, b210r, b40r, b250l, b250r, yb1, yb2), (l40b, l210b, l210t, l40t, l250b, l250t, xl1, xl2) = dims
    xs = [0, 40, 250, 460, 500]
    for h, i in ((b40l, 0), (b210l, 1), (b210r, 2), (b40r, 3)):
        add(t='dimpts', h=h, p1=W(ox + K * xs[i], oy), p2=W(ox + K * xs[i + 1], oy), dl=W(ox + K * (xs[i] + xs[i + 1]) / 2, yb1))
    add(t='dimpts', h=b250l, p1=W(ox, oy), p2=W(ox + K * 250, oy), dl=W(ox + K * 125, yb2))
    add(t='dimpts', h=b250r, p1=W(ox + K * 250, oy), p2=W(ox + K * b, oy), dl=W(ox + K * 375, yb2))
    for h, i in ((l40b, 0), (l210b, 1), (l210t, 2), (l40t, 3)):
        add(t='dimpts', h=h, p1=W(ox, oy + K * xs[i]), p2=W(ox, oy + K * xs[i + 1]), dl=W(xl1, oy + K * (xs[i] + xs[i + 1]) / 2))
    add(t='dimpts', h=l250b, p1=W(ox, oy), p2=W(ox, oy + K * 250), dl=W(xl2, oy + K * 125))
    add(t='dimpts', h=l250t, p1=W(ox, oy + K * 250), p2=W(ox, oy + K * b), dl=W(xl2, oy + K * 375))
    # short 40 texts: outside, along their line, clear of the end ticks
    add(t='dimtx', h=b40l, at=W(ox - 300, yb1)); add(t='dimtx', h=b40r, at=W(ox + K * b + 300, yb1))
    add(t='dimtx', h=l40b, at=W(xl1, oy - 300)); add(t='dimtx', h=l40t, at=W(xl1, oy + K * b + 300))
    # axes through the centre
    av, ah = axes; cx, cy = ox + K * b / 2, oy + K * b / 2
    add(t='spmove', h=av, items=[[0, X0 + cx, Y0 + oy + K * b + 720], [1, X0 + cx, Y0 + oy - 1060]])
    add(t='spmove', h=ah, items=[[0, X0 + ox + K * b + 720, Y0 + cy], [1, X0 + ox - 1090, Y0 + cy]])

# ---------- 1-1 ----------
ox, oy = 9314.0, 17588.0
common(ox, oy, '11130A', ['11130B', '111329', '111345', '111337', '11133E', '111322', '111330', '11134C'], (9422, 18267, '11130B'),
       (('111353', '1113E3', '1113F0', '111361', '11138B', '111398', 17070, 16459), ('11137D', '1113FD', '11140A', '11136F', '1113B2', '1113A5', 8796, 8403)),
       ('111306', '111309'), 'T41s1_')
# hoops: template dynamic blocks moved to the corner / bottom-mid bar and enlarged in proportion
add(t='movegrp', h=['1113BF'], d=[(ox + K * e) - 9421, (oy + K * e) - 17699])
add(t='movegrp', h=['1113D0'], d=[(ox + K * b / 2) - 9713, (oy + K * e) - 17698])
add(t='dyn', h='1113BF', prop='Расстояние1', value=411.928082325122 * HS); add(t='dyn', h='1113BF', prop='Расстояние2', value=577.99372308224 * HS)
add(t='dyn', h='1113D0', prop='Расстояние2', value=408.701438225833 * HS)
# callouts: leader straight to the bar centres, no ticks
B = bars(ox, oy)
top = [p for p in B if abs(p[1] - (oy + K * (b - e))) < 1]; bot = [p for p in B if abs(p[1] - (oy + K * e)) < 1]
add(t='erase', h=['1113E1', '1113E2'])
add(t='note', l1='1 ... 3', l2='(%%C32)', origin=W(ox + K * b + 520, oy + K * b + 230), targets=[W(*p) for p in sorted(top, reverse=True)], arrow='none', **NOTE0)
add(t='note', l1='1 ... 3', l2='(%%C32)', origin=W(ox + K * b + 520, oy - 230), targets=[W(*p) for p in sorted(bot, reverse=True)], arrow='none', **NOTE0)
add(t='spmove', h='11190A', items=[[0, X0 + ox + K * b + 520, Y0 + oy + K * b / 2 + 120], [1, X0 + ox + K * (b - 36), Y0 + oy + K * 360], [2, X0 + ox + K * 357, Y0 + oy + K * 357]])

# ---------- 2-2 ----------
ox, oy = 13824.0, 17641.0
common(ox, oy, '1117EA', ['11188F', '11189D', '1118B9', '1118AB', '1118B2', '111896', '1118A4', '1118C0'], (13932, 18320, '11188F'),
       (('1117EB', '111857', '111864', '1117F9', '111823', '111830', 17123, 16512), ('111815', '111871', '11187E', '111807', '11184A', '11183D', 13306, 12882)),
       ('1117E6', '1117E9'), 'T41s2_')
P = lambda x, y: W(ox + K * x, oy + K * y)
add(t='erase', h=['11188B', '11188C', '11188E', '11188D'])
for i, (a, c) in enumerate((((e, e), (b - e, b - e)), ((e, b - e), (b - e, e)), ((b / 2, b - e), (b - e, b / 2)), ((e, b / 2), (b / 2, e)))):
    add(t='lineset', h='T41s2_B0' if False else '1113C0' if False else 'T41e_COL', s=P(*a), e=P(*c)) if False else None
    add(t='pl', p=[P(*a), P(*c)], layer='диам16', lw=40, tag='T41s2_K%d' % i)
add(t='spmove', h='11190F', items=[[0, X0 + ox + K * b + 300, Y0 + oy - 120], [1, X0 + ox + K * 360, Y0 + oy + K * 360], [2, X0 + ox + K * 400, Y0 + oy + K * 100],
                                   [3, X0 + ox + K * 400, Y0 + oy + K * 100], [4, X0 + ox + K * 400, Y0 + oy + K * 100]])
add(t='save')
json.dump(ops, open('ops/t41b.json', 'w'), ensure_ascii=False)
print(len(ops))
if '--run' in sys.argv: print(gx.run(ops, 't41b')[-1500:])
