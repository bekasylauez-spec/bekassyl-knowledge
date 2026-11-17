import fitz
b="D:/_claude_work/Kasymova/revit/_check/"
def crop(n,pg,r,name,dpi=250):
    d=fitz.open(b+n+".pdf"); p=d[pg-1]
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(*r)).save(b+"dc/z_"+name+".png")
k=72/70
crop("sec7",1,(430*k,280*k,620*k,440*k),"71_open")
crop("sec7",1,(870*k,350*k,940*k,440*k),"71_open3")
crop("sec7",2,(360*k,400*k,560*k,600*k),"72_leaders")
