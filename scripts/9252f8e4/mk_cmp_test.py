import os
here = os.path.dirname(os.path.abspath(__file__))
s = open(r'D:\_claude_work\Kasymova\v10\cmp_v9_v10.py', encoding='utf-8').read()
reps = [
    (r"model(K + r'\v10\v10_user.txt')", r"model(K + r'\v9\v9_final.txt')"),
    (r"plates(K + r'\res_v10')", r"plates(K + r'\res_v9')"),
    (r"bars(K + r'\res_v10')", r"bars(K + r'\res_v9')"),
    (r"open(K + r'\res_v10\cmp_v9_v10.txt'", "open(" + repr(os.path.join(here, 'cmp_test.txt'))),
    ("mp = {}\nfor r in csv.DictReader(open(K + r'\\v10\\map_v9_v10.csv'), delimiter=';'):\n    if r['v10']: mp[int(r['v9'])] = int(r['v10'])",
     "mp = {i: i for i in range(1, len(mod9) + 1)}"),
]
for a, b in reps:
    assert a in s, a
    s = s.replace(a, b)
open(os.path.join(here, 'cmp_test.py'), 'w', encoding='utf-8').write(s)
print('ok')
