p = r'D:\_claude_work\v113r\dwgnet\v113build.cs'
s = open(p, encoding='utf-8').read()
old = '                        tx(num, -32.5); if (num == "1.1") tx(listov.ToString(), -15);'
new = r'''                        tx(num, -32.5); if (num == "1.1") tx(listov.ToString(), -15);
                        // 13.11 (checker): «Согласовано» block of the В109 sheets — left margin x 5…20, y 90…155 mm from the sheet corner (measured on the В109 PDF, every sheet)
                        { double W = r[2].EndsWith("А3х3") ? 891 : r[2].Contains("книжный") ? 297 : r[2].EndsWith("А2") ? 594 : 420, x0 = -W;
                          Action<double, double, double, double, LineWeight> ln = (xa, ya, xb, yb, lw) => { var li = new Line(new Point3d(x0 + xa, ya, 0), new Point3d(x0 + xb, yb, 0)) { Layer = "0", LineWeight = lw, ColorIndex = 7 }; lbtr.AppendEntity(li); t.AddNewlyCreatedDBObject(li, true); };
                          ln(5, 90, 5, 155, LineWeight.LineWeight030); ln(5, 90, 20, 90, LineWeight.LineWeight030); ln(5, 155, 20, 155, LineWeight.LineWeight030); ln(20, 90, 20, 155, LineWeight.LineWeight030);
                          ln(10, 90, 10, 155, LineWeight.LineWeight030); ln(15, 90, 15, 155, LineWeight.LineWeight009);
                          foreach (var yy in new[] { 110.0, 130.0, 145.0 }) ln(10, yy, 20, yy, LineWeight.LineWeight030);
                          var sg = new DBText { TextString = "Согласовано", Height = 3.5, TextStyleId = sty, Layer = "TEXT 2.5", Rotation = Math.PI / 2, Position = new Point3d(x0 + 8.9, 92.0, 0), ColorIndex = 7 };
                          lbtr.AppendEntity(sg); t.AddNewlyCreatedDBObject(sg, true); }'''
assert old in s; s = s.replace(old, new, 1)
# Segoe UI symbol in a Revit note (sheet 26)
old = '                          var mt0 = e as MText;'
new = '                          var mt1 = e as MText; if (mt1 != null && mt1.Contents.Contains("⟂")) { mt1.UpgradeOpen(); mt1.Contents = mt1.Contents.Replace("⟂ ", "перпендикулярно ").Replace("⟂", "перпендикулярно"); }\n                          var mt0 = e as MText;'
assert old in s; s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
