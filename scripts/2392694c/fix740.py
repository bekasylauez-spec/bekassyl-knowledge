import gx
X0, X1 = 2417054, 2420154
def chain(y0, yl, tag):
    ops = []
    for p, q, t, tx in ((X0, X0 + 50, '', [X0 - 250, yl + 180]), (X0 + 50, X1 - 50, '200х15', [(X0 + X1) / 2, yl + 180]), (X1 - 50, X1, '', [X1 + 250, yl + 180])):
        ops.append({'t': 'dim', 'h': '33D191', 'p1': [p, y0, 0], 'p2': [q, y0, 0], 'dl': [p, yl, 0], 'rot': 0, 'txt': t, 'tx': tx + [0]})
    return ops
ops = chain(469064, 469400, 'T') + chain(461414, 460714, 'B')
ops.append({'t': 'erase', 'h': ['33D191', '33D1A0', '33D1AD', '33D1BA', '33D0E2', '33D0F1', '33D0FE', '33D10B']})
# wall chain 200 | 2700 | 200 further out
ops += [{'t': 'dimpts', 'h': '33CFB2', 'p1': [X0, 469064, 0], 'p2': [X0 + 200, 468864, 0], 'dl': [X0, 470050, 0]},
        {'t': 'dimpts', 'h': '33CFC8', 'p1': [X0 + 200, 468864, 0], 'p2': [X1 - 200, 468864, 0], 'dl': [X0 + 200, 470050, 0]},
        {'t': 'dimpts', 'h': '33CFDE', 'p1': [X1 - 200, 468864, 0], 'p2': [X1, 469064, 0], 'dl': [X1 - 200, 470050, 0]}]
# notes 2 ш.200 on the two long walls: apart vertically; level text lower
ops += [{'t': 'spmove', 'h': '33D11A', 'items': [[0, 2418154, 467150], [1, 2417208, 467150]]},
        {'t': 'spmove', 'h': '33D155', 'items': [[0, 2419054, 465700], [1, 2420000, 465700]]},
        {'t': 'move', 'h': ['33CFF5'], 'd': [0, -1300]},
        {'t': 'axis', 'h': '3390BC', 'val': '3'}]
for s in (2280879, 2322879, 2364879):
    ops.append({'t': 'trepl', 'win': [s, 455900, s + 42000, 485700], 'pairs': [['КЖ-7.37 ... 7.39', 'КЖ-7.37 ... 7.41']]})
ops.append({'t': 'save'})
o = gx.run(ops, 'f740'); print('\n'.join(l for l in o.splitlines() if 'ERR' in l or 'trepl' in l or 'spmove' in l))
