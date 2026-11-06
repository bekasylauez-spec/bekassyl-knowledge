# write a table's formulas top->bottom, left->right in one op; repeat until every listed cell reads back as a formula with a number
import gx, os
def fix(h, cells, tries=4):
    for k in range(tries):
        gx.run([dict(t='tformula', h=h, cells=cells), dict(t='tform', h=h)], 'tfx')
        L = [l.split('\t') for l in open(os.environ['TEMP'] + r'\rg_log.txt', encoding='utf-8-sig').read().splitlines() if l.startswith('F ')]
        got = {tuple(map(int, l[0][2:].split(','))): l[3] for l in L}
        bad = [c for c in cells if not c[2].startswith('TEXT:') and (tuple(c[:2]) not in got or '#' in got[tuple(c[:2])])]
        if not bad: return k + 1, got
        cells = sorted(cells, key=lambda c: (c[0], c[1]))
    return -1, got
