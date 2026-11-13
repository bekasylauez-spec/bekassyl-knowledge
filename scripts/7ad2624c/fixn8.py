def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
sub('D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_u10_sheet.cs', [
 ('new object[] { new XYZ(0, Y0, 7400), X, Y, Z, -300.0, 300.0, -520.0, 520.0,', 'new object[] { new XYZ(0, Y0, 7400), X, Y, Z, -300.0, 300.0, -430.0, 430.0 /* 13.11 (checker): the 2-2 mark stood outside the frame */,'),
 ('ns.LD(0, 165, 7275, 330, 7110, "Болты М16", "⟂ скату");', 'ns.LD(0, 165, 7275, 330, 7110, "Болты М16", "перпендикулярно скату");   // 13.11: «⟂» came out in Segoe UI in the DWG')])
print('ok')
