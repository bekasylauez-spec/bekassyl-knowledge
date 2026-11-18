import re, sys
for p in sys.argv[1:]:
    b = open(p, 'rb').read()
    crlf = b.count(b'\r\n')
    lone_cr = len(re.findall(rb'\r(?!\n)', b))
    bare_lf = len(re.findall(rb'(?<!\r)\n', b))
    print(p)
    print('  CRLF %d | lone CR %d | bare LF %d | bytes %d' % (crlf, lone_cr, bare_lf, len(b)))
    t = b.decode('utf-8')
    for i, l in enumerate(t.splitlines(), 1):
        if 'x=32' in l and ('Қалсын' in l or 'консол' in l or 'stub' in l):
            print('  %d: %s' % (i, l[:170]))
