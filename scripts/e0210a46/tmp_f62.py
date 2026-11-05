import ab, os
o = ab.run([{'t': 'dimdef', 'h': ['38320E']}, {'t': 'dimtx', 'h': '345118', 'at': [-1536114, -1716164]},
            {'t': 'geomdump', 'win': [-456453, -1749172, -426753, -1728172], 'file': os.path.join(ab.S, 'w', 'g62.txt')},
            {'t': 'geomdump', 'win': [-1552803, -1749172, -1463703, -1707172], 'file': os.path.join(ab.S, 'w', 'g21.txt')}], 'f62')
print(o[-150:])
for f, h in (('g62', '38320E'), ('g21', '345118')):
    for l in open(os.path.join(ab.S, 'w', f + '.txt'), encoding='utf-8-sig'):
        if l.startswith('T|' + h): print(l.strip())
