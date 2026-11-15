# Compact comparison of the two models' string dumps.
import re, collections
D = r'D:\_claude_work\Erzhan\out'
def load(t):
    rows = []
    for ln in open(D + '\\' + t + '_strings.txt', encoding='utf-8').read().splitlines():
        c, p, s = ln.split('\t', 2); rows.append((int(c), s))
    return rows
A = {t: load(t) for t in ('S03', 'S05')}
for t, rows in A.items():
    txt = [s for c, s in rows]; cnt = dict((s, c) for c, s in rows)
    print('#####', t)
    marks = collections.Counter()
    for s in txt:
        for m in re.findall(r'\b(СЖм-?\d+|СШм-?\d+|Пм-?\d+|Фм-?\d+|ЛМм-?\d+|ЛПм-?\d+|Бм-?\d+|Км-?\d+|Пл-?\d+|Ст-?\d+|Рм-?\d+|ПМм-?\d+|Дм-?\d+)', s):
            marks[re.sub(r'-', '', m)] += 1
    byk = collections.defaultdict(set)
    for m in marks: byk[re.match(r'\D+', m).group(0)].add(int(re.search(r'\d+', m).group(0)))
    print('marks:', {k: (len(v), max(v)) for k, v in byk.items()})
    lv = set()
    for s in txt:
        for m in re.findall(r'отм\.?\s*([+-]?\d{1,2}[.,]\d{3})', s): lv.add(float(m.replace(',', '.')))
    print('levels:', sorted(lv)[:3], '...', sorted(lv)[-3:], 'n', len(lv))
    print('materials:', [s for s in txt if re.search(r'железобетон_t=|^Бетон C\d|^BI_бетон', s)][:12])
    dia = [(s, cnt[s]) for s in txt if re.fullmatch(r'Ø\d+А\d+С? \(ГОСТ 34028-2016\)', s)]
    print('bar types:', sorted(dia, key=lambda x: int(re.search(r'\d+', x[0]).group(0))))
    print('shapes:', sorted(set(s for s in txt if re.match(r'(?i)форма[_ ]?\d', s)))[:40])
    print('sheet refs max:', max([int(x) for s in txt for x in re.findall(r'КЖ-(\d{1,3})', s)] or [0]))
s3 = set(s for c, s in A['S03']);
print('##### notes only in S05')
for c, s in A['S05']:
    if s not in s3 and ('\\n2' in s or s.startswith('Примеч')) and len(s) > 60:
        k = re.sub(r'КЖ-[\d,÷\-]+', 'КЖ-#', s)
        print(' *', s[:600])
