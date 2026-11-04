using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace RB
{
    // DWG sheet 10: truss schemes Ф1 / Ф2 at 1:25 (no grids), panel chain on top, 580 at the end, Р1 marks along every lattice bar,
    // ВП1 / НП1 on the chords, the small «Ведомость элементов ферм Ф1, Ф2» table bottom-left, DWG notes and sheet name
    public partial class App
    {
        static void SetCropWorld(View v, double u0, double u1, double z0, double z1)
        {
            BoundingBoxXYZ cb = v.CropBox;
            Transform inv = cb.Transform.Inverse;
            XYZ R = v.RightDirection, O = v.Origin;
            // u0..u1 are world coordinates along the view's horizontal axis (X or Y)
            bool alongX = Math.Abs(R.X) > 0.5;
            XYZ a = inv.OfPoint(new XYZ(alongX ? u0 * MM : O.X, alongX ? O.Y : u0 * MM, z0 * MM));
            XYZ b = inv.OfPoint(new XYZ(alongX ? u1 * MM : O.X, alongX ? O.Y : u1 * MM, z1 * MM));
            cb.Min = new XYZ(Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), cb.Min.Z);
            cb.Max = new XYZ(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), cb.Max.Z);
            v.CropBox = cb;
        }

        // a tiny detail line at a point of the view plane: a dim reference where the model one is hidden
        static Reference DimAnchor(Document doc, SecCtx c, double u, double z, bool vertical)
        {
            double h = 1.0 * c.S;
            DetailCurve dc = doc.Create.NewDetailCurve(c.V, vertical ? Line.CreateBound(c.P(u, z), c.P(u, z + h)) : Line.CreateBound(c.P(u, z), c.P(u + h, z)));
            return dc.GeometryCurve.Reference;
        }

        static void Sheet10(Document doc, FamilySymbol up, FamilySymbol dn)
        {
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            DimensionType dimT = Find<DimensionType>(doc, x => x.Name == "КМ_СПДС");
            ViewSheet sh = Sheet(doc, "10");
            List<FamilyInstance> frame = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().Where(f => f.Location is LocationCurve).ToList();
            ViewSection v1 = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().First(x => x.Name == "1");
            // name, truss x (mm), crop u0..u1 (Y), z0..z1, sheet left/top
            object[][] tv = { new object[] { "Схема Ф1", 4350.0, -900.0, 8950.0, 1900.0, 4800.0, 110.0, 398.0 },
                              new object[] { "Схема Ф2", 16450.0, -900.0, 7450.0, 2500.0, 4800.0, 65.0, 252.0 } };
            // the sheet name in the stamp goes back to its cell (same place as on sheet 9, also A2)
            if (sh != null)
            {
                ViewSheet s9 = Sheet(doc, "9");
                TextNote n9 = s9 != null ? new FilteredElementCollector(doc, s9.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(x => (x.Text ?? "").Trim() == s9.Name.Trim()) : null;
                TextNote nm = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(x => (x.Text ?? "").Replace("\r", " ").Trim() == sh.Name.Replace("\r", " ").Trim());
                if (n9 != null && nm != null && !nm.Coord.IsAlmostEqualTo(n9.Coord)) { ElementTransformUtils.MoveElement(doc, nm.Id, n9.Coord - nm.Coord); L("  stamp name back on sheet 10"); }
            }
            foreach (object[] t in tv)
            {
                ViewSection v = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().FirstOrDefault(x => x.Name == (string)t[0]);
                if (v == null) continue;
                double tx = (double)t[1];
                v.Scale = 25;
                try { v.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR).Set(600 * MM); } catch { }
                SetCropWorld(v, (double)t[2], (double)t[3], (double)t[4], (double)t[5]);
                try { v.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(1); ViewCropRegionShapeManager sm = v.GetCropRegionShapeManager(); sm.LeftAnnotationCropOffset = 18 * MM; sm.RightAnnotationCropOffset = 3 * MM; sm.TopAnnotationCropOffset = 16 * MM; sm.BottomAnnotationCropOffset = 3 * MM; } catch { }
                foreach (BuiltInCategory hc in new[] { BuiltInCategory.OST_Grids, BuiltInCategory.OST_Levels, BuiltInCategory.OST_Sections, BuiltInCategory.OST_GenericModel })
                    try { v.SetCategoryHidden(new ElementId(hc), true); } catch { }
                string[] show = { "ВП1", "НП1", "Р1" };
                foreach (ElementId fid in v1.GetFilters())
                {
                    if (!v.IsFilterApplied(fid)) v.AddFilter(fid);
                    v.SetFilterOverrides(fid, v1.GetFilterOverrides(fid));
                    string fn = doc.GetElement(fid).Name;
                    bool markF = fn.StartsWith("КМ_") && !fn.StartsWith("КМ_Сечение");
                    v.SetFilterVisibility(fid, markF ? show.Contains(fn.Substring(3)) : v1.GetFilterVisibility(fid));
                }
                // old annotations
                // (dims die with their anchor lines, so delete by id and skip the ones already gone)
                foreach (ElementId id in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().Where(e => e is IndependentTag || e is TextNote || e is Dimension || e is DetailCurve).Select(e => e.Id).ToList())
                    if (doc.GetElement(id) != null) doc.Delete(id);
                doc.Regenerate();
                SecCtx c = new SecCtx { V = v, O = v.Origin, R = v.RightDirection, S = v.Scale };
                Func<FamilyInstance, bool> atTruss = f => Math.Abs(((LocationCurve)f.Location).Curve.GetEndPoint(0).X / MM - tx) < 60 && Math.Abs(((LocationCurve)f.Location).Curve.GetEndPoint(1).X / MM - tx) < 60;
                List<FamilyInstance> tr = frame.Where(f => (Mk(f) == "ВП1" || Mk(f) == "НП1" || Mk(f) == "Р1") && atTruss(f)).ToList();
                if (tr.Count == 0) { L("  " + t[0] + ": no truss members"); continue; }
                Func<FamilyInstance, XYZ> mid = f => (((LocationCurve)f.Location).Curve.GetEndPoint(0) + ((LocationCurve)f.Location).Curve.GetEndPoint(1)) / 2;
                // Р1 along every lattice bar
                int nt = 0;
                foreach (FamilyInstance f in tr.Where(f => Mk(f) == "Р1"))
                {
                    XYZ m = mid(f);
                    try { IndependentTag tg = IndependentTag.Create(doc, up.Id, v.Id, new Reference(f), false, TagOrientation.AnyModelDirection, c.P(c.U(m), m.Z / MM)); tg.TagHeadPosition = c.P(c.U(m), m.Z / MM); nt++; }
                    catch (Exception ex) { L("  Р1 tag " + ex.Message); }
                }
                // ВП1 over the top chord, НП1 under the bottom chord, about a third along
                foreach (string mk in new[] { "ВП1", "НП1" })
                {
                    List<FamilyInstance> ch = tr.Where(f => Mk(f) == mk).OrderBy(f => c.U(mid(f))).ToList();
                    if (ch.Count == 0) continue;
                    FamilyInstance fc = ch[Math.Min(ch.Count - 1, ch.Count / 3)];
                    XYZ m = mid(fc);
                    FamilySymbol s = mk == "ВП1" ? up : dn;
                    try { IndependentTag tg = IndependentTag.Create(doc, s.Id, v.Id, new Reference(fc), false, TagOrientation.AnyModelDirection, c.P(c.U(m), m.Z / MM)); tg.TagHeadPosition = c.P(c.U(m), m.Z / MM); nt++; }
                    catch (Exception ex) { L("  " + mk + " tag " + ex.Message); }
                }
                // panel chain over the truss: the purlin points on this truss
                List<FamilyInstance> pur = frame.Where(f => Mk(f) == "П1").Where(f =>
                {
                    Curve cv = ((LocationCurve)f.Location).Curve; double a0 = Math.Min(cv.GetEndPoint(0).X, cv.GetEndPoint(1).X) / MM, a1 = Math.Max(cv.GetEndPoint(0).X, cv.GetEndPoint(1).X) / MM;
                    return a0 < tx + 1 && a1 > tx - 1;
                }).ToList();
                List<double[]> pts = pur.Select(f => { Curve cv = ((LocationCurve)f.Location).Curve; XYZ p = cv.Evaluate(0.5, true); return new[] { c.U(p), p.Z / MM }; })
                    .GroupBy(p => Math.Round(p[0] / 10)).Select(g => g.First()).OrderBy(p => p[0]).ToList();
                double zTop = tr.SelectMany(f => new[] { ((LocationCurve)f.Location).Curve.GetEndPoint(0), ((LocationCurve)f.Location).Curve.GetEndPoint(1) }).Max(p => p.Z / MM);
                if (dimT != null && pts.Count > 1)
                {
                    ReferenceArray ra = new ReferenceArray();
                    foreach (double[] p in pts) ra.Append(DimAnchor(doc, c, p[0], p[1] + 60, true));
                    try { doc.Create.NewDimension(v, Line.CreateBound(c.P(0, zTop + 10 * c.S), c.P(1000, zTop + 10 * c.S)), ra, dimT); }
                    catch (Exception ex) { L("  panel dim " + ex.Message); }
                }
                // 580: chord ends at the cantilever end
                List<XYZ> eps = tr.Where(f => Mk(f) != "Р1").SelectMany(f => new[] { ((LocationCurve)f.Location).Curve.GetEndPoint(0), ((LocationCurve)f.Location).Curve.GetEndPoint(1) }).ToList();
                double uEnd = eps.Min(p => c.U(p));
                List<XYZ> endPts = eps.Where(p => Math.Abs(c.U(p) - uEnd) < 30).OrderBy(p => p.Z).ToList();
                if (dimT != null && endPts.Count >= 2)
                {
                    ReferenceArray rh = new ReferenceArray();
                    rh.Append(DimAnchor(doc, c, uEnd - 40 * 0 - 2 * c.S, endPts.First().Z / MM, false));
                    rh.Append(DimAnchor(doc, c, uEnd - 2 * c.S, endPts.Last().Z / MM, false));
                    try { doc.Create.NewDimension(v, Line.CreateBound(c.P(uEnd - 12 * c.S, 0), c.P(uEnd - 12 * c.S, 1000)), rh, dimT); }
                    catch (Exception ex) { L("  580 dim " + ex.Message); }
                }
                L("  " + t[0] + ": tags " + nt + ", panel points " + pts.Count);
                // on the sheet
                if (sh != null)
                {
                    Viewport vp = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(Viewport)).Cast<Viewport>().FirstOrDefault(x => x.ViewId == v.Id);
                    if (vp != null)
                    {
                        string title = "Геометрическая схема фермы " + ((string)t[0]).Substring(6);
                        MoveVp(doc, sh, vp, null, (double)t[6], (double)t[7]);
                        TextNote tt = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(x => (x.Text ?? "").Trim() == title);
                        if (tt != null) { Outline o = vp.GetBoxOutline(); ElementTransformUtils.MoveElement(doc, tt.Id, new XYZ((o.MinimumPoint.X + o.MaximumPoint.X) / 2, o.MaximumPoint.Y + 3 * MM, 0) - tt.Coord); }
                    }
                }
            }
            if (sh == null || t25 == null) return;
            // the big element schedule is not on the DWG sheet
            foreach (ScheduleSheetInstance si in new FilteredElementCollector(doc, sh.Id).OfClass(typeof(ScheduleSheetInstance)).Cast<ScheduleSheetInstance>().ToList()) { doc.Delete(si.Id); L("  schedule removed from sheet 10"); }
            // the truss elements table, bottom-left, with its title
            string[][] rows = { new[] { "ВП1", "□", "", "□ 80×3" }, new[] { "НП1", "□", "", "□ 80×3" }, new[] { "Р1", "□", "", "□ 50×2.5" } };
            ElemTable(doc, sh, t25, rows, 20, 49);
            TextNote tht = SheetTitle(doc, sh, "Ведомость элементов ферм");
            if (tht == null)
            {
                TextNoteType tTitle = new FilteredElementCollector(doc).OfClass(typeof(TextNoteType)).Cast<TextNoteType>().FirstOrDefault(x => x.Name.StartsWith("КМ_Заголовок")) ?? t25;
                tht = Txt(doc, sh.Id, 92, 52, "Ведомость элементов ферм Ф1, Ф2", tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
            }
            // notes and sheet name as in the DWG
            TextNote notes = SheetTitle(doc, sh, "1. Общие");
            string nt3 = "1. Общие данные см. на листе 1, спецификацию металлопроката - на листе 2.\r2. Ферма Ф1 - 5 шт. (рамы по осям 1-3), Ф2 - 6 шт.: по схеме Ф1 без элементов пристройки (ВП1 за рядом М).\r3. Размеры даны по осям элементов. Узлы см. на листах 11, 12.";
            if (notes != null)
            {
                notes.Text = nt3;
                try { notes.Width = 180 * MM; } catch { }
                BoundingBoxXYZ nb = notes.get_BoundingBox(sh);
                if (nb != null) ElementTransformUtils.MoveElement(doc, notes.Id, new XYZ(406 * MM - nb.Min.X, 80 * MM - nb.Min.Y, 0));
            }
            string newName = "Геометрическая схема фермы Ф1, Ф2";   // the DWG has «Ф1;Ф2», ';' is not allowed in Revit names
            if (sh.Name != newName)
            {
                TextNote stamp = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(t => (t.Text ?? "").Replace("\r", " ").Trim() == sh.Name.Replace("\r", " ").Trim());
                sh.Name = newName;
                if (stamp != null) stamp.Text = newName;
            }
        }

        // generic element table in the DWG style (same columns as on sheet 7); X0 left, Y1 top, mm on the sheet
        static void ElemTable(Document doc, ViewSheet sh, TextNoteType t25, string[][] rows, double X0, double Y1)
        {
            double[] cw = { 14.5, 35, 10, 25, 15, 15, 15, 10, 20, 25 };
            double[] xs = new double[cw.Length + 1]; xs[0] = X0; for (int i = 0; i < cw.Length; i++) xs[i + 1] = xs[i] + cw[i];
            double h1 = 9.5, h2 = 10, rh = 8;
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
            Ln(xs[0], Y1, xs[cw.Length], Y1); Ln(xs[0], Y0, xs[cw.Length], Y0);
            Ln(xs[1], yH, xs[4], yH); Ln(xs[4], yH, xs[7], yH);
            Ln(xs[0], yN, xs[cw.Length], yN);
            for (int r = 1; r < rows.Length; r++) Ln(xs[0], yN - rh * r, xs[cw.Length], yN - rh * r);
            for (int i = 0; i <= cw.Length; i++) { bool sub = i == 2 || i == 3 || i == 5 || i == 6; Ln(xs[i], sub ? yH : Y1, xs[i], Y0); }
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
                double cx = (xs[1] + xs[2]) / 2, s = 1.75, s2 = 1.25;
                Ln(cx - s, y - s, cx + s, y - s); Ln(cx + s, y - s, cx + s, y + s); Ln(cx + s, y + s, cx - s, y + s); Ln(cx - s, y + s, cx - s, y - s);
                Ln(cx - s2, y - s2, cx + s2, y - s2); Ln(cx + s2, y - s2, cx + s2, y + s2); Ln(cx + s2, y + s2, cx - s2, y + s2); Ln(cx - s2, y + s2, cx - s2, y - s2);
                T((xs[3] + xs[4]) / 2, y, rows[r][3], false);
                T((xs[8] + xs[9]) / 2, y, "С245", false);
            }
        }
    }
}
