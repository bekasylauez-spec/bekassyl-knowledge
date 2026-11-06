# Generate every column sheet from types/types.json: sheet k at SX = 264717 + 29700*(k-1) (adjacent to the schema sheet)
import json, os, subprocess, sys
import gx
T = json.load(open(os.path.join(gx.S, 'types', 'types.json'), encoding='utf-8'))
only = sys.argv[1:]
for i, t in enumerate(T):
    if only and t['mark'] not in only: continue
    t = dict(t); t['SX'] = 264717 + 29700 * i; t['SY'] = 271898
    p = os.path.join(gx.S, 'types', 't_%s.json' % t['mark'].replace('Км-', '').replace('.', '_'))
    json.dump(t, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['bash', os.path.join(gx.S, 'net', 'regen.sh'), p, str(t['SX'])], capture_output=True)
    out = r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
    bad = [l for l in out.splitlines() if 'Error' in l or 'Traceback' in l or 'errors 1' in l]
    print(t['mark'], t['sheet'], 'SX', t['SX'], 'OK' if not bad else bad[:3])
