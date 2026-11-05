# move SPDS notes (origin only, leaders stay) so that their text clears the wall pieces (no text on hatch)
import sys, collections; sys.path.insert(0, 'wl'); from common import *
from notes import notes
def run(SX, H, xs, geom, go=False, gap=120, ylo=0):
    SY = 455939.0
    T = collections.defaultdict(list)
    for l in open(geom, encoding='utf-8-sig').read().splitlines():
        p = l.split('|')
        if p[0] == 'T': T[p[1]].append([float(v) for v in p[3:7]])
    ops = []
    for n in notes(SX, SY, 59400, H):
        ex = T.get(n['h'])
        if not ex or n['pts'][0][1] < ylo: continue
        w = max(e[2] - e[0] for e in ex); ox = n['pts'][0][0]
        if (min(e[0] for e in ex) + max(e[2] for e in ex)) / 2 - SX < ox: tx1 = ox - 100; tx0 = tx1 - w      # text ends at the origin (geomdump text extents are offset)
        else: tx0 = ox + 100; tx1 = tx0 + w
        for a, b in xs:
            if tx1 > a and tx0 < b:
                cx = (tx0 + tx1) / 2
                d = (a - gap - tx1) if cx < (a + b) / 2 else (b + gap - tx0)
                o = n['pts'][0]
                ops.append(dict(t='spmove', h=n['h'], items=[[0, SX + o[0] + d, SY + o[1]]]))
                break
    ops.append(dict(t='save'))
    print('moved', len(ops) - 1)
    if go: out = gx.run(ops, 'nclr'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-3:])
if __name__ == '__main__':
    import importlib; C = importlib.import_module(sys.argv[1]).VERT
    run(C['SX'], 42000, [(C['AX1'] + a, C['AX1'] + b) for a, b in C['PIECES']], sys.argv[2], '--run' in sys.argv, ylo=C['L'][0])
