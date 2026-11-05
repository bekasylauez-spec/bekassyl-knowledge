# См-11 (axis 4) sheets cloned from the corrected См-7 sheets (same analog См-6 «по оси 1 и 4»): 5.24 -> 5.45, 5.25 -> 5.46, 5.26 -> 5.47,
# 5.27 -> 5.48, 5.29 -> 5.49 (spec 5.50 is made by a3make)
import sys, re; sys.path.insert(0, 'wl'); from common import *
from lwin import lw
from notes import notes
Y = 455939.0
SH = [(1934700, 59400, 42000, 2906700), (1994100, 42000, 29700, 2966100), (2036100, 42000, 59400, 3008100), (2078100, 42000, 59400, 3050100), (2149800, 59400, 42000, 3092100)]
tot = 0
for SX, W, H, TX in SH:
    R = [r for r in lw(SX - 5, Y - 900, SX + W + 5, Y + H + 5) if (r['ext'] is None and SX - 5 <= r['sp'][0][0] <= SX + W + 5) or (r['ext'] and r['ext'][0] >= SX - 5 and r['ext'][2] <= SX + W + 5)]
    hs = [r['h'] for r in R]
    hs += [n['h'] for n in notes(SX - 5, Y - 900, W + 10, H + 905) if n['h'] not in hs]
    ops = [dict(t='clone', h=h, base=[SX, 0], to=[TX, 0]) for h in hs]
    out = gx.run(ops + [dict(t='save')], 'c11'); n = len(re.findall(r'clone \w+>', out))
    print(SX, '->', TX, len(hs), 'cloned', n, [l for l in out.splitlines() if 'ERR' in l][:3]); tot += n
print('total', tot)
