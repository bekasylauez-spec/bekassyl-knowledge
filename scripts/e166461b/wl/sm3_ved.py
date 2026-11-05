# См-3 sheet 5.12 «Ведомость деталей» (loose analog sketches): Ск1..Ск4 = our caps (legs 61d, L = 2*61d + 170)
import sys; sys.path.insert(0, 'wl'); from common import *
CK = {1: (980, 2130), 2: (1100, 2370), 3: (860, 1890), 4: (740, 1650)}
# Ск2 group (texts + polyline + multileader) at row y 9000, right column
G2 = {'name': '17E01F', 'top': '17E00F', 'bot': '17E012', 'lab': '17E011', 'L': '17E017'}
G2_other = ['17E00E', '17E021', '17E020', '17E023']
ops = []
for k, (dx, dy) in {3: (-6300, -2000), 4: (0, -2000)}.items():
    for h in list(G2.values()) + G2_other: ops.append(dict(t='clone', h=h, base=[0, 0], to=[dx, dy], tag='V3C%d:%s' % (k, h)))
def put(k, hs):
    leg, L = CK[k]
    for key, s in (('name', 'Ск%d' % k), ('top', str(leg)), ('bot', str(leg)), ('lab', 'по н.г.'), ('L', str(L))): ops.append(dict(t='settext', h=hs[key], s=s))
put(1, {'name': '17DFFA', 'top': '17DFEA', 'bot': '17DFED', 'lab': '17DFEC', 'L': '17DFF2'})
put(2, G2)
for k in (3, 4): put(k, {key: 'V3C%d:%s' % (k, h) for key, h in G2.items()})
ops.append(dict(t='save'))
if '--run' in sys.argv:
    out = gx.run(ops, 'v3'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
