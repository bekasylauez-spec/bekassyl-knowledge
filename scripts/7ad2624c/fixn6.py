def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
sub('D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_u08_sheet.cs', [
 ('ns.CIRCLE(0, 330, 7620, "8", "7");', 'ns.CIRCLE(0, 350, 7750, "8", "7");   // 13.11 (checker): the «Болты М16» shelf entered the circle'),
 ('ns.CIRCLE(3, 360, 7340, "8а", "7");', 'ns.CIRCLE(3, 370, 7440, "8а", "7");   // 13.11: as node 8'),
 ('new object[] { new XYZ(X0, 3000, 7400), X, Y, Z, -440.0, 440.0,', 'new object[] { new XYZ(X0, 3000, 7400), X, Y, Z, -380.0, 380.0 /* 13.11 (checker): the 2-2 mark stood outside the frame */,')])
print('ok')
