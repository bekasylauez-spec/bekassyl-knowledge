p = r'D:\_claude_work\v113r\dwgnet\v113build.cs'
s = open(p, encoding='utf-8').read()
# 1) viewports: shift the view centre (DCS = world for the plan view of the Revit export, target 0)
old = 'vp.ViewTarget = vp.ViewTarget + D; nVp++; continue; }'
new = 'vp.ViewCenter = vp.ViewCenter + new Vector2d(D.X, D.Y); nVp++; continue; }'
assert old in s; s = s.replace(old, new, 1)
# 2) paper texts / lines of the Revit stamp (they are separate paper-space entities, not only the title block) — erased by the same window
old = '                        var br = o as BlockReference; if (br != null && br.OwnerId == dstLayoutBtr && br.Name.StartsWith("БК_штамп")) tb = br; }'
new = ('                        var br = o as BlockReference; if (br != null && br.OwnerId == dstLayoutBtr && br.Name.StartsWith("БК_штамп")) { tb = br; continue; }\n'
       '                        var pe = o as Entity; if (pe != null && pe.OwnerId == dstLayoutBtr && !num.StartsWith("Т")) { try { var ex = pe.GeometricExtents; double cx = (ex.MinPoint.X + ex.MaxPoint.X) / 2, cy = (ex.MinPoint.Y + ex.MaxPoint.Y) / 2;\n'
       '                            if (cx > -190.6 && cx < -4.4 && cy > 4.4 && cy < 60.6 && ex.MaxPoint.X - ex.MinPoint.X < 186.5 && ex.MaxPoint.Y - ex.MinPoint.Y < 56.5) { pe.Erase(); nStampErased++; } } catch { } } }')
assert old in s; s = s.replace(old, new, 1)
# 3) test limit (build.txt line 4 = number of sheets, optional)
old = '            int i = 0;\n            foreach (var r in rows)'
new = ('            int lim = cfg.Length > 3 && cfg[3].Trim() != "" ? int.Parse(cfg[3]) : 999; if (lim < rows.Count) rows = rows.Where(r => cfg[4].Split(\',\').Contains(r[0])).ToList();\n'
       '            int i = 0;\n            foreach (var r in rows)')
assert old in s; s = s.replace(old, new, 1)
# 4) Revit non-plot layer (viewport frames) not plotted
old = '            try { LayoutManager.Current.CurrentLayout = "Model"; } catch { }'
new = ('            using (var t = dst.TransactionManager.StartTransaction()) { var lt = (LayerTable)t.GetObject(dst.LayerTableId, OpenMode.ForRead);\n'
       '                foreach (ObjectId id in lt) { var lr = (LayerTableRecord)t.GetObject(id, OpenMode.ForRead); if (lr.Name.EndsWith("NPLT")) { lr.UpgradeOpen(); lr.IsPlottable = false; } } t.Commit(); }\n'
       '            try { LayoutManager.Current.CurrentLayout = "Model"; } catch { }')
assert old in s; s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
