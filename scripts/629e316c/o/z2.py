import fitz
d=fitz.open('km.pdf')
def z(pg,x0,y0,x1,y1,name,dpi=400):
    d[pg-1].get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(name)
z(5,570,590,650,640,'z5_kc.png')
