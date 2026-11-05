# rebuild all level marks of one elevation with the checked shape (См-9 5.37: 6-char from «+3,950» 27952F, 7-char from «+22,400» 280E8B):
# each mark is replaced by a clone at its own level, reference point sp0 at the common column, value set by levelval.
# usage: python wl/levfix.py X W H x_lo x_hi top_value     (x_lo..x_hi: sheet-relative range of sp0 of this elevation)
import sys, re, collections; sys.path.insert(0, 'wl'); from common import *
X, W, H, lo, hi = (float(v) for v in sys.argv[1:6]); top = float(sys.argv[6])
SRC = {6: ('27952F', 2552031.0, 474830.0, '+3,950'), 7: ('280E8B', 2552031.0, 493280.0, '+22,400')}
VALS = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7] + ([top] if top > 19.71 else [])
M = sorted([r for r in listwin(X, 455939, W, H, None) if r['t'] == 'SPDSLEVELMARK' and lo <= r['sp'][0][0] <= hi], key=lambda r: r['sp'][0][1])
assert len(M) == len(VALS), (len(M), len(VALS))
dz = [round(M[i + 1]['sp'][0][1] - M[i]['sp'][0][1]) for i in range(len(M) - 1)]
assert all(abs(d - round((VALS[i + 1] - VALS[i]) * 1000)) < 3 for i, d in enumerate(dz)), dz
x0 = collections.Counter(round(r['sp'][0][0]) for r in M).most_common(1)[0][0]
fmt = lambda v: ('+' if v >= 0 else '-') + ('%.3f' % abs(v)).replace('.', ',')
ops = [dict(t='erase', h=[r['h'] for r in M])]; plan = []
for r, v in zip(M, VALS):
    s = fmt(v); h, sx, sy, old = SRC[len(s)]
    ops.append(dict(t='clone', h=h, base=[sx, sy], to=[X + x0, 455939 + r['sp'][0][1]])); plan.append((old, s))
out = gx.run(ops, 'lf1'); hs = re.findall(r'clone \w+>(\w+)', out)
ops2 = [dict(t='levelval', h=h, old=a, value=b) for h, (a, b) in zip(hs, plan) if a != b] + [dict(t='save')]
out2 = gx.run(ops2, 'lf2'); print(len(M), 'marks, column', x0, [l for l in out2.splitlines() if 'ERR' in l or 'done' in l or 'not found' in l])
