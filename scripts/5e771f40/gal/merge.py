import fitz, os, glob
d = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e771f40-144d-493e-a1c3-679c0085cfb9\scratchpad\gal\w\pdf3'
fs = sorted(glob.glob(os.path.join(d, '6.*.pdf')), key=lambda f: int(os.path.basename(f)[2:-4]))
out = fitz.open(); toc = []
for f in fs:
    toc.append([1, os.path.basename(f)[:-4], len(out) + 1]); out.insert_pdf(fitz.open(f))
out.set_toc(toc); dst = r'D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 3\6.Ригель Блок 3.pdf'
out.save(dst); print(len(fs), 'pages ->', dst)
