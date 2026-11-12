import io
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
old = "        var o = (XYZ)df[0]; var r = (XYZ)df[1]; var up = (XYZ)df[2]; var dr = (XYZ)df[3]; double dep = (double)df[8];"
new = ("        var o = (XYZ)df[0]; if (Math.Abs(o.Y) < 400) o = new XYZ(o.X, o.Y - 16, o.Z); else if (Math.Abs(o.Y - 12000) < 400) o = new XYZ(o.X, o.Y + 16, o.Z); df[0] = o;   // 12.11 (r02, №103): К1 axis 16 outside the row — views, dims and leaders follow\n"
       "        var r = (XYZ)df[1]; var up = (XYZ)df[2]; var dr = (XYZ)df[3]; double dep = (double)df[8];")
for n in ["03", "04", "05", "06", "07", "07v", "08", "11"]:
    p = A + "v113_u%s_sheet.cs" % n
    s = io.open(p, encoding="utf-8-sig").read()
    if old not in s: print("MISSING", n); continue
    s = s.replace(old, new, 1); io.open(p, "w", encoding="utf-8").write(s); print("ok", n)
p = A + "v113_nsheet_lib.cs"; s = io.open(p, encoding="utf-8-sig").read()
if old in s: s = s.replace(old, new, 1); io.open(p, "w", encoding="utf-8").write(s); print("ok lib")
p = A + "v113_u01_sheet.cs"; s = io.open(p, encoding="utf-8-sig").read()
o1 = "double X0 = 12000, Y0 = 0;"
if o1 in s: s = s.replace(o1, "double X0 = 12000, Y0 = -16;   // 12.11 (r02): К1 axis 16 outside row А", 1); io.open(p, "w", encoding="utf-8").write(s); print("ok u01")
else: print("MISSING u01")
