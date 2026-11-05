import subprocess, os, sys, json, shutil, time
S = os.path.dirname(os.path.abspath(__file__))
EXE = r"C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"
SH = json.load(open(r'D:\РАБОЧКА\От Маке\Завод\АБК\_Инструменты\beka2_v2\sheets.json', encoding='utf-8'))
SH['4.2'] = [244346.9, -1749172.3, 274046.9, -1728172.3]; SH['4.3'] = [274046.9, -1749172.3, 303746.9, -1728172.3]
def paper(w, h):
    sc = 100 if h == 42000 else 50
    W, H = w / sc, h / sc
    for nm, a, b in (('ISO без полей A0 (1189.00 x 841.00 мм)', 1189, 841), ('ISO без полей A1 (841.00 x 594.00 мм)', 841, 594), ('ISO без полей A2 (594.00 x 420.00 мм)', 594, 420), ('ISO без полей A3 (420.00 x 297.00 мм)', 420, 297)):
        pass
    big = max(W, H)
    nm = 'ISO без полей A0 (841.00 x 1189.00 мм)' if big > 841 else ('ISO без полей A1 (841.00 x 594.00 мм)' if big > 594 else 'ISO без полей A2 (594.00 x 420.00 мм)')
    return nm, ('_L' if W >= H else '_P')
def run(sheets, tag):
    snap = os.path.join(S, 'w', 'mp_%d.dwg' % int(time.time()))
    shutil.copyfile(r"D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg", snap)
    scr = ''
    out = {}
    for s in sheets:
        x0, y0, x1, y1 = SH[s]; nm, o = paper(x1 - x0, y1 - y0)
        pdf = os.path.join(S, 'w', 'pp_%s.pdf' % s); out[s] = pdf
        if os.path.exists(pdf): os.remove(pdf)
        scr += "_-PLOT\r\n_Y\r\nModel\r\nDWG To PDF.pc3\r\n%s\r\n_M\r\n%s\r\n_N\r\n_W\r\n%f,%f\r\n%f,%f\r\n_F\r\n_C\r\n_Y\r\nmonochrome.ctb\r\n_Y\r\n_A\r\n%s\r\n_N\r\n_Y\r\n" % (nm, o, x0, y0, x1, y1, pdf)
    scr += "_.QUIT\r\n_Y\r\n"
    sp = os.path.join(S, 'w', 'mp_%s.scr' % tag); open(sp, 'w', encoding='cp1251', newline='').write(scr)
    ps = ("$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s';"
          " $p | Wait-Process -Timeout 900 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }") % (EXE, snap, sp, os.path.join(S, 'w', 'mp_%s.log' % tag))
    subprocess.run(['powershell', '-Command', ps])
    return out
if __name__ == '__main__':
    print(run(sys.argv[2:], sys.argv[1]))
