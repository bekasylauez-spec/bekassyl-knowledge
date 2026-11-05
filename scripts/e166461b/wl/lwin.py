import os, gx
def lw(x0, y0, x1, y1):
    gx.run([{'t': 'list', 'win': [x0, y0, x1, y1]}], 'lst')
    R = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        if not l.startswith(('L\t', 'N\t')): continue
        r = l.split('\t')
        if r[0] == 'N': R.append(dict(t=r[1], h=r[2], lay=r[3], ext=None, sp=[tuple(float(c) for c in r[4].split(','))])); continue
        if 'NaN' in r[4]: continue
        e = [float(v) for v in r[4][1:].split(',')]
        sp = [tuple(float(c) for c in p.split(',')) for p in r[5:] if 'NaN' not in p]
        R.append(dict(t=r[1], h=r[2], lay=r[3], ext=e, sp=sp))
    return R
