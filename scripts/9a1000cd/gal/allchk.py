import sys, os, json, subprocess, gx, prep
W = os.path.join(gx.S, 'w')
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
sh = {}
for M, p in prep.build(marks, first_no=5):
    w = 21000 if p.get('a3') else 31500
    x0 = p['SX']
    sh[p['no']] = [x0, p['SY'], x0 + w, p['SY'] + 14850]
json.dump(sh, open(os.path.join(W, 'sh_all.json'), 'w'))
print(len(sh), list(sh.items())[:2], [k for k in sh if prep and 0])
dxf = os.path.join(W, 'live_all.dxf'); geo = os.path.join(W, 'geo_all.txt')
if 'nodump' not in sys.argv:
    print(gx.run([dict(t='dxfout', file=dxf), dict(t='geomdump', win=[45979, 419800, 2377379, 435050], file=geo)], 'chkall', wait=900)[-300:])
r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(W, 'oc.py'), dxf, os.path.join(W, 'sh_all.json'), '--geom=' + geo], capture_output=True, text=True, encoding='utf-8', errors='replace')
open(os.path.join(W, 'oc_all.txt'), 'w', encoding='utf-8').write(r.stdout + r.stderr)
print(r.stdout[-3000:], r.stderr[-1500:])
