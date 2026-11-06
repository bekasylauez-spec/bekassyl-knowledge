import sys; sys.path.insert(0,r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\663b9254-0821-4243-aa62-da5f6760d929\scratchpad\net')
import gx
gx.run([{'t':'listfile','file':r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\663b9254-0821-4243-aa62-da5f6760d929\scratchpad\dxf\sch3.dwg','win':[217000,-1796000,302000,-1735000]}],'lf')
L=[l.split('\t') for l in gx.log().splitlines() if l[:2]=='L\t']
keep=[]
for r in L:
    x0,y0,x1,y1=map(float,r[4][1:].split(','))
    w,h=round(x1-x0),round(y1-y0)
    if r[1]=='LWPOLYLINE' and r[3]=='Размеры':
        if (w,h) in ((600,600),(700,700),(800,1200)): keep.append(r[2])
        continue
    if r[2] in ('5B9666','5BBFA8'): continue
    keep.append(r[2])
print(len(keep))
print(gx.run([{'t':'import','file':r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\663b9254-0821-4243-aa62-da5f6760d929\scratchpad\dxf\sch3.dwg','h':keep,'base':[217417,-1795185],'to':[180617,271898],'pre':'SCH:'},{'t':'save'}],'impsch')[-300:])
