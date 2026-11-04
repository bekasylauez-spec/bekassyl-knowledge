import sys, os, pickle
SP=sys.argv[1]; out=sys.argv[2]
R=pickle.load(open(os.path.join(SP,'out','mrows.pkl'),'rb'))
L=['LOG|'+os.path.join(SP,'out','fix.log'),'OUT|'+out]
def f(v): return '%.3f'%v
X0=1050766.5; S=220
def X(mm): return X0+mm*S
def Y(mm): return mm*S
cols=sorted(set(round(r[9][0],3) for r in R if r[1]=='LINE' and r[7]=='DXK_LINE_DOT3' and abs(r[9][0]-r[9][2])<1e-6 and X0<r[9][0]<X0+841*S))
assert len(cols)==28, len(cols)
C=';'.join(f(c) for c in cols)
E=75485.320; H=87485.320
SE=72869.81; SH=85819.81
# E row: runway copy above E, PB texts shifted, KN callouts up-left
L.append('|'.join(['MIRROR',f(X(65)),f(E-750-0.1*S),f(X(812.9)),f(E+0.5*S),'H',f(E),f(1.45*S),f(Y(340.3)),f(Y(343.6))]))
L.append('|'.join(['SHIFT',f(X(65)),f(Y(340.3)),f(X(812.9)),f(Y(343.6)),'0','1500','ПБ']))
L.append('|'.join(['LABEL',f(X(65)),f(Y(325.5)),f(X(818.5)),f(Y(341.0)),f(E),f(SE),f(Y(351.0)),f(0.1*S)]))
# H row
L.append('|'.join(['MIRROR',f(X(65)),f(H-0.5*S),f(X(812.9)),f(Y(410)),'H',f(H),f(1.45*S),f(Y(401.7)),f(Y(405.0))]))
L.append('|'.join(['SHIFT',f(X(65)),f(Y(401.7)),f(X(812.9)),f(Y(405.0)),'0','-1500','ПБ']))
L.append('|'.join(['LABEL',f(X(65)),f(Y(386.9)),f(X(818.5)),f(H+2.5*S),f(H),f(SH),f(2*H-SH),f(0.1*S)]))
# dims 750 at x=823 (templates: old 750 text of E row, old tick of E row)
for c in (E,H):
    L.append('|'.join(['DIM',f(X(823)),f(1.56*S),f(X(809.5)),f(1.1*S),f(X(814.4))+';'+f(Y(344.24))+';'+f(3*S),f(X(814.75))+';'+f(Y(338.93))+';'+f(0.3*S),';'.join(f(v) for v in (c-750,c,c+750)),'1']))
for ya,yb,ta,tb in [(338.5,350.5,343.5,350.0),(396.5,409.0,401.5,409.0)]:
    L.append('|'.join(['ERASE',f(X(813.2)),f(Y(ya)),f(X(816.6)),f(Y(yb)),'LINES']))
    L.append('|'.join(['ERASE',f(X(809)),f(Y(ta)),f(X(817)),f(Y(tb)),'TEXT:750']))
    L.append('|'.join(['ERASE',f(X(809.5)),f(Y(ta-0.6)),f(X(815.5)),f(Y(tb+0.6)),'WIPEOUT>'+f(4*S)]))
# sheet 4 sections
X0=445993; S=150
def X(mm): return X0+mm*S
def Y(mm): return mm*S
for c,xa,xb,ya,yb in [(236.02,211,236.02-0.05,135,160),(316.02,316.02+0.05,341,135,160),(231.37,206.4,231.37-0.05,315,345),(311.37,311.37+0.05,336.4,315,345)]:
    L.append('|'.join(['MIRROR',f(X(xa)),f(Y(ya)),f(X(xb)),f(Y(yb)),'V',f(X(c)),f(0.05*S)]))
X0=164910; S=100
T=[(165,345,'9,7','14,6'),(260,345,'9,7','14,6'),(165,297,'9,7','14,6'),(259,297,'148,1','153,0'),(165,249,'9,7','14,6'),(259,249,'433,1','438,0'),
   (165,118,'20,1','30,2'),(260,118,'20,1','30,2'),(166,110,'1,3','2,0'),(260,110,'39,0','39,7'),(165,102,'23,6','35,4'),(260,102,'23,6','35,4'),
   (165,78,'45,0','67,6'),(259,78,'89,6','112,2'),(165,30,'45,0','67,6'),(259,30,'141,4','164,0'),
   (415,362,'54,7','82,2'),(509,362,'749,0','776,5'),(415,344,'54,7','82,2'),(509,344,'412,2','439,7')]
for x,y,o,n in T: L.append('|'.join(['TEXT',f(X0+x*S),f(y*S),'120',o,n,'C']))
open(os.path.join(SP,'out','fixconf.txt'),'w',encoding='utf-8').write('\n'.join(L)+'\n'); print(len(L))
