import ezdxf, sys
doc = ezdxf.readfile(sys.argv[1])
e = doc.entitydb['1285AB']
s = doc.styles.get(e.dxf.style)
print('style', e.dxf.style, s.dxf.font, s.dxf.get('bigfont'), s.dxf.width)
n = 0
for t in doc.modelspace().query('MTEXT'):
    if '²' in t.text or '\\U+00B2' in t.text:
        print('sq', t.dxf.style, repr(t.text[:100]))
        n += 1
        if n > 3:
            break
