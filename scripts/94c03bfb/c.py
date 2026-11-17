import fitz
b="D:/_claude_work/Kasymova/revit/_check/"
def crop(n,pg,r,name,dpi=300):
    d=fitz.open(b+n+".pdf"); p=d[pg-1]
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(*r)).save(b+"dc/z_"+name+".png")
crop("sec4",4,(670,535,810,625),"44_sec22")
crop("sec4",3,(250,130,380,175),"43_c1")
crop("sec4",3,(670,535,810,625),"43_sec22")
crop("sec3",4,(170,140,270,240),"34_tl")
crop("sec3",4,(820,360,1000,560),"34_rc")
crop("sec3",4,(220,500,360,540),"34_m1")
