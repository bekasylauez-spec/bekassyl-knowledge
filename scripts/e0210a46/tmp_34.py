import ab, os
ops = [{'t': 'dimdef', 'h': ['367CA4']}]
for h, sl in (('367F5C', -826765), ('367F83', -820765), ('367FB5', -814765), ('36807D', -790765)):
    ops.append({'t': 'dimtx', 'h': h, 'at': [sl + 1651, -1735416]})
ops += [{'t': 'geomdump', 'win': [-840003, -1749172, -750903, -1707172], 'file': os.path.join(ab.S, 'w', 'g34.txt')}, {'t': 'save'}]
print(ab.run(ops, 'f34b')[-80:])
for l in open(os.path.join(ab.S, 'w', 'g34.txt'), encoding='utf-8-sig'):
    if l.startswith('T|') and any(h in l for h in ('367F5C', '367F83', '367FB5', '36807D', '367CA4', '367FE7')): print(l.strip())
