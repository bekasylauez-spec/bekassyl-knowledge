# «Ведомость деталей»: Г-bar sketch (dop with 90° hook 12d=240) cloned from the Ск1 sketch, 1000 below it
import sys
from common import *

# 6.1 handles of the Ск1 sketch -> role
SK61 = {'2CAA27': 'pl', '2CAA15': 'name', '2CAA16': 'v', '2CAA17': 'top', '2CAA19': 'side', '2CAA1A': 'bot', '2CAA1F': 'len', '2CAA28': 'L'}
GB = {0: ('2', 2525, 2765), 1: ('2', 3055, 3295), 2: ('2', 2125, 2365), 3: ('2', 3360, 3600), 4: ('3', 3020, 3260)}
DY = -1000.0


def find(k):
    E0 = {e['h']: e for e in ents(0)}; E = ents(k); dx = SX(k) - SX(0); out = {}
    for h, role in SK61.items():
        a = E0[h]['e']
        c = [e for e in E if e['t'] == E0[h]['t'] and abs(e['e'][0] - a[0] - dx) < 2 and abs(e['e'][1] - a[1]) < 2 and abs(e['e'][3] - a[3]) < 2]
        assert len(c) == 1, (k, h, len(c)); out[role] = c[0]
    return out


def build(k):
    pos, ls, L = GB[k]; R = find(k); dx = SX(k) - SX(0)
    ops = []; add = lambda **kw: ops.append(kw)
    T = lambda r: 'g%d_%s' % (k, r)
    for r in ('pl', 'name', 'v', 'top', 'side', 'len', 'L'):
        add(t='clone', h=R[r]['h'], base=[0, 0], to=[0, DY], tag=T(r))
    x0 = 201827 + dx; yt = 468087 + DY
    add(t='plset', h=T('pl'), p=[[202577 + dx, yt], [201879 + dx, yt], [x0, yt - 52], [x0, yt - 264]])
    add(t='settext', h=T('name'), s=pos)
    add(t='settext', h=T('v'), s='240')
    add(t='settext', h=T('top'), s=str(ls))
    add(t='settext', h=T('side'), s='по н.г.')
    add(t='settext', h=T('len'), s=str(L))
    return ops


if __name__ == '__main__':
    for k in [int(a) for a in sys.argv[1].split(',')]:
        r, lg, errs = run(build(k), 'v%d' % k); print(k, r[:60], errs)
