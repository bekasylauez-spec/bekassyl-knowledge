import axes,sys
s=sys.argv[1]; X,Y,H,V=axes.axes(s)
for l in open('w/notes.txt',encoding='utf-8'):
    p=l.rstrip('\n').split('\t')
    if p[0]!='N' or '�' in l: continue
    ex=[q for q in p if q.startswith('E')]
    a=[float(v) for v in ex[-1][1:].split(',')]
    cx,cy=(a[0]+a[2])/2,(a[1]+a[3])/2
    if axes.SH[s][0]<=cx<=axes.SH[s][2] and axes.SH[s][1]<=cy<=axes.SH[s][3]:
        pts=[q for q in p[9:] if ',' in q and not q.startswith('E')]
        print(p[1],repr(p[3]),repr(p[4]),'rel',[ (round(float(q.split(',')[0])-X[0]),round(float(q.split(',')[1])-Y[0])) for q in pts])
