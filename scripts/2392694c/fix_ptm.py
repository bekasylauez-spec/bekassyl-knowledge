import gx, os, json, re
os.environ['SLAB'] = 'pm4'
import gen_parapet as GP
m = gx.tagmap()
ops = []
# 1) titles of the cloned sections (outside the group windows): clone them with the same shift as their group
def shift(tagp, h_ref, lst):
    for l in open(os.path.join(gx.S, 'w', lst), encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if len(r) > 5 and r[2] == h_ref: return r
for tagp, ref, title, lst in (('PV1_', '317C95', '317C92', 'v1.txt'), ('PV2_', '318DE1', '318E07', 'v2.txt'), ('PV3_', '31ABE0', '31ABE5', 'v3.txt')):
    r = shift(tagp, ref, lst)
    o = gx.run([{'t': 'spmove', 'h': m[tagp + ref]}], 'sp'); l = [q for q in o.splitlines() if q.startswith('spmove')][0]
    p_new = [tuple(map(float, q.split(','))) for q in re.findall(r'\(([-\d.]+,[-\d.]+)\)', l)][0]
    o = gx.run([{'t': 'spmove', 'h': ref}], 'sp'); l = [q for q in o.splitlines() if q.startswith('spmove')][0]
    p_old = [tuple(map(float, q.split(','))) for q in re.findall(r'\(([-\d.]+,[-\d.]+)\)', l)][0]
    if title not in [k[len(tagp):] for k in m if k.startswith(tagp)]:
        ops.append({'t': 'clone', 'h': title, 'base': [p_old[0], p_old[1]], 'to': [p_new[0], p_new[1]], 'tag': tagp + title})
# 2) section note of 7.33: bar position 42
ops.append({'t': 'noteh', 'h': 'PV1_317D10', 'l1': '42', 'l2': 'ш.200'})
# 3) section marks 1-1 over the left parapet (analog mark 318DDE) on 7.33/7.34/7.35
for k in (33, 34, 35):
    tg = 'PSM%d' % k
    ops += [{'t': 'clone', 'h': '318DDE', 'tag': tg},
            {'t': 'spmove', 'h': tg, 'items': [[0] + GP.P(k, 1200, 9000)[:2], [1] + GP.P(k, -1200, 9000)[:2]]}]
# 4) 7.36 tables: inside the frame + our quantities (ratio of parapet length 82.7 / 72.7 m, analog formulas kept)
x0 = GP.slot(36)
tab = ['PT_' + h for h in GP.G['v3tab']]
ops.append({'t': 'movegrp', 'h': [m[t] for t in tab if t in m], 'd': [1800, 0]})
A = m['PT_31AA9D']
ops.append({'t': 'tformula', 'h': A, 'cells': [[1, 10, '(1323.2*1.05)', '%lu2%pr1'], [2, 10, '(413)', '%lu2%pr0'], [3, 10, '(80)', '%lu2%pr0'],
                                               [4, 10, '(206*4)', '%lu2%pr0'], [6, 12, '(16.54*1.5)', '%lu2%pr2']]})
ops.append({'t': 'tformula', 'h': m['PT_31AA46'], 'cells': [[6, 1, '(Table({T:%s}).Evaluate(Sum(M5:M5)))' % A, '%lu2%pr2'],
                                                            [6, 4, '(Table({T:%s}).Evaluate(Sum(M2:M4)))' % A, '%lu2%pr2']]})
ops += [{'t': 'evalf'}, {'t': 'save'}]
print([l for l in gx.run(ops, 'fptm').splitlines() if 'ERR' in l or 'done' in l])
gx.run([{'t': 'tdump', 'h': A}, {'t': 'tdump', 'h': m['PT_31AA46']}], 'td')
print([l[:160] for l in open(os.environ['TEMP'] + '/pl_log.txt', encoding='utf-8').read().splitlines() if l.startswith('R0 ') or l.startswith('R6 h850')])
