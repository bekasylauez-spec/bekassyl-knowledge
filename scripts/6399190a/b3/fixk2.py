import os
old='D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 3\4.Колонна Блок 3.dwg'
new=r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k\w\m3col.dwg'
for p in ['ab.py','net/start.ps1','net/plotl.ps1','net/job.ps1','net/ab.cs']:
    b=open(p,'rb').read(); enc='utf-8-sig' if b.startswith(b'\xef\xbb\xbf') else 'utf-8'
    s=b.decode(enc).replace(old,new).replace('4.Колонна Блок 3.dwg','m3col.dwg')
    open(p,'w',encoding=enc,newline='').write(s)
