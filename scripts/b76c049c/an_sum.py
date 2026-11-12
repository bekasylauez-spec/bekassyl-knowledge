# -*- coding: utf-8 -*-
import pickle, sys, collections
R = pickle.load(open('an.pkl', 'rb')); LAY = pickle.load(open('an.pkl.lay', 'rb')); DS = pickle.load(open('an.pkl.ds', 'rb')); ST = pickle.load(open('an.pkl.st', 'rb'))
FR = {('an%02d' % (3 + i)): (-41822 + 59400 * i, -1593693) for i in range(10)}
def insheet(d, x0, y0):
    b = d.get('bb')
    if not b: return False
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return x0 <= cx <= x0 + 59400 and y0 <= cy <= y0 + 42000
which = sys.argv[1:] or sorted(FR)
for s in which:
    x0, y0 = FR[s]
    E = [d for d in R if insheet(d, x0, y0)]
    print('=====', s, len(E))
    c = collections.Counter((d['t'], d['layer']) for d in E)
    for k, v in sorted(c.items(), key=lambda a: -a[1])[:40]: print('  ', v, k, LAY.get(k[1], ''))
    # texts heights
    th = collections.Counter((d['t'], round(d.get('ht', 0)), d.get('st'), d['layer']) for d in E if d['t'] in ('MTEXT', 'TEXT'))
    print('  TEXT:', dict(th))
    dm = collections.Counter((d.get('ds'), d.get('dimlfac'), d.get('dimscale'), d['layer']) for d in E if d['t'] == 'DIMENSION')
    print('  DIM:', dict(dm))
    ha = collections.Counter((d.get('pat'), d.get('psc'), d['layer']) for d in E if d['t'] == 'HATCH')
    print('  HATCH:', dict(ha))
    ins = collections.Counter((d.get('blk'), d['layer']) for d in E if d['t'] == 'INSERT')
    print('  INSERT:', dict(ins))
    lt = collections.Counter((d['lt'], round(d['lts'], 1), d['layer']) for d in E if d['lt'] not in ('BYLAYER', 'ByLayer'))
    print('  LTYPE:', dict(lt))
    lw = collections.Counter((d['t'], d['lw'], d['layer']) for d in E if d['lw'] not in (-1,))
    print('  LW:', dict(lw))
