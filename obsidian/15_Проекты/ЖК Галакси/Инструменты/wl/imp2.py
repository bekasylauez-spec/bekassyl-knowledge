# import one analog sheet into the main DWG reading the analog file directly (not open): python wl/imp2.py st1 14 SX SY pre
import sys, os; sys.path.insert(0, 'wl'); from common import *
from imp import SRC
def imp2(k, fi, SX, SY, pre):
    x0, y0, x1, y1 = F[k][fi][:4]
    gx.run([{'t': 'listfile', 'file': SRC[k][0], 'win': [x0 - 5, y0 - 5, x1 + 5, y1 + 5]}], 'lsf')
    hs = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if l.startswith('L\t'):
            e = [float(v) for v in r[4][1:].split(',')]
            if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5: hs.append(r[2])
        elif l.startswith('N\t'): hs.append(r[2])
    out = gx.run([dict(t='import', file=SRC[k][0], h=hs, base=[x0, y0], to=[SX, SY], pre=pre), dict(t='save')], 'imp')
    print(k, fi, len(hs), [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
if __name__ == '__main__':
    imp2(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
