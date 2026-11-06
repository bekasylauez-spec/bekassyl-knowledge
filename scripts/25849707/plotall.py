# one accoreconsole session plots every rigel sheet (model window, A4x3 = 630x297 custom? -> ISO A3 fit) to pv/all/s{k}.pdf
import gx, mk, os, subprocess, shutil, sys
P = os.path.join(gx.S, 'pv', 'all'); os.makedirs(P, exist_ok=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 83
gx.run([dict(t='save')], 'sv')
snap = os.path.join(gx.S, 'pv', 'snap.dwg'); shutil.copy(r'D:\РАБОЧКА\От Шерхан\Бдм Блок 1\Б1.ригели.dwg', snap)
scr = '(setvar "FILEDIA" 0)\n'
for k in range(N):
    x, y = mk.slot(k); pdf = os.path.join(P, 's%03d.pdf' % k).replace(os.sep, '/')
    if os.path.exists(pdf): os.remove(pdf)
    scr += ('_-PLOT\n_Y\nModel\nDWG To PDF.pc3\nISO без полей A3 (420.00 x 297.00 мм)\n_M\n_L\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n' % (x, y, x + 31500, y + 14850, pdf))
scr += '_.QUIT\n_Y\n'
sp = os.path.join(P, 'all.scr'); open(sp, 'w', encoding='cp1251').write(scr)
exe = r'C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe'
subprocess.run([exe, '/i', snap, '/s', sp, '/l', 'ru-RU'], capture_output=True, timeout=5400)
print(sum(1 for f in os.listdir(P) if f.endswith('.pdf')))
