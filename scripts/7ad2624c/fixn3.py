def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o)
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
sub(a + 'v113_u05_sheet.cs', [
 ('ns.LD(0, uX(p), p.Z, -280, 6070, "−t8", "С245"); }', 'ns.LD(0, uX(p), p.Z, -500, 6190, "−t8", "С245"); }   // 13.11 (checker): the shelf lay on the СВ1 tube')])
# DWG: every coloured solid fill (node palette cut / surface) -> light grey; white masks stay white, greys 250..254 stay
p = 'D:/_claude_work/v113r/dwgnet/v113build.cs'
sub(p, [('''                              else if (c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByAci && c.ColorIndex == 7) { e.UpgradeOpen(); e.Color = white; nH++; }''',
'''                              else if (c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByAci && c.ColorIndex == 7) { e.UpgradeOpen(); e.Color = white; nH++; }
                              else if (!(c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByAci && c.ColorIndex >= 250) && !(c.IsByLayer || c.IsByBlock) && !(c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByColor && c.Red == 255 && c.Green == 255 && c.Blue == 255)) { e.UpgradeOpen(); e.Color = fill; nH++; }   // 13.11: node palette cut fills (red on sheet 20) — light grey as В109''')])
print('ok')
