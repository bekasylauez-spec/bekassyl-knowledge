import fitz
d=fitz.open(r"D:\РАБОЧКА\От Маке\Қасымова\ОТЧЕТ геологии Касымова 25.pdf")
import sys
s=sys.argv[1]
for n,rot in ((24,90),(23,90)):
    p=d[n-1]; 
    pm=p.get_pixmap(dpi=170,matrix=fitz.Matrix(170/72,170/72).prerotate(0))
    pm.save(f"{s}\\r{n}.png")
