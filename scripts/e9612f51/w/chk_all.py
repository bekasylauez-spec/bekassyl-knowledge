import sys, os, subprocess, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'net'))
os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'net'))
import gx
W = gx.S + r'\w'
sh = json.load(open(W + r'\sheets_all.json'))
ks = sys.argv[1:] or list(sh)
geo = []
for k in ks:
    x0, y0, x1, y1 = sh[k]
    f = W + r'\geom_%s.txt' % k
    gx.run([dict(t='geomdump', win=[x0, y0, x1, y1], file=f)], 'gd')
    geo.append(f)
open(W + r'\geom_all.txt', 'w', encoding='utf-8').write(''.join(open(f, encoding='utf-8-sig').read() for f in geo))
gx.run([dict(t='dxfout', file=W + r'\all.dxf')], 'dx')
json.dump({k: sh[k] for k in ks}, open(W + r'\sheets_sel.json', 'w'))
r = subprocess.run([sys.executable, '-X', 'utf8', W + r'\oc.py', W + r'\all.dxf', W + r'\sheets_sel.json', '--geom=' + W + r'\geom_all.txt'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
open(W + r'\oc_all.txt', 'w', encoding='utf-8').write(r.stdout + r.stderr)
print('\n'.join(l for l in r.stdout.splitlines() if l.startswith('==') or l.startswith('TOTAL')))
