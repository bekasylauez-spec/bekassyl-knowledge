import ezdxf, sys, collections, re
from ezdxf import bbox
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
def dec(s): return re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda g: chr(int(g.group(1), 16)), s)
c = collections.Counter()
for e in m.query('HATCH'):
    c[(dec(e.dxf.layer), e.dxf.pattern_name, e.dxf.color)] += 1
for k, v in c.items(): print(v, k)
# layers list
for l in d.layers: print('L', dec(l.dxf.name))
