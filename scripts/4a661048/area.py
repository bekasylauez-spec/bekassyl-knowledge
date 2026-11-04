import math
# name, mass t (spec sheet 14), perimeter m, kg/m  (plates: 2 sides)
P=[('I14Б1',0.55,(2*137.4+4*73-2*3.8)/1000,12.9),
   ('I10Б1',0.20,(2*100+4*55-2*4.1)/1000,8.1),
   ('Тр.76х3',0.594,math.pi*0.076,5.40),
   ('Тр.20х1.5',0.192,math.pi*0.020,0.684),
   ('□100х4',0.36,(400-64+2*math.pi*8)/1000,11.73),
   ('L75х5',0.19,(4*75-2*5)/1000,5.80),
   ('L70х5',0.28,(4*70-2*5)/1000,5.38),
   ('L50х5',0.09,(4*50-2*5)/1000,3.77),
   ('[16П',0.09,(2*160+4*64-2*5)/1000,14.2)]
tot=0;terms=[]
for n,m,p,g in P:
    k=round(p/g*1000,1); a=m*k; tot+=a; terms.append(f'{m}*{k}'); print(n,m,k,'m2/t',round(a,2))
for t,m in [(8,0.06),(6,0.10),(4,1.11)]:
    k=round(2/(7.85*t/1000)/1000*1000,1)  # m2 per t
    k=round(2/(7.85*t)*1000,1)
    a=m*k; tot+=a; terms.append(f'{m}*{k}'); print('t',t,m,k,round(a,2))
print('total',round(tot,1)); print('+'.join(terms))
print('ГФ',round(tot*0.10,1),'ПФ',round(tot*2*0.12,1))
