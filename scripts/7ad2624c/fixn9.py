def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
sub('D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_u11_sheet.cs', [
 ('ns.DIM(0, new[] { -270.0, -185, -160, -150, 0, 150 }, true, 2780, 2850);',
  'ns.DIM(0, new[] { -270.0, -185, -150, 0, 150 }, true, 2780, 2850); ns.DIM(0, new[] { -185.0, -160, -150 }, true, 2730, 2850);   // 13.11 (checker): «25» and «10» overlapped — the two small ones on their own chain (texts go past its ends)'),
 ('ns.DIM(0, new[] { 2870.0, 2905, 2975, 3010 }, false, -420, -300);', 'ns.DIM(0, new[] { 2870.0, 2905, 2975, 3010 }, false, -520, -300);   // 13.11 (checker): the 35/70/35 chain lay on the Рф1 body — past the view edge now')])
print('ok')
