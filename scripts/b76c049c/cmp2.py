import json, re, math
D='D:/_claude_work/otst/s4/'
SP='C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/b76c049c-c3b6-4782-bb03-17435529c746/scratchpad/'
q=json.load(open(D+'s4_qty.json',encoding='utf-8')); c=json.load(open(D+'s4_chk_qty.json',encoding='utf-8'))
MASS={8:0.395,12:0.888,16:1.578,18:1.998,22:2.984}
R=c['rows']
def mine(el, keys):
    sel=[r for r in R if r['el']==el and any(r['pos'].startswith(k) for k in keys)]
    assert sel,(el,keys)
    return sum(r['n'] for r in sel), sum(r['tot_m'] for r in sel), sum(r['mass'] for r in sel), sel
MAP={
 'Фм-1':{'1':('Фм-1',['1 ']),'2':('Фм-1',['2 ']),'3':('Фм-1',['3 ']),'4':('Фм-1',['4 ']),'5':('Фм-1',['5 ']),'Ск1':('Фм-1',['Ск1']),'6':('Фм-1',['6 ']),'7':('Фм-1',['7 ']),
        'Кр1/9':('Фм-1',['Кр1 поз.9']),'Кр1/10':('Фм-1',['Кр1 поз.10']),'Шп1':('Фм-1',['Шп1'])},
 'Вп1':{'Вп1':('Вп1',['Вп1'])},
 'См-1':{'1':('См-1',['1 ']),'Ск2':('См-1',['Ск2']),'Шп1':('См-1',['Шп1']),'Обр':('См-1',['Обрамление']),'4к':('См-1',['Консоль поз.4']),'5к':('См-1',['Консоль поз.5']),
         '2л':('См-1',['Лоток поз.2 Г (қалыпты)']),"2л'":('См-1',['Лоток поз.2 Г (терең']),'3л':('См-1',['Лоток поз.3'])},
 'Км-1':{'1':('Км-1+оголовок',['Тік']),'2':('Км-1+оголовок',['Выпуск']),'3':('Км-1+оголовок',['Хомут сыртқы']),'4':('Км-1+оголовок',['Хомут ішкі']),'5':('Км-1+оголовок',['Оголовок тор']),'Ск3':('Км-1+оголовок',['Оголовок П'])},
 'Св1':{'1':('Св1 (41 дана)',['Св1 Ø22']),'2':('Св1 (41 дана)',['Фиксатор'])},
}
TOL=-0.005
def pct(a,b): return (a-b)/b*100
def bad(p): return not (TOL<=p<=3.0)
def mk(p): return f"{p:+.2f}"+(" **✗**" if bad(p) else "")
tab=["| Элемент | Поз. | Профиль | Спец. саны | Спец. L, мм | Спец. масса, кг | Тәуел. саны | Тәуел. L, мм | Тәуел. масса, кг | Δ саны/м.п., % | Δ масса, % |","|---|---|---|---|---|---|---|---|---|---|---|"]
viol=[]
for el,rows in q['elements'].items():
    for r in rows['rows']:
        pos=r['pos']; me,keys=MAP[el][pos]; n,m,ms,sel=mine(me,keys)
        mL=sel[0]['L'] if len(sel)==1 else '/'.join(s['L'] for s in sel)
        mp=r['unit']=='м.п.'
        d=int(re.search(r'∅(\d+)',r['name']).group(1))
        if mp: sq=r['qty']; sm=r['qty']*r['unit_mass']; sL='м.п.'
        else:
            Lm=int(re.search(r'L=(\d+)',r['name']).group(1)); sq=r['qty']; sm=sq*Lm/1000*MASS[d]; sL=str(Lm)
        mq=m if mp else n
        dq=pct(sq,mq); dm=pct(sm,ms)
        tolm = -(50.0/Lm) if not mp else TOL      # L мм-ге дөңгелектелген: жарты мм / L
        okm = tolm<=dm<=3.0
        prof=re.sub(r' м\.п\.| L=\d+','',r['name'])
        tab.append(f"| {el} | {pos} | {prof} | {sq:g}{' м' if mp else ''} | {sL} | {sm:.1f} | {mq:.2f}{' м' if mp else ''} | {mL} | {ms:.1f} | {mk(dq)} | {(f'{dm:+.2f}' + (' (L дөңгелектеу)' if (bad(dm) is False)==False and okm else '')) if okm or not bad(dm) else mk(dm)} |")
        if bad(dq) or not okm: viol.append(('арм',el,pos,sq,mq,sm,ms,dq,dm))
g=c['groups']; gm={'Фм-1':'Фм-1','Вп1':'Вп1','См-1':'См-1','Км-1':'Км-1+оголовок','Св1':'Св1 (41 дана)'}
et=["| Элемент | Спец. болат, кг | Тәуел. болат, кг | Δ, % |","|---|---|---|---|"]
for el in ['Фм-1','Вп1','См-1','Км-1','Св1']:
    a=q['steel'][el]['Итого']; b=sum(g[gm[el]].values()); p=pct(a,b)
    et.append(f"| {el} | {a:.1f} | {b:.1f} | {mk(p)} |")
    if bad(p): viol.append(('эл',el,'Σ',a,b,a,b,p,p))
tot_m=sum(sum(v.values()) for v in g.values()); tot_s=q['steel_total_kg']
et.append(f"| **Барлығы** | {tot_s:.1f} | {tot_m:.1f} | {mk(pct(tot_s,tot_m))} |")
dt=["| Ø | Спец., кг | Тәуел., кг | Δ, % |","|---|---|---|---|"]
for lab,d in [('Ø8 А240',8),('Ø12 А500С',12),('Ø16 А500С',16),('Ø18 А500С',18),('Ø22 А500С',22)]:
    a=q['steel_by_dia'][lab]; b=c['tot_by_d'][str(d)]
    dt.append(f"| {lab} | {a:.1f} | {b:.1f} | {mk(pct(a,b))} |")
