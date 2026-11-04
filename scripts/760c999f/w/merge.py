# crop plotted pages to frame size (centred on the full-bleed sheet) and merge into all.pdf
import fitz, json, sys, os
d = sys.argv[1]
J = json.load(open(os.path.join(d, "plotc.json"), encoding="utf-8"))
mm = 72 / 25.4
out = fitz.open()
for j in J:
    src = fitz.open(j["out"])
    R = src[0].rect
    cw, ch = j["w"] * mm, j["h"] * mm
    x0, y0 = (R.width - cw) / 2, (R.height - ch) / 2
    p = out.new_page(width=cw, height=ch)
    p.show_pdf_page(p.rect, src, 0, clip=fitz.Rect(x0, y0, x0 + cw, y0 + ch))
out.save(os.path.join(d, "all.pdf"))
print("pages", len(out))
