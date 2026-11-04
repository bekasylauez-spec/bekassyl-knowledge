using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.PlottingServices;

[assembly: CommandClass(typeof(PlotW.Cmds))]
namespace PlotW
{
    // window plot of model-space frames to single PDF files (console AutoCAD)
    public class Cmds
    {
        static double D(object o) { return Convert.ToDouble(o, System.Globalization.CultureInfo.InvariantCulture); }
        [CommandMethod("PLOTW")]
        public static void Run()
        {
            var doc = Application.DocumentManager.MdiActiveDocument; var db = doc.Database;
            var log = new StringBuilder();
            var jobs = (object[])new JavaScriptSerializer().DeserializeObject(File.ReadAllText(Environment.GetEnvironmentVariable("TEMP") + "\\plotc.json", Encoding.UTF8));
            Application.SetSystemVariable("BACKGROUNDPLOT", 0);
            try { LayoutManager.Current.CurrentLayout = "Model"; } catch { }
            try { Application.SetSystemVariable("TILEMODE", 1); } catch { }
            var tgs = (Point3d)Application.GetSystemVariable("TARGET");
            Point3d tg;
            using (var tr0 = db.TransactionManager.StartTransaction())
            {
                var vt = (ViewportTable)tr0.GetObject(db.ViewportTableId, OpenMode.ForRead);
                var av = (ViewportTableRecord)tr0.GetObject(vt["*Active"], OpenMode.ForRead);
                tg = av.Target; tr0.Commit();
            }
            log.AppendLine("TARGET sysvar " + tgs + " vport WCS " + tg);
            foreach (Dictionary<string, object> j in jobs)
            {
                try
                {
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var btr = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                        var lay = (Layout)tr.GetObject(btr.LayoutId, OpenMode.ForRead);
                        var ps = new PlotSettings(true); ps.CopyFrom(lay);
                        var v = PlotSettingsValidator.Current;
                        v.SetPlotConfigurationName(ps, "DWG To PDF.pc3", (string)j["media"]);
                        v.SetPlotPaperUnits(ps, PlotPaperUnit.Millimeters);
                        v.SetPlotRotation(ps, PlotRotation.Degrees000);
                        var win = new Extents2d(D(j["x0"]) - tg.X, D(j["y0"]) - tg.Y, D(j["x1"]) - tg.X, D(j["y1"]) - tg.Y);
                        v.SetPlotWindowArea(ps, win);
                        v.SetPlotType(ps, Autodesk.AutoCAD.DatabaseServices.PlotType.Window);
                        v.SetUseStandardScale(ps, false);
                        v.SetCustomPrintScale(ps, new CustomScale(1.0, D(j["sc"])));
                        v.SetPlotCentered(ps, true);
                        v.RefreshLists(ps); try { v.SetCurrentStyleSheet(ps, "monochrome.ctb"); } catch { try { v.SetCurrentStyleSheet(ps, "monochrome.stb"); } catch (System.Exception ex2) { log.AppendLine("style ERR " + ex2.Message); } }
                        ps.ScaleLineweights = false; ps.PrintLineweights = true; ps.PlotPlotStyles = true;
                        var pi = new PlotInfo { Layout = btr.LayoutId, OverrideSettings = ps };
                        var piv = new PlotInfoValidator { MediaMatchingPolicy = MatchingPolicy.MatchEnabled };
                        piv.Validate(pi);
                        string outp = (string)j["out"];
                        using (var pe = PlotFactory.CreatePublishEngine())
                        {
                            pe.BeginPlot(null, null);
                            pe.BeginDocument(pi, doc.Name, null, 1, true, outp);
                            var ppi = new PlotPageInfo();
                            pe.BeginPage(ppi, pi, true, null);
                            pe.BeginGenerateGraphics(null); pe.EndGenerateGraphics(null);
                            pe.EndPage(null); pe.EndDocument(null); pe.EndPlot(null);
                        }
                        tr.Commit();
                        log.AppendLine(j["n"] + " ok " + File.Exists(outp));
                    }
                }
                catch (System.Exception ex) { log.AppendLine(j["n"] + " ERR " + ex.Message); }
            }
            File.WriteAllText(Environment.GetEnvironmentVariable("TEMP") + "\\plotc_log.txt", log.ToString(), Encoding.UTF8);
        }
    }
}
