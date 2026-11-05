import axes,ab,os
s='1.3'; X,Y,_,_=axes.axes(s); x1,yA=X[0],Y[0]
dj=[e.h for e in axes.E() if axes.ins(e,s) and e.lay=='BASE-DJ']
d650=[e.h for e in axes.E() if axes.ins(e,s) and e.dxf=='DIMENSION' and e.kv.get('meas')=='650']
print(len(dj),len(d650))
O=[{'t':'erase','h':dj+d650}]
for i in range(11):
    for j in range(3):
        cx,cy=x1+6000*i,yA+6000*j
        O.append({'t':'circle','c':[cx,cy],'r':350,'layer':'BASE-DJ'})
        O.append({'t':'pl','p':[[cx-150,cy],[cx+150,cy]],'layer':'BASE-DJ'})
        O.append({'t':'pl','p':[[cx,cy-150],[cx,cy+150]],'layer':'BASE-DJ'})
X2,Y2,_,_=axes.axes('2.1')
O.append({'t':'clonexf','hs':['346A11'],'d':[x1-X2[0]-250,yA-Y2[0]-250],'pre':'sv_'})
O.append({'t':'mcset','h':'sv_346A11','set':{'FirstLine':'Св1','SecondLine':'∅700'}})
O.append({'t':'txtrep','win':[-1743353,-1749222,-1552753,-1707122],'pairs':[['забивной свая','буронабивных свай'],['забивной сваи','буронабивных свай'],['забивных свай','буронабивных свай']]})
O.append({'t':'save'})
ab.run(O,'C1'); print(open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read()[-300:])
