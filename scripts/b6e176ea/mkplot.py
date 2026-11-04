import ezdxf,json,sys
from ezdxf import bbox
S=r"C:\Users\Admin\AppData\Local\Temp\claude\D---------\b6e176ea-26b4-4762-a290-80708f71b8b2\scratchpad"
d=ezdxf.readfile("w/cur.dxf"); m=d.modelspace()
st=[e for e in m.query("INSERT") if e.dxf.name=="крпкер"]
L=[]
for e in st:
    b=bbox.extents([e],fast=True); sc=e.dxf.xscale*100
    L.append((b.extmin.x,b,sc,e.dxf.handle))
L.sort()
lines=['(setvar "FILEDIA" 0)','(setvar "OSMODE" 0)','(setvar "BACKGROUNDPLOT" 0)']
sheets=[]
for i,(x,b,sc,h) in enumerate(L,1):
    x2=b.extmax.x+8*sc; y1=b.extmin.y-8*sc; x1=x2-430*sc; y2=y1+307*sc
    sheets.append([i,h,sc,x1,y1,x2,y2])
    lines+=['_-PLOT','_Y','Model','DWG To PDF.pc3','ISO без полей A3 (420.00 x 297.00 мм)','_M','_L','_N','_W',f'{x1:.0f},{y1:.0f}',f'{x2:.0f},{y2:.0f}','_F','_C','_Y','monochrome.ctb','_Y','_A',f'"{S}\pl\s{i:02d}.pdf"','_N','_Y']
lines+=['_.QUIT','_Y','']
open("pl/plot.scr","w",encoding="cp1251",newline="").write("\r\n".join(lines))
json.dump(sheets,open("w/sheets.json","w"))
for s in sheets: print(s[0],s[1],s[2],[round(v) for v in s[3:]])
