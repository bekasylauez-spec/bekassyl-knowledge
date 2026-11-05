# См-2 (ours: y=7550, pieces 1300+250+1300 at axes 2 and 3) from analog См-2 (А/1): pmap + drop axis 2/1
import sys, json; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SY = 455939.0
EL = [(14245, 14220), (14295, 14270), (15520, 15520), (15770, 15770), (16820, 17020), (16870, 17070),
      (20545, 20670), (20595, 20720), (21970, 21970), (22220, 22220), (23445, 23470), (23495, 23520)]
PLAN_DX = 44707 - 15645
PAIRS = [(12000, 12000)] + EL + [(26000, 26000), (40000, 40000)] + [(a + PLAN_DX, b + PLAN_DX) for a, b in EL] + [(56000, 56000)]
DEAD = [19245, 47557]
def run(X0, H=42000):
    R = listwin(X0, SY, 59400, H, None)
    er = [r['h'] for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and min(abs((r['x0'] + r['x1']) / 2 - d) for d in DEAD) < 5]
    er += [r['h'] for r in R if r['t'] == 'DIMENSION' and any(min(abs(a - d) for d in DEAD) < 3 for a, b in r['sp'][:2])]
    ops = [dict(t='erase', h=er), dict(t='pmap', win=[X0 + 1000, SY + 1000, X0 + 57000, SY + H - 1000], pairs=[[X0 + a, X0 + b] for a, b in PAIRS]), dict(t='save')]
    out = gx.run(ops, 'sm2g'); print(int(X0), 'erase', len(er), [l for l in out.splitlines() if 'pmap' in l or 'ERR' in l][-3:])
for X0 in (1100900.0, 1160300.0, 1219700.0): run(X0)
