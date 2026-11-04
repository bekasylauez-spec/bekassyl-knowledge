# for each sheet: axes x, 200-zone dims, and entities overlapping each zone's x-range (candidates crossing a cut)
import re, sys, pickle
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\rg\\'
dump = open(D + 'rig_dump.txt', encoding='utf-8').read()
rows = pickle.load(open(D + 'rigrows.pkl', 'rb'))  # (h,type,x0,y0,x1,y1,txt,layer)
want = sys.argv[1:]
for s in re.split(r'\n==== SHEET ', dump)[1:]:
    hdr, body = s.split('\n', 1); sn = hdr.split()[0]
    if sn not in want: continue
    fr = [int(v) for v in re.search(r'\[([-\d, ]+)\]', hdr).group(1).split(',')]
    axes = re.findall(r'^X (\w+) \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([1-9АБВ])\s*$', body, re.M)
    print('\n##', sn, 'frame', fr, 'axes', [(a[5], (int(a[1]) + int(a[3])) // 2) for a in axes])
    zones = re.findall(r'^D (\w+) \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (\d+) txt=\'(200х\d+.*|100х\d+.*|\d+х\d+)\'$', body, re.M)
    for z in zones: print('  Z', z[0], z[6], 'bbox x', z[1], z[3], 'y', z[2], z[4])
    for z in zones:
        if not z[6].startswith('200х'): continue
        zx0, zx1 = int(z[1]) + 100, int(z[3]) - 100
        print('  200-zone', z[0], z[6], 'x', zx0, zx1)
        for r in rows:
            h, t, x0, y0, x1, y1, txt, lay = r
            if x1 < fr[0] or x0 > fr[2] or y0 < 371000 or y1 > 377050: continue
            if x1 <= zx0 or x0 >= zx1: continue
            if x1 - x0 > 5000 and t in ('LINE', 'LWPOLYLINE', 'POLYLINE', 'DIMENSION', 'HATCH'): continue
            if h == z[0]: continue
            print('     ', t, h, round(x0), round(x1), round(y0), round(y1), repr(txt)[:40])
