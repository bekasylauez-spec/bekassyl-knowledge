def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
sub(a + 'v113_u02_sheet.cs', [
 ('ns.LD(0, 30, bT, 240, 7650, "Болты М20", "40Х «селект»");', 'ns.LD(0, 30, bT, 260, 7450, "Болты М20", "40Х «селект»");   // 13.11 (checker): was over the purlin bolts / cleat'),
 ('ns.SPOT(0, beams, new XYZ(X0 + 50, Y0 - 20, 7603), 1, -230, 7700);', 'ns.SPOT(0, beams, new XYZ(X0 + 50, Y0 - 20, 7603), 1, -260, 7980);   // 13.11 (checker): the shelf crossed the purlin cleat'),
 ('ns.Sheet(SN, SNAME, "А3", new double[] { 0, 4, 4 }', 'ns.Sheet(SN, SNAME, "А3", new double[] { 0, 4, 10 } /* 13.11: «32» of 2-2 hit its title */')])
sub(a + 'v113_u03_sheet.cs', [
 ('ns.LD(2, -187, 2850, -300, 2920, "К1", "");', 'ns.LD(2, -187, 2850, -310, 3010, "К1", "");'),
 ('ns.LD(2, 0, 2760, -110, 2860, "−t8", "С245");', 'ns.LD(2, 0, 2760, -110, 2880, "−t8", "С245");'),
 ('ns.LD(2, 20, 2730, -230, 2580, "Болты М16", "");', 'ns.LD(2, 20, 2730, -120, 2590, "Болты М16", "");   // 13.11 (checker): the leader crossed the column flange — inside the face now')])
print('ok')
