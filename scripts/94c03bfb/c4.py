import fitz
b="D:/_claude_work/Kasymova/revit/_check/"
k=72/70
def crop(n,pg,r,name,dpi=220):
    d=fitz.open(b+n+".pdf"); p=d[pg-1]
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(*[v*k for v in r])).save(b+"dc/z_"+name+".png")
crop("sec7",7,(480,70,700,140),"77_top")
crop("sec7",7,(900,95,1010,160),"77_rtop")
crop("sec7",7,(900,620,1010,680),"77_rbot")
crop("sec7",8,(440,100,620,180),"78_top")
