# mkplot.py <scr_out> <pdf_prefix> x,y,w,h [x,y,w,h ...]  -> accoreconsole -PLOT script (window, fit, A3)
import sys, os
out, pref = sys.argv[1], sys.argv[2]
L = []
for i, a in enumerate(sys.argv[3:]):
    x, y, w, h = map(float, a.split(','))
    o = 'L' if w >= h else 'P'
    L += ['_-PLOT', '_Y', 'Model', 'DWG To PDF.pc3', 'ISO без полей A3 (420.00 x 297.00 мм)', '_M', o, '_N', '_W',
          f'{x},{y}', f'{x + w},{y + h}', '_F', '_C', '_Y', 'monochrome.ctb', '_Y', '_A',
          os.path.abspath(f'{pref}_{i}.pdf'), '_N', '_Y']
L += ['_.QUIT', '_Y']
open(out, 'wb').write(('\r\n'.join(L) + '\r\n').encode('cp1251'))
