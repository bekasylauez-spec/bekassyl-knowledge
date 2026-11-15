import fitz,sys
for src,out in [(r"D:\РАБОЧКА\От Рас груп\3602 NRG Maftun Makon - Порталы\Revit\КМ Портал Ташкент (Revit).pdf","rv"),(r"D:\РАБОЧКА\От Рас груп\3602 NRG Maftun Makon - Порталы\КМ Чертеж Портал Ташкент.pdf","dw")]:
    d=fitz.open(src)
    with open(out+"/text.txt","w",encoding="utf-8") as f:
        for i,p in enumerate(d):
            r=p.rect
            f.write(f"\n===== PAGE {i+1} size {r.width/72*25.4:.0f}x{r.height/72*25.4:.0f} mm rot {p.rotation}\n")
            f.write(p.get_text())
            pix=p.get_pixmap(dpi=100); pix.save(f"{out}/p{i+1:02d}.png")
    print(out,len(d))
