            else if (t == "trepl")
            {
                // replace substrings in MText/DBText inside win: pairs [[old,new],...]
                var w = L(m["win"]); int n = 0;
                var ms = MS(db, tr); var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    if (!(e is MText) && !(e is DBText)) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X < D(w[0]) || x.MaxPoint.X > D(w[2]) || x.MinPoint.Y < D(w[1]) || x.MaxPoint.Y > D(w[3])) continue;
                    string s0 = e is MText ? ((MText)e).Contents : ((DBText)e).TextString, s1 = s0;
                    foreach (var q in L(m["pairs"])) { var a = L(q); s1 = s1.Replace(a[0].ToString(), a[1].ToString()); }
                    if (s1 == s0) continue;
                    e.UpgradeOpen(); if (e is MText) ((MText)e).Contents = s1; else ((DBText)e).TextString = s1; n++;
                }
                log.AppendLine("trepl " + n);
            }
            else if (t == "clonewin")
            {
                // clone every entity whose extents lie inside win (or no-extent SPDS by first stretch point) by d
                var w = L(m["win"]); var dv = L(m["d"]); var mx = Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0));
                var ms = MS(db, tr); var ids = new ObjectIdCollection();
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Point3d a, b;
                    try { var x = e.GeometricExtents; a = x.MinPoint; b = x.MaxPoint; }
                    catch { var pn = new Point3dCollection(); try { e.GetStretchPoints(pn); } catch { } if (pn.Count == 0) continue; a = pn[0]; b = pn[0]; }
                    if (a.X >= D(w[0]) && b.X <= D(w[2]) && a.Y >= D(w[1]) && b.Y <= D(w[3])) ids.Add(id);
                }
                var im = new IdMapping();
                db.DeepCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), im, false);
                int n = 0;
                foreach (IdPair p in im) { if (!p.IsCloned || !p.IsPrimary) continue; var en = tr.GetObject(p.Value, OpenMode.ForWrite) as Entity; if (en == null) continue; en.TransformBy(mx); n++; }
                log.AppendLine("clonewin " + n + " of " + ids.Count);
            }
