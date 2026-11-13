import io
sp = r'C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad'
p = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\rmc_brace_lib.cs'
s = open(p, encoding='utf-8').read()
add = open(sp + r'\xadd.txt', encoding='utf-8').read()
marker = '    // ---------------- 2D көпбұрышта нүкте'
assert marker in s
if 'FindCrosses' not in s:
    s = s.replace(marker, add + marker, 1)
cls = ('class BX { public string Mark; public FamilyInstance Solid, H1, H2; public int E1, E2; public XYZ C; public double R1, R2; }\n'
       'class BXSpec { public string Tag; public XYZ C; public double B = 140, Ti = 8, Wi = 180, CapW = 180, CapH = 140, Tc = 4, LIn = 100, Kfi = 6, Kfc = 4, Kfm = 6; }\n'
       'class BXRes { public Solid Ins; public List<Solid> Caps = new List<Solid>(); public List<Solid> WIns = new List<Solid>(), WCap = new List<Solid>(), WMon = new List<Solid>(); public double Dc, InsLen, TubeCut, InsVol, CosAngle; }\n')
if 'class BXSpec' not in s:
    s = s.replace('class BSx {', cls + 'class BSx {', 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
