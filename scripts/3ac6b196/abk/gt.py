import sys; sys.stdout.reconfigure(encoding='utf-8')
import ezdxf, re
d = ezdxf.readfile(sys.argv[1]); pat = re.compile(sys.argv[2], re.I)
U = re.compile('\\\\U\\+([0-9A-Fa-f]{4})')
def dec(s): return U.sub(lambda g: chr(int(g.group(1), 16)), s)
for lay in [d.modelspace()] + [l for l in d.layouts if l.name != 'Model']:
    for e in lay.query('TEXT MTEXT'):
        t = dec(e.plain_text() if e.dxftype() == 'MTEXT' else e.dxf.text)
        if pat.search(t): print(round(e.dxf.insert.x), round(e.dxf.insert.y), t.replace('\n', ' | ')[:220])
