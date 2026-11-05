S = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad\st'
scr = ''
for i, (x0, y0, x1, y1) in enumerate([(270000, 284000, 282000, 296000), (296000, 288000, 308000, 300000), (340000, 278000, 360000, 316000)]):
    scr += '_-PLOT\n_Y\nModel\nDWG To PDF.pc3\nISO без полей A3 (420.00 x 297.00 мм)\n_M\n_L\n_N\n_W\n%d,%d\n%d,%d\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\tp%d.pdf\n_N\n_Y\n' % (x0, y0, x1, y1, S, i)
scr += '_.QUIT\n_Y\n'
open('pl_tp.scr', 'w', encoding='cp1251').write(scr)
