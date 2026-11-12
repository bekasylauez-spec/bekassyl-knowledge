import json, re, sys
D='D:/_claude_work/otst/s4/'
q=json.load(open(D+'s4_qty.json',encoding='utf-8')); c=json.load(open(D+'s4_chk_qty.json',encoding='utf-8'))
MASS={8:0.395,12:0.888,16:1.578,18:1.998,22:2.984}
R=c['rows']
def mine(el, keys):
    sel=[r for r in R if r['el']==el and any(r['pos'].startswith(k) for k in keys)]
    assert sel,(el,keys)
    n=sum(r['n'] for r in sel); m=sum(r['tot_m'] for r in sel); ms=sum(r['mass'] for r in sel)
    return n,m,ms,sel
# spec pos -> (mine element, startswith keys)
MAP={
 'Фм-1':{'1':('Фм-1',['1 ']),'2':('Фм-1',['2 ']),'3':('Фм-1',['3 ']),'4':('Фм-1',['4 ']),'5':('Фм-1',['5 ']),'Ск1':('Фм-1',['Ск1']),'6':('Фм-1',['6 ']),'7':('Фм-1',['7 ']),
        'Кр1/9':('Фм-1',['Кр1 поз.9']),'Кр1/10':('Фм-1',['Кр1 поз.10']),'Шп1':('Фм-1',['Шп1'])},
 'Вп1':{'Вп1':('Вп1',['Вп1'])},
 'См-1':{'1':('См-1',['1 ']),'Ск2':('См-1',['Ск2']),'Шп1':('См-1',['Шп1']),'Обр':('См-1',['Обрамление']),'4к':('См-1',['Консоль поз.4']),'5к':('См-1',['Консоль поз.5']),
         '2л':('См-1',['Лоток поз.2 Г (қалыпты)']),"2л'":('См-1',['Лоток поз.2 Г (терең']),'3л':('См-1',['Лоток поз.3'])},
 'Км-1':{'1':('Км-1+оголовок',['Тік']),'2':('Км-1+оголовок',['Выпуск']),'3':('Км-1+оголовок',['Хомут сыртқы']),'4':('Км-1+оголовок',['Хомут ішкі']),'5':('Км-1+оголовок',['Оголовок тор']),'Ск3':('Км-1+оголовок',['Оголовок П'])},
 'Св1':{'1':('Св1 (41 дана)',['Св1 Ø22']),'2':('Св1 (41 дана)',['Фиксатор'])},
}
out=[]; viol=[]
def pct(a,b): return (a-b)/b*100
def flag(p): return '' if -0.005<=p<=3.0 else ' **✗**'
tab=["| Элемент | Поз. | Профиль | Спец.: саны | Спец.: L, мм | Спец.: масса, кг | Тәуел.: саны | Тәуел.: L, мм | Тәуел.: масса, кг | Δ саны/м.п. % | Δ масса % |","|---|---|---|---|---|---|---|---|---|---|---|"]
stot={}
for el,rows in q['elements'].items():
    for r in rows['rows']:
        pos=r['pos']; 
        if el not in MAP or pos not in MAP[el]: print('NOMAP',el,pos); continue
        me,keys=MAP[el][pos]; n,m,ms,sel=mine(me,keys)
        mL=sel[0]['L'] if len(sel)==1 else ('/'.join(s['L'] for s in sel))
        mp=r['unit']=='м.п.'
        sq=r['qty']; sm=r['total_mass']
        mq=m if mp else n
        dq=pct(sq,mq); dm=pct(sm,ms)
        sL='м.п.' if mp else re.search(r'L=(\d+)',r['name']).group(1)
        prof=re.sub(r' м\.п\.| L=\d+','',r['name'])
        tab.append(f"| {el} | {pos} | {prof} | {sq:g}{' м' if mp else ''} | {sL} | {sm:.1f} | {mq:.2f}{' м' if mp else ''} | {mL} | {ms:.1f} | {dq:+.2f}{flag(dq)} | {dm:+.2f}{flag(dm)} |")
        if flag(dm) or flag(dq): viol.append((el,pos,prof,sq,mq,sm,ms,dq,dm))
print('\n'.join(tab)); print(); 
for v in viol: print(v)
json.dump(dict(tab=tab,viol=viol),open('C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/b76c049c-c3b6-4782-bb03-17435529c746/scratchpad/cmp1.json','w',encoding='utf-8'),ensure_ascii=False)
