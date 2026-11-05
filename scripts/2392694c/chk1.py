# oc.py on one slab sheet: python chk1.py <k>
import sys, os, json, subprocess, gx
k = int(sys.argv[1]); W = os.path.join(gx.S, 'chk').replace(os.sep, '/')
fr = json.load(open(W + '/sheets.json', encoding='utf-8'))['7.%d' % k]
gx.run([{'t': 'dxfout', 'file': W + '/live.dxf'}, {'t': 'geomdump', 'win': [fr[0] - 10, fr[1] - 10, fr[2] + 10, fr[3] + 10], 'file': W + '/geom.txt'}], 'dmp')
json.dump({'7.%d' % k: fr}, open(W + '/one.json', 'w'))
r = subprocess.run([sys.executable, 'oc.py', 'live.dxf', 'one.json', '--geom=geom.txt'], cwd=W, capture_output=True, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
open(W + '/oc_%d.txt' % k, 'w', encoding='utf-8').write(r.stdout + r.stderr)
print(r.stdout[-6000:], r.stderr[-1500:])
