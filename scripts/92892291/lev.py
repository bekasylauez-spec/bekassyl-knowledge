"""SPDS level mark value text fix (serialized ASCII), any length"""
import re, ab, work
def cur_text(h):
    f = work.W + r'\lm_%s.bin' % h
    ab.run([{'t': 'serdump', 'h': h, 'file': f}], 'sd')
    b = open(f, 'rb').read()
    m = re.findall(rb'[+\-]?\d{1,3}[.,]\d{3}', b)
    return m[0].decode() if m else None
def fix_ops(h, new):
    old = cur_text(h)
    if old is None or old == new: return [], old
    hx = lambda s: ('%02xee02%02x' % (len(s) + 3, len(s))) + s.encode('latin1').hex()
    return [{'t': 'serfix', 'h': h, 'raw': [[hx(old), hx(new)], [hx(old), hx(new)]]}], old
