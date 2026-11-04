import fitz, re, sys
pdf = r'D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\КЖ Чертеж БЦ Байтурсынова Блок 1.pdf'
doc = fitz.open(pdf)
toc = doc.get_toc()
m = {}
for lvl, title, page in toc:
    t = title.split()[0]
    m[t] = page
print(len(toc), list(m.items())[:40])
for w in sys.argv[1:]:
    if w not in m: print(w, 'NOT IN TOC'); continue
    p = doc[m[w] - 1]
    pix = p.get_pixmap(dpi=130)
    pix.save(r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\rg\pg_%s.png' % w.replace('.', '_'))
    print(w, 'page', m[w], pix.width, pix.height)
