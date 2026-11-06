import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'net'))
import gx
D = os.path.join(gx.S, 'mc')
H = sys.argv[1:]
fn = lambda h: os.path.join(D, h.replace(':', '_') + '.bin')
print(gx.run([{'t': 'mcdump', 'h': h, 'file': fn(h)} for h in H], 'mcd')[-200:])
for h in H:
    b = open(fn(h), 'rb').read()
    s1 = re.findall(rb'[+\-]?\d[\d.,]{3,8}', b)
    s2 = re.findall(rb'(?:[+\-.,0-9]\x00){4,9}', b)
    print(h, sorted(set(s1))[:15], sorted(set(x.decode('utf-16le') for x in s2))[:10])
