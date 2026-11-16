using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(LayDump.Cmds))]
namespace LayDump
{
    // dump every layout: page setup + viewports + paper-space entity extents -> %JOB_OUT%
    public class Cmds
    {
        static string P(Point2d p) { return p.X.ToString("0.###") + "," + p.Y.ToString("0.###"); }
        static string P3(Point3d p) { return p.X.ToString("0.###") + "," + p.Y.ToString("0.###"); }

        [CommandMethod("LAYDUMP")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            string outp = Environment.GetEnvironmentVariable("JOB_OUT");
            var sb = new StringBuilder();
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                    var lays = new List<Layout>();
                    foreach (DBDictionaryEntry en in ld) lays.Add((Layout)tr.GetObject(en.Value, OpenMode.ForRead));
                    lays.Sort((a, b) => a.TabOrder.CompareTo(b.TabOrder));
                    foreach (var lo in lays)
                    {
                        sb.AppendLine("LAYOUT|" + lo.TabOrder + "|" + lo.LayoutName + "|model=" + lo.ModelType);
                        sb.AppendLine("  dev=" + lo.PlotConfigurationName + " media=" + lo.CanonicalMediaName +
                            " paper=" + P(lo.PlotPaperSize) + " rot=" + lo.PlotRotation + " type=" + lo.PlotType +
                            " units=" + lo.PlotPaperUnits + " std=" + lo.UseStandardScale + " " + lo.StdScaleType +
                            " cust=" + lo.CustomPrintScale.Numerator + "/" + lo.CustomPrintScale.Denominator +
                            " win=" + P(lo.PlotWindowArea.MinPoint) + ".." + P(lo.PlotWindowArea.MaxPoint) +
                            " origin=" + P(lo.PlotOrigin) + " center=" + lo.PlotCentered + " ctb=" + lo.CurrentStyleSheet +
                            " margins=" + P(lo.PlotPaperMargins.MinPoint) + ".." + P(lo.PlotPaperMargins.MaxPoint));
                        if (lo.ModelType) continue;
                        var btr = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForRead);
                        var ext = new Extents3d(); bool has = false; int n = 0;
                        var types = new Dictionary<string, int>();
                        foreach (ObjectId id in btr)
                        {
                            var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                            if (e == null) continue;
                            string tn = e.GetType().Name;
                            if (e is Viewport)
                            {
                                var v = (Viewport)e;
                                sb.AppendLine("  VP num=" + v.Number + " c=" + P3(v.CenterPoint) + " w=" + v.Width.ToString("0.##") + " h=" + v.Height.ToString("0.##") +
                                    " vc=" + P(v.ViewCenter) + " tgt=" + P3(v.ViewTarget) + " sc=" + v.CustomScale.ToString("0.######") +
                                    " on=" + v.On + " lock=" + v.Locked + " clip=" + v.NonRectClipOn + " twist=" + v.TwistAngle.ToString("0.###") + " h=" + v.Handle);
                                if (v.Number == 1) continue;
                            }
                            n++;
                            if (!types.ContainsKey(tn)) types[tn] = 0; types[tn]++;
                            try { var x = e.GeometricExtents; if (has) ext.AddExtents(x); else { ext = x; has = true; } } catch { }
                        }
                        var ts = new StringBuilder(); foreach (var kv in types) ts.Append(kv.Key + ":" + kv.Value + " ");
                        sb.AppendLine("  PS n=" + n + " ext=" + (has ? P3(ext.MinPoint) + ".." + P3(ext.MaxPoint) : "none") + " types=" + ts);
                    }
                    tr.Commit();
                }
            }
            catch (System.Exception ex) { sb.AppendLine("ERR " + ex); }
            File.WriteAllText(outp, sb.ToString(), Encoding.UTF8);
        }
    }
}
