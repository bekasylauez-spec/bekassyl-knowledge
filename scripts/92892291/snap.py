"""plot a model window of the SAVED working DWG through accoreconsole -> PNG"""
import subprocess, os, shutil, sys, fitz
S = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\92892291-7735-4e20-9a30-a83b0b257986\scratchpad"
DWG = r"D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg"
EXE = r"C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"


def plot(name, win, paper='ISO без полей A1 (841.00 x 594.00 мм)', orient='_L', copy=True):
    w = os.path.join(S, 'w')
    snapd = os.path.join(w, 'snap.dwg')
    if copy: shutil.copyfile(DWG, snapd)
    pdf = os.path.join(w, name + '.pdf')
    if os.path.exists(pdf): os.remove(pdf)
    x0, y0, x1, y1 = win
    scr = "_-PLOT\r\n_Y\r\nModel\r\nDWG To PDF.pc3\r\n%s\r\n_M\r\n%s\r\n_N\r\n_W\r\n%f,%f\r\n%f,%f\r\n_F\r\n_C\r\n_Y\r\nmonochrome.ctb\r\n_Y\r\n_A\r\n%s\r\n_N\r\n_Y\r\n_.QUIT\r\n_Y\r\n" % (paper, orient, x0, y0, x1, y1, pdf)
    sp = os.path.join(w, 'pl_%s.scr' % name)
    open(sp, 'w', encoding='cp1251', newline='').write(scr)
    ps = ("$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s';"
          " $p | Wait-Process -Timeout 240 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }") % (EXE, snapd, sp, os.path.join(w, 'pl_%s.log' % name))
    subprocess.run(['powershell', '-Command', ps])
    return pdf


def png(pdf, out, dpi=110, clip=None):
    d = fitz.open(pdf); p = d[0]
    if clip:
        r = p.rect; cl = fitz.Rect(r.width * clip[0], r.height * clip[1], r.width * clip[2], r.height * clip[3])
        p.get_pixmap(dpi=dpi, clip=cl).save(out)
    else:
        p.get_pixmap(dpi=dpi).save(out)
    return out


if __name__ == '__main__':
    name = sys.argv[1]; win = [float(v) for v in sys.argv[2].split(',')]
    pdf = plot(name, win)
    print(png(pdf, os.path.join(S, 'w', name + '.png'), int(sys.argv[3]) if len(sys.argv) > 3 else 60))
