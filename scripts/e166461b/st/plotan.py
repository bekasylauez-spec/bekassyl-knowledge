import sys, os, subprocess, json
sys.path.insert(0, r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad')
import plot as P
def plot_file(dwg, name, x0, y0, x1, y1, paper='ISO без полей A2 (594.00 x 420.00 мм)', orient='_L'):
    S = P.S; pdf = S + r'\w\%s.pdf' % name
    scr = "_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n" % (paper, orient, x0, y0, x1, y1, pdf)
    open(S + r'\w\pl_%s.scr' % name, 'w', encoding='cp1251').write(scr)
    if os.path.exists(pdf): os.remove(pdf)
    exe = 'C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe'
    ps = "$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s'; $p | Wait-Process -Timeout 200 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }" % (exe, dwg, S + r'\w\pl_%s.scr' % name, S + r'\w\pl_%s.log' % name)
    subprocess.run(['powershell', '-Command', ps])
    return pdf
if __name__ == '__main__':
    k, i = sys.argv[1], int(sys.argv[2])
    F = json.load(open(P.S + r'\st\frames.json', encoding='utf-8'))[k][i]
    w, h = F[2] - F[0], F[3] - F[1]
    pdf = plot_file(P.S + r'\st\%s.dwg' % k, 'an_%s_%d' % (k, i), *F[:4], orient='_L' if w > h else '_P')
    P.png(pdf, P.S + r'\w\an_%s_%d.png' % (k, i), int(sys.argv[3]) if len(sys.argv) > 3 else 80)
    print(pdf)
