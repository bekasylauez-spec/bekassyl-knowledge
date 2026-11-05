import ab, sheets, subprocess, os, sys
X0 = sheets.X0; Y0 = sheets.NEW_Y0
print(ab.dxf()[-40:])
print(ab.run([{'t': 'geomdump', 'win': [X0 - 2000, Y0 - 2000, X0 + 3300000, Y0 + 60000], 'file': ab.S + r'\w\geom.txt'}], 'gd')[-60:])
r = subprocess.run([sys.executable, '-W', 'ignore', 'oc.py', 'live.dxf', 'sheets.json', '--geom=geom.txt'], cwd=ab.S + r'\w', capture_output=True)
open(ab.S + r'\w\oc_out.txt', 'wb').write(r.stdout + r.stderr)
out = r.stdout.decode('utf-8', 'replace')
print(' '.join(l for l in out.splitlines() if l.startswith('==')))
print([l for l in out.splitlines() if l.startswith('TOTAL') or 'ПРОЧИТ' in l])
