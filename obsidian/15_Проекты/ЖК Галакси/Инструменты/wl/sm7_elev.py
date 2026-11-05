# См-7 elevation sheets made from the analog См-6 elevations (A = analog axis A on the sheet): drop the extension left of A,
# the inner band А/2 and the axes А/2, Б/1; remap the pieces (sm7_map); band of См-3 at 13850; axes А/1 0, А 5000, Б 14750, В 22750
import sys; sys.path.insert(0, 'wl'); from common import *
from sm7_map import pairs
from notes import notes
Y = 455939.0
def run(X, A, YL, YH, go=True):
    R = listwin(X, Y, 42000, 59400, None)
    er = []
    for r in R:
        if r['y0'] < YL - 400 or r['y1'] > YH or r['x1'] > A + 20000: continue
        if r['t'] in ('SPDSLEVELMARK', 'SPDSSECTION', 'SPDSCONSTRUCTIONLINE'): continue
        if r['x0'] >= A - 3135 and r['x1'] <= A - 120 and r['y0'] > YL - 5: er.append(r['h'])                 # extension (and its bars / notes / dims)
        elif r['x0'] >= A + 8745 and r['x1'] <= A + 9005 and r['t'] in ('LWPOLYLINE', 'LINE', 'HATCH') and r['lay'] == 'Размеры': er.append(r['h'])   # band А/2
    for n in notes(X, Y, 42000, 59400):
        xs = [p[0] for p in n['pts']]
        if all(A - 3400 < x < A - 120 for x in xs) and n['pts'][0][1] > YL: er.append(n['h'])
    ax = sorted([r for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and r['y1'] - r['y0'] > 5000], key=lambda r: r['x0'])
    print('axes', [(r['h'], round((r['x0'] + r['x1']) / 2)) for r in ax])
    hA, hA1, hA2, hB, hB1, hV = [r['h'] for r in ax]
    sp = {r['h']: r['sp'] for r in ax}
    ops = [dict(t='erase', h=er + [hA2, hB1]), dict(t='pmap', win=[X + 1000, Y + YL - 400, X + 41000, Y + YH], pairs=pairs(X, A))]
    for h, x, v in ((hA, 0, 'А/1'), (hA1, 5000, 'А'), (hB, 14750, 'Б'), (hV, 22750, 'В')):
        (sx, sy), (ex, ey) = sp[h][0], sp[h][1]
        ops.append(dict(t='axis', h=h, s=[X + A + x, Y + sy], e=[X + A + x, Y + ey], val=v))
    ops.append(dict(t='save'))
    print('erase', len(er))
    if go:
        out = gx.run(ops, 'sm7e'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-3:])
    # band of См-3 (clone of the A band) after the remap
    R = listwin(X, Y, 42000, 59400, None)
    band = [r['h'] for r in R if r['t'] == 'LWPOLYLINE' and abs(r['x0'] - (A - 125)) < 3 and abs(r['x1'] - (A + 125)) < 3 and r['y0'] > YL - 5]
    ops = [dict(t='clone', h=h, base=[0, 0], to=[13850, 0]) for h in band] + [dict(t='save')]
    if go:
        out = gx.run(ops, 'sm7e2'); print('band', len(band), [l for l in out.splitlines() if 'ERR' in l or 'done' in l][-2:])
if __name__ == '__main__':
    run(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
