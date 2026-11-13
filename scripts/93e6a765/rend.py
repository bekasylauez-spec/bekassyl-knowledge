import fitz,sys
p=r"D:\РАБОЧКА\От Маке\Қасымова\1 Касымова.pdf"
d=fitz.open(p)
for i in [1,4]+list(range(20,31)):
    pg=d[i]
    pm=pg.get_pixmap(matrix=fitz.Matrix(1.6,1.6))
    pm.save(f"pg/ar_{i+1:02d}.png")
g=fitz.open(r"D:\РАБОЧКА\От Маке\Қасымова\ОТЧЕТ геологии Касымова 25.pdf")
for i in list(range(8,15))+list(range(25,31)):
    pm=g[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5))
    pm.save(f"pg/geo_{i+1:02d}.png")
print("ok")
