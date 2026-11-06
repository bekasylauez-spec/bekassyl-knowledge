import gx, json, sys, subprocess, os
k = int(sys.argv[1]); SX = 172179 + 31500 * k
win = [SX, 455939, SX + 31500, 470789]
g = os.path.join(gx.S, 'w', 'geom%d.txt' % k); dx = os.path.join(gx.S, 'w', 'chk%d.dxf' % k)
print(gx.run([dict(t='geomdump', win=win, file=g), dict(t='dxfout', file=dx)], 'gd')[-120:])
json.dump({'s%d' % k: win}, open(gx.S + r'\w\sh%d.json' % k, 'w'))
r = subprocess.run([sys.executable, '-X', 'utf8', gx.S + r'\tools\oc.py', dx, gx.S + r'\w\sh%d.json' % k, '--geom=' + g], capture_output=True, text=True, encoding='utf-8')
print(r.stdout[-6000:], r.stderr[-1500:])
