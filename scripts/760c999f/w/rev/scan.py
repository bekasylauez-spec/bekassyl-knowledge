import json, re, collections, sys
R = 'C:/Users/Admin/AppData/Local/Temp/claude/D---------/760c999f-c28c-44e9-ba81-9cb2aa467e81/scratchpad/w/rev/'
out = open(R + 'scan.txt', 'w', encoding='utf-8')
def P(*a): print(*a, file=out)

def sheetno(t):
    L = [l.strip() for l in t.split('\n')]
    idx = [i for i, l in enumerate(L) if l == 'Камалбек']
    for i in reversed(idx):
        if i + 1 < len(L) and re.fullmatch(r'\d+(\.\d+)?', L[i + 1]): return L[i + 1]
    if re.fullmatch(r'\d+(\.\d+)?', L[0]): return L[0]
    return '?'

albums = {k: json.load(open(R + k + '.json', encoding='utf-8')) for k in ('b1', 'b2', 'km')}
sheets = {}; SH = json.load(open(R + "sheets.json"))
for k, pages in albums.items():
    sheets[k] = SH[k]
    P('==', k, 'sheets:', ' '.join(sheets[k]))
    c = collections.Counter(sheets[k]); P('  dup:', {s: n for s, n in c.items() if n > 1})

KG = {6: .222, 8: .395, 10: .617, 12: .888, 14: 1.208, 16: 1.578, 18: 1.998, 20: 2.466, 22: 2.984, 25: 3.853, 28: 4.834, 32: 6.313, 36: 7.99, 40: 9.865}
pat = {
    'broken': r'#{2,}',
    'levels>17.7': r'[+]\s?(1[89]|2\d|3\d)[,.]\d{3}',
    'storeys': r'(?i)(пят[иь]|5-?ти|шести|семи|девяти|десяти)[\s-]*этаж|5\s*этаж',
    'conc': r'[CС]\s?\d{1,2}/\d{2}|\b[BВ]\s?\d{2}(,\d)?\b',
    'W/F': r'\bW\s?\d{1,2}\b|\bF\s?\d{2,3}\b',
    'rebar': r'[AА]\s?(240|400|500)\s?[CС]?|[AА]-?(I{1,3}|IV)\b|Вр-?I|B500',
    'norms': r'(СНиП|СП РК|СН РК|ГОСТ|МСН|НТП РК)\s?[\w.\-:/*]+',
    'см.лист': r'(?i)(см\.?\s*(на\s*)?(лист[а-я]*|л\.)\s*[-–]?\s*)([\d.,\s…и-]+)',
}
for k, pages in albums.items():
    for name, rx in pat.items():
        agg = collections.defaultdict(set)
        for i, t in enumerate(pages):
            for m in re.finditer(rx, t):
                agg[re.sub(r'\s+', ' ', m.group(0)).strip()].add(sheets[k][i])
        P('\n##', k, name)
        for v, s in sorted(agg.items(), key=lambda x: -len(x[1]))[:80]:
            P('  ', repr(v), '->', ','.join(sorted(s))[:200])

# spec rows: ∅ d class L= len n unit total
P('\n## spec arithmetic (|err| > 1%)')
for k, pages in albums.items():
    for i, t in enumerate(pages):
        toks = [x.strip() for x in t.split('\n') if x.strip()]
        for j in range(len(toks) - 7):
            if toks[j] != '∅': continue
            try:
                d = int(toks[j + 1]); cls = toks[j + 2]
                if not toks[j + 3].startswith('L='): continue
                rest = toks[j + 3][2:].strip()
                q = [rest] if rest else []
                q += toks[j + 4:j + 8]
                ln = float(q[0].replace(',', '.')); n = float(q[1]); m1 = float(q[2].replace(',', '.')); mt = float(q[3].replace(',', '.'))
            except Exception:
                continue
            if d not in KG: P(k, sheets[k][i], 'p', i + 1, 'unknown d', d); continue
            e1 = ln / 1000 * KG[d]
            bad = []
            if abs(e1 - m1) > max(0.011, 0.01 * m1): bad.append('unit %.2f exp %.2f' % (m1, e1))
            if abs(m1 * n - mt) > max(0.06, 0.01 * mt): bad.append('total %.2f exp %.2f' % (mt, m1 * n))
            if bad: P(k, sheets[k][i], 'p', i + 1, 'Ø%d L=%g n=%g' % (d, ln, n), '; '.join(bad))
out.close()
