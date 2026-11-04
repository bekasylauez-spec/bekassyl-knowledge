using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    // annotation families drawn like the SPDS objects of «КМ Чертеж Навес 1 Рампа.dwg» (sizes in paper mm, measured from the DWG)
    public partial class App
    {
        static View FamView(Document fd) { return new FilteredElementCollector(fd).OfClass(typeof(View)).Cast<View>().First(v => !v.IsTemplate); }

        static void FLine(Document fd, View v, double x1, double y1, double x2, double y2)
        {
            fd.FamilyCreate.NewDetailCurve(v, Line.CreateBound(new XYZ(x1 * MM, y1 * MM, 0), new XYZ(x2 * MM, y2 * MM, 0)));
        }

        static void FThick(Document fd, View v, double x1, double y1, double x2, double y2)
        {
            Category fc = fd.OwnerFamily.FamilyCategory;
            Category sc = fc.SubCategories.Contains("КМ_Толстая") ? fc.SubCategories.get_Item("КМ_Толстая") : fd.Settings.Categories.NewSubcategory(fc, "КМ_Толстая");
            sc.SetLineWeight(8, GraphicsStyleType.Projection);
            sc.LineColor = new Color(0, 0, 0);
            DetailCurve dc = fd.FamilyCreate.NewDetailCurve(v, Line.CreateBound(new XYZ(x1 * MM, y1 * MM, 0), new XYZ(x2 * MM, y2 * MM, 0)));
            dc.LineStyle = sc.GetGraphicsStyle(GraphicsStyleType.Projection);
        }

        static void FFill(Document fd, View v, params double[] xy)
        {
            ElementId ft = new FilteredElementCollector(fd).OfClass(typeof(FilledRegionType)).Cast<FilledRegionType>()
                .Where(t => { FillPatternElement fp = fd.GetElement(t.ForegroundPatternId) as FillPatternElement; return fp != null && fp.GetFillPattern().IsSolidFill; })
                .Select(t => t.Id).FirstOrDefault();
            if (ft == null || ft == ElementId.InvalidElementId)
            {
                FilledRegionType any = new FilteredElementCollector(fd).OfClass(typeof(FilledRegionType)).Cast<FilledRegionType>().FirstOrDefault();
                if (any == null) { L("  no filled region type"); return; }
                FilledRegionType n = (FilledRegionType)any.Duplicate("КМ_Сплошная");
                n.ForegroundPatternId = new FilteredElementCollector(fd).OfClass(typeof(FillPatternElement)).Cast<FillPatternElement>().First(f => f.GetFillPattern().IsSolidFill).Id;
                n.ForegroundPatternColor = new Color(0, 0, 0);
                ft = n.Id;
            }
            CurveLoop cl = new CurveLoop();
            for (int i = 0; i < xy.Length; i += 2)
            {
                int j = (i + 2) % xy.Length;
                cl.Append(Line.CreateBound(new XYZ(xy[i] * MM, xy[i + 1] * MM, 0), new XYZ(xy[j] * MM, xy[j + 1] * MM, 0)));
            }
            FilledRegion.Create(fd, ft, v.Id, new List<CurveLoop> { cl });
        }

        // label: own type (ISOCPEUR italic, size), alignment, anchor point
        static void FLabel(Document fd, TextElement te, double mm, HorizontalTextAlignment ha, VerticalTextAlignment va, double x, double y)
        {
            ElementType bt = (ElementType)fd.GetElement(te.GetTypeId());
            string tn = "КМ_ISOCPEUR " + mm.ToString("0.0").Replace(".", ",");
            ElementType t = new FilteredElementCollector(fd).OfClass(typeof(ElementType)).Cast<ElementType>().FirstOrDefault(e => e is TextElementType && e.Name == tn) ?? bt.Duplicate(tn);
            try { t.get_Parameter(BuiltInParameter.TEXT_FONT).Set(ISO); } catch { }
            try { t.get_Parameter(BuiltInParameter.TEXT_SIZE).Set(mm * MM); } catch { }
            try { t.get_Parameter(BuiltInParameter.TEXT_STYLE_ITALIC).Set(1); } catch { }
            try { t.get_Parameter(BuiltInParameter.TEXT_WIDTH_SCALE).Set(1.0); } catch { }
            try { t.get_Parameter(BuiltInParameter.TEXT_BACKGROUND).Set(1); } catch { }
            try { t.get_Parameter(BuiltInParameter.TEXT_BOX_VISIBILITY).Set(0); } catch { }
            te.ChangeTypeId(t.Id);
            try { te.HorizontalAlignment = ha; } catch (Exception ex) { L("  label ha " + ex.Message); }
            try { te.VerticalAlignment = va; } catch (Exception ex) { L("  label va " + ex.Message); }
            fd.Regenerate();
            ElementTransformUtils.MoveElement(fd, te.Id, new XYZ(x * MM, y * MM, 0) - te.Coord);
        }

        static void ClearGeometry(Document fd)
        {
            foreach (ElementId id in new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToElementIds().ToList()) { try { fd.Delete(id); } catch { } }
            foreach (ElementId id in new FilteredElementCollector(fd).OfClass(typeof(FilledRegion)).ToElementIds().ToList()) { try { fd.Delete(id); } catch { } }
        }

        // edit an existing annotation family, redraw it, save under a new name and load it as a new family
        static Family RemakeFamily(Document doc, string srcName, string newName, string dir, Action<Document, View, List<TextElement>> draw)
        {
            Family src = Find<Family>(doc, f => f.Name == srcName);
            if (src == null) { L("  no family " + srcName); return null; }
            Document fd = doc.EditFamily(src);
            using (Transaction t = new Transaction(fd, "remake"))
            {
                t.Start();
                ClearGeometry(fd);
                List<TextElement> labels = new FilteredElementCollector(fd).OfClass(typeof(TextElement)).Cast<TextElement>().ToList();
                draw(fd, FamView(fd), labels);
                t.Commit();
            }
            string p = Path.Combine(dir, newName + ".rfa");
            SaveAsOptions so = new SaveAsOptions(); so.OverwriteExistingFile = true; so.MaximumBackups = 1;
            fd.SaveAs(p, so);
            fd.Close(false);
            Family nf = null;
            Tx(doc, "load " + newName, delegate { doc.LoadFamily(p, new LoadOpts(), out nf); });
            if (nf == null) nf = Find<Family>(doc, f => f.Name == newName);
            L("  family " + newName + (nf != null ? " ok" : " FAILED"));
            return nf;
        }

        static FamilySymbol Sym(Document doc, Family f)
        {
            if (f == null) return null;
            FamilySymbol s = (FamilySymbol)doc.GetElement(f.GetFamilySymbolIds().First());
            return s;
        }

        class AnnoSet { public FamilySymbol Section, Tail, Grid, Level, Callout, TagBeam, TagCol; }

        static AnnoSet MakeAnnoFamilies(Document doc, string dir)
        {
            AnnoSet a = new AnnoSet();
            // section head: stroke 6 x 0.5 at the line end, arrow 8.4 from 1.3 mm off the outer end, filled head 3 x 1 at the stroke, number 3 mm beside the arrow
            a.Section = Sym(doc, RemakeFamily(doc, "Заголовок разреза", "КМ_Разрез", dir, delegate (Document fd, View v, List<TextElement> lb)
            {
                FThick(fd, v, -6, 0, 0, 0);
                FLine(fd, v, -1.3, -0.25, -1.3, -8.4);
                FFill(fd, v, -1.3, -0.25, -0.8, -3.25, -1.8, -3.25);
                foreach (TextElement te in lb) FLabel(fd, te, 3.0, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 1.3, -6.3);
            }));
            // tail: the same stroke and arrow; the number label is copied from the head when the tail family accepts it
            a.Tail = Sym(doc, RemakeFamily(doc, "Задняя часть разреза", "КМ_Разрез хвост", dir, delegate (Document fd, View v, List<TextElement> lb)
            {
                FThick(fd, v, -6, 0, 0, 0);
                FLine(fd, v, -1.3, -0.25, -1.3, -8.4);
                FFill(fd, v, -1.3, -0.25, -0.8, -3.25, -1.8, -3.25);
            }));
            // grid head: circle Ø7, name 3.5 mm in the centre, tangent to the grid line end
            a.Grid = Sym(doc, RemakeFamilyGrid(doc, dir));
            // level mark: stem 7.5, open arrow 2 x 2, shelf 12.54 to the left, elevation 2.5 mm 1.5 mm from the shelf end
            a.Level = Sym(doc, RemakeFamily(doc, LevelHeadFamily(doc), "КМ_Отметка", dir, delegate (Document fd, View v, List<TextElement> lb)
            {
                FLine(fd, v, 0, 0, 0, 7.5);
                FLine(fd, v, 0, 0, -2, 2);
                FLine(fd, v, 0, 0, 2, 2);
                FLine(fd, v, 0, 7.5, -12.54, 7.5);
                TextElement el = lb.FirstOrDefault(t => (t.Text ?? "").Any(char.IsDigit)) ?? lb.FirstOrDefault();
                foreach (TextElement te in lb.Where(t => t.Id != (el != null ? el.Id : ElementId.InvalidElementId)).ToList()) { try { fd.Delete(te.Id); } catch { } }
                if (el != null) FLabel(fd, el, 2.5, HorizontalTextAlignment.Left, VerticalTextAlignment.Bottom, -11.04, 8.3);
            }));
            // node mark: shelf 7.6, number 3.5 above, sheet 2.5 below
            a.Callout = Sym(doc, RemakeFamily(doc, "Заголовок фрагмента - Без марки", "КМ_Узел", dir, delegate (Document fd, View v, List<TextElement> lb)
            {
                FLine(fd, v, 0, 0, 7.6, 0);
                foreach (TextElement te in lb)
                {
                    string s = (te.Text ?? "").Trim();
                    if (s == "1") FLabel(fd, te, 3.5, HorizontalTextAlignment.Left, VerticalTextAlignment.Bottom, 0.7, 0.7);
                    else if (s.StartsWith("A")) FLabel(fd, te, 2.5, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, 0.5, -0.7);
                    else { try { fd.Delete(te.Id); } catch { } }
                }
            }));
            // element mark: text 2.5 mm on a 9 mm shelf
            Action<Document, View, List<TextElement>> note = delegate (Document fd, View v, List<TextElement> lb)
            {
                FLine(fd, v, 0, 0, 9, 0);
                TextElement first = lb.FirstOrDefault();
                foreach (TextElement te in lb.Skip(1).ToList()) { try { fd.Delete(te.Id); } catch { } }
                if (first != null)
                {
                    XYZ bd = first.BaseDirection;
                    double ang = Math.Atan2(bd.Y, bd.X);
                    if (Math.Abs(ang) > 1e-3) ElementTransformUtils.RotateElement(fd, first.Id, Line.CreateBound(first.Coord, first.Coord + XYZ.BasisZ), -ang);
                    FLabel(fd, first, 2.5, HorizontalTextAlignment.Left, VerticalTextAlignment.Bottom, 1.5, 1.0);
                }
            };
            a.TagBeam = Sym(doc, RemakeFamily(doc, "M_Марка несущего каркаса", "КМ_Марка каркаса", dir, note));
            a.TagCol = Sym(doc, RemakeFamily(doc, "M_Марка несущей колонны-45", "КМ_Марка колонны", dir, note));
            return a;
        }

        static string LevelHeadFamily(Document doc)
        {
            Level lv = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().First();
            ElementType lt = (ElementType)doc.GetElement(lv.GetTypeId());
            Parameter p = lt.get_Parameter(BuiltInParameter.LEVEL_HEAD_TAG);
            Element s = p != null ? doc.GetElement(p.AsElementId()) : null;
            string n = s is FamilySymbol ? ((FamilySymbol)s).FamilyName : "M_Заголовок уровня - Окружность";
            L("  level head source " + n);
            return n;
        }

        static Family RemakeFamilyGrid(Document doc, string dir)
        {
            GridType gt = new FilteredElementCollector(doc).OfClass(typeof(GridType)).Cast<GridType>().First();
            Element hs = doc.GetElement(gt.get_Parameter(BuiltInParameter.GRID_HEAD_TAG).AsElementId());
            string src = hs is FamilySymbol ? ((FamilySymbol)hs).FamilyName : "M_Заголовок сетки - Окружность";
            L("  grid head source " + src);
            Family f = Find<Family>(doc, x => x.Name == src);
            Document fd = doc.EditFamily(f);
            using (Transaction t = new Transaction(fd, "grid head"))
            {
                t.Start();
                List<Arc> arcs = new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).Cast<CurveElement>().Select(c => c.GeometryCurve).OfType<Arc>().ToList();
                XYZ c0 = arcs.Count > 0 ? arcs[0].Center : new XYZ(0, 4 * MM, 0);
                double r0 = arcs.Count > 0 ? arcs[0].Radius : 4 * MM;
                XYZ dir1 = c0.GetLength() > 1e-9 ? c0.Normalize() : XYZ.BasisY;
                XYZ c1 = dir1 * (3.5 * MM);
                ClearGeometry(fd);
                View v = FamView(fd);
                fd.FamilyCreate.NewDetailCurve(v, Arc.Create(c1, 3.5 * MM, 0, Math.PI, XYZ.BasisX, XYZ.BasisY));
                fd.FamilyCreate.NewDetailCurve(v, Arc.Create(c1, 3.5 * MM, Math.PI, 2 * Math.PI, XYZ.BasisX, XYZ.BasisY));
                foreach (TextElement te in new FilteredElementCollector(fd).OfClass(typeof(TextElement)).Cast<TextElement>())
                    FLabel(fd, te, 3.5, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, c1.X / MM, c1.Y / MM);
                L("  grid head: old centre " + Math.Round(c0.X / MM, 1) + "," + Math.Round(c0.Y / MM, 1) + " r " + Math.Round(r0 / MM, 1));
                t.Commit();
            }
            string p = Path.Combine(dir, "КМ_Ось.rfa");
            SaveAsOptions so = new SaveAsOptions(); so.OverwriteExistingFile = true; so.MaximumBackups = 1;
            fd.SaveAs(p, so); fd.Close(false);
            Family nf = null;
            Tx(doc, "load grid head", delegate { doc.LoadFamily(p, new LoadOpts(), out nf); });
            return nf ?? Find<Family>(doc, x => x.Name == "КМ_Ось");
        }

        // apply the new families to the types used by the album
        static void ApplyAnno(Document doc, AnnoSet a, ViewFamilyType vtSec, ViewFamilyType vtDet, ViewFamilyType vtPlan)
        {
            Tx(doc, "apply anno", delegate
            {
                foreach (FamilySymbol s in new[] { a.Section, a.Tail, a.Grid, a.Level, a.Callout, a.TagBeam, a.TagCol }) if (s != null && !s.IsActive) s.Activate();
                if (a.Grid != null) foreach (GridType gt in new FilteredElementCollector(doc).OfClass(typeof(GridType)).Cast<GridType>())
                    { try { gt.get_Parameter(BuiltInParameter.GRID_HEAD_TAG).Set(a.Grid.Id); } catch (Exception ex) { L("grid tag " + ex.Message); } }
                if (a.Level != null) foreach (ElementType lt in new FilteredElementCollector(doc).OfClass(typeof(LevelType)).Cast<ElementType>())
                    { try { lt.get_Parameter(BuiltInParameter.LEVEL_HEAD_TAG).Set(a.Level.Id); } catch (Exception ex) { L("level tag " + ex.Message); } }
                if (a.Section != null)
                {
                    Parameter ps = vtSec.LookupParameter("Марка разреза");
                    ElementType st = ps != null ? doc.GetElement(ps.AsElementId()) as ElementType : null;
                    if (st != null)
                    {
                        ElementType nst = new FilteredElementCollector(doc).OfClass(typeof(ElementType)).Cast<ElementType>().FirstOrDefault(t => !(t is FamilySymbol) && t.Name == "КМ_Обозначение разреза") ?? st.Duplicate("КМ_Обозначение разреза");
                        Parameter ph = nst.LookupParameter("Заголовок разреза"); if (ph != null) ph.Set(a.Section.Id);
                        Parameter pt = nst.LookupParameter("Задняя часть разреза"); if (pt != null && a.Tail != null) pt.Set(a.Tail.Id);
                        ps.Set(nst.Id);
                    }
                    else L("no section tag param");
                }
                // DWG shows only the two end marks: the section line itself is drawn white (not printed)
                try
                {
                    foreach (BuiltInCategory bc in new[] { BuiltInCategory.OST_Sections, BuiltInCategory.OST_Viewers })
                    {
                        Category secCat = Category.GetCategory(doc, bc);
                        if (secCat == null) continue;
                        L("cat " + secCat.Name + " subs: " + string.Join(", ", secCat.SubCategories.Cast<Category>().Select(c => c.Name)));
                        secCat.LineColor = new Color(255, 255, 255);
                        foreach (Category sc2 in secCat.SubCategories) { try { sc2.LineColor = new Color(255, 255, 255); } catch { } }
                    }
                    doc.Regenerate();
                    foreach (GraphicsStyle gs in new FilteredElementCollector(doc).OfClass(typeof(GraphicsStyle)).Cast<GraphicsStyle>().Where(g => g.Name == "КМ_Обозначение разреза" && g.GraphicsStyleCategory != null))
                    { gs.GraphicsStyleCategory.LineColor = new Color(255, 255, 255); L("section line style white: " + gs.Name); }
                }
                catch (Exception ex) { L("section line " + ex.Message); }
                if (a.Callout != null)
                {
                    ElementType ct = new FilteredElementCollector(doc).OfClass(typeof(ElementType)).Cast<ElementType>().First(t => !(t is FamilySymbol) && t.FamilyName == "Марка фрагмента");
                    ElementType nct = new FilteredElementCollector(doc).OfClass(typeof(ElementType)).Cast<ElementType>().FirstOrDefault(t => !(t is FamilySymbol) && t.Name == "КМ_Обозначение узла") ?? ct.Duplicate("КМ_Обозначение узла");
                    Parameter ph = nct.LookupParameter("Заголовок фрагмента"); if (ph != null) ph.Set(a.Callout.Id);
                    foreach (Parameter p in nct.Parameters) if (p.StorageType == StorageType.Double && p.Definition.Name.StartsWith("Радиус")) p.Set(4.0 * MM);
                    foreach (ViewFamilyType vft in new[] { vtDet, vtPlan, vtSec })
                    {
                        Parameter pc = vft.LookupParameter("Марка фрагмента");
                        if (pc != null && !pc.IsReadOnly) pc.Set(nct.Id);
                    }
                }
            });
        }
    }
}
