import io
s = io.open('prep.py', encoding='utf-8').read()
old = '''def parts(M):
    """split at support centres into parts <= PMAX"""
    E = M['E']
    if E <= PMAX: return [(0.0, E)]'''
new = '''def pmax(M):
    """tall rigels: sections go right of the elevation (A4x3 height is short) -> shorter parts"""
    if M['h'] < 1150: return PMAX
    return 11600 if M['b'] < 700 else 11000


def parts(M):
    """split at support centres into parts <= PMAX"""
    E = M['E']; PMAX = pmax(M)
    if E <= PMAX: return [(0.0, E)]'''
assert old in s; s = s.replace(old, new)
old2 = '''    ee = 3003.0 + elev_len + 2500
    if ee < 16000: bands.append((ee, 21900.0, 3500.0, 14300.0))'''
new2 = '''    ee = 3003.0 + elev_len + 2500
    if ee < 17200:
        b3 = (ee, 21900.0, 3500.0, 14300.0)
        if h >= 1150: bands.insert(0, b3)
        else: bands.append(b3)'''
assert old2 in s; s = s.replace(old2, new2)
io.open('prep.py', 'w', encoding='utf-8').write(s)
print('ok')
