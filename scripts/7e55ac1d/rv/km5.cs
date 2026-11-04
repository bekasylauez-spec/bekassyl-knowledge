using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    // SPDS section marks on the plans: generic annotation (stroke 6 mm, arrow 8.4 mm with a 3 x 1 filled head) + number text, at both ends of each section
    public partial class App
    {
        static FamilySymbol[] MakeSectionSigns(Application app, Document doc, string rft, string dir)
        {
            FamilySymbol[] res = new FamilySymbol[2];
            for (int m = 0; m < 2; m++)
            {
                string name = m == 0 ? "КМ_Знак разреза" : "КМ_Знак разреза (зерк)";
                double sg = m == 0 ? -1 : 1;   // stroke goes to -Y (normal) or +Y (mirrored) from the outer end
                Document fd = app.NewFamilyDocument(rft);
                using (Transaction t = new Transaction(fd, "sign"))
                {
                    t.Start();
                    foreach (ElementId id in new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).ToElementIds().ToList()) { try { fd.Delete(id); } catch { } }
                    foreach (ElementId id in new FilteredElementCollector(fd).OfClass(typeof(TextElement)).ToElementIds().ToList()) { try { fd.Delete(id); } catch { } }
                    View v = FamView(fd);
                    FThick(fd, v, 0, 0, 0, sg * 6);
                    FLine(fd, v, 0, sg * 1.3, 8.4, sg * 1.3);
                    FFill(fd, v, 0, sg * 1.3, 3, sg * 1.3 + 0.5, 3, sg * 1.3 - 0.5);
                    t.Commit();
                }
                string p = Path.Combine(dir, name + ".rfa");
                SaveAsOptions so = new SaveAsOptions(); so.OverwriteExistingFile = true; so.MaximumBackups = 1;
                fd.SaveAs(p, so); fd.Close(false);
                Family f = null;
                Tx(doc, "load " + name, delegate { doc.LoadFamily(p, new LoadOpts(), out f); });
                if (f == null) f = Find<Family>(doc, x => x.Name == name);
                res[m] = f != null ? (FamilySymbol)doc.GetElement(f.GetFamilySymbolIds().First()) : null;
                L("  sign " + name + (res[m] != null ? " ok" : " FAILED"));
            }
            return res;
        }

        // one mark: P = outer end of the stroke, inward = towards the other end, d = view direction (all in plan)
        static void PlaceSign(Document doc, View v, FamilySymbol[] signs, XYZ P, XYZ inward, XYZ d, string num, TextNoteType tt)
        {
            XYZ xl = d.Negate();
            // normal family: stroke along -Y_l = inward  -> Y_l = -inward; mirrored: stroke along +Y_l -> Y_l = inward
            XYZ ylN = inward.Negate();
            bool normal = xl.CrossProduct(ylN).Z > 0;
            XYZ yl = normal ? ylN : inward;
            FamilySymbol s = normal ? signs[0] : signs[1];
            if (s == null) return;
            if (!s.IsActive) s.Activate();
            FamilyInstance fi = doc.Create.NewFamilyInstance(P, s, v);
            double ang = Math.Atan2(xl.Y, xl.X);
            if (Math.Abs(ang) > 1e-6) ElementTransformUtils.RotateElement(doc, fi.Id, Line.CreateBound(P, P + XYZ.BasisZ), ang);
            double sc = v.Scale * MM;
            // number above the arrow line, on the outer side of it (DWG: 6.3 mm along the arrow, 2 mm off it)
            XYZ outer = normal ? yl : yl.Negate();
            XYZ arrowY = (normal ? yl.Negate() : yl) * (1.3 * sc);
            XYZ tp = P + arrowY + xl * (6.3 * sc) + outer * (2.0 * sc);
            TextNoteOptions o = new TextNoteOptions(tt.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Middle;
            TextNote.Create(doc, v.Id, tp, num, o);
        }

        static void SectionSigns(Document doc, Dictionary<string, View> V, FamilySymbol[] signs, TextNoteType tt)
        {
            // plan positions (mm): 1-1 / 2-2 on x = frame - 150, looking to -X; 3-3 / 4-4 on y = 6900 / -1100, looking to +Y
            object[][] secs = {
                new object[]{ "1", new XYZ(4200, 9350, 0), new XYZ(4200, -2350, 0), new XYZ(-1, 0, 0) },
                new object[]{ "2", new XYZ(16300, 9350, 0), new XYZ(16300, -2350, 0), new XYZ(-1, 0, 0) },
                new object[]{ "3", new XYZ(-2350, 6900, 0), new XYZ(24350, 6900, 0), new XYZ(0, 1, 0) },
                new object[]{ "4", new XYZ(-2350, -1100, 0), new XYZ(24350, -1100, 0), new XYZ(0, 1, 0) } };
            foreach (string k in new[] { "p3", "p4", "p5", "p6" })
            {
                View v = V[k];
                try { v.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Sections), true); } catch { }
                foreach (object[] s in secs)
                {
                    XYZ a = ((XYZ)s[1]) * MM, b = ((XYZ)s[2]) * MM, d = (XYZ)s[3];
                    XYZ ab = (b - a).Normalize();
                    try
                    {
                        PlaceSign(doc, v, signs, a, ab, d, (string)s[0], tt);
                        PlaceSign(doc, v, signs, b, ab.Negate(), d, (string)s[0], tt);
                    }
                    catch (Exception ex) { L("sign " + k + " " + s[0] + " " + ex.Message); }
                }
            }
        }
    }
}
