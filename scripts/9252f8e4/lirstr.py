import re, sys
def strs(p, n=6):
    b = open(p, 'rb').read()
    return b, [(m.start(), m.group().decode('latin1')) for m in re.finditer(rb'[\x20-\x7e]{%d,}' % n, b)]
b1, s1 = strs(r'D:\_claude_work\Kasymova\Kasymova_v9.lir')
b2, s2 = strs(r'D:\_claude_work\Kasymova\_old_versions\Kasymova_R_1611_2230.lir')
print(len(b1), len(b2), len(s1), len(s2))
# first differing byte
n = min(len(b1), len(b2))
i = next((k for k in range(0, n, 1) if b1[k] != b2[k]), None) if False else None
import itertools
step = 1 << 16
for k in range(0, n, step):
    if b1[k:k+step] != b2[k:k+step]:
        for j in range(k, min(k+step, n)):
            if b1[j] != b2[j]:
                i = j; break
        break
print('first diff at', i)
# strings near start
for o, s in s1[:60]:
    print('A', o, s[:80])
print('----')
for o, s in s2[:60]:
    print('B', o, s[:80])
