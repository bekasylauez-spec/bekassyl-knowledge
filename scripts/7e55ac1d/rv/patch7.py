import re
k2 = open('km2.cs', encoding='utf-8').read()
k3 = open('km3.cs', encoding='utf-8').read()
kk = open('km.cs', encoding='utf-8').read()


def rep(src, a, b, cnt=1):
    assert src.count(a) == cnt, (src.count(a), a[:90])
    return src.replace(a, b)


# portrait A3 from the empty «Новый размер» template (the A3 template carries its own landscape frame)
k2 = rep(k2, 'string tbA3k = MakeTitleblock(app, J["rfttb3"], famDir, "КМ_Штамп А3 книжный"', 'string tbA3k = MakeTitleblock(app, J["rfttbn"], famDir, "КМ_Штамп А3 книжный"')
# node views: annotation crop, lines only (no fill), hidden grid heads
k2 = rep(k2, '''                foreach (KeyValuePair<string, View> kv in NV)
                    StyleView(doc, kv.Value, flt, solid, (kv.Key == "8" || kv.Key == "9") ? new[] { "НП1", "СГ1", "РС1", "СВ3" } : null);''',
'''                foreach (KeyValuePair<string, View> kv in NV)
                {
                    View nv = kv.Value;
                    StyleView(doc, nv, flt, solid, (kv.Key == "8" || kv.Key == "9") ? new[] { "НП1", "СГ1", "РС1", "СВ3" } : null);
                    foreach (ElementId fid in nv.GetFilters())
                    {
                        OverrideGraphicSettings o = nv.GetFilterOverrides(fid);
                        OverrideGraphicSettings o2 = new OverrideGraphicSettings();
                        o2.SetProjectionLineColor(o.ProjectionLineColor); o2.SetCutLineColor(o.CutLineColor);
                        o2.SetProjectionLineWeight(4); o2.SetCutLineWeight(5);
                        nv.SetFilterOverrides(fid, o2);
                    }
                    try { nv.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(1); } catch (Exception ex) { L("acrop " + ex.Message); }
                    try
                    {
                        ViewCropRegionShapeManager sm = nv.GetCropRegionShapeManager();
                        double off = 22 * MM;
                        sm.TopAnnotationCropOffset = off; sm.BottomAnnotationCropOffset = off; sm.LeftAnnotationCropOffset = off; sm.RightAnnotationCropOffset = off;
                    }
                    catch (Exception ex) { L("acrop off " + ex.Message); }
                    foreach (Grid g in new FilteredElementCollector(doc).OfClass(typeof(Grid)).Cast<Grid>())
                    { try { g.HideBubbleInView(DatumEnds.End0, nv); g.HideBubbleInView(DatumEnds.End1, nv); } catch { } }
                }''')
# node packing: rows inside the free area, never over the stamp
k2 = rep(k2, '''                    double x = 25, yTopRow = 287, rowH = 0;
                    foreach (Viewport vp in vps)
                    {
                        Outline ol = vp.GetBoxOutline();
                        double w = (ol.MaximumPoint.X - ol.MinimumPoint.X) / MM, h = (ol.MaximumPoint.Y - ol.MinimumPoint.Y) / MM;
                        if (x + w > 410) { x = 25; yTopRow -= rowH + 22; rowH = 0; }
                        vp.SetBoxCenter(new XYZ((x + w / 2) * MM, (yTopRow - 14 - h / 2) * MM, 0));
                        x += w + 14; rowH = Math.Max(rowH, h);
                    }''', '''                    double x = 25, yTopRow = 287, rowH = 0;
                    foreach (Viewport vp in vps)
                    {
                        Outline ol = vp.GetBoxOutline();
                        double w = (ol.MaximumPoint.X - ol.MinimumPoint.X) / MM, h = (ol.MaximumPoint.Y - ol.MinimumPoint.Y) / MM;
                        if (x + w > 410) { x = 25; yTopRow -= rowH + 18; rowH = 0; }
                        double yc = yTopRow - 16 - h / 2;
                        if (yc - h / 2 < 62 && x + w > 222) { x = 25; yTopRow -= rowH + 18; rowH = 0; yc = yTopRow - 16 - h / 2; }
                        vp.SetBoxCenter(new XYZ((x + w / 2) * MM, yc * MM, 0));
                        L("  vp " + vs.SheetNumber + " " + ((View)doc.GetElement(vp.ViewId)).Name + " " + Math.Round(w) + "x" + Math.Round(h) + " at " + Math.Round(x) + "," + Math.Round(yc));
                        x += w + 12; rowH = Math.Max(rowH, h);
                    }''')
