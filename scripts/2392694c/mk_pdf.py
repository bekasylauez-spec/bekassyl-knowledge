# python mk_pdf.py <k0> <k1> "<file name.pdf>"  — sheets 7.k0..7.k1 from the frames (A2/A3 by size)
import os, sys, json, shutil, fitz, gx
sys.path.insert(0, os.path.join(gx.S, 'an')); import plt
k0, k1, name = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
fr = json.load(open(os.path.join(gx.S, 'chk', 'sheets.json'), encoding='utf-8'))
gx.run([{'t': 'save'}], 'sv')
SNAP = os.path.join(gx.S, 'w', 'snap.dwg')
shutil.copy('D:/РАБОЧКА/От Алмас аға/ЖК Галакси/Кж чертеж/2.Схема каркас для клауда (плиты).dwg', SNAP)
out = fitz.open()
for k in range(k0, k1 + 1):
    x0, y0, x1, y1 = fr['7.%d' % k]; w, h = x1 - x0, y1 - y0
    big = max(w, h)
    paper = 'ISO без полей A2 (594.00 x 420.00 мм)' if big > 50000 else 'ISO без полей A3 (420.00 x 297.00 мм)'
    pdf = plt.plot(SNAP, 'pg%d' % k, x0, y0, x1, y1, paper=paper, orient='_L' if w > h else '_P')
    out.insert_pdf(fitz.open(pdf))
dst = 'D:/РАБОЧКА/От Алмас аға/ЖК Галакси/Кж чертеж/' + name
out.save(dst); print(dst, len(out))
