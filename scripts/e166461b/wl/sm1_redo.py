# См-1 sheets 5.1-5.4: fresh import of analog 4.1-4.4, drop piece 2/1, proportional remap (pmap) of the pieces to ours
import sys, os, json; sys.path.insert(0, 'wl'); from common import *
from imp import imp
from notes import notes
SX = {0: 830000.0, 1: 889400.0, 2: 948800.0, 3: 1008200.0}; SY = 455939.0
PAIRS = [(9935, 9935), (9985, 9985), (10760, 10985), (10810, 11035), (15710, 15685), (16485, 16485), (16735, 16735), (17510, 17535),
         (22160, 22135), (22935, 22935), (23185, 23185), (23960, 23985), (28860, 28635), (28910, 28685), (29685, 29685), (29735, 29735)]
PL = lambda x: 7075 + 2 * (x - 9810)                       # 5.4 plan is drawn x2, axis 1 at 7075
def clear(X0, H):
    gx.run([{'t': 'list', 'win': [X0 - 5, SY - 5, X0 + 59405, SY + H + 5]}], 'lst')
    hs = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if l.startswith('L\t'):
            e = [float(v) for v in r[4][1:].split(',')]
            if e[0] >= X0 - 5 and e[2] <= X0 + 59405 and e[1] >= SY - 5 and e[3] <= SY + H + 5: hs.append(r[2])
        elif l.startswith('N\t'): hs.append(r[2])
    gx.run([{'t': 'erase', 'h': hs}], 'clr')
def run(fi):
    X0 = SX[fi]; H = 84100 if fi == 3 else 42000
    clear(X0, H)
    imp('st1', fi, X0, SY, 'S1R%d:' % fi)
    R = listwin(X0, SY, 59400, H, None)
    for r in R:
        if r['t'] == 'INSERT' and r['x1'] - r['x0'] > 15000 and r['x0'] < 12000: gx.run([{'t': 'explode', 'h': r['h']}], 'ex')
    R = listwin(X0, SY, 59400, H, None)
    plan = fi == 3
    g = (lambda x: PL(x)) if plan else (lambda x: x)
    lo, hi = (g(19100), g(20300)) if not plan else (25600, 28300)
    dead_dim = [g(v) for v in (19185, 20185, 19460, 20210)] + ([25925, 27725, 26375] if plan else [])
    ylo, yhi = (8000, 21000) if plan else (3000, 42000)
    er = []; left = []
    for r in R:
        if r['y1'] < ylo or r['y0'] > yhi: continue
        cx = (r['x0'] + r['x1']) / 2
        if r['t'] == 'SPDSCONSTRUCTIONLINE' and r['x1'] - r['x0'] < 1500 and min(abs(cx - v) for v in dead_dim) < 5: er.append(r['h'])
        elif r['t'] == 'DIMENSION' and any(min(abs(a - v) for v in dead_dim) < 3 for a, b in r['sp'][:2]): er.append(r['h'])
        elif r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][0] - 20185) < 3: er.append(r['h'])
        elif r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][0] - 17510) < 3 and abs(r['sp'][2][0] - 19185) < 3: left.append(r)
        elif r['t'] != 'SPDSNOTEPOSITION' and r['x0'] > lo and r['x1'] < hi: er.append(r['h'])
    for n in notes(X0, SY, 59400, H):
        xs = [p[0] for p in n['pts'][1:]] or [n['pts'][0][0]]
        if all(lo - 300 < x < hi + 100 for x in xs) and ylo < n['pts'][0][1] < yhi: er.append(n['h'])
    pairs = [[X0 + g(a), X0 + g(b)] for a, b in PAIRS]
    ops = [dict(t='erase', h=er), dict(t='pmap', win=[X0 + 1000, SY + ylo, X0 + (50000 if plan else 33000), SY + yhi], pairs=pairs)]
    for r in left: ops.append(dict(t='spmove', h=r['h'], items=[[2, X0 + 22135, SY + r['sp'][2][1]]]))
    ops.append(dict(t='save'))
    out = gx.run(ops, 'sm1r%d' % fi)
    print(fi, 'erase', len(er), 'diag', len(left), [l for l in out.splitlines() if 'pmap' in l or 'ERR' in l][-6:])
if __name__ == '__main__':
    for fi in [int(v) for v in sys.argv[1].split(',')]: run(fi)
