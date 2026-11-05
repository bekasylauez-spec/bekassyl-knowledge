# check «Ведомость расхода стали» against the spec table: mass per Ø, class totals, grand total, headers
# usage: python wl/ved_check.py SP ST [SP ST ...]
import sys, os, re, collections; sys.path.insert(0, 'wl'); from common import *
def dump(h):
    gx.run([{'t': 'tdump', 'h': h}], 'td')
    rows = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        m = re.match(r'R(\d+) h\d+: \| (.*)', l)
        if m: rows.append([c.strip() for c in m.group(2).split(' | ')])
    return rows
def num(s):
    m = re.match(r'^\s*(-?[\d.]+)', s or '')
    return float(m.group(1)) if m else None
def check(SP, ST):
    T = dump(SP); S = dump(ST); bad = []
    by = collections.defaultdict(float); tot = 0; n = 0
    for r in T:
        if r and re.match(r'^(Шп|Х|Ск|\d)', r[0]):
            d = int(r[3]); L = num(r[9]); k = num(r[10]); m1 = num(r[11]); m = num(r[12])
            if None in (L, k, m1, m): bad.append('row %s: empty L/count/mass (%s)' % (r[0], r[9:13])); continue
            calc1 = d * d * 3.1415926 / 4 * 0.00785 * L / 1000
            if abs(calc1 - m1) > 0.006: bad.append('row %s: unit mass %.2f != %.2f' % (r[0], m1, calc1))
            if abs(m1 * k - m) > 0.02 * max(1, m) and abs(calc1 * k - m) > 0.05: bad.append('row %s: total %.2f != %.2f' % (r[0], m, calc1 * k))
            by[d] += m; tot += m; n += 1
    spec_total = num(T[1][12]) if len(T) > 1 else None
    if spec_total is None or abs(spec_total - tot) > 0.05: bad.append('spec total %s != Σ rows %.2f' % (spec_total, tot))
    hdr = S[5]; val = S[6]
    cols = {}
    for c, h in enumerate(hdr):
        m = re.search(r'%%C(\d+)', h)
        if m: cols[int(m.group(1))] = c
    for d, mass in by.items():
        if d not in cols: bad.append('Ø%d (%.2f kg) has no column' % (d, mass)); continue
        v = num(val[cols[d]])
        if v is None or abs(v - mass) > 0.05: bad.append('Ø%d: ведомость %s != spec %.2f' % (d, val[cols[d]], mass))
    for d, c in cols.items():
        if d not in by and num(val[c]) not in (0, None): bad.append('Ø%d column %s but no rows' % (d, val[c]))
    a240 = sum(m for d, m in by.items() if d < 10); a500 = sum(m for d, m in by.items() if d >= 10)
    it = [c for c, h in enumerate(hdr) if 'Итого' in h]
    if len(it) >= 2:
        v1, v2 = num(val[it[0]]), num(val[it[1]])
        if v1 is None or abs(v1 - a240) > 0.05: bad.append('Итого A240 %s != %.2f' % (val[it[0]], a240))
        if v2 is None or abs(v2 - a500) > 0.05: bad.append('Итого A500 %s != %.2f' % (val[it[1]], a500))
    vs = num(val[-1])
    if vs is None or abs(vs - tot) > 0.05: bad.append('Всего %s != %.2f' % (val[-1], tot))
    print(SP, ST, 'rows', n, 'total %.2f' % tot, {d: round(m, 2) for d, m in sorted(by.items())})
    for b in bad: print('  BAD', b)
    return bad
if __name__ == '__main__':
    a = sys.argv[1:]; allbad = 0
    for i in range(0, len(a), 2): allbad += len(check(a[i], a[i + 1]))
    print('TOTAL BAD', allbad)
