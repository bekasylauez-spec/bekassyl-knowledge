import sys, os; sys.path.insert(0, 'wl'); from common import *
def notes(X0, Y0, W, H, doc=None):
    gx.run([{'t': 'notelist'}], 'nl', doc)
    out = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        if not l.startswith('N\t'): continue
        r = l.split('\t')
        pts = [tuple(float(v) for v in p.split(',')) for p in r[9:] if not p.startswith('E')]
        if not pts: continue
        ox, oy = pts[0]
        if not (X0 <= ox <= X0 + W and Y0 <= oy <= Y0 + H): continue
        out.append(dict(h=r[1], t=r[2], l1=r[3], l2=r[4], pts=[(x - X0, y - Y0) for x, y in pts]))
    return out
if __name__ == '__main__':
    X0 = float(sys.argv[1])
    for n in notes(X0, 455939, 59400, float(sys.argv[2]) if len(sys.argv) > 2 else 42000):
        print(n['h'], n['l1'], '|', n['l2'], [(round(x), round(y)) for x, y in n['pts']])
