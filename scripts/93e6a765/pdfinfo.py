import fitz,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
for p in [r"D:\РАБОЧКА\От Маке\Қасымова\1 Касымова.pdf", r"D:\РАБОЧКА\От Маке\Қасымова\ОТЧЕТ геологии Касымова 25.pdf"]:
    d=fitz.open(p)
    print("=====",p,len(d))
    for i,pg in enumerate(d):
        t=pg.get_text().strip()
        print(f"--- p{i+1} {pg.rect.width:.0f}x{pg.rect.height:.0f} textlen={len(t)} imgs={len(pg.get_images())}")
        print(t[:300].replace("\n"," | "))
