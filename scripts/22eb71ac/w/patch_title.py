BS = chr(92)
NEW = ("    def title(s, text, x, y, cx=None):\n"
       "        # Bekassyl 31.10 sample: one line, underlined, layer 0, Standard, 3 mm on paper, centred (MText middle-centre)\n"
       "        h = 3.0 * s.sc; w = len(text) * 0.75 * h + 2 * h\n"
       "        c = cx if cx is not None else x + w / 2\n"
       "        add(t='mtext', at=s.P(c, y - h / 2), h=h, w=w, att=5, style='Standard', layer='0', s='{" + BS + BS + "L' + text + '}')\n")
NEW6 = ("    def title(s, text, x, y, cx=None):\n"
        "        h = 300.0; w = len(text) * 0.75 * h + 2 * h                     # paper 1:100, one line, centred\n"
        "        c = cx if cx is not None else x + w / 2 / s.k\n"
        "        add(t='mtext', at=s.P(c, y - h / 2 / s.k), h=h, w=w, att=5, style='Standard', layer='0', s='{" + BS + BS + "L' + text + '}')\n")
for p, new, nlines in (('common.py', NEW, 4), ('gen1.py', NEW, 4), ('gen6.py', NEW6, 2)):
    L = open(p, encoding='utf-8').read().split('\n')
    i = next(k for k, l in enumerate(L) if l.startswith('    def title(s, text, x, y'))
    L[i:i + nlines] = new.rstrip('\n').split('\n')
    open(p, 'w', encoding='utf-8').write('\n'.join(L))
    print(p, 'title at line', i + 1)
