import fitz
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
pg = d[20]
mm = 25.4/72
dr = pg.get_drawings()
print(len(dr))
# find vertical long lines in facade region x 190..330pt, y 380..800pt
xs = {}
for p in dr:
    for it in p["items"]:
        if it[0]=="l":
            a,b = it[1],it[2]
            if abs(a.x-b.x)<0.2 and abs(a.y-b.y)>120 and 150<a.x<340:
                xs.setdefault(round(a.x,1), []).append((round(min(a.y,b.y),0), round(max(a.y,b.y),0), p.get("width")))
for k in sorted(xs): print(k, round(k*mm,1), xs[k][:3])
