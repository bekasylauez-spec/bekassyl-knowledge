using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    public static class SecDumper
    {
        public static void Dump(Application app, string tpl, string outTxt)
        {
            StringBuilder sb = new StringBuilder();
            Document d = app.NewProjectDocument(tpl);
            foreach (ViewFamilyType vt in new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().Where(v => v.ViewFamily == ViewFamily.Section || v.ViewFamily == ViewFamily.Detail))
            {
                sb.AppendLine("VFT " + vt.ViewFamily + " " + vt.Name);
                foreach (Parameter p in vt.Parameters) sb.AppendLine("   " + p.Definition.Name + " = " + (p.StorageType == StorageType.ElementId && d.GetElement(p.AsElementId()) != null ? d.GetElement(p.AsElementId()).Name + " [" + d.GetElement(p.AsElementId()).GetType().Name + "]" : p.AsValueString()));
            }
            foreach (ElementType et in new FilteredElementCollector(d).OfClass(typeof(ElementType)).Cast<ElementType>().Where(t => t.GetType().Name.Contains("Tag") || t.FamilyName.Contains("разрез") || t.FamilyName.Contains("Разрез") || t.FamilyName.Contains("рагмент")))
            {
                sb.AppendLine("TYPE " + et.GetType().Name + " " + et.FamilyName + " : " + et.Name);
                foreach (Parameter p in et.Parameters) sb.AppendLine("   " + p.Definition.Name + " = " + (p.StorageType == StorageType.ElementId && d.GetElement(p.AsElementId()) != null ? d.GetElement(p.AsElementId()).Name : p.AsValueString()));
            }
            DimensionType dt = new FilteredElementCollector(d).OfClass(typeof(DimensionType)).Cast<DimensionType>().First(t => t.StyleType == DimensionStyleType.Linear && t.Name.Contains("2,5"));
            sb.AppendLine("DIM " + dt.Name);
            foreach (Parameter p in dt.Parameters) sb.AppendLine("   " + p.Definition.Name + " = " + (p.StorageType == StorageType.ElementId && d.GetElement(p.AsElementId()) != null ? d.GetElement(p.AsElementId()).Name : p.AsValueString()) + " (" + (p.Definition as InternalDefinition).BuiltInParameter + ")");
            foreach (Family f in new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().Where(f => f.FamilyCategory != null && (f.FamilyCategory.Id.Value == (long)BuiltInCategory.OST_SectionHeads || f.FamilyCategory.Id.Value == (long)BuiltInCategory.OST_CalloutHeads)).ToList())
            {
                sb.AppendLine("FAM " + f.Name);
                try
                {
                    Document fd = d.EditFamily(f);
                    foreach (CurveElement ce in new FilteredElementCollector(fd).OfClass(typeof(CurveElement)).Cast<CurveElement>())
                    {
                        Curve c = ce.GeometryCurve;
                        sb.AppendLine("   curve " + c.GetType().Name + " " + P(c.GetEndPoint(0)) + " -> " + P(c.GetEndPoint(1)) + " style " + (ce.LineStyle != null ? ce.LineStyle.Name : ""));
                    }
                    foreach (TextElement te in new FilteredElementCollector(fd).OfClass(typeof(TextElement)).Cast<TextElement>())
                    {
                        string lab = "";
                        try { foreach (Parameter pp in te.Parameters) if (pp.Definition.Name.Contains("Метк") || pp.Definition.Name.Contains("Label")) lab += pp.Definition.Name + "=" + pp.AsValueString() + ";"; } catch { }
                        sb.AppendLine("   text " + te.GetType().Name + " '" + te.Text + "' at " + P(te.Coord) + " " + lab + " align " + te.HorizontalAlignment);
                    }
                    foreach (Element fr in new FilteredElementCollector(fd).OfClass(typeof(FilledRegion))) sb.AppendLine("   filled region " + fr.Id);
                    foreach (Element e in new FilteredElementCollector(fd).WhereElementIsNotElementType().Where(e => e.GetType().Name.Contains("Label") || e.GetType().Name == "FamilyElement")) sb.AppendLine("   other " + e.GetType().Name);
                    fd.Close(false);
                }
                catch (Exception ex) { sb.AppendLine("   ERR " + ex.Message); }
            }
            File.WriteAllText(outTxt, sb.ToString(), Encoding.UTF8);
            d.Close(false);
        }
        static string P(XYZ p) { return "(" + Math.Round(p.X * 304.8, 1) + "," + Math.Round(p.Y * 304.8, 1) + ")"; }
    }
}
