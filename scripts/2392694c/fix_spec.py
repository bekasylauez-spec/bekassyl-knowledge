import gx, re, json
import gen_spec as GS
m = gx.tagmap()
ops, rows, area = GS.build()
A, B = m['SP_2BDB7E'], m['SPB' + GS.C['tag']]
out = []
for o in ops:
    if o['t'] == 'tformula':
        for c in o['cells']:
            c[2] = c[2].replace('{T:SP_2BDB7E}', '{T:%s}' % A).replace('{T:SPB%s}' % GS.C['tag'], '{T:%s}' % B)
            if c[2] == '(%s)' % rows[0][3]: c[3] = '%lu2%pr0'
            if o['h'] == 'SP_2BDEA3' and c[1] in (5, 11, 12): c[3] = '%lu2%pr1'
        out.append(o)
out = [x for x in out]
n2 = max(0, len(rows) - 46)
out.append({'t': 'theight', 'h': 'SPB' + GS.C['tag'], 'rows': [[r, 800] for r in range(n2, n2 + 5)]})

out += [{'t': 'evalf'}, {'t': 'save'}]
print([l for l in gx.run(out, 'fspec').splitlines() if 'ERR' in l or 'done' in l])
