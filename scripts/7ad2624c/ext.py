import fitz,sys
d=fitz.open(sys.argv[1])
out=open("text.txt","w",encoding="utf-8")
for i,p in enumerate(d):
    r=p.rect
    out.write(f"\n=== PAGE {i+1} size {r.width/72*25.4:.0f}x{r.height/72*25.4:.0f}mm ===\n")
    out.write(p.get_text())
    pix=p.get_pixmap(dpi=150)
    pix.save(f"pg/p{i+1:02d}.png")
print(len(d))
