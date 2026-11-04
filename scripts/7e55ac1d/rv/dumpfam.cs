using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    public static class FamDumper
    {
        public static void Dump(Application app, string src, string famName, string outTxt)
        {
            StringBuilder sb = new StringBuilder();
            Document d = app.OpenDocumentFile(src);
            try
            {
                Family fam = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().First(f => f.Name == famName);
                Document fd = d.EditFamily(fam);
                FamilyManager fm = fd.FamilyManager;
                sb.AppendLine("== params (current type " + (fm.CurrentType != null ? fm.CurrentType.Name : "-") + ")");
                foreach (FamilyParameter p in fm.Parameters.Cast<FamilyParameter>().OrderBy(p => p.Definition.Name))
                {
                    string v = "";
                    try { if (fm.CurrentType != null) v = p.StorageType == StorageType.String ? fm.CurrentType.AsString(p) : fm.CurrentType.AsValueString(p); } catch { }
                    sb.AppendLine("  " + (p.IsInstance ? "I " : "T ") + (p.IsShared ? "S " : "  ") + p.Definition.Name + " = " + v + (string.IsNullOrEmpty(p.Formula) ? "" : "   f: " + p.Formula));
                }
                sb.AppendLine("== text elements");
                foreach (TextElement t in new FilteredElementCollector(fd).OfClass(typeof(TextElement)).Cast<TextElement>())
                {
                    BoundingBoxXYZ bb = t.get_BoundingBox(null);
                    sb.AppendLine("  " + t.GetType().Name + " | " + (t.Text ?? "").Replace("\r", " ").Replace("\n", " ") + " | " + (bb != null ? Math.Round(bb.Min.X * 304.8) + "," + Math.Round(bb.Min.Y * 304.8) : ""));
                }
                foreach (Element t in new FilteredElementCollector(fd).WhereElementIsNotElementType().Where(e => e.GetType().Name.Contains("Label") || (e.Category != null && e.Category.Name.Contains("Метк"))))
                    sb.AppendLine("  label? " + t.GetType().Name + " " + t.Name);
                sb.AppendLine("== nested instances");
                foreach (FamilyInstance fi in new FilteredElementCollector(fd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
                {
                    BoundingBoxXYZ bb = fi.get_BoundingBox(null);
                    sb.AppendLine("  " + fi.Symbol.FamilyName + " : " + fi.Symbol.Name + " @ " + (bb != null ? Math.Round(bb.Min.X * 304.8) + "," + Math.Round(bb.Min.Y * 304.8) + " - " + Math.Round(bb.Max.X * 304.8) + "," + Math.Round(bb.Max.Y * 304.8) : ""));
                }
                sb.AppendLine("== images");
                foreach (ImageType it in new FilteredElementCollector(fd).OfClass(typeof(ImageType)).Cast<ImageType>()) sb.AppendLine("  " + it.Name + " " + it.Path);
                sb.AppendLine("== nested families");
                foreach (Family f in new FilteredElementCollector(fd).OfClass(typeof(Family)).Cast<Family>())
                {
                    sb.AppendLine("  " + f.Name);
                    try
                    {
                        Document nd = fd.EditFamily(f);
                        foreach (TextElement t in new FilteredElementCollector(nd).OfClass(typeof(TextElement)).Cast<TextElement>())
                            if ((t.Text ?? "").Length > 0) sb.AppendLine("     text " + (t.Text ?? "").Replace("\r", " ").Replace("\n", " "));
                        foreach (ImageType it in new FilteredElementCollector(nd).OfClass(typeof(ImageType)).Cast<ImageType>()) sb.AppendLine("     image " + it.Name);
                        foreach (FamilyParameter p in nd.FamilyManager.Parameters) sb.AppendLine("     param " + p.Definition.Name + (string.IsNullOrEmpty(p.Formula) ? "" : " f: " + p.Formula));
                        nd.Close(false);
                    }
                    catch (Exception ex) { sb.AppendLine("     ERR " + ex.Message); }
                }
                fd.Close(false);
            }
            catch (Exception ex) { sb.AppendLine("ERR " + ex); }
            File.WriteAllText(outTxt, sb.ToString(), Encoding.UTF8);
            d.Close(false);
        }
    }
}
