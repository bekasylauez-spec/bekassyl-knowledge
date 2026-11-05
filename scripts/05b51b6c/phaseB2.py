import axes,ab,os
O=[]
def win(s,p=50): a,b,c,d=axes.SH[s]; return [a-p,b-p,c+p,d+p]
O.append({'t':'mcrep','win':win('3.3'),'pairs':[['(ф12)','(ф16)'],['(ф14)','(ф16)']]})
O.append({'t':'mcrep','win':win('2.5'),'pairs':[['Фм-2','Фм-1']]})
# 3.2
X,Y,_,_=axes.axes('3.2'); x1,yA=X[0],Y[0]; yB=Y[1]
# fix A bars mirrored (+275,+75,-125 -> -275,-75,+125)
for h,y in (('35C536',-275),('35C537',125),('35C538',-75)):
    O.append({'t':'plset','h':h,'p':[[x1-960,yA+y],[x1+61000,yA+y]]})
Anotes=['35D822','35D823','35D824','35D825','35D826','35D827','35D828','35D829','35D82A']
O.append({'t':'move','h':Anotes,'d':[0,-150]})
for i,dy in enumerate((-200,0,200)):
    O.append({'t':'clone','h':'35C536','tag':'b32_%d'%i})
    O.append({'t':'plset','h':'b32_%d'%i,'p':[[x1-275,yB+dy],[x1+60275,yB+dy]]})
for k in range(10):
    O.append({'t':'clonexf','hs':['35D822'],'d':[3000+6000*k-5978-22, 6000-75],'pre':'n32_%d_'%k})
# 3.3
X,Y,_,_=axes.axes('3.3'); x1,yA=X[0],Y[0]
for k in range(1,10):
    for i,dx in enumerate((-200,0,200)):
        tg='b33_%d_%d'%(k,i)
        O.append({'t':'clone','h':'363327','tag':tg})
        O.append({'t':'plset','h':tg,'p':[[x1+6000*k+dx,yA-275],[x1+6000*k+dx,yA+12275]]})
    O.append({'t':'clonexf','hs':['3636C1'],'d':[6000*k-60075,0],'pre':'n33_%d_'%k})
O.append({'t':'save'})
ab.run(O,'B2'); L=open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read(); print(L[:600]); print(L[-300:])
