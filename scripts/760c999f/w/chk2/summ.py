# per sheet summary from <file>_dump.txt: stamp title, levels, axes, big dims (no override)
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk2\\'
for f in sys.argv[1:]:
    dump = open(D + f + '_dump.txt', encoding='utf-8').read()
    print('\n######', f)
    for s in re.split(r'\n==== SHEET ', dump)[1:]:
        hdr, body = s.split('\n', 1); sn = hdr.split()[0]
        fr = [int(v) for v in re.search(r'\[([-\d, ]+)\]', hdr).group(1).split(',')]
        # stamp title: MTEXT in the bottom 2500 of the frame, right half, not the sheet number
        titles = [m for m in re.finditer(r'^M \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (.*)$', body, re.M)
                  if int(m.group(2)) < fr[1] + 2500 and int(m.group(1)) > fr[0] + (fr[2] - fr[0]) * 0.6 and not re.fullmatch(r'\d+\.\d+', m.group(5).strip())]
        title = titles[-1].group(5)[:90] if titles else '?'
        levels = re.findall(r'^X \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([+-]\d+[.,]\d{3})\s*$', body, re.M)
        axes = re.findall(r'^X \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([1-9]|1[0-2]|[А-Д])\s*$', body, re.M)
        dims = re.findall(r'^D \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (\d+) txt=\'(.*)\'$', body, re.M)
        big = sorted({int(d[4]) for d in dims if int(d[4]) >= 2500 and d[5] == ''})
        ov = sorted({d[5] for d in dims if d[5] and not re.match(r'(100|200|150)х', d[5]) and d[5] != '<>'})
        lv = sorted({l[4].replace(',', '.') for l in levels})
        ax = ''.join(sorted({a[4] for a in axes}, key=lambda v: (v.isdigit(), int(v) if v.isdigit() else v)))
        print('%-5s %-70s lv %-45s ax %-14s big %s %s' % (sn, title, ','.join(lv), ax, big[:14], ('ov ' + ','.join(ov)[:60]) if ov else ''))

