# import one analog sheet (all entities of its frame) into the main DWG at (SX, SY)
import sys, os; sys.path.insert(0, 'wl'); from common import *
SRC = {'st1': (r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Аналог\4.1.Стена См-1 ...См-5 Тип С.dwg', '4.1.Стена См-1 ...См-5 Тип С.dwg'),
       'st2': (r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Аналог\4.2.Стена См-6...См-8 Тип С1.dwg', '4.2.Стена См-6...См-8 Тип С1.dwg'),
       'st3': (r'D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Аналог\4.3.Стена См-9...См-11 Тип С1.dwg', '4.3.Стена См-9...См-11 Тип С1.dwg')}
def handles(k, fi):
    x0, y0, x1, y1 = F[k][fi][:4]
    gx.run([{'t': 'list', 'win': [x0 - 5, y0 - 5, x1 + 5, y1 + 5]}], 'lst', SRC[k][1])
    hs = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if l.startswith('L\t'):
            e = [float(v) for v in r[4][1:].split(',')]
            if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5: hs.append(r[2])
        elif l.startswith('N\t'): hs.append(r[2])
    return hs, (x0, y0)
def imp(k, fi, SX, SY, pre):
    hs, (x0, y0) = handles(k, fi)
    out = gx.run([dict(t='import', file=SRC[k][0], h=hs, base=[x0, y0], to=[SX, SY], pre=pre), dict(t='save')], 'imp')
    print(k, fi, len(hs), [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
if __name__ == '__main__':
    imp(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
