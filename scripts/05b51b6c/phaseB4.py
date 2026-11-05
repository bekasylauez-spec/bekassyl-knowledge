import ab,os
O=[]
# 3.1 section 3-3 opalubka
g31='355A2D 355A2E 355A2F 355A30 355A31 355A32 355A33 355A34 355A35 355A37 355A38 355A39 355A3A'.split()
O.append({'t':'clonexf','hs':g31,'d':[9000,0],'pre':'s31_'})
O.append({'t':'move','h':['s31_355A34'],'d':[300,0]})
ax=-1077314.969+9000+300; yb=-1737084.861; xl=-1078014.969+9000; xr=-1076014.969+9000
O.append({'t':'dimpts','h':'s31_355A37','p1':[ax,yb],'p2':[xl,yb]})
O.append({'t':'dimpts','h':'s31_355A38','p1':[ax,-1736884.861],'p2':[xr,yb]})
O.append({'t':'settext','h':'s31_355A35','s':'{\LРазрез 3 - 3 (Опалубка)}'})
O.append({'t':'clonexf','hs':['357D3A'],'d':[12000,6000],'pre':'m31_'})
O.append({'t':'mcset','h':'m31_357D3A','set':{'Word':'3'}})
# 3.5 section 4-4 armirovanie (levels omitted)
g35='37FB04 37FB05 37FB06 37FB09 37FB0A 37FB0B 37FB0C 37FB0D 37FB0E 37FB16 37FB17 37FB18 37FB19 37FB28 37FB29 37FB2B 37FB36 37FB37 37FB38'.split()
O.append({'t':'clonexf','hs':g35,'d':[0,-26000],'pre':'s35_'})
O.append({'t':'move','h':['s35_37FB0A'],'d':[750,0]})
ax=-742357.505+750; yb=-1717039.167-26000; xl=-744107.505; xr=-739107.505
O.append({'t':'dimpts','h':'s35_37FB0B','p1':[ax,yb],'p2':[xl,yb]})
O.append({'t':'dimpts','h':'s35_37FB0C','p1':[ax,-1716539.167-26000],'p2':[xr,yb]})
O.append({'t':'settext','h':'s35_37FB38','s':'{\LРазрез 4 - 4 (Армирования)}'})
ab.run(O,'B4'); L=open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read(); print(L[-700:])
