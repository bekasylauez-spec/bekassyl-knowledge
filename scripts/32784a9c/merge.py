import fitz, glob, os, sys, re
src, out = sys.argv[1], sys.argv[2]
mm = 72/25.4
doc = fitz.open(); toc = []
for f in sorted(glob.glob(os.path.join(src, '*.pdf'))):
    s = fitz.open(f); p = s[0]
    lay = re.sub(r'^\d+_', '', os.path.splitext(os.path.basename(f))[0])
    Wm, Hm = p.rect.width/mm, p.rect.height/mm
    R = fitz.Rect((Wm-125)*mm, (Hm-25)*mm, (Wm-55)*mm, (Hm-5)*mm) * ~p.rotation_matrix
    name = ' '.join(p.get_textbox(R).split())
    name = re.sub(r'^Лестница\s+', '', name)
    doc.insert_pdf(s)
    toc.append([1, f'Лист {lay} — {name}', doc.page_count])
doc.set_toc(toc)
doc.set_metadata({'title': 'КМ Чертеж БЦ', 'creator': 'AutoCAD 2021 (Layout plot)'})
doc.save(out, garbage=3, deflate=True)
print(doc.page_count, 'pages'); [print(t) for t in toc]
