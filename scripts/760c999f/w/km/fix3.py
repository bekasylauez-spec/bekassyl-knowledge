import json
o = json.load(open('km3_ops.json', encoding='utf-8'))
refs = {(6, 0): [3, 0], (6, 1): [3, 1], (12, 0): [3, 0], (12, 1): [3, 1], (0, 4): [0, 3]}
for c in o[0]['cells']:
    k = (c[0], c[1])
    if k in refs and len(c) == 3: c.append(refs[k])
    if k == (0, 4): c[2] = '{\\C256;Масса металла по элементам конструкций, т}'
json.dump(o, open('km3_ops.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(o[0]['cells'])
