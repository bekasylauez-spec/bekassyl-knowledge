# per rigel sheet: level marks, axes, long dims, spec pog.m formulas
import re, collections
D = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\rg\\'
dump = open(D + 'rig_dump.txt', encoding='utf-8').read()
tabs = open(D + 'rig.tables.txt', encoding='utf-8').read()
# table handle -> rows
T = {}
cur = None
for ln in tabs.splitlines():
    m = re.match(r'TABLE (\w+) pos \(([-\d.]+),([-\d.]+)', ln)
    if m: cur = m.group(1); T[cur] = {'x': float(m.group(2)), 'y': float(m.group(3)), 'rows': []}; continue
    m = re.match(r'  R(\d+) h=[\d.]+ \|(.*)', ln)
    if m and cur: T[cur]['rows'].append([c.strip() for c in m.group(2).split('|')])
sheets = re.split(r'\n==== SHEET ', dump)[1:]
for s in sheets:
    hdr, body = s.split('\n', 1)
    sn = hdr.split()[0]
    fr = [int(v) for v in re.search(r'\[([-\d, ]+)\]', hdr).group(1).split(',')]
    title = re.findall(r'^M \w+ .*?\\L(Ригель Рм-\d+.*)$', body, re.M)
    levels = re.findall(r'^X (\w+) \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([+-]\d+[.,]\d{3})\s*$', body, re.M)
    axes = re.findall(r'^X \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([1-9АБВГД])\s*$', body, re.M)
    dims = re.findall(r'^D (\w+) \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (\d+) txt=\'(.*)\'$', body, re.M)
    big = sorted({int(d[5]) for d in dims if int(d[5]) >= 2500 and d[6] == ''})
    # axis chain: dims between consecutive axes ~ 3000..7000 with no txt
    print('\n##', sn, title[0] if title else '?')
    print('  levels:', [(l[5], int(l[1]), int(l[2])) for l in levels])
    print('  axes:', ' '.join(a[4] for a in sorted(axes, key=lambda a: int(a[0]))))
    print('  dims>=2500 (no override):', big)
    spans = sorted(d for d in dims if d[6] == '' and 2500 <= int(d[5]) <= 8000)
    # overall = largest
    # spec table inside frame
    for h, t in T.items():
        if fr[0] <= t['x'] <= fr[2] and fr[1] <= t['y'] <= fr[3] and t['rows'] and any('Рм-' in c for c in t['rows'][0]):
            print('  SPEC', h, t['rows'][0][2], 'total', t['rows'][0][-2])
            for r in t['rows'][1:]:
                if len(r) < 13 or not r[0]: continue
                if 'пог' in r[9] or r[0] in ('1', '2', '3', '4', '5', '6') or r[0].startswith('Н'):
                    print('    ', r[0], 'd' + r[3], r[5], r[9], 'n=' + r[10], 'm=' + r[12])