# node marks: spread the heads, no two heads close together
k3 = rep(k3, '''                done.Add(mk);
                double sc = v.Scale;
                XYZ off = (Math.Abs(u) < 1e-6 && Math.Abs(w) < 1e-6) ? right : (right * u + up * w).Normalize();
                XYZ head = a + (off + up * 0.6).Normalize() * (14 * MM * sc);''', '''                done.Add(mk);
                double sc = v.Scale;
                XYZ head = null;
                double[] angs = { 45, 135, -45, -135, 90, -90, 0, 180, 60, 120, -60, -120 };
                foreach (double ag in angs)
                {
                    double r = ag * Math.PI / 180;
                    XYZ h2 = a + (right * Math.Cos(r) + up * Math.Sin(r)) * (16 * MM * sc);
                    double hu = (h2 - cen).DotProduct(right), hw = (h2 - cen).DotProduct(up);
                    if (Math.Abs(hu) > halfW + 18 * MM * sc || Math.Abs(hw) > halfH + 18 * MM * sc) continue;
                    if (heads.Any(q => q.DistanceTo(h2) < 11 * MM * sc)) continue;
                    head = h2; break;
                }
                if (head == null) head = a + (right + up).Normalize() * (16 * MM * sc);
                heads.Add(head);''')
k3 = rep(k3, '''            HashSet<string> done = new HashSet<string>();
            List<Element> els = new FilteredElementCollector(doc, v.Id)''', '''            HashSet<string> done = new HashSet<string>();
            List<XYZ> heads = new List<XYZ>();
            List<Element> els = new FilteredElementCollector(doc, v.Id)''')
# plate names unified per mark (schedule shows one name), lengths not shown for plates
k3 = rep(k3, 'SolidDS(doc, cap, "-t10", "-10", "Оголовок стойки", Kg(cap), 31);', 'SolidDS(doc, cap, "-t10", "-10", "Пластина (оголовки, фасонки)", Kg(cap), 31);')
k3 = rep(k3, 'SolidDS(doc, g, "-t10", "-10", "Фасонка", Kg(g), 31);', 'SolidDS(doc, g, "-t10", "-10", "Пластина (оголовки, фасонки)", Kg(g), 31);')
k3 = rep(k3, 'int g = nm.StartsWith("Фасонка") ? 3', 'int g = (nm.StartsWith("Пластина") && e.get_BoundingBox(null).Max.Z - e.get_BoundingBox(null).Min.Z < 15 * MM && Math.Abs((e.get_BoundingBox(null).Max.Y - e.get_BoundingBox(null).Min.Y) / MM - 200) < 3) ? 3')
# tech spec: rotated headers wrapped, plates with 3 decimals
k3 = rep(k3, '''                if (rot) o.Rotation = Math.PI / 2;
                TextNote.Create(doc, vs.Id, new XYZ(x * MM, y * MM, 0), s, o);''', '''                if (rot) { o.Rotation = Math.PI / 2; TextNote.Create(doc, vs.Id, new XYZ(x * MM, y * MM, 0), 26 * MM, s, o); }
                else TextNote.Create(doc, vs.Id, new XYZ(x * MM, y * MM, 0), s, o);''')
k3 = rep(k3, '''"t" + plates[i].Substring(1), "", F2(mpl[i, 0]), F2(mpl[i, 1]), F2(mpl[i, 2]), F2(mpl[i, 3]), F2(mpl[i, 4]), F(s), "" });''',
         '''"t" + plates[i].Substring(1), "", F(mpl[i, 0]), F(mpl[i, 1]), F(mpl[i, 2]), F(mpl[i, 3]), F(mpl[i, 4]), F(s), "" });''')
k3 = rep(k3, 'double X0 = 25, yTop = 405, hh1 = 15, hh2 = 30, hn = 7, rh = 8;', 'double X0 = 25, yTop = 405, hh1 = 15, hh2 = 34, hn = 7, rh = 8;')
open('km2.cs', 'w', encoding='utf-8').write(k2)
open('km3.cs', 'w', encoding='utf-8').write(k3)
# ОД: superscripts lost in the plain text
od = open('od.txt', encoding='utf-8').read().replace('a^gv', 'agv').replace('a^g', 'ag')
open('od.txt', 'w', encoding='utf-8', newline='\n').write(od)
print('patched')
