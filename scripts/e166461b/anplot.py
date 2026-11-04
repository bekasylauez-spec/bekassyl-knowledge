import plot, subprocess, os, fitz, sys
S=plot.S
def plotf(dwg, name, x0,y0,x1,y1, paper, orient, dpi=75):
    pdf=S+r'\an\%s.pdf'%name
    scr="_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n"%(paper,orient,x0,y0,x1,y1,pdf)
    open(S+r'\an\pl_%s.scr'%name,'w',encoding='cp1251').write(scr)
    exe='C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe'
    ps="$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s'; $p | Wait-Process -Timeout 200 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }"%(exe,dwg,S+r'\an\pl_%s.scr'%name,S+r'\an\pl_%s.log'%name)
    subprocess.run(['powershell','-Command',ps])
    if os.path.exists(pdf): fitz.open(pdf)[0].get_pixmap(dpi=dpi).save(S+r'\an\%s.png'%name)
    return pdf
A2L=('ISO без полей A2 (594.00 x 420.00 мм)','_L'); A2P=('ISO без полей A2 (594.00 x 420.00 мм)','_P'); A1=('ISO без полей A1 (594.00 x 841.00 мм)','_P')
