import io
s = io.open('prep.py', encoding='utf-8').read()
old = '''def parts(M):
    """split at support centres into parts <= PMAX"""
    E = M['E']; PMAX = pmax(M)
    if E <= PMAX: return [(0.0, E)]'''
new = '''TALL = 1150
P_LAST, P_MID = 11000.0, 19000.0
NODE0 = (1892.0, 6186.0)          # kit node «А» bbox lower-left (sheet-relative)
NODE_TALL = (11600.0, 3200.0)     # tall sheets: node «А» below the section, right of the splice table


def greedy(E0, E1, P, cuts):
    out = []; start = E0
    while E1 - start > P:
        cand = [c for c in cuts if start + 3000 < c <= start + P]
        if not cand: break
        tgt = start + (E1 - start) / math.ceil((E1 - start) / P)
        c = min(cand, key=lambda c: abs(c - tgt))
        out.append((start, c)); start = c
    out.append((start, E1))
    return out


def parts(M):
    """split at support centres into parts <= PMAX"""
    E = M['E']; PMAX = pmax(M)
    if M['h'] >= TALL:
        if E <= P_LAST: return [(0.0, E)]
        cuts = [(a + b) / 2.0 for a, b, _ in M['sups']]
        c = min([q for q in cuts if E - q <= P_LAST and q > 3000] or [max(q for q in cuts if q < E - 1)])
        return greedy(0.0, c, P_MID, cuts) + [(c, E)]
    if E <= PMAX: return [(0.0, E)]'''
assert old in s; s = s.replace(old, new)
old2 = '''def place(M, secs, SX, splices, elev_len):'''
new2 = '''def place(M, secs, SX, splices, elev_len, tables=True):'''
assert old2 in s; s = s.replace(old2, new2)
old3 = '''    ee = 3003.0 + elev_len + 2500
    if ee < 17200:
        b3 = (ee, 21900.0, 3500.0, 14300.0)
        if h >= 1150: bands.insert(0, b3)
        else: bands.append(b3)'''
new3 = '''    ee = 3003.0 + elev_len + 2500
    if h >= TALL:
        bands = [(ee, 21900.0 if tables else 30500.0, 6400.0 if splices else (3500.0 if tables else 5000.0), 14300.0)]
    elif ee < 17200: bands.append((ee, 21900.0, 3500.0, 14300.0))'''
assert old3 in s; s = s.replace(old3, new3)
old4 = '''                    part['secpos'] = place(M, secs, SX, bool(spl), u1 - u0); break'''
new4 = '''                    part['secpos'] = place(M, secs, SX, bool(spl), u1 - u0, part['tables']); break'''
assert old4 in s; s = s.replace(old4, new4)
old5 = '''            sheets.append((M, part)); k += 1'''
new5 = '''            if spl and M['h'] >= TALL: part['node'] = (NODE_TALL[0] - NODE0[0], NODE_TALL[1] - NODE0[1])
            sheets.append((M, part)); k += 1'''
assert old5 in s; s = s.replace(old5, new5)
io.open('prep.py', 'w', encoding='utf-8').write(s)

b = io.open('b4rig.py', encoding='utf-8').read()
old6 = '''        s.spans = spans; s.sups = sups'''
new6 = '''        s.spans = spans; s.sups = sups
        if s.part.get('node'):      # tall rigel: node «А» moved below the section
            s.add(t='move', h=[s.P + 'N' + r[3:] for r in NODE_A], d=list(s.part['node']))'''
assert old6 in b; b = b.replace(old6, new6)
io.open('b4rig.py', 'w', encoding='utf-8').write(b)
print('ok')
