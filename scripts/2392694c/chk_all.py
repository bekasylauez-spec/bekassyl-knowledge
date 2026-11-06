import os, sys, subprocess, gx, re
W = os.path.join(gx.S, 'chk').replace(os.sep, '/')
gx.run([{'t': 'dxfout', 'file': W + '/live.dxf'}, {'t': 'geomdump', 'win': [172000, 455000, 2510000, 498500], 'file': W + '/geom.txt'}], 'gd')
r = subprocess.run([sys.executable, 'oc.py', 'live.dxf', 'sheets.json', '--geom=geom.txt'], cwd=W, capture_output=True, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
out = r.stdout + r.stderr
open(W + '/oc_out.txt', 'w', encoding='utf-8').write(out)
print(' '.join(l for l in out.splitlines() if l.startswith('==')), [l for l in out.splitlines() if 'TOTAL' in l or 'НЕ ПРОЧ' in l])
