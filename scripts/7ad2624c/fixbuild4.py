p = r'D:\_claude_work\v113r\dwgnet\v113build.cs'
s = open(p, encoding='utf-8').read()
old = '                    var lt2 = (LayerTable)t.GetObject(db.LayerTableId, OpenMode.ForRead);'
new = r'''                    // 13.11: the first view viewport of the Revit layout became the paper-space overall viewport on save (4685 × 2654, main view lost) —
                    // every view viewport is recreated at the end of the layout (same centre / size / view / scale / layer / frozen layers), the small overall one stays first
                    { var vps = new List<Viewport>(); foreach (ObjectId id in lbtr) { var vp = t.GetObject(id, OpenMode.ForRead) as Viewport; if (vp != null && vp.Width > 30) vps.Add(vp); }
                      foreach (var vp in vps) { var nv = new Viewport(); lbtr.AppendEntity(nv); t.AddNewlyCreatedDBObject(nv, true);
                        nv.SetPropertiesFrom(vp); nv.CenterPoint = vp.CenterPoint; nv.Width = vp.Width; nv.Height = vp.Height; nv.ViewDirection = vp.ViewDirection; nv.ViewTarget = vp.ViewTarget;
                        nv.ViewCenter = vp.ViewCenter; nv.ViewHeight = vp.ViewHeight; nv.TwistAngle = vp.TwistAngle; nv.CustomScale = vp.CustomScale; try { nv.StandardScale = vp.StandardScale; } catch { } nv.CustomScale = vp.CustomScale; nv.ViewCenter = vp.ViewCenter;
                        var fl = vp.GetFrozenLayers(); if (fl != null && fl.Count > 0) nv.FreezeLayersInViewport(fl.GetEnumerator());
                        nv.Locked = vp.Locked; nv.On = true; vp.UpgradeOpen(); vp.Erase(); }
                      L.WriteLine("   viewports recreated " + vps.Count); }
                    var lt2 = (LayerTable)t.GetObject(db.LayerTableId, OpenMode.ForRead);'''
assert old in s; s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
