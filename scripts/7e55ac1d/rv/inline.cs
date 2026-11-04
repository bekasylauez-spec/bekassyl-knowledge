using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    // plan marks as in the DWG (sheets 4-6): the mark is written along the member over its middle, no leader, no shelf;
    // one mark per bay for members along the rows, one per diagonal; trusses get «Ферма Ф1/Ф2» along their line
    public partial class App
    {
        static FamilySymbol InlineTagFamily(Document doc, string name, bool below, string dir)
        {
            Family f = Find<Family>(doc, x => x.Name == name);
            if (f != null) return Sym(doc, f);
            string src = Find<Family>(doc, x => x.Name == "M_Марка несущего каркаса") != null ? "M_Марка несущего каркаса" : "КМ_Марка каркаса";
            return Sym(doc, RemakeFamily(doc, src, name, dir, delegate (Document fd, View v, List<TextElement> lb)
            {
                TextElement first = lb.FirstOrDefault();
                foreach (TextElement te in lb.Skip(1).ToList()) { try { fd.Delete(te.Id); } catch { } }
                if (first == null) return;
                XYZ bd = first.BaseDirection;
                double ang = Math.Atan2(bd.Y, bd.X);
                if (Math.Abs(ang) > 1e-3) ElementTransformUtils.RotateElement(fd, first.Id, Line.CreateBound(first.Coord, first.Coord + XYZ.BasisZ), -ang);
                if (below) FLabel(fd, first, 2.5, HorizontalTextAlignment.Center, VerticalTextAlignment.Top, 0, -0.8);
                else FLabel(fd, first, 2.5, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0, 0.8);
            }));
        }

        static string Mk(Element e) { Parameter p = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK); return p != null ? p.AsString() : null; }

        static void InlineMarks(Document doc, FamilySymbol up, FamilySymbol dn)
        {
            if (up == null || dn == null) { L("inline tag families FAILED"); return; }
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            List<FamilyInstance> frame = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().Where(f => f.Location is LocationCurve).ToList();
            // truss lines: chords running along Y, grouped by X
            Func<FamilyInstance, bool> alongY = f => { XYZ d = ((LocationCurve)f.Location).Curve.GetEndPoint(1) - ((LocationCurve)f.Location).Curve.GetEndPoint(0); return Math.Abs(d.Y) > 5 * Math.Abs(d.X); };
            var trusses = frame.Where(f => (Mk(f) == "НП1" || Mk(f) == "ВП1") && alongY(f))
                .GroupBy(f => Math.Round(((LocationCurve)f.Location).Curve.GetEndPoint(0).X / MM / 50) * 50)
                .Select(g => new { X = g.Key, YMax = g.Max(f => Math.Max(((LocationCurve)f.Location).Curve.GetEndPoint(0).Y, ((LocationCurve)f.Location).Curve.GetEndPoint(1).Y) / MM) })
                .OrderBy(t => t.X).ToList();
            List<double> tx = trusses.Select(t => t.X).ToList();
            L("  trusses x: " + string.Join(" ", trusses.Select(t => t.X + (t.YMax > 8000 ? "(Ф1)" : "(Ф2)"))));

            object[][] plans = {
                new object[]{ "стоек и вертикальных", new[]{ "СВ1", "СВ2" }, null, 0.0 },
                new object[]{ "нижним", new[]{ "СВ3", "РС1", "СГ1", "П1" }, new[]{ "НП1" }, 2700.0 },
                new object[]{ "верхним", new[]{ "П1" }, new[]{ "ВП1" }, 5100.0 } };
            foreach (object[] pl in plans)
            {
                View v = new FilteredElementCollector(doc).OfClass(typeof(ViewPlan)).Cast<View>().FirstOrDefault(x => !x.IsTemplate && x.Name.Contains((string)pl[0]));
                if (v == null) { L("  no plan " + pl[0]); continue; }
                string[] marks = (string[])pl[1];
                string[] chord = (string[])pl[2];
                HashSet<string> drop = new HashSet<string>(marks); if (chord != null) foreach (string c in chord) drop.Add(c);
                // old marks of these members: tags and fallback notes
                int del = 0;
                foreach (IndependentTag tg in new FilteredElementCollector(doc, v.Id).OfClass(typeof(IndependentTag)).Cast<IndependentTag>().ToList())
                {
                    Element te = tg.GetTaggedLocalElements().FirstOrDefault();
                    if (te != null && te.Category != null && te.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming && drop.Contains(Mk(te))) { doc.Delete(tg.Id); del++; }
                }
                foreach (TextNote tn in new FilteredElementCollector(doc, v.Id).OfClass(typeof(TextNote)).Cast<TextNote>().ToList())
                    if (drop.Contains((tn.Text ?? "").Trim()) || (tn.Text ?? "").Trim().StartsWith("Ферма Ф")) { doc.Delete(tn.Id); del++; }
                HashSet<ElementId> inView = new HashSet<ElementId>(new FilteredElementCollector(doc, v.Id).OfCategory(BuiltInCategory.OST_StructuralFraming).ToElementIds());
                List<XYZ> taken = new List<XYZ>();
                HashSet<string> rowTaken = new HashSet<string>();   // DWG: one mark per row/bay (СВ3 wins over РС1 lying in the same place)
                int made = 0;
                foreach (string mk in marks)
                {
                    List<FamilyInstance> els = frame.Where(f => Mk(f) == mk && inView.Contains(f.Id) && !f.IsHidden(v)).ToList();
                    // groups: members along X -> one mark per (row, bay); others -> one per member
                    var groups = new Dictionary<string, List<FamilyInstance>>();
                    foreach (FamilyInstance f in els)
                    {
                        Curve c = ((LocationCurve)f.Location).Curve;
                        XYZ a = c.GetEndPoint(0), b = c.GetEndPoint(1);
                        XYZ d = new XYZ(b.X - a.X, b.Y - a.Y, 0);
                        string key;
                        if (d.GetLength() < 50 * MM) continue;   // vertical in plan
                        if (Math.Abs(d.Y) < 0.05 * Math.Abs(d.X))
                        {
                            double xm = (a.X + b.X) / 2 / MM;
                            int bay = tx.Count(x => x < xm);
                            key = "row " + Math.Round((a.Y + b.Y) / 2 / MM / 50) + " bay " + bay;
                        }
                        else key = "el " + f.Id.Value;
                        if (!groups.ContainsKey(key)) groups[key] = new List<FamilyInstance>();
                        groups[key].Add(f);
                    }
                    foreach (var kv in groups)
                    {
                        if (kv.Key.StartsWith("row")) { if (rowTaken.Contains(kv.Key)) continue; rowTaken.Add(kv.Key); }
                        List<XYZ> pts = kv.Value.SelectMany(f => new[] { ((LocationCurve)f.Location).Curve.GetEndPoint(0), ((LocationCurve)f.Location).Curve.GetEndPoint(1) }).ToList();
                        XYZ mid;
                        if (kv.Key.StartsWith("row"))
                        {
                            double x0 = pts.Min(p => p.X), x1 = pts.Max(p => p.X);
                            mid = new XYZ((x0 + x1) / 2, pts.Average(p => p.Y), 0);
                        }
                        else { Curve c = ((LocationCurve)kv.Value[0].Location).Curve; XYZ m = c.Evaluate(0.5, true); mid = new XYZ(m.X, m.Y, 0); }
                        FamilyInstance host = kv.Value.OrderBy(f => { XYZ m = ((LocationCurve)f.Location).Curve.Evaluate(0.5, true); return Math.Abs(m.X - mid.X) + Math.Abs(m.Y - mid.Y); }).First();
                        // outer edge of the cantilever: СВ3 goes under the line (the СГ1 marks sit above it)
                        bool busy = taken.Any(p => p.DistanceTo(mid) < 300 * MM) || (mk == "СВ3" && mid.Y < -500 * MM);
                        FamilySymbol s = busy ? dn : up;
                        if (!s.IsActive) s.Activate();
                        try
                        {
                            IndependentTag tg = IndependentTag.Create(doc, s.Id, v.Id, new Reference(host), false, TagOrientation.AnyModelDirection, mid);
                            tg.TagHeadPosition = mid;
                            made++;
                        }
                        catch (Exception ex) { L("  tag " + mk + " " + ex.Message); }
                        taken.Add(mid);
                    }
                }
                // «Ферма Ф1/Ф2» along each truss line, left of it, reading upwards
                if (chord != null && t25 != null)
                    foreach (var t in trusses)
                    {
                        TextNoteOptions o = new TextNoteOptions(t25.Id);
                        o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                        o.Rotation = Math.PI / 2;
                        TextNote.Create(doc, v.Id, new XYZ(t.X * MM - 0.8 * MM * v.Scale, (double)pl[3] * MM, 0), t.YMax > 8000 ? "Ферма Ф1" : "Ферма Ф2", o);
                        made++;
                    }
                L("  " + v.Name + ": removed " + del + ", placed " + made);
            }
        }
    }
}
