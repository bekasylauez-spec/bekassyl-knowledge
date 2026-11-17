import fitz,sys
b="D:/_claude_work/Kasymova/revit/_check/"
k=72/70
def crop(n,pg,r,name,dpi=200):
    d=fitz.open(b+n+".pdf"); p=d[pg-1]
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(*[v*k for v in r])).save(b+"dc/z_"+name+".png")
crop("sec7",6,(370,420,800,680),"76_mid")
crop("sec7",6,(530,770,1060,940),"76_tab")
crop("sec7",4,(370,500,560,600),"74_lead")
