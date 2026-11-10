import json,sys
sys.stdout.reconfigure(encoding='utf-8')
fr=json.load(open("D:/_claude_work/v113/ozh/frames.json",encoding='utf-8'))
sc=json.load(open("D:/_claude_work/v113/ozh/scales.json"))
M={'Н100':'1:100','Н10':'1:10','Н50':'1:50','Н25':'1:25'}
rows=[]
for f in fr:
    st=f['sttx'];n=f['n']
    if n==1: no,nm='-','Титульный лист'
    elif n==2: no,nm='-','Лист утверждения'
    else:
        s=[t for t in st if t!='М24']
        no=s[0]; nm=' / '.join(s[1:])
    if no=='-' : sk='-'
    elif n==3 or n==4 or n==5 or n==6: sk='без масштаба (текст/таблица)'
    else:
        ds=sc[str(n)][1]
        sk=', '.join(M.get(k,k) for k in ds) + ' (по размерному стилю, DIMLFAC)'
    fmt=f['src'].split(' (')[0].replace('polyline 1Штамп','A3 альбом').replace('polyline 1Планы-рабочие + stamp','A3 альбом').replace('polyline 1Планы-рабочие','A3 альбом')
    rows.append((int(no) if no.isdigit() else (0 if no=='-' else float(no)),n,no,nm,fmt,sk,round(f['x0']),round(f['y0'])))
rows.sort(key=lambda r:(r[1]) )
L=["\n\n## 12. СВОДНАЯ ТАБЛИЦА ЛИСТОВ (порядок по ведомости)\n","Масштаб листа в тексте не указан нигде (нет «М 1:n»); выведен из размерных стилей: Н100 (DIMLFAC 1) = 1:100, Н10 (DIMLFAC 0.1) = 1:10, Н50 = 1:50, Н25 = 1:25. Рамка в модели 1:100 (A1=84100x59400, A2=42000x59400 портрет, A3=42000x29700, A4=21000x29700 портрет).\n","| № листа | модель-# | наименование | формат | масштаб | x0 | y0 |","|--|--|--|--|--|--|--|"]
def key(r):
    no=r[2]
    if no=='-': return (-1,r[1])
    return (float(no),r[1])
for r in sorted(rows,key=key): L.append(f"| {r[2]} | {r[1]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} |")
open("D:/_claude_work/v113/ozh/inventory.md","a",encoding="utf-8").write("\n".join(L))
print("\n".join(L))
