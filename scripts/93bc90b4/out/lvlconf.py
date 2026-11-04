import sys, os
SP=sys.argv[1]; mode=sys.argv[2]
L=['LOG|'+os.path.join(SP,'out','lvl_%s.log'%mode)]
L.append('OUT|'+os.path.join(SP,'out','KM_lvl_test.dwg') if mode=='test' else 'COPY|'+os.path.join(SP,'out','KM_live_copy3.dwg'))
X0=445993; S=150
def f(v): return '%.3f'%v
def X(mm): return X0+mm*S
def Y(mm): return mm*S
L.append('|'.join(['COPYGRP',f(X(43.0)),f(Y(131.9)),f(X(63.0)),f(Y(141.5)),'0','3400','5;1','+7.600=+11.000']))
for lv in (5.020,10.340):
    L.append('|'.join(['COPYGRP',f(X(26.0)),f(Y(550.5)),f(X(46.2)),f(Y(560.5)),'0',f((lv-14.490)*1000),'5;1','+14.490=+%.3f'%lv]))
L.append('|'.join(['RECLOUD',f(X(60.0)),f(Y(131.5)),f(X(495.0)),f(Y(176.0)),f(2.5*S),f(X(36.0)),f(Y(131.5)),f(X(495.0)),f(Y(176.0)),f(6*S),'0.4']))
p=os.path.join(SP,'out','lvlconf_test.txt') if mode=='test' else os.path.join(os.environ['TEMP'],'kmfix_conf.txt')
open(p,'w',encoding='utf-8').write('\n'.join(L)+'\n'); print(p); print('\n'.join(L))
