# import analog «6.1 Ригель» pieces into the rigel DWG
import sys, os, gx
SRC = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\9a1000cd-e0d9-42b2-b432-f6f3db0e7099\scratchpad\gal\an\a61.dwg'
LST = os.path.join(gx.S, 'an', 'list61.txt')
def handles(x0, y0, x1, y1, excl=()):
    hs = []
    for l in open(LST, encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if l.startswith('L\t'):
            e = [float(v) for v in r[4][1:].split(',')]
            if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5 and r[2] not in excl: hs.append(r[2])
        elif l.startswith('N\t'):
            x, y = map(float, r[4].split(','))
            if x0 <= x <= x1 and y0 <= y <= y1 and r[2] not in excl: hs.append(r[2])
    return hs
def imp(win, base, to, pre, excl=()):
    hs = handles(*win, excl=excl)
    out = gx.run([dict(t='import', file=SRC, h=hs, base=base, to=to, pre=pre)], 'imp')
    print(len(hs), [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:4])
    return hs
if __name__ == '__main__':
    a = sys.argv
    imp([float(v) for v in a[1:5]], [float(a[5]), float(a[6])], [float(a[7]), float(a[8])], a[9])
