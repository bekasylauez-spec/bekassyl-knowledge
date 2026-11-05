import subprocess, os, sys, pymupdf as fitz, ab
S = ab.S
EXE = r"C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"
import time
SNAP = None
def take():
    """сақталған DWG-ның көшірмесі (wblock AutoCAD-ты құлатты)"""
    global SNAP
    import shutil
    SNAP = os.path.join(S, 'w', 'snap_%d.dwg' % int(time.time()))
    shutil.copyfile(r"D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg", SNAP)
    return SNAP
def plot(name, win, paper='ISO без полей A1 (841.00 x 594.00 мм)', orient='_L'):
    w = os.path.join(S, 'w'); pdf = os.path.join(w, name + '.pdf')
    if os.path.exists(pdf): os.remove(pdf)
    x0, y0, x1, y1 = win
    scr = "_-PLOT\r\n_Y\r\nModel\r\nDWG To PDF.pc3\r\n%s\r\n_M\r\n%s\r\n_N\r\n_W\r\n%f,%f\r\n%f,%f\r\n_F\r\n_C\r\n_Y\r\nmonochrome.ctb\r\n_Y\r\n_A\r\n%s\r\n_N\r\n_Y\r\n_.QUIT\r\n_Y\r\n" % (paper, orient, x0, y0, x1, y1, pdf)
    sp = os.path.join(w, 'pl_%s.scr' % name)
    open(sp, 'w', encoding='cp1251', newline='').write(scr)
    ps = ("$p=Start-Process '%s' -ArgumentList '/i \"%s\" /s \"%s\" /l ru-RU' -PassThru -NoNewWindow -RedirectStandardOutput '%s';"
          " $p | Wait-Process -Timeout 240 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force }") % (EXE, SNAP, sp, os.path.join(w, 'pl_%s.log' % name))
    subprocess.run(['powershell', '-Command', ps])
    return pdf
def png(pdf, out, dpi=110, clip=None):
    p = fitz.open(pdf)[0]
    if clip:
        r = p.rect; p.get_pixmap(dpi=dpi, clip=fitz.Rect(r.width*clip[0], r.height*clip[1], r.width*clip[2], r.height*clip[3])).save(out)
    else: p.get_pixmap(dpi=dpi).save(out)
    return out
