p = r'D:\_claude_work\v113r\dwgnet\v113build.cs'
s = open(p, encoding='utf-8').read()
old = '            int lim = cfg.Length > 3'
new = ('            if (cfg.Length > 5 && cfg[5].Trim() == "persheet") { PerSheet(dst, stamp113, rows, expDir, outPath, listov); HostApplicationServices.WorkingDatabase = prevWdb; dst.Dispose(); return; }\n'
       '            int lim = cfg.Length > 3')
assert old in s; s = s.replace(old, new, 1)
method = r'''
        // 13.11: one DWG per sheet, processed in place (moving the model of a sheet broke the Revit dimensions): the stamp of В109 replaces the Revit stamp
        static void PerSheet(Database stampDb, ObjectId stamp113, List<string[]> rows, string expDir, string outDir, int listov)
        {
            Directory.CreateDirectory(outDir);
            foreach (var r in rows)
            {
                string num = r[0], name = r[1]; var file = Path.Combine(expDir, num.Replace(".", "_") + ".dwg"); if (!File.Exists(file)) { L.WriteLine("missing " + file); continue; }
                var db = new Database(false, true); db.ReadDwgFile(file, FileOpenMode.OpenForReadAndAllShare, true, ""); db.CloseInput(true);
                HostApplicationServices.WorkingDatabase = db;
                // stamp block, style and layers into the sheet database
                var map = new IdMapping(); stampDb.WblockCloneObjects(new ObjectIdCollection { stamp113 }, db.BlockTableId, map, DuplicateRecordCloning.Ignore, false); var st113 = map[stamp113].Value;
                ObjectId sty = ObjectId.Null;
                using (var t = stampDb.TransactionManager.StartTransaction()) { var tst = (TextStyleTable)t.GetObject(stampDb.TextStyleTableId, OpenMode.ForRead); if (tst.Has("Isocpeur")) { var m2 = new IdMapping(); stampDb.WblockCloneObjects(new ObjectIdCollection { tst["Isocpeur"] }, db.TextStyleTableId, m2, DuplicateRecordCloning.Ignore, false); sty = m2[tst["Isocpeur"]].Value; }
                    var lt = (LayerTable)t.GetObject(stampDb.LayerTableId, OpenMode.ForRead); foreach (var ln in new[] { "TEXT 2.5", "Нумерация" }) if (lt.Has(ln)) { var m3 = new IdMapping(); stampDb.WblockCloneObjects(new ObjectIdCollection { lt[ln] }, db.LayerTableId, m3, DuplicateRecordCloning.Ignore, false); } t.Commit(); }
                int nEr = 0; string layName = "";
                using (var t = db.TransactionManager.StartTransaction())
                {
                    if (sty.IsNull) sty = db.Textstyle;
                    var ld = (DBDictionary)t.GetObject(db.LayoutDictionaryId, OpenMode.ForRead); BlockTableRecord lbtr = null; Layout lay = null;
                    foreach (DBDictionaryEntry e in ld) { var l = (Layout)t.GetObject(e.Value, OpenMode.ForRead); if (l.ModelType) continue; var b = (BlockTableRecord)t.GetObject(l.BlockTableRecordId, OpenMode.ForRead); int c = 0; foreach (ObjectId id in b) c++; if (c > 2 && lbtr == null) { lbtr = b; lay = l; } }
                    lbtr.UpgradeOpen(); layName = lay.LayoutName;
                    if (!num.StartsWith("Т"))
                    {
                        BlockReference tb = null; var ers = new List<Entity>();
                        foreach (ObjectId id in lbtr) { var o = t.GetObject(id, OpenMode.ForRead) as Entity; if (o == null || o is Viewport) continue;
                            var br = o as BlockReference; if (br != null && br.Name.StartsWith("БК_штамп")) { tb = br; continue; }
                            if (InStamp(o)) ers.Add(o); }
                        foreach (var e in ers) { e.UpgradeOpen(); e.Erase(); nEr++; }
                        if (tb != null) { tb.UpgradeOpen(); var parts = new DBObjectCollection(); tb.Explode(parts);
                            foreach (DBObject po in parts) { var ent = po as Entity; if (ent == null) continue; if (InStamp(ent)) { ent.Dispose(); nEr++; continue; } lbtr.AppendEntity(ent); t.AddNewlyCreatedDBObject(ent, true); }
                            tb.Erase(); }
                        var st = new BlockReference(new Point3d(-5, 5, 0), st113) { ScaleFactors = new Scale3d(0.01) }; lbtr.AppendEntity(st); t.AddNewlyCreatedDBObject(st, true);
                        var mt = new MText { Location = new Point3d(-85, 7.5, 0), Attachment = AttachmentPoint.MiddleCenter, TextHeight = 2.5, Width = 70, Contents = name, TextStyleId = sty, Layer = "TEXT 2.5", LineSpacingFactor = 0.85 };
                        lbtr.AppendEntity(mt); t.AddNewlyCreatedDBObject(mt, true);
                        Action<string, double> tx = (s0, x) => { var dt = new DBText { TextString = s0, Height = 2.5, TextStyleId = sty, Layer = "Нумерация", HorizontalMode = TextHorizontalMode.TextCenter, VerticalMode = TextVerticalMode.TextVerticalMid, AlignmentPoint = new Point3d(x, 20, 0), Position = new Point3d(x, 20, 0) };
                            lbtr.AppendEntity(dt); t.AddNewlyCreatedDBObject(dt, true); dt.AdjustAlignment(db); };
                        tx(num, -27.5); if (num == "1.1") tx(listov.ToString(), -10);
                    }
                    var lt2 = (LayerTable)t.GetObject(db.LayerTableId, OpenMode.ForRead);
                    foreach (ObjectId id in lt2) { var lr = (LayerTableRecord)t.GetObject(id, OpenMode.ForRead); if (lr.Name.EndsWith("NPLT")) { lr.UpgradeOpen(); lr.IsPlottable = false; } }
                    t.Commit();
                }
                string lname = "Лист " + num; try { LayoutManager.Current.RenameLayout(layName, lname); } catch (System.Exception ex) { L.WriteLine("   rename " + ex.Message); }
                foreach (var dn in new[] { "Layout2", "Лист2" }) { try { if (LayoutManager.Current.LayoutExists(dn)) LayoutManager.Current.DeleteLayout(dn); } catch { } }
                string safe = name.Replace("\"", "").Replace(":", "").Replace("/", "-").Replace("\\", "-").Replace("?", "").Replace("*", "");
                var outF = Path.Combine(outDir, "227-23-П-УВПиОС-ВП-В113-КМ Лист " + num + " - " + safe + ".dwg");
                db.SaveAs(outF, DwgVersion.AC1032); HostApplicationServices.WorkingDatabase = stampDb; db.Dispose();
                L.WriteLine(num + "\t" + name + "\terased " + nEr + "\t" + Path.GetFileName(outF));
            }
            L.WriteLine("saved per sheet " + rows.Count + ", listov " + listov);
        }
        static bool InStamp(Entity e) { try { var ex = e.GeometricExtents; double cx = (ex.MinPoint.X + ex.MaxPoint.X) / 2, cy = (ex.MinPoint.Y + ex.MaxPoint.Y) / 2;
            return cx > -190.6 && cx < -4.4 && cy > 4.4 && cy < 60.6 && ex.MaxPoint.X - ex.MinPoint.X < 186.5 && ex.MaxPoint.Y - ex.MinPoint.Y < 56.5; } catch { return false; } }
'''
anchor = '        static ObjectId CloneTableRecord('
assert anchor in s; s = s.replace(anchor, method + anchor, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
