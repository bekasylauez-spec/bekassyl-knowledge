import io
p="D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_u09_sheet.cs"; s=io.open(p,encoding="utf-8-sig").read()
for o,n in [('ns.DIM(0, new[] { 6200.0, 6500, 6520 }, false, 450, 340);','ns.DIM(0, new[] { 6200.0, 6500, 6520 }, false, -450, -340);'),
            ('ns.LD(0, -230, 6470, -390, 6330, "Болты М16", "кл. 8.8");','ns.LD(0, -230, 6470, -360, 6300, "Болты М16", "кл. 8.8");'),
            ('ns.LD(0, 300, 6510, 410, 6440, "−t20", "С245");','ns.LD(0, 300, 6510, 390, 6410, "−t20", "С245");'),
            ('ns.CIRCLE(0, 420, 6180, "9", "5");','ns.CIRCLE(0, 420, 6200, "9", "5");')]:
    if o not in s: print("MISSING",o[:50])
    s=s.replace(o,n,1)
io.open(p,"w",encoding="utf-8").write(s); print("ok")
