"""SPDS level mark texts: relative value + absolute value (any length), via serdump/serfix raw"""
import re, os, ab
W = os.path.join(ab.S, 'w')
hx = lambda s: ('%02xee02%02x' % (len(s) + 3, len(s))) + s.encode('latin1').hex()
def texts(hs):
    ab.run([{'t': 'serdump', 'h': h, 'file': os.path.join(W, 'lm_%s.bin' % h)} for h in hs], 'sd')
    r = {}
    for h in hs:
        b = open(os.path.join(W, 'lm_%s.bin' % h), 'rb').read()
        r[h] = sorted(set(m.decode() for m in re.findall(rb'[+\-]?\d{1,3}[.,]\d{2,3}', b)))
    return r
def ops(h, pairs):
    return [{'t': 'serfix', 'h': h, 'raw': [[hx(o), hx(n)] for o, n in pairs for _ in range(2)]}] if pairs else []
