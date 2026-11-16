import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
p = sys.argv[1]
a = np.asarray(Image.open(p).convert("L")) < 160
H, W = a.shape
# find horizontal line segments longer than 300px
res = []
for y in range(H):
    row = a[y]
    # run-lengths
    x = 0
    while x < W:
        if row[x]:
            s = x
            while x < W and row[x]: x += 1
            if x - s > 300: res.append((y, s, x))
        else:
            x += 1
# group by y-adjacent
groups = []
for r in res:
    if groups and r[0] - groups[-1][-1][0] <= 2 and abs(r[1]-groups[-1][-1][1])<10:
        groups[-1].append(r)
    else:
        groups.append([r])
for g in groups:
    print("y%d-%d x%d-%d" % (g[0][0], g[-1][0], g[0][1], g[0][2]))
