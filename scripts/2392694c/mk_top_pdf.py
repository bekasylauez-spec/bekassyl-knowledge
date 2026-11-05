import os, sys, shutil, fitz, gx
sys.path.insert(0, os.path.join(gx.S, 'an')); import plt
gx.run([{'t': 'save'}], 'sv')
SNAP = os.path.join(gx.S, 'w', 'snap.dwg')
shutil.copy('D:/РАБОЧКА/От Алмас аға/ЖК Галакси/Кж чертеж/2.Схема каркас для клауда (плиты).dwg', SNAP)
Y0 = 455939
sh = [(2280879, 42000, 29700, 'A3'), (2322879, 42000, 29700, 'A3'), (2364879, 42000, 29700, 'A3'), (2406879, 42000, 29700, 'A3'), (2448879, 59400, 42000, 'A2')]
P = {'A3': 'ISO без полей A3 (420.00 x 297.00 мм)', 'A2': 'ISO без полей A2 (594.00 x 420.00 мм)'}
out = fitz.open()
for i, (x, w, h, f) in enumerate(sh):
    pdf = plt.plot(SNAP, 'top%d' % i, x, Y0, x + w, Y0 + h, paper=P[f], orient='_L')
    d = fitz.open(pdf); p = d[0]; print(i, p.rect, p.rotation)
    out.insert_pdf(d)
    d[0].get_pixmap(dpi=110).save(os.path.join(gx.S, 'w', 'top%d.png' % i))
dst = 'D:/РАБОЧКА/От Алмас аға/ЖК Галакси/Кж чертеж/Плита Пм-5, Пм-6, парапет ПтМ-2 листы 7.37-7.41.pdf'
out.save(dst); print(dst, len(out))
