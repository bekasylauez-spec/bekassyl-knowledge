# plot layouts of the saved working DWG and rasterize: snap.py 4.1 [4.2 ...] [--dpi N] [--quarters]
import subprocess, sys, os, fitz
S = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\s"
DWG = r"D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 3\4.Колонна Блок 3.dwg"
OUT = os.path.join(S, 'w', 'snap')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
dpi = 110
for a in sys.argv:
    if a.startswith('--dpi='): dpi = int(a[6:])
q = '--quarters' in sys.argv
os.makedirs(OUT, exist_ok=True)
r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(S, 't', 'plotl.ps1'), '-Dwg', DWG, '-Layouts', ','.join(args), '-OutDir', OUT], capture_output=True)
for l in args:
    p = os.path.join(OUT, l + '.pdf')
    if not os.path.exists(p): print('NO PDF', l); continue
    d = fitz.open(p); pg = d[0]; R = pg.rect
    if q:
        for i, (x0, y0) in enumerate(((0, 0), (0.5, 0), (0, 0.5), (0.5, 0.5))):
            clip = fitz.Rect(R.width * x0, R.height * y0, R.width * (x0 + 0.5), R.height * (y0 + 0.5))
            o = os.path.join(OUT, '%s_q%d.png' % (l, i + 1)); pg.get_pixmap(dpi=dpi, clip=clip).save(o); print(o)
    else:
        o = os.path.join(OUT, l + '.png'); pg.get_pixmap(dpi=dpi).save(o); print(o)
