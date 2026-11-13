import re
def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, (p, o[:80])
        s = s.replace(o, n)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
# u04: sheet instance at column axis 2 row А (x 6000), СВ1 toward +x — same geometry as the former axis 1 (u = x − 6000 by the view origins)
sub(a + 'v113_u04_sheet.cs', [
 ('// СВ1 lower end at the column x = 0, y = 0:', '// 13.11 r10 (СВ1 by LIRA): the instance is the column at axis 2 row А (x 6000), СВ1 toward +x; the view origins / spot / 3D boxes are +6000, u stays relative.\n    // СВ1 lower end at the column x = 0, y = 0 (relative):'),
 ('new object[] { new XYZ(0, -60, 0), X, Z, -Y, -350.0, 650.0', 'new object[] { new XYZ(6000, -60, 0), X, Z, -Y, -350.0, 650.0'),
 ('new object[] { new XYZ(0, 0, -200), X, Y, Z,', 'new object[] { new XYZ(6000, 0, -200), X, Y, Z,'),
 ('new object[] { new XYZ(200, 0, 0), Y, Z, X,', 'new object[] { new XYZ(6200, 0, 0), Y, Z, X,'),
 ('new object[] { new XYZ(0, 0, -90), X, Y, Z,', 'new object[] { new XYZ(6000, 0, -90), X, Y, Z,'),
 ('ns.SPOT(0, baseDs, new XYZ(250, 100, -370), 1, 650, -410);', 'ns.SPOT(0, baseDs, new XYZ(6250, 100, -370), 1, 650, -410);'),
 ('new XYZ(-350, -400, -420), new XYZ(700, 400, 300)', 'new XYZ(5650, -400, -420), new XYZ(6700, 400, 300)'),
 ('2. Узел 4 показан у колонны по оси 1 ряда А; у колонн 2 (ряды А, В), 6 и 7 (ряд В) - то же (зеркально).', '2. Узел 4 показан у колонны по оси 2 ряда А; у колонн по осям 2, 3, 8, 9 рядов А и В - то же (у осей 3 и 9 - зеркально).')])
# u05: instance at axis 3 row А (x 12000), СВ1 from −x (was axis 2)
sub(a + 'v113_u05_sheet.cs', [
 ('double X0 = 6000;', 'double X0 = 12000;   /* 13.11 r10: СВ1 by LIRA — the instance at axis 3 (was 2) */'),
 ('var E = new XYZ(5790, 0, 6187.5);', 'var E = new XYZ(11790, 0, 6187.5);'),
 ('2. Узел 5 показан у колонны по оси 2 ряда А; у колонн 1 (ряды А, В), 6 и 7 - то же (зеркально). У колонн по осям 1 и 10 (балка Б2) фасонка выше - до ребра колонны.', '2. Узел 5 показан у колонны по оси 3 ряда А; у колонн по осям 2, 3, 8, 9 рядов А и В - то же (у осей 2 и 8 - зеркально).')])
# u06: node at x 9000 (bay 2–3)
sub(a + 'v113_u06_sheet.cs', [
 ('double X0 = 3000;', 'double X0 = 9000;   /* 13.11 r10: СВ1 by LIRA — bay 2–3 (was 1–2) */'),
 ('var Eur = new XYZ(3199.9, 0, 2949.88);', 'var Eur = new XYZ(9199.9, 0, 2949.88);'),
 ('var Ell = new XYZ(2777.47, 0, 2470.05);', 'var Ell = new XYZ(8777.47, 0, 2470.05);'),
 ('var Eul = new XYZ(2800.1, 0, 2949.88);', 'var Eul = new XYZ(8800.1, 0, 2949.88);'),
 ('2. Узел 6 показан в пролёте между осями 1 и 2 ряда А; в пролёте 6-7 ряда В - то же; в пролёте 6-7 ряда А - только верхние связи.', '2. Узел 6 показан в пролёте между осями 2 и 3 ряда А; в пролётах 2-3 и 8-9 рядов А и В - то же.')])
print('ok')
