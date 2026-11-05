import gx, sec1
from rigx import YB, YBB
ops = []
add = lambda **k: ops.append(k)
# 6.5: texts off the axis В/1 line
add(t='dimtx', h='2D24D3', at=[307150, 466886, 0]); add(t='dimtx', h='2D2581', at=[307150, 467400, 0])
# 6.5 section 3-3: pos 3 comb just under the main comb, text clear of the chain
T = (316179, 463100); f = lambda x, y: [T[0] + (x - 173965) * 2.5, T[1] + (y - 431659) * 2.5]
ys = 431215; y = sec1.YBOT
e = f(173965 + (y - ys) * 70 / 151.0, ys)
add(t='combsegs', h='A5S2_DC3', segs=[[f(173965, y - 2), e]], start=[e[0] + 400 * 2.5 / 2.5 * 2.5, e[1]], end=e)
# 6.4: duplicate node title left from the first build
add(t='erase', h=['2CF82D'])
NOTE = ('\pxi-3.3333,l3.3333,t3.3333;1.\tОбщие указания см. л. - 1.1\P2.\tДанный лист читать совместно с л. КЖ-2.1 ... 2.7\P3.\tСтержни, '
        'указанные в "Ведомости деталей", должны гнуться механическим способом в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня')
for P in ('A1:', 'A2:', 'A3:', 'A4:', 'A5:'):
    add(t='move', h=[P + '4064A4', P + '406499'], d=[-250, 0])                        # «L=1740» inside the frame
    add(t='settext', h=P + '40443D', s=NOTE, w=8900)
    add(t='settext', h=P + '406493', s='380'); add(t='settext', h=P + '40648A', s='280'); add(t='settext', h=P + '406499', s='1740')
# 6.1–6.3: bottom splices +1100/+1600 from the axes (plate dims clear of the hoop extension lines), combs follow
AX = [0, 6800, 13250, 20050]
for P, T1 in (('A1:', 175307.0), ('A2:', 175307.0 + 31500), ('A3:', 175307.0 + 63000)):
    X = lambda x: T1 + x
    for (h1, h2, d1, d2, comb), ax in zip([('403948', '403947', '403992', '40394A', '403949'), ('4039A0', '40399F', '4039A5', '4039A2', '4039A1')], AX[1:3]):
        c1, c2 = ax + 1100, ax + 1600
        for h, c in ((h1, c1), (h2, c2)):
            add(t='plset', h=P + h, p=[[X(c) - 125, YBB - 15], [X(c) - 125, YBB + 15], [X(c) + 125, YBB + 15], [X(c) + 125, YBB - 15]], closed=True)
        add(t='dimpts', h=P + d1, p1=[X(c1), YB, 0], p2=[X(ax), YB, 0], dl=[X(ax), 467665, 0])
        add(t='dimpts', h=P + d2, p1=[X(c2), YBB, 0], p2=[X(c1), YBB, 0], dl=[X(c1), 467665, 0])
        add(t='move', h=[P + comb], d=[600, 0])
add(t='save')
if __name__ == '__main__':
    out = gx.run(ops, 'fx2'); print(len(ops), [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:10])
