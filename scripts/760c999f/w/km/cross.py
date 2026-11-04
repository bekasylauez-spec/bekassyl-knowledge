import pickle,sys,collections
rows=pickle.load(open('rows.pkl','rb'))
X0,X1,Y0,Y1,cut=map(float,sys.argv[1:6])
above=collections.Counter(); 
for h,t,x0,y0,x1,y1,txt,l in rows:
    if x0>=X0 and x1<=X1 and y0>=Y0 and y1<=Y1:
        if y0>cut: above[t]+=1
        elif y1>cut: print('X',h,t,round(x0),round(y0),round(x1),round(y1),repr(txt[:30]),l)
print('above',above)
