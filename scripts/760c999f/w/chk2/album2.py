# Block 2 album from layout plots (pL2_*), TOC = sheet numbers (register is OLE)
import fitz, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
C = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk2'
A = r'D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\КЖ Чертеж  БЦ Байтурсынова Блок 2.pdf'
order = ['ved', 'sch', 'fnd', 'col', 'wal', 'rig', 'p71']
out = fitz.open(); toc = []
for k in order:
    J = json.load(open(os.path.join(C, 'pL2_' + k, 'plotc.json'), encoding='utf-8-sig')); src = fitz.open(os.path.join(C, 'pL2_' + k, 'all.pdf'))
    assert len(J) == src.page_count, (k, len(J), src.page_count)
    for i, j in enumerate(J):
        out.insert_pdf(src, from_page=i, to_page=i); toc.append([1, j['n'], out.page_count])
out.set_toc(toc)
out.save(A + '.tmp', garbage=3, deflate=True); out.close(); os.replace(A + '.tmp', A)
d = fitz.open(A); print('album2', d.page_count, 'MB', round(os.path.getsize(A) / 1e6, 1), [t for l, t, p in d.get_toc()][:6], '...', [t for l, t, p in d.get_toc()][-3:])
