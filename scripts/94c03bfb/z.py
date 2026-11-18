import fitz,sys
i=int(sys.argv[1]);x0,y0,x1,y1=map(float,sys.argv[2:6]);dpi=int(sys.argv[6]) if len(sys.argv)>6 else 300
p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{i}.pdf")[0]
p.get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(f"q/z.png")
