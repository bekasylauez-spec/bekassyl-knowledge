# put a dim's text back to its standard place: centre of its segment, point on the dim line (rule 31.10)
import sys, json, ezdxf, logging
logging.disable(logging.CRITICAL)
d = ezdxf.readfile('w/live.dxf'); ops = []
for h in sys.argv[1].split(','):
    e = d.entitydb.get(h); p1, p2, dp = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
    vert = abs((e.dxf.get('angle', 0) or 0) % 180 - 90) < 1
    if vert: ops.append({'t': 'dimtx', 'h': h, 'at': [dp.x, (p1.y + p2.y) / 2]})
    else: ops.append({'t': 'dimtx', 'h': h, 'at': [(p1.x + p2.x) / 2, dp.y + 155]})
json.dump(ops, open('ops/recenter.json', 'w'))
print(ops)
