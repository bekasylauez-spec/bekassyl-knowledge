import fitz
b="D:/_claude_work/Kasymova/revit/_check/"
k=72/70
def crop(n,pg,r,name,dpi=220):
    d=fitz.open(b+n+".pdf"); p=d[pg-1]
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(*[v*k for v in r])).save(b+"dc/z_"+name+".png")
crop("sec7",5,(860,370,1010,690),"75_right")
crop("sec7",5,(200,60,1010,110),"75_top")
crop("sec7",13,(900,70,1010,140),"713_rtop")
