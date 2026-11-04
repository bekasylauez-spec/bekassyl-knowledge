# full consistency check of Block 1 КЖ from scratchpad plots/dumps (read-only)
import fitz, re, os, sys, json, collections, subprocess
sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad'
C = SP + r'\w\chk'
RG = SP + r'\w\rg'
keys = ['g11', 'g12', 'sch', 'fnd', 'vyp', 'col', 'wal', 'rig', 'p71', 'p72', 'st8', 'rmp']
rx = {'g11': r'1\.\d+', 'g12': r'1\.\d+', 'sch': r'2\.\d+', 'fnd': r'3\.\d+', 'vyp': r'3\.\d+', 'col': r'4\.\d+', 'wal': r'5\.\d+', 'rig': r'6\.\d+', 'p71': r'7\.\d+', 'p72': r'7\.\d+', 'st8': r'8\.\d+', 'rmp': r'9\.\d+'}
out = open(C + r'\result.txt', 'w', encoding='utf-8')
def P(*a): print(*a, file=out); print(*a)

def sheetno(t):
    L = [l.strip() for l in t.split('\n')]
    idx = [i for i, l in enumerate(L) if l == 'Камалбек']
    for i in reversed(idx):
        for j in range(i + 1, min(i + 6, len(L))):
            if re.fullmatch(r'\d+\.\d+', L[j]): return L[j]
    c = [l for l in L if re.fullmatch(r'\d\.\d{1,2}', l)]
    return c[-1] if c else '?'

# ---- pages text ----
pages = []  # (key, sheet, text, pageidx)
for k in keys:
    f = os.path.join(C, 'pl_' + k, 'all.pdf')
    if not os.path.exists(f): P('NO PDF', k); continue
    d = fitz.open(f)
    J = json.load(open(os.path.join(C, 'pl_' + k, 'plotc.json'), encoding='utf-8'))
    for i, p in enumerate(d):
        t = p.get_text(); pages.append((k, J[i]['n'], t, i))
nums = [s for k, s, t, i in pages]
P('== sheets plotted:', len(pages)); P(' '.join(nums))
c = collections.Counter(nums); P('dup:', {s: n for s, n in c.items() if n > 1})
def key(s):
    try: return [int(v) for v in s.split('.')]
    except: return [99]
# gaps
by = collections.defaultdict(set)
for s in nums:
    if s != '?': by[int(s.split('.')[0])].add(int(s.split('.')[1]))
for g in sorted(by):
    mx = max(by[g]); miss = [n for n in range(1, mx + 1) if n not in by[g]]
    if miss: P('gap in %d.x:' % g, miss)

# ---- register from 1.1 tables ----
reg = {}
tabs = open(os.path.join(C, 'g11.tables.txt'), encoding='utf-8').read()
for ln in tabs.splitlines():
    m = re.match(r'  R\d+ h=[\d.]+ \| (\d+\.\d+) \| (.*?) \|', ln)
    if m: reg[m.group(1)] = re.sub(r'\s+', ' ', m.group(2)).strip()
P('\n== register rows:', len(reg))
P('in register but not plotted:', sorted(set(reg) - set(nums), key=key))
P('plotted but not in register:', sorted(set(nums) - set(reg) - {'?'}, key=key))

# ---- stamp titles from dumps ----
titles = {}
for k in keys:
    df = os.path.join(C, k + '_dump.txt')
    if not os.path.exists(df): continue
    dump = open(df, encoding='utf-8').read()
    for s in re.split(r'\n==== SHEET ', dump)[1:]:
        hdr, body = s.split('\n', 1); sn = hdr.split()[0]
        fr = [int(v) for v in re.search(r'\[([-\d, ]+)\]', hdr).group(1).split(',')]
        tt = [m for m in re.finditer(r'^M \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (.*)$', body, re.M)
              if int(m.group(2)) < fr[1] + 2500 and int(m.group(1)) > fr[0] + (fr[2] - fr[0]) * 0.6 and not re.fullmatch(r'\d+\.\d+', m.group(5).strip())]
        if tt: titles[sn] = re.sub(r'\s+', ' ', tt[-1].group(5).replace(' / ', ' ')).strip()
