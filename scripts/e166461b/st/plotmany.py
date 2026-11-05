import sys, os, subprocess, json
sys.path.insert(0, r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad')
import plot as P
S = P.S
k = sys.argv[1]; idx = [int(v) for v in sys.argv[2].split(',')]; dpi = int(sys.argv[3])
F = json.load(open(S + r'\st\frames.json', encoding='utf-8'))[k]
scr = ''
outs = []
for i in idx:
    x0, y0, x1, y1 = F[i][:4]; w, h = x1 - x0, y1 - y0
    pdf = S + r'\w\an_%s_%d.pdf' % (k, i); outs.append((i, pdf))
    if os.path.exists(pdf): os.remove(pdf)
    paper = 'ISO без полей A2 (594.00 x 420.00 мм)'
    scr += "_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n" % (paper, '_L' if w >= h else '_P', x0, y0, x1, y1, pdf)
scr += "_.QUIT\n_Y\n"
open(S + r'\w\pm_%s.scr' % k, 'w', encoding='cp1251').write(scr)
exe = 'C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe'
ps = "$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s'; $p | Wait-Process -Timeout 560 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }" % (exe, S + r'\st\%s.dwg' % k, S + r'\w\pm_%s.scr' % k, S + r'\w\pm_%s.log' % k)
subprocess.run(['powershell', '-Command', ps])
for i, pdf in outs:
    if os.path.exists(pdf): P.png(pdf, S + r'\w\an_%s_%d.png' % (k, i), dpi); print('ok', i)
    else: print('MISSING', i)
