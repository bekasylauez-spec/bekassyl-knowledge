import sys, os
SP=sys.argv[1]; mode=sys.argv[2]  # test | live
src=os.path.join(SP,'tx','tx3.dwg')
L=['LOG|'+os.path.join(SP,'out','lower_%s.log'%mode)]
if mode=='test': L.append('OUT|'+os.path.join(SP,'out','KM_low_test.dwg'))
else: L.append('COPY|'+os.path.join(SP,'out','KM_live_copy2.dwg'))
def f(v): return '%.3f'%v
X0=445993; S=150
def X(mm): return X0+mm*S
def Y(mm): return mm*S
for cm in (76.02,236.02,316.02,476.02):
    L.append('|'.join(['LOWER',f(X(cm-15)),f(Y(135)),f(X(cm+15)),f(Y(166)),f(X(cm)),'-893','190','300','23010','23220']))
for cm in (71.37,231.37,311.37,471.37):
    L.append('|'.join(['LOWER',f(X(cm-15)),f(Y(315)),f(X(cm+15)),f(Y(352)),f(X(cm)),'-893','190','300','50540','50750']))
dx=457396-146791; dy=24109-(-123075)
exL='STELL WELDMENT;中心线;АР-Размеры;6文字层;91文本;TEXT;标题12'
for rl,rr in ((147291,170291),(171291,182291),(183291,206291)):
    L.append('|'.join(['CRANEMOVE',src,str(rl-450),'-124450',str(rr+450),'-122000',str(rl),str(rr),'-123075',str(dx),str(dy),exL,'41','-893']))
L.append('|'.join(['MOVEY',f(X(55)),f(X(480)),'51638.2','50745.2','0.5']))
L.append('|'.join(['MOVET',f(X(20)),f(Y(343.4)),f(X(70)),f(Y(358)),'0','-893','*','+11.893=+11.000']))
# sheet 1 crane note
L.append('|'.join(['SETTXT',f(96600+219.74*100),f(323.25*100),'60','- рельс Р24','- рельс Р24, верх подкрановой балки на отм. +11,000.']))
p=os.path.join(SP,'out','lowconf_%s.txt'%mode) if mode=='test' else os.path.join(os.environ['TEMP'],'kmfix_conf.txt')
open(p,'w',encoding='utf-8').write('\n'.join(L)+'\n'); print(p); print('\n'.join(L[:3]))
