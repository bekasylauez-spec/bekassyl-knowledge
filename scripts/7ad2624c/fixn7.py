def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
sub('D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_u09_sheet.cs', [
 ('ns.LD(0, -65, 6300, -230, 6230, "ПБ1", "");', 'ns.LD(0, -7, 6300, -230, 6230, "ПБ1", "");   // 13.11 (checker): the arrow ended in the air — on the web face now'),
 ('-400.0, 400.0, -400.0, 400.0, 100.0, 100.0, 70.0, 128.0 }', '-400.0, 400.0, -400.0, 400.0, 100.0, 100.0, 70.0, 120.0 /* 13.11: 8 mm lower, the title hit «+6,200» / mark 1 */ }')])
print('ok')
