import pymupdf,sys
d=pymupdf.open(r'R:\От Шерхан\Завод\Том 14 Водоподготовка ВП-В113\КМ Чертеж\227-23-П-УВПиОС-ВП-В113-КМ (Блок 1 стилі).pdf')
n,x0,y0,x1,y1,name,dpi=int(sys.argv[1]),*map(float,sys.argv[2:6]),sys.argv[6],int(sys.argv[7])
d[n-1].get_pixmap(dpi=dpi,clip=pymupdf.Rect(x0,y0,x1,y1)).save('r/'+name)
