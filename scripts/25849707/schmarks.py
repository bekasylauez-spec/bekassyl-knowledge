# rigel marks «Рм-N» on the scheme sheets 2.2 (−0.050), 2.3 (+4.500), 2.4 (+7.000): clones of the scheme text 5B4DF9
import json, math, gx
M = json.load(open('w/marks2.json', encoding='utf-8'))
SHEET = {-0.05: 1, 4.5: 2, 7.0: 3}
PROTO, PB = '5B4DF9', [214667.3304096889, -1785684.128777295]       # TEXT (Isocpeur 2.5, layer Нумерация), alignment point
ops = []
# old marks (re-run): erase previous clones
old = [v for k, v in gx.tagmap().items() if k.startswith('SM_')]
if old: ops += [dict(t='erase', h=[v]) for v in old]
n = 0
for m in M:
    b = m['r']['b']
    for l in m['locs']:
        k = SHEET[round(l['z'], 2)]
        OX, OY = 141317.0 + 84100.0 * k, -1773284.0
        um = (l['endL'] + l['endR']) / 2.0
        tg = 'SM_%d' % n; n += 1
        if l['d'] == 'X':
            to = [OX + um, OY + l['c'] + b / 2.0 + 220]
            ops.append(dict(t='clone', h=PROTO, base=PB, to=to, tag=tg, text=m['name']))
        else:
            to = [OX + l['c'] + b / 2.0 + 220, OY + um]
            ops.append(dict(t='clone', h=PROTO, base=PB, to=to, tag=tg, text=m['name']))
            ops.append(dict(t='xform', h=tg, base=to, to=to, ang=math.pi / 2))
ops.append(dict(t='save'))
out = gx.run(ops, 'schm')
print(n, [l for l in out.splitlines() if 'ERR' in l][:5])
