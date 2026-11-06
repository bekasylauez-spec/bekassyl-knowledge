import sys, importlib, runpy, io, contextlib
sys.path.insert(0, 'wl')
cfg = sys.argv[1]; sx = sys.argv[2] if len(sys.argv) > 2 else None
sys.argv = ['wall_vert.py', cfg]
if sx:
    m = importlib.import_module(cfg); m.VERT['SX'] = float(sx)
g = runpy.run_path('wl/wall_vert.py', run_name='chk')
D = g['D']
for i, piece in enumerate(D):
    for kind in 'LMR':
        seq = [next(((z[3], z[4]) for z in (zs or []) if z[0] == kind), None) for zs in piece]
        if any(seq): print(cfg, 'P%d %s' % (i + 1, kind), ' | '.join('%d@%d' % s if s else '-' for s in seq))
