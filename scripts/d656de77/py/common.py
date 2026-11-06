# shared helpers: sheet entity lists (from AutoCAD 'list' op dumps w/l6k.txt), transforms
import os, sys, json
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(S, 'net'))
import gx

Y0 = 455939.0
def SX(k): return 172179.0 + 31500.0 * k

def ents(k):
    out = []
    for l in open(os.path.join(S, 'w', 'l6%d.txt' % (k + 1)), encoding='utf-8-sig'):
        f = l.rstrip('\n').split('\t')
        if len(f) < 5 or f[0] != 'L' or not f[4].startswith('E'): continue
        e = [float(v) for v in f[4][1:].split(',')]
        pts = [tuple(float(v) for v in p.split(',')) for p in f[5:]]
        out.append(dict(t=f[1], h=f[2], lay=f[3], e=e, p=pts))
    return out

def inside(E, w):
    return [x for x in E if x['e'][0] >= w[0] and x['e'][2] <= w[2] and x['e'][1] >= w[1] and x['e'][3] <= w[3]]

def relist(k):
    import shutil
    X0 = SX(k)
    r = gx.run([dict(t='list', win=[X0 - 100, 455839, X0 + 31600, 470900])], 'ls')
    shutil.copy(os.path.join(os.environ['TEMP'], 'gq_log.txt'), os.path.join(S, 'w', 'l6%d.txt' % (k + 1)))
    return r

def run(ops, name):
    r = gx.run(ops, name)
    lg = gx.log()
    errs = [l for l in lg.splitlines() if l.startswith('ERR') or 'error' in l.lower() and 'errors 0' not in l]
    return r, lg, errs
