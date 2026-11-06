import os, subprocess
W = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(W, 'pdf2'), exist_ok=True)
scr = "FILEDIA\n0\nBACKGROUNDPLOT\n0\n"
for k in range(1, 31):
    scr += "_-PLOT\n_N\n6.%d\n\n\n_Y\n%s\n_N\n_Y\n" % (k, os.path.join(W, 'pdf2', '6.%d.pdf' % k))
scr += "_.QUIT\n_Y\n"
open(os.path.join(W, 'plotlay.scr'), 'w', encoding='cp1251').write(scr)
ps = "$p=Start-Process 'C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s'; $p | Wait-Process -Timeout 900 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }" % (
    os.path.join(W, 'snap.dwg'), os.path.join(W, 'plotlay.scr'), os.path.join(W, 'plotlay.log'))
subprocess.run(['powershell', '-Command', ps])
print(len(os.listdir(os.path.join(W, 'pdf2'))))
