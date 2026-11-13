def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
sub(a + 'v113_u07_sheet.cs', [
 ('new object[] { new XYZ(12000, 2900, 0), X, Z, -Y, -450.0, 450.0,', 'new object[] { new XYZ(12000, 2900, 0), X, Z, -Y, -620.0, 620.0 /* 13.11 (checker): the 1-1 marks stood on the ГС1 bodies — past the main view now */,'),
 ('ns.LD(1, -200, 7205, -330, 7330, "−t8", "С245");', 'ns.LD(1, -200, 7205, -400, 7100, "−t8", "С245");   // 13.11: the shelf lay on the Б1 flange')])
print('ok')
