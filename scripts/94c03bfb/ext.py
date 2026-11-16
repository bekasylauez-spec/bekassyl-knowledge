import fitz,sys
p,out=sys.argv[1],sys.argv[2]
d=fitz.open(p)
with open(out,'w',encoding='utf-8') as f:
    for i,pg in enumerate(d,1):
        f.write(f"\n=== PAGE {i} ({pg.rect.width:.0f}x{pg.rect.height:.0f}) ===\n")
        for b in sorted(pg.get_text("blocks"),key=lambda b:(round(b[0]/200),b[1])):
            f.write(f"[{b[0]:.0f},{b[1]:.0f}] {b[4].strip()}\n")
print(len(d))
