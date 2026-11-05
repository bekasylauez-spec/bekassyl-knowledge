import ab,os
xl,xr=-1593896.88,-1591188.379
cx=-1592542.63; px0,px1=cx-350,cx+350
top,toe=-1729368.773,-1738868.773
y347,y1,y2,y3,ybot_old,ybot=-1728018.773,-1731218.773,-1733518.773,None,-1736924.516,-1739518.773
def R(x0,y0,x1,y1): return [[x0,y0,0],[x1,y0,0],[x1,y1,0],[x0,y1,0]]
pad=[[-1593635.456,-1729118.818,0],[-1591635.511,-1729118.818,0],[-1591635.511,-1729418.818,0],[-1593635.456,-1729418.818,0]]
prep=[[-1593735.701,-1729418.818,0],[-1593735.701,-1729518.773,0],[-1591535.211,-1729518.773,0],[-1591535.211,-1729418.818,0]]
O=[]
O.append({'t':'erase','h':['37E9FA','37EA0E','37EA0F','37EA10','37EA11','37EA12','37EA13','37EA14','37EA15','37EA16','37EA17','37EA18']})
# extend bottom layer
O.append({'t':'stretchwin','win':[-1594400,-1737400,-1590700,-1736600],'d':[0,ybot-ybot_old]})
O.append({'t':'hatchset','h':'37E9F1','loops':[R(xl,y347,xr,y1),R(px0,-1729518.773,px1,y1),pad,prep]})
O.append({'t':'hatchset','h':'37E9FF','loops':[R(xl,y1,xr,y2),R(px0,y1,px1,y2)]})
O.append({'t':'hatchset','h':'37E9F3','loops':[R(xl,y2,xr,ybot),R(px0,y2,px1,toe)]})
O.append({'t':'clone','h':'37EA12','tag':'pile'}) if False else None
O=[o for o in O if o]
O.append({'t':'pl','p':[[px0,top],[px1,top],[px1,toe],[px0,toe]],'closed':True,'layer':'Размеры','lw':30,'tag':'pile'})
O.append({'t':'dimpts','h':'37EA73','p1':[px1,top],'p2':[px1,toe]})
O.append({'t':'settext','h':'37EA19','s':'%%Uс буронабивной сваей Св1 %%C700'})
O.append({'t':'mcset','h':'37EA05','set':{'FirstLine':'Буронабивная свая','SecondLine':'Св1 ∅700, L=9500'}})
O.append({'t':'move','h':['37EA05'],'d':[372,0]})
O.append({'t':'move','h':['37E9F8'],'d':[0,toe-(-1735518.773)]})
ab.run(O,'C2'); print(open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read()[-600:])
