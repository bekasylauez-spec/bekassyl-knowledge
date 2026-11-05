# Generic specification update for a wall (analog spec table kept: input cells only, mass formulas kept, steel summary formulas by Ø)
# usage: python wl/wall_spec.py cfg_sm2 [--run]
import sys, os, json, re, collections, importlib; sys.path.insert(0, 'wl'); from common import *
CFG = importlib.import_module(sys.argv[1]).SPEC
SP, ST = CFG['SP'], CFG['ST']
GOST = {8: '214-210-0101-0002', 10: '214-210-0501-0005', 12: '214-210-0502-0001', 14: '214-210-0502-0002', 16: '214-210-0502-0003',
        18: '214-210-0502-0004', 20: '214-210-0502-0005', 22: '214-210-0502-0006', 25: '214-210-0502-0007', 28: '214-210-0502-0008'}
def dump(h):
    gx.run([{'t': 'tdump', 'h': h}], 'td')
    rows = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        m = re.match(r'R(\d+) h\d+: \| (.*)', l)
        if m: rows.append([c.strip() for c in m.group(2).split(' | ')])
    return rows
T = dump(SP)
body = [i for i, r in enumerate(T) if r and re.match(r'^(Шп|Х|Ск|\d)', r[0])]
b0, b1 = body[0], body[-1] + 1
keep = [] if CFG.get('HOOPS') else [i for i in body if re.match(r'^(Шп|Х)', T[i][0])]   # hoops / pins: analog rows kept, or given
c = collections.defaultdict(int); dl = {}
for f in CFG['JSONS']:
    for b in json.load(open(f, encoding='utf-8'))['BARS']: c[str(b['pos'])] += b['n']; dl[str(b['pos'])] = (b['d'], b['L'])
rows = [(p, d, L, n) for p, d, L, n in CFG.get('HOOPS', [])]
for k in sorted([k for k in c if k.startswith('Ск')], key=lambda k: int(k[2:])): rows.append((k + '*', dl[k][0], dl[k][1], c[k]))
for k in sorted([k for k in c if not k.startswith('Ск')], key=int): rows.append((k, dl[k][0], dl[k][1], c[k]))
need = len(keep) + len(rows); have = b1 - b0
ops = []
first = b0 + len(keep)                                                # our rows start after the kept hoop rows (they are first in the analog)
if need < have: ops.append(dict(t='trows', h=SP, mode='del', at=b0 + need, n=have - need))
if need > have: ops.append(dict(t='trows', h=SP, mode='ins', at=b1, **{'from': b1 - 1}, n=need - have))
cells = []
for j, (p, d, L, n) in enumerate(rows):
    r = first + j
    cells += [[r, 0, p], [r, 1, 'ГОСТ 34028-2016 (%s)' % GOST[d]], [r, 3, str(d)], [r, 5, '240' if d < 10 else '500С'], [r, 9, str(L)]]
ops.append(dict(t='tset', h=SP, cells=cells))
last = b0 + need
fm = []
for j in range(len(rows)):
    r = first + j
    fm += [[r, 10, str(rows[j][3])], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (r + 1, r + 1, r + 1)], [r, 12, 'L%d*K%d' % (r + 1, r + 1)]]
for i in keep:                                                     # kept rows lose their formulas when neighbours change: restore
    fm += [[i, 10, T[i][10].split('{')[0]], [i, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (i + 1, i + 1, i + 1)], [i, 12, 'L%d*K%d' % (i + 1, i + 1)]]
fm.append([CFG['TOTAL_ROW'], 12, 'Sum(M%d:M%d)' % (b0 + 1, last)])
fm.append([last + CFG['CONC_OFF'], 12, '%.4f' % CFG['CONC']])
ops.append(dict(t='tformula', h=SP, cells=fm))
ops.append(dict(t='theight', h=SP, rows=[[last, 739], [last + 1, 739]] + ([[last + 2, 739]] if CFG['CONC_OFF'] > 1 else [])))
# steel summary
S = dump(ST)
hdr = S[5]; ncol = len(hdr)
dset = sorted({d for (_, d, _, _) in rows} | set(CFG.get('HOOP_D', [])) | {int(T[i][3]) for i in keep})
a500 = [d for d in dset if d >= 10]
c0 = 4; slots = ncol - 2 - c0                                         # A500 Ø columns between «Итого A240» and «Итого», «Всего»
if len(a500) > slots: ops.append(dict(t='tcols', h=ST, mode='ins', at=c0 + slots, **{'from': c0 + slots - 1}, n=len(a500) - slots)); slots = len(a500)
cols = {d: c0 + i for i, d in enumerate(a500)}
hc = [[5, c0 + i, '%%%%C%d' % d] for i, d in enumerate(a500)] + [[5, c0 + i, '-'] for i in range(len(a500), slots)]
ops.append(dict(t='tset', h=ST, cells=hc))
byd = collections.defaultdict(list)
for i in keep: byd[int(T[i][3])].append(i + 1)
for j, row in enumerate(rows): byd[row[1]].append(first + j + 1)
ev = lambda lst: '+'.join('Table({T:%s}).Evaluate(Sum(M%d:M%d))' % (SP, a, a) for a in lst) if lst else '0'
sf = [[6, 1, '0'], [6, 2, ev(byd[8])], [6, 3, 'C7']]
for d, cc in cols.items(): sf.append([6, cc, ev(byd[d])])
for i in range(len(a500), slots): sf.append([6, c0 + i, '0'])
it = c0 + slots
sf += [[6, it, 'Sum(%s7:%s7)' % (chr(65 + c0), chr(65 + c0 + slots - 1))], [6, it + 1, '%s7+D7' % chr(65 + it)]]
ops.append(dict(t='tformula', h=ST, cells=sf))
ops.append(dict(t='save'))
print('body', b0, b1, 'keep', [T[i][0] for i in keep], 'rows', len(rows), 'need', need, 'have', have, 'A500', a500)
for r in rows: print(r)
if '--run' in sys.argv:
    out = gx.run(ops, 'wspec'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