cc=c['conc']
def mm(x): return x['M1']
conc_rows=[
 ('Фм-1 (днище+вут+приямок), м³', q['elements']['Фм-1']['concrete_m3'], mm(cc['Фм-1']),3),
 ('См-1 (қабырға+консоль+лоток), м³', q['elements']['См-1']['concrete_m3'], mm(cc['См-1']),3),
 ('Км-1 + оголовок, м³', q['elements']['Км-1']['concrete_m3'], mm(cc['Км-1+оголовок']),3),
 ('Σ монолит (Фм+См+Км), м³', q['concrete_total_m3'], mm(cc['Фм-1'])+mm(cc['См-1'])+mm(cc['Км-1+оголовок']),3),
 ('Подготовка C8/10, м³', q['elements']['Фм-1']['prep_m3'], mm(cc['Подготовка']),3),
 ('Св1 (41 дана), м³', q['elements']['Св1']['concrete_m3'], mm(cc['Сваи Св1']),3),
 ('Св2 (12 дана), м³', q['elements']['Св2']['concrete_m3'], mm(cc['Сваи Св2']),3),
 ('Сваи Σ, м³', q['concrete_piles_m3'], mm(cc['Сваи Св1'])+mm(cc['Сваи Св2']),3),
]
e=q['earth']; ce=c['earth']; w=q['waterproof']
conc_rows+= [
 ('Котлован негізгі (қазу), м³', e['kotlovan_main_m3_exact'], ce['V_kot'],3),
 ('Приямок шұңқыры, м³', e['pit_m3_exact'], ce['V_pit'],3),
 ('Қазу жиыны, м³', e['excavation_total_m3'], ce['V_exc'],3),
 ('Подушка (суглинок), м³', e['cushion_m3'], ce['V_podu'][0],3),
 ('Кері көму, м³', e['backfill_m3'], ce['V_back'][0],3),
 ('Геомембрана жазбасы (нахлёссіз), м²', e['geomembrane_m2_base'], ce['A_gm'][0],3),
 ('Геомембрана +10 %, м²', e['geomembrane_m2'], ce['A_gm'][2],3),
 ('Гидроизоляция (мастика/грунтовка беті), м²', w['total_m2'], ce['A_hydro'][0],2),
 ('Грунтовка 0,3 кг/м², кг', 35.67, ce['A_hydro'][0]*0.3,2),
 ('Мастика 4 кг/м², кг', 475.64, ce['A_hydro'][0]*4,2),
]
bt=["| Көрсеткіш | Спец. | Тәуел. | Δ, % |","|---|---|---|---|"]
for nme,a,b,dec in conc_rows:
    p=pct(a,b)
    noise=(a<b) and abs(a-b)<=0.5*10**(-dec)+1e-12
    ft=f"{p:+.3f}"+("" if (not bad(p) or noise) else " **✗**")+(" (дөңгелектеу)" if bad(p) and noise else "")
    bt.append(f"| {nme} | {a:.{dec}f} | {b:.{dec}f} | {ft} |")
    if bad(p) and not noise: viol.append(('бет/жер',nme,'',a,b,a,b,p,p))
Vm=mm(cc['Фм-1'])+mm(cc['См-1'])+mm(cc['Км-1+оголовок'])
steel_struct_m=tot_m-sum(g['Св1 (41 дана)'].values())
summ=["| Көрсеткіш | Спецификация (s4_qty) | Тәуелсіз | Δ, % |","|---|---|---|---|"]
def row(n,a,b,fmt='{:.1f}'): summ.append(f"| {n} | {fmt.format(a)} | {fmt.format(b)} | {mk(pct(a,b))} |")
row('Болат барлығы (Св1-мен), кг',tot_s,tot_m)
row('Болат конструкция (Св1-сіз), кг',q['steel_structures_kg'],steel_struct_m)
row('Бетон монолит Фм+Км+См, м³',q['concrete_total_m3'],Vm,'{:.3f}')
row('кг/м³ конструкция (Фм+Вп1+См+Км)',q['kg_per_m3']['Итого конструкции (Фм-1+Вп1+См-1+Км-1)'],steel_struct_m/Vm)
mFm=sum(g['Фм-1'].values()); mVp=sum(g['Вп1'].values()); mSm=sum(g['См-1'].values()); mKm=sum(g['Км-1+оголовок'].values())
row('кг/м³ Фм-1+Вп1',q['kg_per_m3']['Фм-1+Вп1'],(mFm+mVp)/mm(cc['Фм-1']))
row('кг/м³ См-1',q['kg_per_m3']['См-1'],mSm/mm(cc['См-1']))
row('кг/м³ Км-1',q['kg_per_m3']['Км-1'],mKm/mm(cc['Км-1+оголовок']))
Vall=Vm+mm(cc['Сваи Св1'])+mm(cc['Сваи Св2'])
row('кг/м³ барлығы (сваялармен)',q['kg_per_m3']['Все вместе (с сваями)'],tot_m/Vall)
json.dump(dict(tab=tab,et=et,dt=dt,bt=bt,summ=summ,viol=viol,Vm=Vm,ssm=steel_struct_m,tot_m=tot_m,Vall=Vall),open(SP+'cmp2.json','w',encoding='utf-8'),ensure_ascii=False)
for t in (tab,et,dt,bt,summ): print('\n'.join(t)); print()
for v in viol: print(v)
