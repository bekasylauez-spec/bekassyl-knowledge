p = r'D:\_claude_work\v113r\dwgnet\v113build.cs'
s = open(p, encoding='utf-8').read()
# 1) stamp style renamed in the stamp db so that a Revit «Isocpeur» (upright) in a sheet does not replace it (checker 13.11: stamp upright on 3, 6, 8–12, 16–31)
old = '                var tst = (TextStyleTable)t.GetObject(dst.TextStyleTableId, OpenMode.ForRead); styIso = tst.Has("Isocpeur") ? tst["Isocpeur"] : dst.Textstyle;'
new = ('                var tst = (TextStyleTable)t.GetObject(dst.TextStyleTableId, OpenMode.ForRead); styIso = tst.Has("Isocpeur") ? tst["Isocpeur"] : dst.Textstyle;\n'
       '                if (tst.Has("Isocpeur")) { var sr = (TextStyleTableRecord)t.GetObject(tst["Isocpeur"], OpenMode.ForWrite); sr.Name = "Isocpeur_В109"; }')
assert old in s; s = s.replace(old, new, 1)
old = 'if (tst.Has("Isocpeur")) { var m2 = new IdMapping(); stampDb.WblockCloneObjects(new ObjectIdCollection { tst["Isocpeur"] }, db.TextStyleTableId, m2, DuplicateRecordCloning.Ignore, false); sty = m2[tst["Isocpeur"]].Value; }'
new = 'if (tst.Has("Isocpeur_В109")) { var m2 = new IdMapping(); stampDb.WblockCloneObjects(new ObjectIdCollection { tst["Isocpeur_В109"] }, db.TextStyleTableId, m2, DuplicateRecordCloning.Ignore, false); sty = m2[tst["Isocpeur_В109"]].Value; }'
assert old in s; s = s.replace(old, new, 1)
# 2) black and white as В109 (checker 13.11: Revit layer colours plotted in colour, plate fills ACI 255 plotted black)
old = '                    var lt2 = (LayerTable)t.GetObject(db.LayerTableId, OpenMode.ForRead);'
new = r'''                    { var white = Autodesk.AutoCAD.Colors.Color.FromRgb(255, 255, 255); var fill = Autodesk.AutoCAD.Colors.Color.FromRgb(FR, FG, FB); var blk = Autodesk.AutoCAD.Colors.Color.FromColorIndex(Autodesk.AutoCAD.Colors.ColorMethod.ByAci, 7);
                      int nH = 0, nC = 0; var bt2 = (BlockTable)t.GetObject(db.BlockTableId, OpenMode.ForRead);
                      foreach (ObjectId bid in bt2) { var btr = (BlockTableRecord)t.GetObject(bid, OpenMode.ForRead); if (btr.Name == "Штамп№1_В113") continue;
                        foreach (ObjectId id in btr) { var e = t.GetObject(id, OpenMode.ForRead) as Entity; if (e == null || e is Viewport || e is RasterImage || e is Ole2Frame) continue;
                          var h = e as Hatch; var c = e.Color;
                          if (h != null && h.IsSolidFill) { if (c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByAci && c.ColorIndex == 255) { e.UpgradeOpen(); e.Color = fill; nH++; }
                              else if (c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByAci && c.ColorIndex == 7) { e.UpgradeOpen(); e.Color = white; nH++; }
                              continue; }
                          if (c.IsByLayer || c.IsByBlock) { } else if (!(c.ColorMethod == Autodesk.AutoCAD.Colors.ColorMethod.ByAci && c.ColorIndex == 7)) { e.UpgradeOpen(); e.Color = blk; nC++; }
                          var mt0 = e as MText; if (mt0 != null && mt0.Contents.Contains("\C")) { mt0.UpgradeOpen(); mt0.Contents = System.Text.RegularExpressions.Regex.Replace(mt0.Contents, @"\C\d+;", ""); }
                          var dm = e as Dimension; if (dm != null) { dm.UpgradeOpen(); dm.Dimclrd = blk; dm.Dimclre = blk; dm.Dimclrt = blk; } } }
                      var lt3 = (LayerTable)t.GetObject(db.LayerTableId, OpenMode.ForRead);
                      foreach (ObjectId id in lt3) { var lr = (LayerTableRecord)t.GetObject(id, OpenMode.ForWrite); lr.Color = blk; }
                      L.WriteLine("   bw: fills " + nH + ", colours " + nC); }
                    var lt2 = (LayerTable)t.GetObject(db.LayerTableId, OpenMode.ForRead);'''
assert old in s; s = s.replace(old, new, 1)
# fill colour configurable (build.txt line 7 = "R,G,B")
old = '        static StreamWriter L; static string[] cfg;'
new = '        static StreamWriter L; static string[] cfg; static byte FR = 235, FG = 235, FB = 235;'
assert old in s; s = s.replace(old, new, 1)
# 3) only some sheets (build.txt line 5 = list, when not empty) + fill colour line 7
old = '            Directory.CreateDirectory(outDir);\n            foreach (var r in rows)'
new = ('            Directory.CreateDirectory(outDir);\n'
       '            if (cfg.Length > 4 && cfg[4].Trim() != "") { var only = cfg[4].Split(\',\').Select(x => x.Trim()).ToList(); rows = rows.Where(r => only.Contains(r[0])).ToList(); }\n'
       '            if (cfg.Length > 6 && cfg[6].Trim() != "") { var q = cfg[6].Split(\',\'); FR = byte.Parse(q[0]); FG = byte.Parse(q[1]); FB = byte.Parse(q[2]); }\n'
       '            foreach (var r in rows)')
assert old in s; s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
