import gx, sys, subprocess
mark, k, pi = sys.argv[1], int(sys.argv[2]), sys.argv[3]
SX = 172179 + 31500 * k
print(gx.run([{'t': 'eraseregion', 'win': [SX + 11, 455950, SX + 31489, 470780], 'mode': 'intersect'},
              {'t': 'eraseregion', 'win': [2599000 + 20000 * k, 250000, 2616000 + 20000 * k, 400000], 'mode': 'intersect'}, {'t': 'save'}], 'er')[-20:])
r = subprocess.run([sys.executable, '-X', 'utf8', 'run2.py', mark, str(k), pi, '--import'], capture_output=True, text=True, encoding='utf-8')
print('\n'.join(l for l in r.stdout.splitlines() if not l.startswith('R')), r.stderr[-1500:])
