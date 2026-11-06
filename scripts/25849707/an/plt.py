import subprocess, sys, os
P = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad\an'
def plot(dwg, name, x0, y0, x1, y1, paper='ISO без полей A0 (841.00 x 1189.00 мм)', orient='_P'):
    pdf = os.path.join(P, name + '.pdf')
    scr = ('(setvar "FILEDIA" 0)\n_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n'
           % (paper, orient, x0, y0, x1, y1, pdf.replace(os.sep, '/')))
    sp = os.path.join(P, 'pl_' + name + '.scr')
    open(sp, 'w', encoding='cp1251').write(scr)
    if os.path.exists(pdf): os.remove(pdf)
    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(P, 'run.ps1'), dwg, sp, os.path.join(P, 'pl_' + name + '.log')])
    return pdf
if __name__ == '__main__':
    a = sys.argv
    print(plot(a[1], a[2], *map(float, a[3:7]), **({'paper': a[7]} if len(a) > 7 else {})))
