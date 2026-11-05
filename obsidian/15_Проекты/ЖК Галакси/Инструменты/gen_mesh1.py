# Км-1 sheet 4.1 — mesh С1 (from the analog's С2 for a 500 column) and its node detail (beam 550, 5 meshes).
import json, sys, gx
X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
R = json.load(open('w/k41_list3.json'))
ops = []
def add(**k): ops.append(k); return k
def inwin(r, x0, y0, x1, y1): return r['x0'] > x0 and r['x1'] < x1 and r['y0'] > y0 and r['y1'] < y1

# 1) erase the analog's 600-column mesh С1 (upper group), splice details А / а-а, node С1 (600), knot В
er = [r['h'] for r in R if inwin(r, 13000, 18000, 31800, 25000)]
er += [r['h'] for r in R if inwin(r, 13000, 1000, 22300, 9000)]
er += [r['h'] for r in R if inwin(r, 1500, 500, 13600, 8600)]
er += ['10BC93', '10BC94']
add(t='erase', h=er)

# 2) mesh element 1 (left view): 5 rods + cross rod, L = 460, rods at 30..430, cross rod 30 below the top
L = 1840.0; x0, y0 = 17096.0, 12896.0
rx = [x0 + 4 * v for v in (30, 130, 230, 330, 430)]
for i, x in enumerate(rx): add(t='lineset', h='10B628', s=W(x, y0), e=W(x, y0 + L), tag='K41m_L%d' % i)
yc = y0 + L - 120
add(t='lineset', h='10B629', s=W(x0, yc), e=W(x0 + L, yc), tag='K41m_LC')
add(t='erase', h=['10B628', '10B63A', '10B63B', '10B64D', '10B629'])
add(t='dimpts', h='10B5D9', p1=W(rx[0], y0), p2=W(x0, y0 + L))
add(t='dimpts', h='10B63C', p1=W(rx[0], y0), p2=W(rx[-1], y0)); add(t='dimtext', h='10B63C', s='100х4')
add(t='dimpts', h='10B62A', p1=W(rx[-1], y0), p2=W(x0 + L, yc))
add(t='dimpts', h='10B5EA', p1=W(x0 + L, yc), p2=W(x0, yc))
add(t='dimpts', h='10B5F9', p1=W(x0 + L, yc), p2=W(rx[-1], y0 + L))
add(t='dimpts', h='10B60A', p1=W(x0 + L, yc), p2=W(rx[-1], y0))
add(t='dimpts', h='10B619', p1=W(rx[-1], y0 + L), p2=W(rx[-1], y0))
add(t='spmove', h='10C8E9', items=[[1, X0 + rx[0], Y0 + 14074], [2, X0 + rx[1], Y0 + 14074], [3, X0 + rx[2], Y0 + 14074], [4, X0 + rx[4], Y0 + 14074]])
add(t='mcset', h='10C8E9', set={'FirstLine': '3', 'SecondLine': 'ш.100'})
add(t='spmove', h='10C8EA', items=[[1, X0 + 17847, Y0 + yc]]); add(t='mcset', h='10C8EA', set={'FirstLine': '3', 'SecondLine': ''})

# 3) mesh element 2 (right view): 5 rods horizontal, cross rod vertical 30 from the right end
xa, yb = 24752.0, 12733.0
ry = [yb + 4 * v for v in (30, 130, 230, 330, 430)]
for i, y in enumerate(ry): add(t='lineset', h='10B78C', s=W(xa, y), e=W(xa + L, y), tag='K41m_R%d' % i)
xr = xa + L - 120
add(t='lineset', h='10B77B', s=W(xr, yb), e=W(xr, yb + L), tag='K41m_RC')
add(t='erase', h=['10B77A', '10B78C', '10B78D', '10B79E', '10B77B'])
add(t='dimpts', h='10B72B', p1=W(xa, ry[0]), p2=W(xr, yb))
add(t='dimpts', h='10B78E', p1=W(xa, ry[0]), p2=W(xa, ry[-1])); add(t='dimtext', h='10B78E', s='100х4')
add(t='dimpts', h='10B77C', p1=W(xa, ry[-1]), p2=W(xr, yb + L))
add(t='dimpts', h='10B73C', p1=W(xr, yb), p2=W(xr, yb + L))
add(t='dimpts', h='10B74B', p1=W(xr, yb + L), p2=W(xa + L, ry[-1]))
add(t='dimpts', h='10B75C', p1=W(xr, yb + L), p2=W(xa, ry[-1]))
add(t='dimpts', h='10B76B', p1=W(xa + L, ry[-1]), p2=W(xa, ry[-1]))
add(t='spmove', h='10C8EF', items=[[1, X0 + 25930, Y0 + ry[0]], [2, X0 + 25930, Y0 + ry[1]], [3, X0 + 25930, Y0 + ry[2]], [4, X0 + 25930, Y0 + ry[4]]])
add(t='mcset', h='10C8EF', set={'FirstLine': '3', 'SecondLine': 'ш.100'})
add(t='spmove', h='10C8F0', items=[[1, X0 + xr, Y0 + 13862]]); add(t='mcset', h='10C8F0', set={'FirstLine': '3', 'SecondLine': ''})
add(t='spmove', h='10B79D', items=[[1, X0 + xr, Y0 + ry[-1]]])
add(t='settext', h='10B64B', s='{\\LСетка С1}')
# move the mesh group up into the freed place
add(t='movewin', win=[X0 + 13000, Y0 + 11000, X0 + 31800, Y0 + 17900], d=[0, 7093])

# 4) node: beam 550 (scale 3.6525), meshes at 100..500 below the slab top, label С1, knot 'А'
k = 1461.0 / 400.0; top = 6338.0; bot = top - 550 * k
add(t='stretchwin', win=[X0 + 22500, Y0 + 4800, X0 + 30300, Y0 + 4950], d=[0, bot - 4877])
m1, m5 = top - 100 * k, top - 500 * k
add(t='movegrp', h=['10BCB2', '10BD2C', '10BD2B', '10BCB6', '10BCB5', '10BCB4', '10BCB3', '10BCC4'], d=[0, m1 - 6022])
add(t='movegrp', h=['10BCB7', '10BD2E', '10BD2D', '10BCBB', '10BCBA', '10BCB9', '10BCB8', '10BCC5'], d=[0, m5 - 5190])
add(t='dimpts', h='10BD19', p1=W(25805, m1), p2=W(25416, top)); add(t='dimtext', h='10BD19', s='')
add(t='dimpts', h='10BCE8', p1=W(25805, m1), p2=W(25768, m5)); add(t='dimtext', h='10BCE8', s='100х4')
add(t='dimpts', h='10BD07', p1=W(25768, m5), p2=W(25416, bot)); add(t='dimtext', h='10BD07', s='')
add(t='spmove', h='10BCC3', items=[[1, X0 + 26533, Y0 + m1]])
add(t='settext', h='10BCC6', s='С1')
add(t='settext', h='10BCC1', s='%%UУзел расположения сетки С1')
add(t='settext', h='10BD30', s='А')
add(t='save')
json.dump(ops, open('ops/k41m.json', 'w'), ensure_ascii=False)
print(len(ops), 'erase', len(er))
if '--run' in sys.argv: print(gx.run(ops, 'k41m')[-1500:])
