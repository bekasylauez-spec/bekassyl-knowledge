# См-1 (our axis А/1) from analog См-1 (axis А): drop piece 2/1, stretch pieces to ours. Applies to every См-1 sheet frame given.
import sys; sys.path.insert(0, 'wl'); from common import *
MAP = [(10810, 11035), (15710, 15685), (16485, 16485), (16735, 16735), (17510, 17535), (22160, 22135), (22935, 22935), (23185, 23185), (23960, 23985), (28860, 28635), (29735, 29735)]
SXS = {0: 830000.0, 1: 889400.0, 2: 948800.0, 3: 1008200.0}
DOC = None
def run(fi, tag):
    X0, Y0 = SXS[fi], 455939.0
    R = listwin(X0, Y0, 59400, 42000 if fi != 3 else 84100, DOC)
    for r in R:
        if r['t'] == 'INSERT' and r['x1'] - r['x0'] > 15000 and r['x0'] < 12000:
            gx.run([{'t': 'explode', 'h': r['h']}], 'ex', DOC)
    R = listwin(X0, Y0, 59400, 42000 if fi != 3 else 84100, DOC)
    er = []; left = []
    for r in R:
        x0, x1 = r['x0'], r['x1']
        if r['t'] == 'SPDSCONSTRUCTIONLINE' and (abs((x0 + x1) / 2 - 19460) < 5 or abs((x0 + x1) / 2 - 20210) < 5): er.append(r['h'])
        elif r['t'] in ('LWPOLYLINE', 'LINE', 'SPDSNOTEPOSITION', 'MTEXT', 'TEXT', 'HATCH') and x0 > 19100 and x1 < 20300 and r['y0'] > 3000: er.append(r['h'])
        elif r['t'] == 'DIMENSION' and any(abs(a - 19460) < 3 or abs(a - 20210) < 3 or abs(a - 19185) < 3 or abs(a - 20185) < 3 for a, b in r['sp'][:2]): er.append(r['h'])
        elif r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][0] - 20185) < 3: er.append(r['h'])
        elif r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][0] - 17510) < 3 and abs(r['sp'][2][0] - 19185) < 3: left.append(r)
    ops = [dict(t='erase', h=er)]
    ops += stretch_ops(X0, Y0, MAP, ymax=42000 if fi != 3 else 84100)
    for r in left:
        ops.append(dict(t='spmove', h=r['h'], items=[[2, X0 + 22135, Y0 + r['sp'][2][1]]]))
    ops.append(dict(t='save'))
    print(tag, 'erase', len(er), 'diag', len(left), 'ops', len(ops))
    out = gx.run(ops, 'sm1g_' + tag, DOC)
    print('\n'.join(l for l in out.splitlines() if 'stretch' in l or 'ERR' in l or 'done' in l)[-1500:])
if __name__ == '__main__':
    for fi in [int(v) for v in sys.argv[1].split(',')]: run(fi, str(fi))
