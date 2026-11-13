p = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_u07v_sheet.cs'
s = open(p, encoding='utf-8').read()
o = 'ns.CIRCLE(0, 0, 330, "7в", "6");'
assert o in s; s = s.replace(o, 'ns.CIRCLE(0, -300, 360, "7в", "6");   /* 13.11 (checker): at u 0 the 1-1 cut line ran through it */', 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
