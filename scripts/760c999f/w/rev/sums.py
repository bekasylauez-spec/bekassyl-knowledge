import json, re
S = json.load(open('sheets.json'))
A = {k: json.load(open(k + '.json', encoding='utf-8')) for k in ('b1', 'b2')}
num = lambda s: float(s.replace(',', '.'))
isnum = lambda s: re.fullmatch(r'-?\d+([.,]\d+)?', s) is not None
for k, pages in A.items():
    for i, t in enumerate(pages):
        T = [x.strip() for x in t.split('\n') if x.strip()]
        for j in range(len(T) - 3):
            # header end: 'Примечан' 'ие' <name> <total>
            if T[j] == 'ие' and T[j - 1] == 'Примечан' and j + 2 < len(T) and isnum(T[j + 2]) and not isnum(T[j + 1]):
                name, total = T[j + 1], num(T[j + 2])
                s = 0.0; rows = 0; q = j + 3
                while q < len(T) and not T[q].startswith('Материалы') and T[q] != 'Спецификация элементов':
                    if T[q].startswith('L='):
                        rest = T[q][2:].strip(); v = ([rest] if rest else []) + T[q + 1:q + 5]
                        try: s += num(v[3]); rows += 1
                        except Exception: pass
                    if T[q] in ('данный лист',) or re.fullmatch(r'(лист|л\.)\s*[\d.]+', T[q]):
                        try: s += num(T[q + 4]); rows += 1
                        except Exception: pass
                    q += 1
                flag = '' if abs(s - total) <= max(0.05, total * 0.002) else '  <-- DIFF %.2f' % (s - total)
                if flag or True:
                    print(k, S[k][i], name, 'header', total, 'sum', round(s, 2), 'rows', rows, flag)
