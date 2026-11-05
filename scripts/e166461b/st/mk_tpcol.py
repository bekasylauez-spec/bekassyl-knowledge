import os
S = os.path.dirname(os.path.abspath(__file__))
scr = '_-PLOT\n_Y\nModel\nDWG To PDF.pc3\nISO без полей A2 (594.00 x 420.00 мм)\n_M\n_L\n_N\n_W\n264717,271898\n294417,292898\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n' + os.path.join(S, 'tpcol.pdf') + '\n_N\n_Y\n_.QUIT\n_Y\n'
open(os.path.join(S, 'pl_tpcol.scr'), 'w', encoding='cp1251').write(scr)
