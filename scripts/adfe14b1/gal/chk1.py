# check one sheet: dxfout of the live drawing + geomdump of the sheet window + oc.py
import sys, os, json, subprocess, gx
no, x0, y0 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
W = os.path.join(gx.S, 'w')
dxf = os.path.join(W, 'live.dxf'); geo = os.path.join(W, 'geo_%s.txt' % no)
win = [x0, y0, x0 + 31500, y0 + 14850]
print(gx.run([dict(t='dxfout', file=dxf), dict(t='geomdump', win=win, file=geo)], 'chk')[-300:])
json.dump({no: win}, open(os.path.join(W, 'sh_%s.json' % no), 'w'))
r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(W, 'oc.py'), dxf, os.path.join(W, 'sh_%s.json' % no), '--geom=' + geo, '--dump=' + os.path.join(W, 'dump_%s.pkl' % no)], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout[-6000:], r.stderr[-2000:])
