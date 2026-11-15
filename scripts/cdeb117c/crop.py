import fitz,sys
# args: which(rv/dw) page x0 y0 x1 y1 (fractions) out dpi
w,pg,x0,y0,x1,y1,out=sys.argv[1:8]; dpi=int(sys.argv[8]) if len(sys.argv)>8 else 190
src={"rv":r"D:\РАБОЧКА\От Рас груп\3602 NRG Maftun Makon - Порталы\Revit\КМ Портал Ташкент (Revit).pdf","dw":r"D:\РАБОЧКА\От Рас груп\3602 NRG Maftun Makon - Порталы\КМ Чертеж Портал Ташкент.pdf"}[w]
d=fitz.open(src); p=d[int(pg)-1]; r=p.rect
clip=fitz.Rect(r.width*float(x0),r.height*float(y0),r.width*float(x1),r.height*float(y1))
p.get_pixmap(dpi=dpi,clip=clip).save(out)
