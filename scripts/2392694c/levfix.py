# level marks cloned from the scheme sections have a long leader: bring them to the analog proportions (p2 = p0-808, p1 = p0-2049)
import gx, os, re, sys
def fix(x):
    gx.run([{'t': 'list', 'win': [x, 455900, x + 59400, 498000]}], 'ls')
    lv = [l.split('\t')[2] for l in open(os.environ['TEMP'] + '/pl_log.txt', encoding='utf-8').read().splitlines() if '\tSPDSLEVELMARK\t' in l]
    for h in lv:
        o = gx.run([{'t': 'spmove', 'h': h}], 'sp'); l = [q for q in o.splitlines() if q.startswith('spmove')][0]
        p = [tuple(map(float, q.split(','))) for q in re.findall(r'\(([-\d.]+,[-\d.]+)\)', l)]
        if len(p) >= 3 and p[0][0] - p[2][0] > 1200:
            gx.run([{'t': 'spmove', 'h': h, 'items': [[2, p[0][0] - 808, p[0][1]], [1, p[0][0] - 2049, p[1][1]]]}], 'sp2')
            print('fixed', h)
    gx.run([{'t': 'save'}], 'sv')
if __name__ == '__main__':
    fix(float(sys.argv[1]))
