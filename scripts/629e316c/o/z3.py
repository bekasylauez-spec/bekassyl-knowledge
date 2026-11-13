import fitz
d=fitz.open('km.pdf')
def z(pg,x0,y0,x1,y1,name,dpi=500):
    d[pg-1].get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(name)
z(7,690,285,840,335,'z7_t8.png')
z(7,130,600,230,630,'z7_50.png')
z(7,435,365,535,390,'z7_75.png')
