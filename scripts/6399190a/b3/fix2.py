for p in ['t/mb.py','t/net/start.ps1','t/restart.ps1','t/snap.py']:
    b=open(p,'rb').read(); enc='utf-8-sig' if b.startswith(b'\xef\xbb\xbf') else 'utf-8'
    s=b.decode(enc).replace('Маслоподготовка Блок 2','Маслоподготовка Блок 3')
    open(p,'w',encoding=enc,newline='').write(s)
