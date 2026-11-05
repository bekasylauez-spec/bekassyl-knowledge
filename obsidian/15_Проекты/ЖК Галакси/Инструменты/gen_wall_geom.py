# Wall См-1 (axis А/1): adapt the exploded analog elevation (Блок F2 «См-1 по оси А») to our pieces.
# analog piece boundaries -> ours (sheet x, axis 1 at 9810): P1 125..1225, P2 925 around axis 2 (800+250+800), no 2/1 piece, P3 same, P4 1225..125
import json, sys, gx, colsheet as C
MAPX = {9935: 9935, 10810: 11035, 15710: 15685, 16485: 16485, 16735: 16735, 17510: 17535, 22160: 22135, 22935: 22935, 23185: 23185, 23960: 23985, 28860: 28635, 29735: 29735}
DEAD = [(19185, 20185), (20185, 22160)]          # piece 2/1 and the opening after it
def run(SX, SY, tag):
    R = C.listwin(SX, SY, 59400, 42000)
    ops = []; er = []
    for r in R:
        if r['t'] not in ('LWPOLYLINE', 'HATCH'): continue
        x0, x1 = round(r['x0']), round(r['x1'])
        if r['y0'] < 7000: continue
        if any(abs(x0 - a) < 2 and abs(x1 - b) < 2 for a, b in DEAD): er.append(r['h']); continue
        if r['t'] != 'LWPOLYLINE' or x0 < 9930 or x1 > 29740: continue
        pts = r['sp']
        if x0 == 17510 and x1 == 19185 and len(pts) == 3:       # opening B now runs to piece P3
            a, b = pts[0], pts[2]; nx0, nx1 = 17535, 22135
            mid = (nx0 + (pts[1][0] - a[0]) / (b[0] - a[0]) * (nx1 - nx0), pts[1][1])
            ops.append(dict(t='spmove', h=r['h'], items=[[0, SX + nx0, SY + a[1]], [1, SX + mid[0], SY + mid[1]], [2, SX + nx1, SY + b[1]]]))
            continue
        if len(pts) == 3:                                          # other openings: keep the mid point proportion
            a, b = pts[0], pts[2]
            nx0, nx1 = MAPX.get(round(a[0]), a[0]), MAPX.get(round(b[0]), b[0])
            if (nx0, nx1) == (a[0], b[0]): continue
            mid = (nx0 + (pts[1][0] - a[0]) / (b[0] - a[0]) * (nx1 - nx0), pts[1][1])
            ops.append(dict(t='spmove', h=r['h'], items=[[0, SX + nx0, SY + a[1]], [1, SX + mid[0], SY + mid[1]], [2, SX + nx1, SY + b[1]]]))
            continue
        items = []
        for i, (x, y) in enumerate(pts):
            nx = MAPX.get(round(x))
            if nx is not None and nx != round(x): items.append([i, SX + nx, SY + y])
        if items: ops.append(dict(t='spmove', h=r['h'], items=items))
    # axis 2/1
    for r in R:
        if r['t'] == 'SPDSCONSTRUCTIONLINE' and abs((r['x0'] + r['x1']) / 2 - 20210) < 5: er.append(r['h'])
    ops.insert(0, dict(t='erase', h=er))
    ops.append(dict(t='save'))
    print(tag, len(ops), 'erase', len(er))
    return gx.run(ops, 'wg_' + tag)[-200:]
if __name__ == '__main__':
    for SX, tag in ((830000.0, '51'), (889400.0, '52'), (948800.0, '53')):
        print(run(SX, 455939.0, tag))
