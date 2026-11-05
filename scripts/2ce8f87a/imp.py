# import one analog sheet (by frame window) into the slab DWG: python imp.py 51|52 x0 y0 x1 y1 SX SY pre
import sys, os, gx
A = 'D:/РАБОЧКА/От Алмас аға/ЖК Галакси/Аналог'
SRC = {'51': os.path.normpath(os.path.join(A, '5.1 Плита  Тип C1 отм. -0.100.dwg')),
       '52': os.path.normpath(os.path.join(A, '5.2 Плита  Тип C1  отм+3,050,+21,500.dwg'))}
LST = {'51': os.path.join(gx.S, 'an', 'list_5.1.txt'), '52': os.path.join(gx.S, 'an', 'list_5.2.txt')}


def imp(k, x0, y0, x1, y1, SX, SY, pre, save=True):
    hs = []
    for l in open(LST[k], encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if l.startswith('L\t'):
            e = [float(v) for v in r[4][1:].split(',')]
            if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5: hs.append(r[2])
        elif l.startswith('N\t'):
            x, y = map(float, r[4].split(','))
            if x0 <= x <= x1 and y0 <= y <= y1: hs.append(r[2])
    ops = [dict(t='import', file=SRC[k], h=hs, base=[x0, y0], to=[SX, SY], pre=pre)]
    if save: ops.append(dict(t='save'))
    out = gx.run(ops, 'imp')
    print(k, len(hs), [l for l in out.splitlines() if 'import' in l or 'ERR' in l or 'saved' in l][:4])


if __name__ == '__main__':
    a = sys.argv
    imp(a[1], *map(float, a[2:8]), a[8])
