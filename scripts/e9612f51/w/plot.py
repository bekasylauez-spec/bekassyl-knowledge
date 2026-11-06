import gx, subprocess, sys, os, fitz
S=gx.S
def snap():
    print(gx.run([{'t':'wblock','file':S+r'\w\snap.dwg'}],'wb')[-200:])
def plot(name, x0, y0, x1, y1, paper='ISO без полей A2 (594.00 x 420.00 мм)', orient='_L'):
    pdf=S+r'\w\%s.pdf'%name
    scr="_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n"%(paper,orient,x0,y0,x1,y1,pdf)
    open(S+r'\w\pl_%s.scr'%name,'w',encoding='cp1251').write(scr)
    if os.path.exists(pdf): os.remove(pdf)
    exe='C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe'
    ps="$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s'; $p | Wait-Process -Timeout 150 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }"%(exe,S+r'\w\snap.dwg',S+r'\w\pl_%s.scr'%name,S+r'\w\pl_%s.log'%name)
    subprocess.run(['powershell','-Command',ps])
    return pdf
def png(pdf, out, dpi=110, clip=None):
    d=fitz.open(pdf); p=d[0]
    if clip: r=p.rect; cl=fitz.Rect(r.width*clip[0],r.height*clip[1],r.width*clip[2],r.height*clip[3]); p.get_pixmap(dpi=dpi,clip=cl).save(out)
    else: p.get_pixmap(dpi=dpi).save(out)
if __name__=='__main__':
    snap()
    k=int(sys.argv[1]); fx=-243621+59400*(k-1)
    pdf=plot('s%d'%k, fx, 455939, fx+59400, 497939)
    png(pdf, S+r'\w\s%d.png'%k, 60)
    png(pdf, S+r'\w\s%da.png'%k, 140, (0,0,0.6,1))
