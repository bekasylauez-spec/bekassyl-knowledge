# Section bars to 45 | 120х3=360 | 45 (equal step, chain written as «120х3=360»), on every placed section instance.
import gx, sec1
xL, xR = sec1.xL, sec1.xR
YB0, YBOT, YTOP, yb = sec1.YBOT, sec1.YBOT, sec1.YTOP, sec1.yb
BX = [xL + 45, xL + 165, xL + 285, xL + 405]
BOT = ['2CAF83', '2CB036', '2CB03D', '2CAFDE']; TOP = ['2CAFF5', '2CB044', '2CB04B', '2CAFFC']; HOOP = ['2CB003', '2CB080']
D_L, D_1, D_2, D_3, D_R = '2CAF9A', '2CB052', '2CB070', '2CB061', '2CAFE5'
# instance prefix, centre on the sheet, доп bars of the instance: [(pos, top, n)]
INST = [('R61S_', (185300, 462700), []), ('A2S_', (216800, 462700), []), ('A3S_', (248300, 462700), []),
        ('A4S0_', (274679, 463100), []), ('A4S1_', (279679, 463100), [('2', True, 1)]),
        ('A5S0_', (306179, 463100), []), ('A5S1_', (311179, 463100), [('2', True, 3)]), ('A5S2_', (316179, 463100), [('3', False, 1)])]


def ops_for(pre, T, dop):
    f = lambda x, y: [T[0] + (x - 173965) * 2.5, T[1] + (y - 431659) * 2.5]
    P = lambda h: pre + h
    ops = []
    for h, x in zip(BOT, BX): ops.append(dict(t='insat', h=P(h), at=f(x, YBOT)))
    for h, x in zip(TOP, BX): ops.append(dict(t='insat', h=P(h), at=f(x, YTOP)))
    for h, x in zip(HOOP, BX[:2]):
        ops.append(dict(t='insat', h=P(h), at=f(x, YBOT + 11)))
        ops.append(dict(t='dyn', h=P(h), prop='Расстояние1', value=(BX[2] - BX[0]) * 2.5))
    yd = 431078
    ops.append(dict(t='dimpts', h=P(D_L), p1=f(BX[0], yb) + [0], p2=f(xL, yb) + [0], dl=f(xL, yd) + [0]))
    ops.append(dict(t='dimtx', h=P(D_L), at=f(xL - 75, yd + 40) + [0]))
    ops.append(dict(t='dimpts', h=P(D_1), p1=f(BX[3], yb) + [0], p2=f(BX[0], yb) + [0], dl=f(BX[0], yd) + [0]))
    ops.append(dict(t='dimtext', h=P(D_1), s='120х3=360'))
    ops.append(dict(t='dimtx', h=P(D_1), at=f(173965, yd + 40) + [0]))
    ops.append(dict(t='erase', h=[P(D_2), P(D_3)]))
    ops.append(dict(t='dimpts', h=P(D_R), p1=f(xR, yb) + [0], p2=f(BX[3], yb) + [0], dl=f(BX[3], yd) + [0]))
    ops.append(dict(t='dimtx', h=P(D_R), at=f(xR + 75, yd + 40) + [0]))
    ops.append(dict(t='combsegs', h=P('2CB019'), segs=[[f(x, YTOP - 1), f(x + 88, 432097)] for x in BX], start=f(BX[3] + 88, 432097), end=f(BX[0] + 88, 432097)))
    yk = YBOT - 151
    ops.append(dict(t='combsegs', h=P('2CB01A'), segs=[[f(x, YBOT - 2), f(x + 70, yk)] for x in BX], start=f(BX[3] + 110, yk), end=f(BX[0] + 70, yk)))
    ym = (YBOT + YTOP) / 2
    ops.append(dict(t='combsegs', h=P('2CB07F'), segs=[[f(BX[2] + 15, ym), f(xR + 175, ym)], [f(BX[3] + 15, ym), f(xR + 175, ym)]]))
    for pos, top, n in dop:
        bx = [173965] if n == 1 else [(BX[i] + BX[i + 1]) / 2 for i in range(3)]
        y = YTOP if top else YBOT
        for i, xx in enumerate(bx): ops.append(dict(t='insat', h='%sD%s_%d' % (pre, pos, i), at=f(xx, y)))
        if top:
            ys = 432300; segs = [[f(xx, y - 1), f(xx + (ys - y) * 88 / 213.0, ys)] for xx in bx]
        else:   # below the bar chain: shelf under the 45|360|45 dims, text right of the section
            ys = 430930; segs = [[f(xx, y - 2), f(xx + (y - ys) * 70 / 151.0, ys)] for xx in bx]
        xe = [q[1][0] for q in segs]
        ops.append(dict(t='combsegs', h='%sDC%s' % (pre, pos), segs=segs, start=[max(xe) + (0 if top else 300), segs[0][1][1]], end=[min(xe), segs[0][1][1]]))
    return ops


if __name__ == '__main__':
    ops = []
    for pre, T, dop in INST: ops += ops_for(pre, T, dop)
    ops.append(dict(t='save'))
    out = gx.run(ops, 'sfx')
    print(len(ops), [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:10])
