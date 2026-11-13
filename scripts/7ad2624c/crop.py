import fitz,sys
# crop.py page x0 y0 x1 y1 (mm) dpi out
d=fitz.open(r'D:/Бекасыл КЖ КМ/Завод_В113_КМ/227-23-П-УВПиОС-ВП-В113-КМ (Revit).pdf')
n,x0,y0,x1,y1,dpi,out=sys.argv[1:]
k=72/25.4
p=d[int(n)-1]
p.get_pixmap(dpi=int(dpi),clip=fitz.Rect(float(x0)*k,float(y0)*k,float(x1)*k,float(y1)*k)).save('v/'+out)