def norm(s): return re.sub(r'[\s.,;:\-–]+', ' ', s.lower().replace('ё', 'е')).strip()
P('\n== stamp title vs register name (different):')
for sn in sorted(set(reg) & set(titles), key=key):
    if norm(reg[sn]) != norm(titles[sn]): P('  %-5s reg: %s | stamp: %s' % (sn, reg[sn][:80], titles[sn][:80]))

# ---- references ----
P('\n== references to missing sheets:')
exist = set(nums) | set(reg)
for k, s, t, i in pages:
    tt = t.replace('\n', ' ')
    for m in re.finditer(r'(?:лист[а-я]*|л\.)\s*(?:КЖ\s*-?\s*)?[-–]?\s*((?:\d+\.\d+)(?:\s*(?:[,;]|и|\.{2,}|…|-|–)\s*(?:КЖ\s*-?\s*)?\d+\.\d+)*)', tt, re.I):
        refs = re.findall(r'\d+\.\d+', m.group(1))
        for r in refs:
            if r not in exist and not re.fullmatch(r'\d\.\d{3}', r): P('  %s (%s): "%s" -> %s missing' % (s, k, m.group(0)[:50], r))
    for m in re.finditer(r'КЖ\s*-\s*(\d+\.\d+)', tt):
        if m.group(1) not in exist: P('  %s (%s): КЖ-%s missing' % (s, k, m.group(1)))

# ---- keywords ----
P('\n== suspicious texts:')
pat = {'####': r'#{2,}', 'storeys': r'(?i)(пят[иь]|5-?ти|шест[иь]|семи|девяти)[\s-]*этаж', 'high levels': r'[+]\s?(2[3-9]|3\d)[,.]\d{3}', '+3.800': r'\+3[.,]800',
       'latin marks': r'\b(Bn|Km|Pm|Sm|Fm|Lm)-\d', 'old gost': r'14098-91|Э-?42|B7[.,]5|А-I{1,3}\b|Вр-?I\b', 'typos': r'(?i)данные лист|стена См|лестицы|основных арматуры|Землянные|обьект', 'analog names': r'Бисенов|девятиэтаж|17[.,]5х22[.,]4'}
for k, s, t, i in pages:
    for name, r in pat.items():
        hits = sorted(set(re.sub(r'\s+', ' ', m.group(0)) for m in re.finditer(r, t)))
        if hits: P('  %s (%s) %s: %s' % (s, k, name, hits[:6]))

# ---- spec arithmetic ----
KG = {5: .144, 6: .222, 8: .395, 10: .617, 12: .888, 14: 1.208, 16: 1.578, 18: 1.998, 20: 2.466, 22: 2.984, 25: 3.853, 28: 4.834, 32: 6.313, 36: 7.99, 40: 9.865}
P('\n== spec arithmetic (|err| > 1%):')
for k, s, t, i in pages:
    toks = [x.strip() for x in t.split('\n') if x.strip()]
    for j in range(len(toks) - 7):
        if toks[j] not in ('∅', 'Ф', 'Ø'): continue
        try:
            d = int(toks[j + 1]); cls = toks[j + 2]
            if not toks[j + 3].startswith('L='): continue
            rest = toks[j + 3][2:].strip(); q = [rest] if rest else []
            q += toks[j + 4:j + 8]
            ln = float(q[0].replace(',', '.')); n = float(q[1].replace(',', '.')); m1 = float(q[2].replace(',', '.')); mt = float(q[3].replace(',', '.'))
        except Exception: continue
        if d not in KG: continue
        e1 = ln / 1000 * KG[d]; bad = []
        if abs(e1 - m1) > max(0.011, 0.01 * m1): bad.append('unit %.2f exp %.2f' % (m1, e1))
        if abs(m1 * n - mt) > max(0.06, 0.012 * mt): bad.append('total %.2f exp %.2f' % (mt, m1 * n))
        if bad: P('  %s (%s) Ø%d L=%g n=%g: %s' % (s, k, d, ln, n, '; '.join(bad)))
out.close()
