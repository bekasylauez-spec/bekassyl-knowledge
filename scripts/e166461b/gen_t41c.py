# Км-1 sheet 4.1 (template sheet) — node «Узел расположения сетки С1» (beam 550) and mesh С1 (460, rods 35 | 100x3 | 125).
import json, sys, gx
X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
ops = []
def add(**k): ops.append(k); return k
NOTE = dict(scale=50, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')
POS = '4'                                   # mesh rod position in the specification

# ---- node (schematic, texts per our beam 550 / column 500) ----
for h, s in (('111534', '550'), ('111583', '50'), ('111563', '100х4'), ('111572', '100'), ('111514', '250'), ('111523', '250'), ('111546', '500')):
    add(t='dimtext', h=h, s=s)

# ---- mesh element 1 (left view): rods vertical ----
L = 920.0; x0, y0 = 13769.0, 11403.0
rx = [x0 + 2 * v for v in (35, 135, 235, 335)]
for i, x in enumerate(rx): add(t='lineset', h='111466', s=W(x, y0), e=W(x, y0 + L), tag='T41m_L%d' % i)
yc = y0 + L - 70
add(t='lineset', h='111467', s=W(x0, yc), e=W(x0 + L, yc), tag='T41m_LC')
add(t='erase', h=['111466', '111478', '111479', '111467'])
add(t='dimpts', h='111417', p1=W(rx[0], y0), p2=W(x0, y0 + L))
add(t='dimpts', h='11147A', p1=W(rx[0], y0), p2=W(rx[-1], y0)); add(t='dimtext', h='11147A', s='100х3')
add(t='dimpts', h='111468', p1=W(rx[-1], y0), p2=W(x0 + L, yc))
add(t='dimpts', h='111428', p1=W(x0 + L, yc), p2=W(x0, yc))
add(t='dimpts', h='111437', p1=W(x0 + L, yc), p2=W(rx[-1], y0 + L))
add(t='dimpts', h='111448', p1=W(x0 + L, yc), p2=W(rx[-1], y0))
add(t='dimpts', h='111457', p1=W(rx[-1], y0 + L), p2=W(rx[-1], y0))
add(t='erase', h=['11190B'])
add(t='note', l1=POS, l2='ш.100', origin=W(13346, 11792), targets=[W(x, 11792) for x in rx], **NOTE)
add(t='spmove', h='11190C', items=[[1, X0 + 14144, Y0 + yc]]); add(t='mcset', h='11190C', set={'FirstLine': POS})

# ---- mesh element 2 (right view): rods horizontal, cross rod vertical ----
xa, yb = 17797.0, 11121.0
ry = [yb + 2 * v for v in (35, 135, 235, 335)]
for i, y in enumerate(ry): add(t='lineset', h='1114DA', s=W(xa, y), e=W(xa + L, y), tag='T41m_R%d' % i)
xr = xa + L - 70
add(t='lineset', h='1114DB', s=W(xr, yb), e=W(xr, yb + L), tag='T41m_RC')
add(t='erase', h=['1114DA', '1114EC', '1114ED', '1114DB'])
add(t='dimpts', h='11148B', p1=W(xa, ry[0]), p2=W(xr, yb))
add(t='dimpts', h='1114EE', p1=W(xa, ry[0]), p2=W(xa, ry[-1])); add(t='dimtext', h='1114EE', s='100х3')
add(t='dimpts', h='1114DC', p1=W(xa, ry[-1]), p2=W(xr, yb + L))
add(t='dimpts', h='11149C', p1=W(xr, yb), p2=W(xr, yb + L))
add(t='dimpts', h='1114AB', p1=W(xr, yb + L), p2=W(xa + L, ry[-1]))
add(t='dimpts', h='1114BC', p1=W(xr, yb + L), p2=W(xa, ry[-1]))
add(t='dimpts', h='1114CB', p1=W(xa + L, ry[-1]), p2=W(xa, ry[-1]))
add(t='erase', h=['11190D'])
add(t='note', l1=POS, l2='ш.100', origin=W(18186, 10698), targets=[W(18186, y) for y in ry], **NOTE)
add(t='spmove', h='11190E', items=[[1, X0 + xr, Y0 + 11686]]); add(t='mcset', h='11190E', set={'FirstLine': POS})
add(t='spmove', h='1114FD', items=[[1, X0 + xr, Y0 + ry[0]]])
add(t='save')
json.dump(ops, open('ops/t41c.json', 'w'), ensure_ascii=False)
print(len(ops))
if '--run' in sys.argv: print(gx.run(ops, 't41c')[-800:])
