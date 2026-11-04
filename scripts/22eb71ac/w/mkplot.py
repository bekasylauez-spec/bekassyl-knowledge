import sys, json
# args: out.scr  name:x0,y0,x1,y1 ...
out = sys.argv[1]; L = ['(setvar "FILEDIA" 0)', '(setvar "BACKGROUNDPLOT" 0)']
pd = sys.argv[2]
for a in sys.argv[3:]:
    pp = a.split(':'); n, w = pp[0], pp[1]; x0, y0, x1, y1 = w.split(',')
    fm = pp[2] if len(pp) > 2 else 'A2'
    paper = 'ISO без полей A3 (420.00 x 297.00 мм)' if fm in ('A3', 'A3P') else 'ISO без полей A2 (594.00 x 420.00 мм)'
    ori = '_P' if fm == 'A3P' else '_L'
    L += ['_-PLOT', '_Y', 'Model', 'DWG To PDF.pc3', paper, '_M', ori, '_N', '_W',
          '%s,%s' % (x0, y0), '%s,%s' % (x1, y1), '_F', '_C', '_Y', 'monochrome.ctb', '_Y', '_A', '"%s\%s.pdf"' % (pd, n), '_N', '_Y']
L += ['_.QUIT', '_Y', '']
open(out, 'w', encoding='cp1251').write('\n'.join(L))
