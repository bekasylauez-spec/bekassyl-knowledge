import pickle,sys
rows=pickle.load(open('rows.pkl','rb'))
X0,X1,cut=map(float,sys.argv[1:4]); lo=float(sys.argv[4]) if len(sys.argv)>4 else 400
for h,t,x0,y0,x1,y1,txt,l in sorted(rows,key=lambda r:(r[3],r[2])):
    if X0<=x0 and x1<=X1 and -1756151<y0 and y1<-1714151:
        if cut-lo<y0<=cut+250 or (y0<=cut-lo and y1>cut+50):
            print(h,t,round(x0),round(y0-cut),round(x1),round(y1-cut),repr(txt[:25]),l)
