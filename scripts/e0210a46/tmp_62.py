import ab, os, sys
x, y = float(sys.argv[1]), float(sys.argv[2])
o = ab.run([{'t': 'dimset', 'h': ['38320E'], 'tmove': 1}, {'t': 'dimtx', 'h': '38320E', 'at': [x, y]},
            {'t': 'geomdump', 'win': [-456453, -1749172, -426753, -1728172], 'file': os.path.join(ab.S, 'w', 'g62.txt')}], 'f62b')
for l in open(os.path.join(ab.S, 'w', 'g62.txt'), encoding='utf-8-sig'):
    if '|38320E|' in l: print(l.strip())
