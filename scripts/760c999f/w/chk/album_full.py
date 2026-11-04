# build the Block 1 album from per-file PDFs (folder prefix in argv[1], e.g. pL_), TOC from the 1.1 register
import fitz, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
C = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk'
D = r'D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый'
pre = sys.argv[1] if len(sys.argv) > 1 else 'pL_'
order = ['g11', 'g12', 'sch', 'fnd', 'vyp', 'col', 'wal', 'rig', 'p71', 'p72', 'st8', 'rmp']
reg = {}
for ln in open(os.path.join(C, 'g11_fx.tables.txt'), encoding='utf-8'):
    m = re.match(r'  R\d+ h=[\d.]+ \| (\d+\.\d+) \| (.*?) \|', ln)
    if m: reg[m.group(1)] = re.sub(r'\s+', ' ', m.group(2)).strip()
out = fitz.open(); toc = []; nums = []
for k in order:
    folder = os.path.join(C, pre + k)
    J = json.load(open(os.path.join(folder, 'plotc.json'), encoding='utf-8-sig')); src = fitz.open(os.path.join(folder, 'all.pdf'))
    assert len(J) == src.page_count, (k, len(J), src.page_count)
    for i, j in enumerate(J):
        out.insert_pdf(src, from_page=i, to_page=i); n = j['n']; nums.append(n)
        toc.append([1, n + ' ' + reg.get(n, '?'), out.page_count])
print('pages', out.page_count, 'missing in reg', [n for n in nums if n not in reg], 'reg not plotted', [n for n in reg if n not in nums])
out.set_toc(toc)
A = os.path.join(D, 'КЖ Чертеж БЦ Байтурсынова Блок 1.pdf')
out.save(A + '.tmp', garbage=3, deflate=True); out.close(); os.replace(A + '.tmp', A)
d = fitz.open(A); print('album', d.page_count, 'MB', round(os.path.getsize(A) / 1e6, 1))
sizes = {}
for p in d: sizes[(round(p.rect.width / 72 * 25.4), round(p.rect.height / 72 * 25.4))] = sizes.get((round(p.rect.width / 72 * 25.4), round(p.rect.height / 72 * 25.4)), 0) + 1
print('page sizes mm:', sizes)
