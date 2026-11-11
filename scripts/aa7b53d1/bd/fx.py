s=open('bfix.cs',encoding='utf8').read()
B=chr(92)
for x in ['k','Q','b','0','gR','g','4']:
    s=s.replace(B+'H0.7x;'+B+'S'+x+'^;'+B+'H1.4286x;', B+'S^'+x+';')
open('bfix.cs','w',encoding='utf8').write(s)
