p = r'D:\_claude_work\v113r\dwgnet\v113build.cs'
s = open(p, encoding='utf-8').read()
# 1) stamp window: centre inside and size within the stamp (Revit texts overhang the window)
old = 'bool inStamp = false; try { var ex = ent.GeometricExtents; inStamp = ex.MinPoint.X > -190.6 && ex.MaxPoint.X < -4.4 && ex.MinPoint.Y > 4.4 && ex.MaxPoint.Y < 60.6; } catch { }'
new = ('bool inStamp = false; try { var ex = ent.GeometricExtents; double cx = (ex.MinPoint.X + ex.MaxPoint.X) / 2, cy = (ex.MinPoint.Y + ex.MaxPoint.Y) / 2;\n'
       '                                inStamp = cx > -190.6 && cx < -4.4 && cy > 4.4 && cy < 60.6 && ex.MaxPoint.X - ex.MinPoint.X < 186.5 && ex.MaxPoint.Y - ex.MinPoint.Y < 56.5; } catch { }')
assert old in s; s = s.replace(old, new, 1)
# 2) viewports: log, switch the layout current and turn the viewports on
old = 'var vp = o as Viewport; if (vp != null) { vp.ViewTarget = vp.ViewTarget + D; nVp++; continue; }'
new = ('var vp = o as Viewport; if (vp != null) { if (nVp == 0) L.WriteLine("   vp before: target " + vp.ViewTarget + " center " + vp.ViewCenter + " dir " + vp.ViewDirection + " on " + vp.On + " layer " + vp.Layer);\n'
       '                            vp.ViewTarget = vp.ViewTarget + D; nVp++; continue; }')
assert old in s; s = s.replace(old, new, 1)
old = '                L.WriteLine(num + "\\t" + name + "\\tmodel "'
new = ('                try { LayoutManager.Current.CurrentLayout = lname;\n'
       '                    using (var t = dst.TransactionManager.StartTransaction()) { var lbtr = (BlockTableRecord)t.GetObject(dstLayoutBtr, OpenMode.ForRead); int on = 0;\n'
       '                        foreach (ObjectId id in lbtr) { var vp = t.GetObject(id, OpenMode.ForWrite) as Viewport; if (vp == null || vp.Number == 1) continue; if (!vp.On) { vp.On = true; on++; } }\n'
       '                        Extents3d? me = null; int k = 0; foreach (IdPair p in mm) { if (!p.IsCloned || !p.IsPrimary || k > 400) continue; var ent = t.GetObject(p.Value, OpenMode.ForRead, false) as Entity; if (ent == null || ent.OwnerId != dstModel) continue; try { var ex = ent.GeometricExtents; if (me == null) me = ex; else { var x = me.Value; x.AddExtents(ex); me = x; } k++; } catch { } }\n'
       '                        L.WriteLine("   viewports switched on " + on + ", model extents " + (me == null ? "-" : me.Value.MinPoint + " .. " + me.Value.MaxPoint)); t.Commit(); } }\n'
       '                catch (System.Exception ex) { L.WriteLine("   vp on ERR " + ex.Message); }\n'
       '                L.WriteLine(num + "\\t" + name + "\\tmodel "')
assert old in s; s = s.replace(old, new, 1)
s = s.replace('dst.SaveAs(outPath, DwgVersion.AC1032);', 'try { LayoutManager.Current.CurrentLayout = "Model"; } catch { }\n            dst.SaveAs(outPath, DwgVersion.AC1032);', 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
