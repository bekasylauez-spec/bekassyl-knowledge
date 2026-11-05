import gx, re, json
import gen_spec as GS
m = gx.tagmap()
ops, rows, area = GS.build()
A, B = m['SP_2BDB7E'], m['SPB']
out = []
for o in ops:
    if o['t'] == 'tformula':
        for c in o['cells']:
            c[2] = c[2].replace('{T:SP_2BDB7E}', '{T:%s}' % A).replace('{T:SPB}', '{T:%s}' % B)
            if c[2] == '(%s)' % rows[0][3]: c[3] = '%lu2%pr0'
            if o['h'] == 'SP_2BDEA3' and c[1] in (5, 11, 12): c[3] = '%lu2%pr1'
        out.append(o)
out = [x for x in out]
if 0: out.append({'t': 'theight', 'h': 'SPB', 'rows': [[r, 800] for r in range(18, 23)]})

out += [{'t': 'evalf'}, {'t': 'save'}]
print([l for l in gx.run(out, 'fspec').splitlines() if 'ERR' in l or 'done' in l])
