import gx, re
vals=['+7,100','+10,250','+13,400','+16,550','+19,700']
# column: (x0, y_m4650, src6 handle,src6 y, src6 val, src7 handle, src7 y, bad handles)
cols=[(2552031,477980,'27952F',474830,'+22,400','280E8B',493280,['286644','286645','286646','286647'],1),
      (2569477,477980,'279617',474830,'+22,400','280E8C',493280,['286648','286649','28664A','28664B','28664C'],0),
      (2493722,479982,'27C05D',476832,'+22,400','280E8D',495282,['28664D','28664E','28664F','286650','286651'],0)]
ops=[];plan=[]
for x,y71,s6,y6,_,s7,y7,bad,skip in cols:
    for i,v in enumerate(vals):
        if i<skip: continue
        yy=y71+3150*i
        src,ys,old=(s6,y6,'+3,950') if len(v)==6 else (s7,y7,'+22,400')
        ops.append({'t':'clone','h':src,'base':[x,ys],'to':[x,yy]}); plan.append((old,v))
    ops.append({'t':'erase','h':bad})
o=gx.run(ops,'lv1'); print(o)
hs=re.findall(r'clone \w+>(\w+)',o)
ops2=[{'t':'levelval','h':h,'old':a,'value':b} for h,(a,b) in zip(hs,plan)]
print(gx.run(ops2,'lv2'))
