B=chr(92)
old=B.join(['D:','РАБОЧКА','От Маке','Завод','Маслоподготовка Блок 3','m3col.dwg'])
new=B.join(['C:','Users','Admin','AppData','Local','Temp','claude','210ab68cad67e8c1','6399190a-f172-4888-a7c9-e3d967ee3eb0','scratchpad','b3','k','w','m3col.dwg'])
for p in ['ab.py','net/start.ps1','net/plotl.ps1']:
    b=open(p,'rb').read(); enc='utf-8-sig' if b.startswith(b'\xef\xbb\xbf') else 'utf-8'
    open(p,'w',encoding=enc,newline='').write(b.decode(enc).replace(old,new))
