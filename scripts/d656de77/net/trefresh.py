# set input cells, then rewrite every formula of the table (as read back) in one op top->bottom, verify
import gx, os, sys
def read(h):
    gx.run([dict(t='tform', h=h)], 'tr')
    L = [l.split('\t') for l in open(os.environ['TEMP'] + r'\gq_log.txt', encoding='utf-8-sig').read().splitlines() if l.startswith('F ')]
    return [(tuple(map(int, l[0][2:].split(','))), l[1], l[3]) for l in L]
def refresh(h, nums=()):
    F = read(h)
    if nums: gx.run([dict(t='tnum', h=h, cells=[list(n) for n in nums])], 'tn')
    cells = []
    for (r, c), f, v in sorted(F):
        fm = f.strip()
        if fm.startswith('(') and fm.endswith(')'): fm = fm[1:-1]
        fmt = '%lu2%pr0' if (c == 10 and '.' not in fm and '*' in fm or fm.isdigit()) else '%lu2%pr2'
        cells.append([r, c, fm, fmt])
    gx.run([dict(t='tformula', h=h, cells=cells)], 'trw')
    G = read(h)
    bad = [x for x in G if '#' in x[2]]
    return len(cells), bad, {k: v for k, f, v in G}
if __name__ == '__main__':
    pass
