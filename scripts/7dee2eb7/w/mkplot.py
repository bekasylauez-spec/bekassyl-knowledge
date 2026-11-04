import sys
# mkplot.py out.scr out.pdf x0 y0 x1 y1 [paper]
scr,pdf,x0,y0,x1,y1=sys.argv[1:7]
paper=sys.argv[7] if len(sys.argv)>7 else "ISO без полей A0 (841.00 x 1189.00 мм)"
w=float(x1)-float(x0); h=float(y1)-float(y0); ori='_L' if w>=h else '_P'
L=["FILEDIA 0","_.TILEMODE 1","_-PLOT","_Y","Model","DWG To PDF.pc3",paper,"_M",ori,"_N","_W",f"{x0},{y0}",f"{x1},{y1}","_F","_C","_Y","monochrome.ctb","_Y","_A",pdf,"_N","_Y","_.QUIT","_Y"]
open(scr,'w',encoding='cp1251').write("\n".join(L)+"\n")
