import ab,json
sh=json.load(open('w/sheets.json'))
order=['2.1','2.2','2.3','3.1','3.2','3.3','3.4','3.5','3.6','3.7','4.1','4.2','4.3','5.1']+['6.%d'%i for i in range(1,14)]+['7.1','7.2','8.1']
def media(w,h,sc):
    pw,ph=round(w/sc),round(h/sc)
    return 'ISO_full_bleed_%s_(%d.00_x_%d.00_MM)'%({(841,594):'A1',(594,841):'A1',(594,420):'A2',(420,594):'A2',(420,297):'A3',(297,420):'A3'}[(pw,ph)],pw,ph)
SC={'3.7':25,'5.1':25,'8.1':25}
for n in order:
    if n.startswith('4.') or n.startswith('6.'): SC[n]=50
ops=[]; info=[]
for n in order:
    x0,y0,x1,y1=sh[n]; sc=SC.get(n,100)
    md=media(x1-x0,y1-y0,sc)
    ops.append({'t':'laycopy','src':'0','dst':'КЖ-'+n})
    ops.append({'t':'vpset2','layout':'КЖ-'+n,'media':md,'win':[x0,y0,x1,y1],'scale':sc})
    info.append((n,md,sc))
ops.append({'t':'save'})
print(ab.run(ops,'lay',1200)[-600:])
json.dump(order,open('w/order.json','w'))
for i in info: print(i)
