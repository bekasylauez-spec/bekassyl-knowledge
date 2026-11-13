def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
sub(a + 'v113_u04_sheet.cs', [
 ('new object[] { new XYZ(0, 0, -200), X, Y, Z, -440.0, 720.0,', 'new object[] { new XYZ(0, 0, -200), X, Y, Z, -370.0 /* 13.11 (checker): the cut ends crossed the 39/300 chain */, 720.0,'),
 ('new object[] { new XYZ(0, 0, -90), X, Y, Z, -440.0, 720.0,', 'new object[] { new XYZ(0, 0, -90), X, Y, Z, -370.0 /* 13.11: as 1-1 */, 720.0,'),
 ('ns.DIM(0, new[] { -400.0, -370, -70, -31.5 }, false, -560, -340);', 'ns.DIM(0, new[] { -400.0, -370, -70, -31.5 }, false, -640, -340);   // 13.11: outside the section marks 1, 3'),
 ('ns.LD(0, p.X, p.Z, 470, -260, "−t8", "С245"); }', 'ns.LD(0, p.X, p.Z, 470, -330, "−t8", "С245"); }   // 13.11 (checker): it lay over «Болты М16»')])
print('ok')
