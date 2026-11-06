import subprocess, os, sys
S=os.path.dirname(os.path.abspath(__file__))
def tryplot(name, erase_wins, win):
    pdf=S+'/%s.pdf'%name
    pre=''.join('_.ERASE\n_C\n%f,%f\n%f,%f\n\n'%tuple(w) for w in erase_wins)
    scr="FILEDIA\n0\n"+pre+"_-PLOT\n_Y\nModel\nDWG To PDF.pc3\nISO без полей A2 (594.00 x 420.00 мм)\n_M\n_L\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n"%(win[0],win[1],win[2],win[3],pdf)
    open(S+'/bis.scr','w',encoding='cp1251').write(scr)
    if os.path.exists(pdf): os.remove(pdf)
    ps="$p=Start-Process 'C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s'; $p | Wait-Process -Timeout 200 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }"%(S+'/snap.dwg',S+'/bis.scr',S+'/bis.log')
    subprocess.run(['powershell','-Command',ps])
    return os.path.exists(pdf)
if __name__=='__main__':
  w1=[172179,455939,203679,470789]; w20=[172179+31500*19,455939,172179+31500*20,470789]
  print('erase20 plot1', tryplot('b1',[w20],w1))
  print('erase1 plot20', tryplot('b2',[w1],w20))
