# replace page ranges of the Block 1 album with freshly plotted PDFs; keep/patch TOC
import fitz, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
A = r'D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\КЖ Чертеж БЦ Байтурсынова Блок 1.pdf'
C = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk'
jobs = [('g11', '1.1', '1.4'), ('sch', '2.1', '2.10'), ('col', '4.1', '4.14'), ('rig', '6.1', '6.17'), ('p72', '7.25', '7.42'), ('st8', '8.1', '8.5'), ('rmp', '9.1', '9.3')]
newtitles = {'7.41': 'Парапет ПтМ-1 на отм. +17.600. Узел сопряжения, спецификация', '9.1': 'Схема расположения и опалубочный чертеж рампы',
             '2.6': 'Схема расположения элементов на отм. +17.600 и +21.500', '8.2': 'Разрезы 1 - 1...4 - 4'}
doc = fitz.open(A); toc = doc.get_toc(); n0 = doc.page_count
pg = {t.split()[0]: p for l, t, p in toc}
# process from the back so earlier page numbers stay valid
for k, a, b in sorted(jobs, key=lambda j: -pg[j[1]]):
    pa, pb = pg[a], pg[b]
    new = fitz.open(os.path.join(C, 'pf_' + k, 'all.pdf'))
    assert new.page_count == pb - pa + 1, (k, new.page_count, pa, pb)
    doc.delete_pages(pa - 1, pb - 1); doc.insert_pdf(new, start_at=pa - 1)
    print(k, 'pages', pa, pb, 'replaced')
t2 = []
for l, t, p in toc:
    n = t.split()[0]
    if n in newtitles: t = n + ' ' + newtitles[n]
    t2.append([l, t, p])
doc.set_toc(t2)
for l, t, p in t2:
    n = t.split()[0]; txt = doc[p - 1].get_text()
    if not re.search(r'\n' + re.escape(n) + r'\n', txt) and p > 6: print('WARN stamp', n, p)
assert doc.page_count == n0
doc.save(A + '.tmp', garbage=3, deflate=True); doc.close(); os.replace(A + '.tmp', A)
print('album ok', n0)
