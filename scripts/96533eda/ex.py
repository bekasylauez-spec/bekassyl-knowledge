import fitz,sys
p=sys.argv[1]; out=sys.argv[2]; tag=sys.argv[3]
d=fitz.open(p)
with open(out+f"/{tag}_text.txt","w",encoding="utf-8") as f:
    for i,pg in enumerate(d):
        f.write(f"\n===== PAGE {i+1} size {pg.rect.width:.0f}x{pg.rect.height:.0f}\n"); f.write(pg.get_text())
        if tag=="v": pg.get_pixmap(dpi=150).save(out+f"/{tag}_{i+1:02d}.png")
print(len(d))
