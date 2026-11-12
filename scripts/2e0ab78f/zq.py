import sys; sys.path.insert(0, r'D:\_claude_work\otst\s1')
# -*- coding: utf-8 -*-
"""тексеріс суреті: python s1_zoomq.py <парақ> x0 y0 x1 y1 [dpi] → png\s1_zoom.png (парақ координатасы, мм модель)"""
import sys, s1_run, s1_lib as L
n = sys.argv[1]; x0, y0, x1, y1 = map(float, sys.argv[2:6]); dpi = int(sys.argv[6]) if len(sys.argv) > 6 else 200
X = L.SHEETX[n]
print(s1_run.plot([('s1_zoom', X + x0, L.ROW_Y + y0, X + x1, L.ROW_Y + y1)], dpi))
