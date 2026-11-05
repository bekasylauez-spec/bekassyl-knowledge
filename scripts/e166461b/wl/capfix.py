# vertical sheets: Ск legs as in the analog — left leg 20 OUTSIDE the zone's left bar (was +20 inside); notes follow
import sys; sys.path.insert(0, 'wl'); from common import *
from notes import notes
def run(SX, go=False):
    SY = 455939.0
    R = listwin(SX, SY, 59400, 42000, None)
    legs = sorted([r for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].startswith('диам') and abs(r['x1'] - r['x0']) < 1 and r['y1'] > 34000 and r['y1'] - r['y0'] < 1700], key=lambda r: r['x0'])
    ops = []; moved = {}
    i = 0
    while i + 1 < len(legs):
        a, b = legs[i], legs[i + 1]
        if a['lay'] == b['lay'] and abs(a['y0'] - b['y0']) < 2:
            ops.append(dict(t='move', h=[a['h']], d=[-40, 0])); moved[round(a['x0'])] = a['x0'] - 40; i += 2
        else: i += 1
    for n in notes(SX, SY, 59400, 42000):
        if not n['l1'].startswith('Ск'): continue
        it = [[j, SX + moved[round(p[0])], SY + p[1]] for j, p in enumerate(n['pts']) if j > 0 and round(p[0]) in moved]
        if it: ops.append(dict(t='spmove', h=n['h'], items=it))
    ops.append(dict(t='save'))
    print(SX, 'legs', len(legs), 'moved', len(moved), 'note edits', len([o for o in ops if o['t'] == 'spmove']))
    if go: print(gx.run(ops, 'capfix')[-60:])
if __name__ == '__main__':
    for sx in sys.argv[1].split(','): run(float(sx), '--run' in sys.argv)
