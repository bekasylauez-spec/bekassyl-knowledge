"""BEKA-2 helpers: copy analog sheets to new slots"""
import ext, ab, sheets, plan
W = ab.S + r'\w'
_E0 = None
def E0():
    global _E0
    if _E0 is None: _E0 = ext.load(W + r'\ext0.txt')
    return _E0

def copy_sheet(sheet):
    f = sheets.FRAME[sheet][1]
    inn = [e for e in E0() if ext.inside(e, f, 1)]
    d = sheets.shift(sheet)
    tag = sheet.replace('.', '')
    out = ab.run([{'t': 'clonexf', 'hs': [e.h for e in inn], 'd': list(d), 'pre': 'C%s_' % tag}, {'t': 'save'}], 'c' + tag)
    print(sheet, len(inn), [l for l in out.splitlines() if 'errors' in l][:1])

def win(sheet, pad=100):
    f = sheets.FRAME[sheet][1]; sx, sy = sheets.slot(sheet)
    return (sx - pad, sy - pad, sx + (f[2] - f[0]) + pad, sy + (f[3] - f[1]) + pad)

def loc(sheet, x, y):
    sx, sy = sheets.slot(sheet); return [sx + x, sy + y]
