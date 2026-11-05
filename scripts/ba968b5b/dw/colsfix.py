import json, km2_sec as K, cols, ab, sys
SH=json.load(open('w/sheets2.json'))
def run(s):
    ops=[]; n=0
    for i,row,x,y in cols.nodes(s):
        if cols.kind(i,row)!=2 or row=='Б': continue
        sg=1 if row=='А' else -1
        own=[]
        for e in K.listwin([x-350,y-550,x+350,y+550]):
            if e['lay']!='0' or e['t'] not in ('LWPOLYLINE','HATCH'): continue
            a=e['e']
            if abs(a[0]-(x-200))<2 and abs(a[2]-(x+200))<2 and abs(a[1]-(y-400))<2 and abs(a[3]-(y+400))<2: own.append(e['h'])   # rect, hatch
            elif abs(a[0]-x)<2 and abs(a[2]-x)<2 and abs(a[1]-(y-500))<2: own.append(e['h'])   # vertical centre line
            elif abs(a[1]-y)<2 and abs(a[3]-y)<2 and abs(a[0]-(x-300))<2: own.append(e['h'])   # horizontal centre line
        if len(own)!=4: print('WARN',s,i,row,own)
        ops.append({'t':'movegrp','h':own,'d':[0,sg*200]})
        for yy in (y-400,y+400):
            for yb in (yy-20, yy+20) if False else (yy,):
                ops.append({'t':'stretchwin','win':[x-290,yb-35,x+290,yb+35],'d':[0,sg*200],'only':['DIMENSION','LWPOLYLINE:Ригель','LWPOLYLINE:Размеры']})
        n+=1
    print(s,n, ab.run(ops+[{'t':'save'}],'fix'+s,900)[-60:])
for s in sys.argv[1:]: run(s)
