import fitz, sys, re, json
# dump per-page: sheet number guess + full text (for diffing 4 vs 5 storey albums)
out = {}
for p in sys.argv[2:]:
    d = fitz.open(p)
    pages = []
    for i, pg in enumerate(d):
        t = pg.get_text()
        pages.append({"i": i + 1, "w": round(pg.rect.width), "h": round(pg.rect.height), "text": t})
    out[p] = pages
json.dump(out, open(sys.argv[1], "w", encoding="utf8"), ensure_ascii=False)
