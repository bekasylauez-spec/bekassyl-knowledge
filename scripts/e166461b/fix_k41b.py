import json, math, gx, colhoops as CH
X0, Y0 = 706779.0, 455939.0
def W(x, y): return [X0 + x, Y0 + y]
m = gx.tagmap()
B = 20117.0; LV = [B, B + 4550, B + 8600]; CX0, CX1 = 7787.0, 8287.0; FMB = B - 700
ops = []
# old hoop lines / dims
old = [k for k in m if k.startswith('K41_H_') or k.startswith('K41_HD_')]
ops.append({'t': 'erase', 'h': old + ['K41_BK_24667', 'K41_BK_28717']})
P, segs = CH.chain(LV)
# zone-end hoops: per storey
for a, b in zip(LV, LV[1:]):
    p, (n1, n2, n3) = CH.storey(a, b)
    ends = {p[0], p[n1], p[n1 + 1], p[n1 + n2], p[n1 + n2 + 1], p[-1]}
    for y in sorted(ends):
        ops.append({'t': 'lineset', 'h': 'K41_LT', 's': W(CX0 + 20, y), 'e': W(CX1 - 20, y), 'layer': 'диам8', 'lw': -1, 'tag': 'K41_H_%d' % y})
DL = 10702
for (y1, y2, st, n) in segs:
    o = {'t': 'dim', 'h': 'K41_HDT', 'p1': W(CX1, y1), 'p2': W(CX1, y2), 'dl': W(DL, (y1 + y2) / 2), 'rot': math.pi / 2,
         'txt': ('%dх%d' % (st, n)) if n > 1 else '', 'tag': 'K41_HD_%d' % y1}
    if st < 200 and n == 1:          # short value: text outside the chain on a shelf
        o['tx'] = W(DL + 420, (y1 + y2) / 2 + (250 if y1 > LV[0] + 100 else -250))
    ops.append(o)
# breaks at beam stubs from the Фм break (vertical, 800 long)
for lv in LV[1:]:
    ops.append({'t': 'clone', 'h': '10B2B7', 'base': W(9669, (FMB - 100 + B) / 2), 'to': W(CX1 + 600, lv - 275), 'tag': 'K41_BK_%d' % lv})
ops.append({'t': 'levelval', 'h': 'K41_L1', 'old': '+0,200', 'value': '-0,100', 'tag': 'K41_L1'})
ops.append({'t': 'levelval', 'h': 'K41_L2', 'old': '+4,250', 'value': '+3,950', 'tag': 'K41_L2'})
ops.append({'t': 'movegrp', 'h': ['10C8E3'], 'd': [0, -600]})
ops.append({'t': 'movegrp', 'h': ['K41_N1'], 'd': [0, -100]})
ops.append({'t': 'save'})
json.dump(ops, open('ops/k41b.json', 'w'), ensure_ascii=False)
print(segs)
