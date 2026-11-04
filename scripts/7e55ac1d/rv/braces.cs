using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace RB
{
    // DWG sheets 7/8: «Связь вертикальная СВ1/СВ2/СВ3» details (sections through one brace bay, 1:25),
    // the sections table on sheet 7, and the sheet layout (main section top-left, notes over the stamp)
    public partial class App
    {
        // name, title, sheet, cut point (mm), right, u0..u1 (mm along right), z0..z1, depth, marks shown
        static readonly object[][] BraceViews = {
            new object[]{ "СВ1", "Связь вертикальная СВ1", "7", new XYZ(0, 6700, 0), new XYZ(1, 0, 0), 9000.0, 12400.0, 820.0, 2350.0, 900.0, "К1,СВ1" },
            new object[]{ "СВ2", "Связь вертикальная СВ2", "8", new XYZ(0, -600, 0), new XYZ(1, 0, 0), 9000.0, 12400.0, 820.0, 4100.0, 900.0, "К1,СВ2" },
            new object[]{ "СВ3", "Связь вертикальная СВ3", "8", new XYZ(0, 3300, 0), new XYZ(1, 0, 0), 9000.0, 11700.0, 0.0, 0.0, 700.0, "СВ3,РС1" } };

        static ViewSheet Sheet(Document doc, string num) { return new FilteredElementCollector(doc).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().FirstOrDefault(s => s.SheetNumber == num); }

        // the underlined title text over a viewport (sheet text that starts with the given words)
        static TextNote SheetTitle(Document doc, ViewSheet sh, string starts)
        {
            return new FilteredElementCollector(doc, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(t => (t.Text ?? "").Trim().StartsWith(starts));
        }

        static void MoveVp(Document doc, ViewSheet sh, Viewport vp, TextNote title, double left, double top)
        {
            Outline o = vp.GetBoxOutline();
            XYZ d = new XYZ(left * MM - o.MinimumPoint.X, top * MM - o.MaximumPoint.Y, 0);
            if (d.GetLength() < 0.5 * MM) return;
            ElementTransformUtils.MoveElement(doc, vp.Id, d);
            if (title != null) ElementTransformUtils.MoveElement(doc, title.Id, d);
        }

        static void BraceDetails(Document doc)
        {
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            TextNoteType tTitle = new FilteredElementCollector(doc).OfClass(typeof(TextNoteType)).Cast<TextNoteType>().FirstOrDefault(x => x.Name.StartsWith("КМ_Заголовок")) ?? Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 3,5") ?? t25;
            ViewSection v1 = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().First(x => x.Name == "1");
            // section z0/z1 for СВ3: around the lower chord at the middle row
            foreach (object[] b in BraceViews)
            {
                string name = (string)b[0];
                ViewSection v = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().FirstOrDefault(x => !x.IsTemplate && x.Name == name);
                // a first version came out looking from the north (mirrored): drop it and build it again
                if (v != null) { doc.Delete(v.Id); v = null; }   // no manual edits live in these: rebuilt every run
                if (v == null)
                {
                    double z0 = (double)b[7], z1 = (double)b[8];
                    if (name == "СВ3")
                    {
                        // the V brace between trusses on the middle row: its own z range
                        List<XYZ> pts = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>()
                            .Where(f => Mk(f) == "СВ3" && f.Location is LocationCurve).SelectMany(f => new[] { ((LocationCurve)f.Location).Curve.GetEndPoint(0), ((LocationCurve)f.Location).Curve.GetEndPoint(1) })
                            .Where(p => Math.Abs(p.Y / MM - 3650) < 400).ToList();
                        z0 = pts.Min(p => p.Z) / MM - 250; z1 = pts.Max(p => p.Z) / MM + 250;
                    }
                    // the build's recipe for 3-3 (origin = far plane, right = +X): looks along +Y from cut, X to the right
                    XYZ cut = (XYZ)b[3]; double depth = (double)b[9];
                    v = Sec(doc, v1.GetTypeId(), name, (string)b[1], new XYZ(0, (cut.Y + depth) * MM, 0), XYZ.BasisX, (double)b[5], (double)b[6], z0, z1, depth, 25);
                    try { v.get_Parameter(BuiltInParameter.SECTION_COARSER_SCALE_PULLDOWN_METRIC).Set(10); } catch (Exception ex) { L("  coarser " + ex.Message); }
                    v.DetailLevel = ViewDetailLevel.Fine;
                    v.CropBoxActive = true; v.CropBoxVisible = false;
                    try { v.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(1); } catch { }
                    try
                    {
                        ViewCropRegionShapeManager sm = v.GetCropRegionShapeManager();
                        L("  " + name + " annotation offsets were " + Math.Round(sm.LeftAnnotationCropOffset / MM, 1) + "/" + Math.Round(sm.RightAnnotationCropOffset / MM, 1));
                        sm.LeftAnnotationCropOffset = 3 * MM; sm.RightAnnotationCropOffset = 3 * MM;
                        sm.TopAnnotationCropOffset = 3 * MM; sm.BottomAnnotationCropOffset = 3 * MM;
                    }
                    catch (Exception ex) { L("  annotation crop " + ex.Message); }
                    L("  view " + name + " created");
                }
                // crop: the brace bay plus room on the right for the level marks; members outside the bay hidden
                {
                    List<ElementId> outBay = new List<ElementId>();
                    foreach (FamilyInstance f in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().OfType<FamilyInstance>()
                        .Where(f => f.Category != null && (f.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || f.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)))
                    {
                        double mx = f.Location is LocationCurve ? (((LocationCurve)f.Location).Curve.GetEndPoint(0).X + ((LocationCurve)f.Location).Curve.GetEndPoint(1).X) / 2 / MM : ((LocationPoint)f.Location).Point.X / MM;
                        if ((mx < 9100 || mx > 11600) && f.CanBeHidden(v)) outBay.Add(f.Id);
                    }
                    if (outBay.Count > 0) v.HideElements(outBay);
                }
                // same colours as section 1-1, only this detail's marks shown; datums and other sections hidden
                string[] show = ((string)b[10]).Split(',');
                foreach (ElementId fid in v1.GetFilters())
                {
                    if (!v.IsFilterApplied(fid)) v.AddFilter(fid);
                    v.SetFilterOverrides(fid, v1.GetFilterOverrides(fid));
                    string fn = doc.GetElement(fid).Name;
                    bool markF = fn.StartsWith("КМ_") && !fn.StartsWith("КМ_Сечение");
                    v.SetFilterVisibility(fid, markF ? show.Contains(fn.Substring(3)) : v1.GetFilterVisibility(fid));
                }
                foreach (BuiltInCategory hc in new[] { BuiltInCategory.OST_Grids, BuiltInCategory.OST_Sections, BuiltInCategory.OST_Elev, BuiltInCategory.OST_Viewers, BuiltInCategory.OST_GenericModel })
                    try { v.SetCategoryHidden(new ElementId(hc), true); } catch { }
                if (name == "СВ3") try { v.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Levels), true); } catch { }
                // on its sheet
                ViewSheet sh = Sheet(doc, (string)b[2]);
                if (sh == null) continue;
                Viewport vp = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(Viewport)).Cast<Viewport>().FirstOrDefault(x => x.ViewId == v.Id);
                if (vp == null && Viewport.CanAddViewToSheet(doc, sh.Id, v.Id)) vp = Viewport.Create(doc, sh.Id, v.Id, new XYZ(330 * MM, 150 * MM, 0));
                if (vp != null)
                {
                    try { vp.ChangeTypeId(new FilteredElementCollector(doc, sh.Id).OfClass(typeof(Viewport)).Cast<Viewport>().First(x => x.Id != vp.Id).GetTypeId()); } catch { }
                    if (SheetTitle(doc, sh, (string)b[1]) == null)
                    {
                        TextNote tt = Txt(doc, sh.Id, 330, 200, (string)b[1], tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                        FormattedText ft = tt.GetFormattedText(); ft.SetUnderlineStatus(true); tt.SetFormattedText(ft);
                    }
                }
            }
        }

        // brace detail annotations: «□50×2.5» note with a leader to each member shown
        static void BraceNotes(Document doc, SecCtx c, TextNoteType t25, List<FamilyInstance> mem)
        {
            Func<FamilyInstance, XYZ[]> ends = e => new[] { ((LocationCurve)e.Location).Curve.GetEndPoint(0), ((LocationCurve)e.Location).Curve.GetEndPoint(1) };
            List<FamilyInstance> br = mem.Where(e => e.Location is LocationCurve && (Mk(e).StartsWith("СВ") || Mk(e) == "РС1")).ToList();
            br = br.GroupBy(e => Math.Round(c.U(ends(e)[0]) / 50) + "_" + Math.Round(ends(e)[0].Z / MM / 50) + "_" + Math.Round(c.U(ends(e)[1]) / 50) + "_" + Math.Round(ends(e)[1].Z / MM / 50)).Select(g => g.First()).ToList();
            if (br.Count == 0) return;
            double uMid = br.Average(e => c.U((ends(e)[0] + ends(e)[1]) / 2));
            // DWG: one note per diagonal direction of an X (СВ1/СВ2), one note with two leaders for the V (СВ3), one for the strut
            Func<FamilyInstance, string> grp = e =>
            {
                XYZ a = ends(e)[0], b = ends(e)[1];
                if (Math.Abs(a.Z - b.Z) < 50 * MM) return "flat";
                if (Mk(e) == "СВ3") return "V";
                return ((c.U(b) - c.U(a)) * (b.Z - a.Z) > 0) ? "up" : "down";
            };
            foreach (var g in br.GroupBy(grp))
            {
                List<FamilyInstance> es = g.OrderBy(e => c.U((ends(e)[0] + ends(e)[1]) / 2)).ToList();
                List<XYZ> pts = new List<XYZ>();
                if (g.Key == "V") foreach (FamilyInstance e in es) pts.Add(ends(e)[0] + (ends(e)[1] - ends(e)[0]) * 0.5);
                else { FamilyInstance e = es.OrderByDescending(x => (ends(x)[1] - ends(x)[0]).GetLength()).First(); XYZ a = ends(e)[0], b = ends(e)[1]; pts.Add(a + (b - a) * (g.Key == "down" ? 0.7 : 0.3)); }
                XYZ p0 = pts[0];
                double tu, tz;
                if (g.Key == "flat") { tu = c.U(p0) + 10 * c.S; tz = p0.Z / MM - 9 * c.S; }
                else if (g.Key == "V") { tu = pts.Average(p => c.U(p)) - 8 * c.S; tz = pts.Max(p => p.Z / MM) + 8 * c.S; }
                else { tu = c.U(p0) + (g.Key == "up" ? -26 : 10) * c.S; tz = p0.Z / MM + 8 * c.S; }
                TextNote tn = SecText(doc, c, t25, tu, tz, "□50×2.5", 0, HorizontalTextAlignment.Left, VerticalTextAlignment.Bottom, true);
                foreach (XYZ pt in pts)
                    try { Leader ld = tn.AddLeader(c.U(pt) >= tu ? TextNoteLeaderTypes.TNLT_STRAIGHT_R : TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = c.P(c.U(pt), pt.Z / MM); } catch (Exception ex) { L("  brace leader " + ex.Message); }
            }
        }

        // the DWG sections table (sheet 7, bottom-left): Марка | Сечение (эскиз, поз., состав) | Опорные усилия (M, N, Q) | Группа | Марка металла | Примечание
        static void SectionsTable(Document doc, ViewSheet sh, TextNoteType t25)
        {
            // drop an earlier copy (detail lines inside the table box and its texts)
            double X0 = 20, Y1 = 113;
            double[] cw = { 14.5, 35, 10, 25, 15, 15, 15, 10, 20, 25 };
            double[] xs = new double[cw.Length + 1]; xs[0] = X0; for (int i = 0; i < cw.Length; i++) xs[i + 1] = xs[i] + cw[i];
            double h1 = 9.5, h2 = 10, rh = 8;
            string[][] rows = {
                new[]{ "К1", "□", "", "□ 140×100×4" }, new[]{ "К2", "□", "", "□ 80×3" }, new[]{ "Пк1", "□", "", "□ 80×3" }, new[]{ "П1", "□", "", "□ 60×2.5" },
                new[]{ "СВ1", "□", "", "□ 50×2.5" }, new[]{ "СВ2", "□", "", "□ 50×2.5" }, new[]{ "СВ3", "□", "", "□ 50×2.5" }, new[]{ "СГ1", "□", "", "□ 50×2.5" },
                new[]{ "РС1", "□", "", "□ 50×2.5" }, new[]{ "Ф1", "*", "", "" }, new[]{ "Ф2", "*", "", "" } };
            double Y0 = Y1 - h1 - h2 - rh * rows.Length;
            Outline box = new Outline(new XYZ((X0 - 1) * MM, (Y0 - 1) * MM, -1), new XYZ((xs[cw.Length] + 1) * MM, (Y1 + 1) * MM, 1));
            foreach (Element e in new FilteredElementCollector(doc, sh.Id).WherePasses(new BoundingBoxIsInsideFilter(box)).Where(e => e is DetailCurve || e is TextNote).ToList()) doc.Delete(e.Id);
            Action<double, double, double, double> Ln = (a, b2, c2, d2) => doc.Create.NewDetailCurve(sh, Line.CreateBound(new XYZ(a * MM, b2 * MM, 0), new XYZ(c2 * MM, d2 * MM, 0)));
            Action<double, double, string, bool> T = (x, y, s, rot) =>
            {
                TextNoteOptions o = new TextNoteOptions(t25.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Middle;
                if (rot) o.Rotation = Math.PI / 2;
                TextNote.Create(doc, sh.Id, new XYZ(x * MM, y * MM, 0), s, o);
            };
            double yH = Y1 - h1, yN = yH - h2;
            // grid: outer box, header split, rows
            Ln(xs[0], Y1, xs[cw.Length], Y1); Ln(xs[0], Y0, xs[cw.Length], Y0);
            Ln(xs[1], yH, xs[4], yH); Ln(xs[4], yH, xs[7], yH);
            Ln(xs[0], yN, xs[cw.Length], yN);
            for (int r = 1; r < rows.Length; r++) Ln(xs[0], yN - rh * r, xs[cw.Length], yN - rh * r);
            for (int i = 0; i <= cw.Length; i++)
            {
                bool sub = i == 2 || i == 3 || i == 5 || i == 6;
                Ln(xs[i], sub ? yH : Y1, xs[i], sub ? yN - rh * 9 : Y0);   // the Ф rows merge эскиз..состав
                if (sub && (i == 5 || i == 6)) Ln(xs[i], yN - rh * 9, xs[i], Y0);
            }
            T((xs[0] + xs[1]) / 2, (Y1 + yN) / 2, "Марка", false);
            T((xs[1] + xs[4]) / 2, (Y1 + yH) / 2, "Сечение", false);
            T((xs[1] + xs[2]) / 2, (yH + yN) / 2, "эскиз", false);
            T((xs[2] + xs[3]) / 2, (yH + yN) / 2, "поз.", false);
            T((xs[3] + xs[4]) / 2, (yH + yN) / 2, "состав", false);
            T((xs[4] + xs[7]) / 2, (Y1 + yH) / 2, "Опорные усилия", false);
            T((xs[4] + xs[5]) / 2, (yH + yN) / 2, "M, тс·м", false);
            T((xs[5] + xs[6]) / 2, (yH + yN) / 2, "N, тс", false);
            T((xs[6] + xs[7]) / 2, (yH + yN) / 2, "Q, тс", false);
            T((xs[7] + xs[8]) / 2, (Y1 + yN) / 2, "Группа\rконстр.", true);
            T((xs[8] + xs[9]) / 2, (Y1 + yN) / 2, "Марка\rметалла", false);
            T((xs[9] + xs[10]) / 2, (Y1 + yN) / 2, "Приме-\rчание", false);
            for (int r = 0; r < rows.Length; r++)
            {
                double y = yN - rh * r - rh / 2;
                T((xs[0] + xs[1]) / 2, y, rows[r][0], false);
                if (rows[r][1] == "*") T((xs[1] + xs[4]) / 2, y, "сложное, см. геом. схему", false);
                else
                {
                    // sketch: a hollow square tube 3.5 mm
                    double cx = (xs[1] + xs[2]) / 2, s = 1.75, s2 = 1.25;
                    Ln(cx - s, y - s, cx + s, y - s); Ln(cx + s, y - s, cx + s, y + s); Ln(cx + s, y + s, cx - s, y + s); Ln(cx - s, y + s, cx - s, y - s);
                    Ln(cx - s2, y - s2, cx + s2, y - s2); Ln(cx + s2, y - s2, cx + s2, y + s2); Ln(cx + s2, y + s2, cx - s2, y + s2); Ln(cx - s2, y + s2, cx - s2, y - s2);
                    T((xs[3] + xs[4]) / 2, y, rows[r][3], false);
                }
                T((xs[8] + xs[9]) / 2, y, "С245", false);
            }
        }

        // the detail views snap their level lines back to the crop width: set the short right-hand lines once more at the very end
        static void DetailLevels(Document doc)
        {
            foreach (string name in new[] { "СВ1", "СВ2" })
            {
                ViewSection v = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().FirstOrDefault(x => x.Name == name);
                if (v == null) continue;
                BoundingBoxXYZ cb = v.CropBox;
                double xr = Math.Max(cb.Transform.OfPoint(cb.Min).X, cb.Transform.OfPoint(cb.Max).X) / MM;
                foreach (Level lv in new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().Where(l => !l.IsHidden(v)))
                {
                    try
                    {
                        IList<Curve> cs = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v);
                        if (cs.Count == 0) continue;
                        XYZ a = cs[0].GetEndPoint(0), b = cs[0].GetEndPoint(1);
                        double y = a.Y, z = a.Z;
                        XYZ pa = new XYZ((xr - 120 - 500) * MM, y, z), pb = new XYZ((xr - 120) * MM, y, z);
                        bool same = (b - a).DotProduct(pb - pa) > 0;
                        lv.SetCurveInView(DatumExtentType.ViewSpecific, v, same ? Line.CreateBound(pa, pb) : Line.CreateBound(pb, pa));
                        doc.Regenerate();
                        Curve n = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v)[0];
                        L("  " + name + " level " + lv.Name + " now " + Math.Round(n.GetEndPoint(0).X / MM) + ".." + Math.Round(n.GetEndPoint(1).X / MM));
                    }
                    catch (Exception ex) { L("  " + name + " level " + lv.Name + ": " + ex.Message.Split('\n')[0]); }
                }
            }
        }

        // sheet layout like the DWG: main section top-left, details on the right, table bottom-left, notes over the stamp
        static void SheetLayout78(Document doc)
        {
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            foreach (string num in new[] { "7", "8" })
            {
                ViewSheet sh = Sheet(doc, num);
                if (sh == null) continue;
                List<Viewport> vps = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(Viewport)).Cast<Viewport>().ToList();
                Viewport main = vps.FirstOrDefault(x => doc.GetElement(x.ViewId).Name == (num == "7" ? "1" : "2"));
                string mainTitle = num == "7" ? "Разрез 1 - 1" : "Разрез 2 - 2";
                if (main != null) MoveVp(doc, sh, main, SheetTitle(doc, sh, mainTitle), 24, 272);
                // the sheet name in the stamp goes back to its cell (same place as on sheet 6, also A3)
                ViewSheet s6 = Sheet(doc, "6");
                TextNote n6 = s6 != null ? new FilteredElementCollector(doc, s6.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(t => (t.Text ?? "").Trim() == s6.Name.Trim()) : null;
                TextNote nm = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(t => (t.Text ?? "").Trim() == sh.Name.Trim());
                if (n6 != null && nm != null && !nm.Coord.IsAlmostEqualTo(n6.Coord)) { ElementTransformUtils.MoveElement(doc, nm.Id, n6.Coord - nm.Coord); L("  stamp name back on sheet " + num); }
                // notes: from the bottom-left to over the stamp (x 232, bottom 64)
                TextNote notes = SheetTitle(doc, sh, "1. Общие");
                if (notes != null)
                {
                    try { if (notes.Width > 180 * MM) notes.Width = 180 * MM; } catch { }   // the text box ran past the sheet edge
                    BoundingBoxXYZ nb = notes.get_BoundingBox(sh);
                    if (nb != null) ElementTransformUtils.MoveElement(doc, notes.Id, new XYZ(232 * MM - nb.Min.X, 64 * MM - nb.Min.Y, 0));
                }
                if (num == "7")
                {
                    Viewport d1 = vps.FirstOrDefault(x => doc.GetElement(x.ViewId).Name == "СВ1");
                    if (d1 != null) { Outline o1 = d1.GetBoxOutline(); MoveVp(doc, sh, d1, SheetTitle(doc, sh, "Связь вертикальная СВ1"), 412 - (o1.MaximumPoint.X - o1.MinimumPoint.X) / MM, 160); }
                    if (t25 != null) SectionsTable(doc, sh, t25);
                }
                else
                {
                    Viewport d2 = vps.FirstOrDefault(x => doc.GetElement(x.ViewId).Name == "СВ2");
                    if (d2 != null) { Outline o2 = d2.GetBoxOutline(); MoveVp(doc, sh, d2, SheetTitle(doc, sh, "Связь вертикальная СВ2"), 412 - (o2.MaximumPoint.X - o2.MinimumPoint.X) / MM, 262); L("  СВ2 viewport width " + Math.Round((o2.MaximumPoint.X - o2.MinimumPoint.X) / MM)); }
                    Viewport d3 = vps.FirstOrDefault(x => doc.GetElement(x.ViewId).Name == "СВ3");
                    if (d3 != null) MoveVp(doc, sh, d3, SheetTitle(doc, sh, "Связь вертикальная СВ3"), 45, 95);
                }
                // titles sit 3 mm over their viewports
                foreach (Viewport vp in new FilteredElementCollector(doc, sh.Id).OfClass(typeof(Viewport)).Cast<Viewport>())
                {
                    View vv = (View)doc.GetElement(vp.ViewId);
                    string title = vv.Name == "1" ? "Разрез 1 - 1" : vv.Name == "2" ? "Разрез 2 - 2" : vv.Name.StartsWith("СВ") ? "Связь вертикальная " + vv.Name : null;
                    TextNote tt = title != null ? SheetTitle(doc, sh, title) : null;
                    if (tt == null) continue;
                    Outline o = vp.GetBoxOutline();
                    XYZ want = new XYZ((o.MinimumPoint.X + o.MaximumPoint.X) / 2, o.MaximumPoint.Y + 3 * MM, 0);
                    ElementTransformUtils.MoveElement(doc, tt.Id, want - tt.Coord);
                }
            }
        }
    }
}
