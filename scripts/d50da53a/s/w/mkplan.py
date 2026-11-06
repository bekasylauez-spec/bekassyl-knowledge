import json
S=r'C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/d50da53a-3ac3-4689-a264-f515b6d8bdb3/scratchpad/s'
rows=json.load(open(S+'/rows.json',encoding='utf-8'))
mark={}
for a in ['А/9','А/10','А/11','К/9','К/13']: mark[a]='Км-1.1'
for a in ['А/12','А/13','К/12']: mark[a]='Км-1.2'
for a in ['К/10','К/11']: mark[a]='Км-2'
for a in ['Б/9','Б/13','Д/9','Д/10','Д/11','Д/12','Д/13','Ж/9','Ж/12','Ж/13']: mark[a]='Км-3.1'
mark['В/13']='Км-3.2'; mark['Б/10']='Км-4'; mark['Ж/10']='Км-5'; mark['Ж/11']='Км-5'; mark['Б/11']='Км-6'; mark['Б/12']='Км-7'
cols=[]
for r in rows:
    k=r['ay']+'/'+r['ax']
    cols.append(dict(id=k,x=r['sx'],y=r['sy'],bx=r['w'],by=r['h'],mark=mark[k],lira=list(r['lira'])))
extra=[('Д/12-13',83650,16500,700,700,'Км-3.1',(82.45,15.15)),('Ж/12-13',83650,22000,700,700,'Км-3.1',(82.45,20.65)),
('Б-В/10-11',70650,10000,700,700,'Км-8',(69.45,8.65)),('Б-В/11',73650,11750,700,700,'Км-8',(72.45,10.4)),
('А-Б/11',73650,1850,550,550,'Км-9',(72.45,0.5)),('А-Б/12',79650,1850,550,550,'Км-9',(78.45,0.5)),
('А-Б/12-13',83900,1850,550,550,'Км-9',(82.7,0.5)),('Б/12-13',83900,7000,550,550,'Км-9',(82.7,5.65))]
for e in extra: cols.append(dict(id=e[0],x=e[1],y=e[2],bx=e[3],by=e[4],mark=e[5],lira=list(e[6])))
json.dump(cols,open(S+'/colplan.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
import collections; c=collections.Counter(x['mark'] for x in cols); print(sorted(c.items()), sum(c.values()))
