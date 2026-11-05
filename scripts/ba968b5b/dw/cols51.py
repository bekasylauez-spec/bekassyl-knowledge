import json, km2_sec as K, cols, ab, re, sys
SH=json.load(open('w/sheets2.json'))
def run(s, XA, AY, walls=True):
    X0,Y0,X1,Y1=SH[s]
    ents={}
    for e in K.listwin([X0,Y0,X1,Y1]):
        a=e['e']
        if e['t']=='INSERT' and abs((a[2]-a[0])-900)<5 and abs((a[3]-a[1])-900)<5:
            ents[(round((a[0]+a[2])/2),round((a[1]+a[3])/2))]=e['h']
    ops=[]; n=0
    for k_,row in enumerate('АБВ'):
        for i in range(1,12):
            x=X0+XA+6000*(i-1); y=Y0+AY+6000*k_
            k=cols.kind(i,row)
            if k==1: continue
            h=[v for (cx,cy),v in ents.items() if abs(cx-x)<30 and abs(cy-y)<30]
            if not h: continue
            if row=='Б': y0,y1=y-750,y+750
            elif row=='А': y0,y1=y-200,y+600
            else: y0,y1=y-600,y+200
            yc=(y0+y1)/2
            rect=[[x-200,y0],[x+200,y0],[x+200,y1],[x-200,y1]]
            ops+=[{'t':'erase','h':h},{'t':'pl','p':rect,'closed':True,'layer':'0','lw':30},
                  {'t':'hatch','pat':'ANSI36','sc':25,'layer':'0','loops':[rect]},
                  {'t':'pl','p':[[x,y0-100],[x,y1+100]],'layer':'0','ltype':'CENTER2','color':12,'ltscale':1},
                  {'t':'pl','p':[[x-300,yc],[x+300,yc]],'layer':'0','ltype':'CENTER2','color':12,'ltscale':1}]
            # бет өзгерген жақтар: размерлер
            for yo,yn in ((y-200,y0),(y+200,y1)):
                if abs(yo-yn)>1:
                    ops.append({'t':'stretchwin','win':[x-215,yo-15,x+215,yo+15],'d':[0,yn-yo],'only':['DIMENSION']})
            n+=1
    if walls:
        y=Y0+AY
        for ax,(xa,xb) in ((X0+XA,(-215,65)),(X0+XA+60000,(-65,215))):
            for yo,yn in ((200,600),(5800,5250),(6200,6750),(11800,11400),(11600,11400)):
                ops.append({'t':'stretchwin','win':[ax+xa,y+yo-15,ax+xb,y+yo+15],'d':[0,yn-yo],'only':['LWPOLYLINE:О_Формат']})
    o=ab.run(ops+[{'t':'save'}],'c'+s,900); print(s,n,o[-60:])
if __name__=='__main__':
    run('5.1',11506,16391)
