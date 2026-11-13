import fitz,sys
d=fitz.open('km.pdf')
def z(pg,x0,y0,x1,y1,name,dpi=400):
    d[pg-1].get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(name)
z(4,120,440,290,515,'z4_nv1.png')
# q4_2 origin x offset = 0.48*842=404.2 ; M2/Kc1 px (490-600,540-650)/2.639
ox=0.48*842
z(4,ox+170,185,ox+240,260,'z4_m2.png')
z(4,ox+235,275,ox+300,320,'z4_s22.png')
