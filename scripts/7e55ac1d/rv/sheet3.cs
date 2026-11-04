using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace RB
{
    // DWG sheet 3 «Схема расположения закладных деталей»: only columns and the Зд plates, a «Зд-1» / «Зд-2» shelf mark at every plate,
    // no section / callout marks, and the 1500 to the К2 row on the left
    public partial class App
    {
        static void Sheet3(Document doc)
        {
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            DimensionType dimT = Find<DimensionType>(doc, x => x.Name == "КМ_СПДС");
            View v = new FilteredElementCollector(doc).OfClass(typeof(ViewPlan)).Cast<View>().FirstOrDefault(x => !x.IsTemplate && x.Name.Contains("закладных"));
            if (v == null) { L("  no plan of embedded parts"); return; }
            double S = v.Scale, z0 = v.Origin.Z;
            // section signs, callouts and their numbers are not on the DWG sheet
            foreach (BuiltInCategory hc in new[] { BuiltInCategory.OST_Viewers, BuiltInCategory.OST_Sections, BuiltInCategory.OST_GenericAnnotation, BuiltInCategory.OST_CalloutHeads })
                try { v.SetCategoryHidden(new ElementId(hc), true); } catch { }
            // the а-а / б-б callout marks (category «Виды»): hidden one by one
            List<ElementId> marks = new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType()
                .Where(e => e.Category != null && e.Category.Name == "Виды" && (e.Name.StartsWith("Разрез а") || e.Name.StartsWith("Разрез б")) && e.CanBeHidden(v)).Select(e => e.Id).ToList();
            if (marks.Count > 0) { v.HideElements(marks); L("  sheet 3: callout marks hidden " + marks.Count); }
            // old marks and notes in the view
            foreach (ElementId id in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().Where(e => e is IndependentTag || e is TextNote).Select(e => e.Id).ToList())
                if (doc.GetElement(id) != null) doc.Delete(id);
            // only the Зд plates among the plates
            List<Element> plates = new FilteredElementCollector(doc, v.Id).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToList();
            List<ElementId> hide = plates.Where(e => { string m = Mk(e) ?? ""; return !m.StartsWith("Зд") && e.CanBeHidden(v); }).Select(e => e.Id).ToList();
            if (hide.Count > 0) v.HideElements(hide);
            List<Element> zd = plates.Where(e => (Mk(e) ?? "").StartsWith("Зд")).ToList();
            int n = 0;
            if (t25 != null)
                foreach (Element e in zd)
                {
                    BoundingBoxXYZ bb = e.get_BoundingBox(null);
                    if (bb == null) continue;
                    double cx = (bb.Min.X + bb.Max.X) / 2 / MM, cy = (bb.Min.Y + bb.Max.Y) / 2 / MM, hx = (bb.Max.X - bb.Min.X) / 2 / MM, hy = (bb.Max.Y - bb.Min.Y) / 2 / MM;
                    bool below = cy < 3000;   // row Л: the mark under the plate (DWG)
                    double ax = cx + hx, ay = below ? cy - hy : cy + hy;
                    double tx = cx + 2.5 * S, ty = below ? cy - hy - 8 * S : cy + hy + 3.5 * S;
                    TextNoteOptions o = new TextNoteOptions(t25.Id); o.HorizontalAlignment = HorizontalTextAlignment.Left; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                    TextNote tn = TextNote.Create(doc, v.Id, new XYZ(tx * MM, ty * MM, z0), Mk(e), o);
                    FormattedText f = tn.GetFormattedText(); f.SetUnderlineStatus(true); tn.SetFormattedText(f);
                    try { Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = new XYZ(ax * MM, ay * MM, z0); } catch { }
                    n++;
                }
            // 1500: row М to the К2 row, on the line of the 7300 dim
            Grid gM = new FilteredElementCollector(doc).OfClass(typeof(Grid)).Cast<Grid>().FirstOrDefault(g => g.Name == "М");
            Dimension d7300 = new FilteredElementCollector(doc, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>().FirstOrDefault(d => d.Curve is Line && Math.Abs(((Line)d.Curve).Direction.Y) > 0.9 && d.Value.HasValue && Math.Abs(d.Value.Value / MM - 7300) < 5);
            List<Element> zd2 = zd.Where(e => Mk(e) == "Зд-2").ToList();
            if (dimT != null && gM != null && d7300 != null && zd2.Count > 0 && !new FilteredElementCollector(doc, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>().Any(d => d.Value.HasValue && Math.Abs(d.Value.Value / MM - 1500) < 60))
            {
                double xd = d7300.Origin.X / MM;   // (a dim curve is unbound: take its origin)
                double yk = zd2.Average(e => (e.get_BoundingBox(null).Min.Y + e.get_BoundingBox(null).Max.Y) / 2) / MM;
                try
                {
                    DetailCurve dc = doc.Create.NewDetailCurve(v, Line.CreateBound(new XYZ((xd + 2 * S) * MM, yk * MM, z0), new XYZ((xd + 4 * S) * MM, yk * MM, z0)));
                    ReferenceArray ra = new ReferenceArray(); ra.Append(new Reference(gM)); ra.Append(dc.GeometryCurve.Reference);
                    doc.Create.NewDimension(v, Line.CreateBound(new XYZ(xd * MM, 0, z0), new XYZ(xd * MM, 1, z0)), ra, dimT);
                    L("  sheet 3: 1500 dim added (К2 row at " + Math.Round(yk) + ")");
                }
                catch (Exception ex) { L("  1500 dim " + ex.Message.Split('\n')[0]); }
            }
            L("  sheet 3: Зд marks " + n + ", other plates hidden " + hide.Count);
        }
    }
}
