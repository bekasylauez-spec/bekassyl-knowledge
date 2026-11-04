# horizontal lines (bars) in the rigel elevation per sheet, relative to axis A
import re, sys, pickle
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\rg\\'
dump = open(D + 'rig_dump.txt', encoding='utf-8').read()
rows = pickle.load(open(D + 'rigrows.pkl', 'rb'))
for s in re.split(r'\n==== SHEET ', dump)[1:]:
    hdr, body = s.split('\n', 1); sn = hdr.split()[0]
    if sn not in sys.argv[1:]: continue
    fr = [int(v) for v in re.search(r'\[([-\d, ]+)\]', hdr).group(1).split(',')]
    axes = {a[5]: (int(a[1]) + int(a[3])) // 2 for a in re.findall(r'^X (\w+) \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([1-9АБВ])\s*$', body, re.M)}
    A = axes.get('А', axes.get('8'))
    print('\n##', sn, 'axes', {k: v - A for k, v in axes.items()}, 'A=', A)
    seg = []
    for h, t, x0, y0, x1, y1, txt, lay in rows:
        if x1 < fr[0] or x0 > fr[2] or y0 < 373000 or y1 > 376500: continue
        if t in ('LINE', 'LWPOLYLINE') and y1 - y0 < 5 and x1 - x0 > 300:
            seg.append((round(x0 - A), round(x1 - A), round(y0), t, h, round(x1 - x0)))
    for g in sorted(seg): print('  ', g)
