import gx, json, sys, subprocess, os, batch_util as bu
S = gx.S
slots = [int(a) for a in sys.argv[1:]] or list(range(1, 50))
geo = os.path.join(S, 'w', 'geom_all.txt'); open(geo, 'w').close()
bu.restart()
for i, k in enumerate(slots):
    if i and i % 8 == 0: bu.restart()
    SX = 172179 + 31500 * k; g = os.path.join(S, 'w', 'geom%d.txt' % k)
    gx.run([dict(t='geomdump', win=[SX, 455939, SX + 31500, 470789], file=g)], 'gd')
    open(geo, 'a', encoding='utf-8').write(open(g, encoding='utf-8-sig').read())
bu.restart()
dx = os.path.join(S, 'w', 'all.dxf')
print(gx.run([dict(t='dxfout', file=dx)], 'dx')[-100:])
bu.kill()
json.dump({'6.%d' % k: [172179 + 31500 * k, 455939, 172179 + 31500 * k + 31500, 470789] for k in slots}, open(os.path.join(S, 'w', 'sh_all.json'), 'w'))
r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(S, 'tools', 'oc.py'), dx, os.path.join(S, 'w', 'sh_all.json'), '--geom=' + geo], capture_output=True, text=True, encoding='utf-8')
open(os.path.join(S, 'w', 'oc_all.txt'), 'w', encoding='utf-8').write(r.stdout + r.stderr)
print('\n'.join(l for l in r.stdout.splitlines() if l.startswith('==') or l.startswith('TOTAL')))
