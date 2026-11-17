import fitz
b="D:/_claude_work/Kasymova/revit/_check/"
k=72/70
def crop(n,pg,r,name,dpi=220):
    d=fitz.open(b+n+".pdf"); p=d[pg-1]
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(*[v*k for v in r])).save(b+"dc/z_"+name+".png")
crop("sec7",16,(500,120,780,260),"716_lead")
crop("sec7",10,(1290,1090,1630,1145),"710_stamp")
crop("sec7",15,(130,80,330,290),"715_dims")
crop("sec7",4,(370,500,560,600),"74_lead")
