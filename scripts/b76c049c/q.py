# -*- coding: utf-8 -*-
"""q.py sheet_i [x0 y0 x1 y1 in sheet-relative 1:100 units] [types,comma] — list analog entities fully inside window"""
import pickle, sys
sys.stdout.reconfigure(encoding='utf-8')
D = pickle.load(open(__file__.replace('q.py', 'an.pkl'), 'rb'))
i = int(sys.argv[1]); X0 = -41822 + 59400 * i; Y0 = -1593693
if len(sys.argv) > 5:
    w = [float(v) for v in sys.argv[2:6]]; w = [X0 + w[0], Y0 + w[1], X0 + w[2], Y0 + w[3]]
else:
    w = [X0, Y0, X0 + 59400, Y0 + 42000]
ty = sys.argv[6].split(',') if len(sys.argv) > 6 else None
n = 0
for e in D:
    b = e['bb']
    if not b: continue
    if b[0] >= w[0] - 1 and b[1] >= w[1] - 1 and b[2] <= w[2] + 1 and b[3] <= w[3] + 1:
        if ty and e['t'] not in ty: continue
        n += 1
        print('%s\t%s\t%s\t%.0f,%.0f,%.0f,%.0f\t%s\t%s' % (e['h'], e['t'], e['l'], b[0] - X0, b[1] - Y0, b[2] - X0, b[3] - Y0, (e['txt'] or '')[:90].replace('\n', ' '), {k: v for k, v in e['ex'].items() if k not in ('att',)} if e['t'] != 'INSERT' else e['ex']))
print('N', n)
