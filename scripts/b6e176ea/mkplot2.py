import json
S=r"C:\Users\Admin\AppData\Local\Temp\claude\D---------\b6e176ea-26b4-4762-a290-80708f71b8b2\scratchpad"
F={1:(2313717,-1724313,2373117,-1682276),2:(2373117,-1724304,2395392,-1692776),3:(2395392,-1724304,2426892,-1702001),
4:(2426892,-1724304,2458392,-1702001),5:(2458392,-1724304,2489892,-1702001),6:(2489892,-1724304,2521392,-1702001),
7:(2521392,-1724294,2542392,-1709426),8:(2542392,-1724294,2563392,-1709426),9:(2563392,-1724295,2593092,-1703276),
10:(2593092,-1724285,2607942,-1713776)}
import sys
F.update(json.loads(sys.argv[1]) if len(sys.argv)>1 else {})
lines=['(setvar "FILEDIA" 0)','(setvar "OSMODE" 0)','(setvar "BACKGROUNDPLOT" 0)']
for i,(x1,y1,x2,y2) in sorted(F.items(),key=lambda p:int(p[0])):
    i=int(i); w=x2-x1;h=y2-y1; port=h>w
    paper='ISO без полей A3 (420.00 x 297.00 мм)' if max(w,h)/min(w,h)>1.3 else 'ISO без полей A3 (420.00 x 297.00 мм)'
    lines+=['_-PLOT','_Y','Model','DWG To PDF.pc3',paper,'_M','_P' if port else '_L','_N','_W',f'{x1-200:.0f},{y1-200:.0f}',f'{x2+200:.0f},{y2+200:.0f}','_F','_C','_Y','monochrome.ctb','_Y','_A','"'+S+chr(92)+'pl'+chr(92)+'t%02d.pdf"'%i,'_N','_Y']
lines+=['_.QUIT','_Y','']
open("pl/plot2.scr","w",encoding="cp1251",newline="").write("\r\n".join(lines))
json.dump(F,open("w/frames.json","w"))
