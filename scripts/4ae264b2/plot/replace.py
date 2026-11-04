import fitz, os, shutil
S = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый"
album = os.path.join(ROOT, "КЖ Чертеж БЦ Байтурсынова Блок 1.pdf")
single = os.path.join(ROOT, "Блок 1", "ПДФ", "7.2 Плита на отм +13,400;+17,600;+21,500 БЦ Байтурсынова Блок1.pdf")
new = fitz.open(os.path.join(S, "all.pdf"))
assert new.page_count == 18

bk = os.path.join(S, "backup"); os.makedirs(bk, exist_ok=True)
shutil.copy2(album, bk); shutil.copy2(single, bk)

# single-file PDF: keep its TOC titles
old1 = fitz.open(single); toc1 = old1.get_toc(); old1.close()
out1 = fitz.open(); out1.insert_pdf(new); out1.set_toc(toc1)
out1.save(single + ".tmp", garbage=3, deflate=True); out1.close()
os.replace(single + ".tmp", single)

# album: pages 101..118 (1-based) -> new
a = fitz.open(album); toc = a.get_toc(); n = a.page_count
out = fitz.open()
out.insert_pdf(a, from_page=0, to_page=99)
out.insert_pdf(new)
out.insert_pdf(a, from_page=118, to_page=n - 1)
a.close()
assert out.page_count == n, out.page_count
out.set_toc(toc)
out.save(album + ".tmp", garbage=3, deflate=True); out.close()
os.replace(album + ".tmp", album)

chk = fitz.open(album)
bad = [i + 1 for i, p in enumerate(chk) if "Формат" not in p.get_text()]
print("album pages", chk.page_count, "toc", len(chk.get_toc()), "pages without 'Формат':", bad)
s = fitz.open(single); print("7.2 pdf pages", s.page_count, "toc", len(s.get_toc()), [i + 1 for i, p in enumerate(s) if "Формат" not in p.get_text()])
