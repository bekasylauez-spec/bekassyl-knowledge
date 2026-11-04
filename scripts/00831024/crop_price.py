import fitz, glob, os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'price')
f = [x for x in glob.glob(r'D:\РАБОЧКА\*\Проект\Ақтау\Прайс на 2026.pdf')][0]
d = fitz.open(f)
crops = {'c1': (0, 590, 785), 'c2': (1, 55, 90), 'c3': (2, 205, 372), 'c4': (3, 625, 790)}
for k, (pg, y0, y1) in crops.items():
    d[pg].get_pixmap(dpi=200, clip=fitz.Rect(40, y0, 530, y1)).save(os.path.join(out, k + '.png'))
print('ok', d.page_count)
