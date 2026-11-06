using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Globalization;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.PlottingServices;

namespace LAY3
{
    // %TEMP%\lay3.txt lines: name|x0|y0|x1|y1|scale   (model window of a sheet frame, plot scale 1:scale)
    // creates/updates one Layout per line: DWG To PDF, media = smallest list entry that holds the frame, one viewport 1:scale
    // optional %TEMP%\lay3_pdf.txt: folder -> plots every listed layout to <folder>\<name>.pdf
    public class Cmds
    {
        static CultureInfo IC = CultureInfo.InvariantCulture;
        public static void Apply()
        {
            var doc = Application.DocumentManager.MdiActiveDocument; var db = doc.Database;
            string tmp = Environment.GetEnvironmentVariable("TEMP");
            var log = new StringBuilder();
            var lines = File.ReadAllLines(Path.Combine(tmp, "lay3.txt"), Encoding.UTF8);
            string pdfdir = File.Exists(Path.Combine(tmp, "lay3_pdf.txt")) ? File.ReadAllText(Path.Combine(tmp, "lay3_pdf.txt"), Encoding.UTF8).Trim() : null;
            var lm = LayoutManager.Current;
            var names = new List<string>();
            foreach (var ln in lines)
            {
                if (ln.Trim() == "") continue;
                var f = ln.Split('|'); string name = f[0];
                double x0 = double.Parse(f[1], IC), y0 = double.Parse(f[2], IC), x1 = double.Parse(f[3], IC), y1 = double.Parse(f[4], IC), sc = double.Parse(f[5], IC);
                double pw = (x1 - x0) / sc, ph = (y1 - y0) / sc;   // paper mm
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                    ObjectId lid = ld.Contains(name) ? ld.GetAt(name) : lm.CreateLayout(name);
                    var lo = (Layout)tr.GetObject(lid, OpenMode.ForWrite);
                    var v = PlotSettingsValidator.Current;
                    var ps = new PlotSettings(false); ps.CopyFrom(lo);
                    v.SetPlotConfigurationName(ps, "DWG To PDF.pc3", null); v.RefreshLists(ps);
                    string best = null; double ba = 1e18; bool rot = false;
                    foreach (string mn in v.GetCanonicalMediaNameList(ps))
                    {
                        if (!mn.StartsWith("ISO_full_bleed")) continue;
                        v.SetCanonicalMediaName(ps, mn);
                        var sz = ps.PlotPaperSize; double a = sz.X * sz.Y;
                        bool fit0 = sz.X >= pw - 0.5 && sz.Y >= ph - 0.5, fit1 = sz.Y >= pw - 0.5 && sz.X >= ph - 0.5;
                        if ((fit0 || fit1) && a < ba) { ba = a; best = mn; rot = !fit0; }
                    }
                    v.SetCanonicalMediaName(ps, best);
                    v.SetPlotType(ps, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout);
                    v.SetUseStandardScale(ps, true); v.SetStdScaleType(ps, StdScaleType.StdScale1To1);
                    v.SetPlotRotation(ps, rot ? PlotRotation.Degrees090 : PlotRotation.Degrees000);
                    v.SetPlotCentered(ps, true);
                    v.SetCurrentStyleSheet(ps, "monochrome.ctb"); ps.ShowPlotStyles = true; ps.PrintLineweights = true;
                    lo.CopyFrom(ps);
                    var btr = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForWrite);
                    Viewport vp = null;
                    foreach (ObjectId id in btr) { var q = tr.GetObject(id, OpenMode.ForWrite) as Viewport; if (q == null) continue; if (q.Number == 1 || vp != null) { if (q.Number != 1 && vp != null) q.Erase(); continue; } vp = q; }
                    // paper origin = lower-left of the printable sheet; centre the frame on the paper
                    var pp = lo.PlotPaperSize; double PW = rot ? pp.Y : pp.X, PH = rot ? pp.X : pp.Y;
                    if (vp == null) { vp = new Viewport(); btr.AppendEntity(vp); tr.AddNewlyCreatedDBObject(vp, true); }
                    vp.CenterPoint = new Point3d(PW / 2.0, PH / 2.0, 0); vp.Width = pw; vp.Height = ph;
                    vp.ViewDirection = Vector3d.ZAxis; vp.ViewTarget = Point3d.Origin; vp.TwistAngle = 0;
                    vp.ViewCenter = new Point2d((x0 + x1) / 2.0, (y0 + y1) / 2.0);
                    vp.CustomScale = 1.0 / sc; vp.Locked = true; vp.On = true;
                    log.AppendLine("layout " + name + " media " + best + (rot ? " rot" : "") + " paper " + PW.ToString("0", IC) + "x" + PH.ToString("0", IC));
                    tr.Commit();
                }
                names.Add(name);
            }
            if (pdfdir != null)
            {
                Autodesk.AutoCAD.ApplicationServices.Core.Application.SetSystemVariable("BACKGROUNDPLOT", 0);
                foreach (var name in names)
                {
                    lm.CurrentLayout = name;
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                        var lo = (Layout)tr.GetObject(ld.GetAt(name), OpenMode.ForRead);
                        var pi = new PlotInfo(); pi.Layout = lo.ObjectId;
                        var piv = new PlotInfoValidator(); piv.MediaMatchingPolicy = MatchingPolicy.MatchEnabled; piv.Validate(pi);
                        string file = Path.Combine(pdfdir, name + ".pdf");
                        using (var pe = PlotFactory.CreatePublishEngine())
                        {
                            var ppi = new PlotPageInfo();
                            pe.BeginPlot(null, null);
                            pe.BeginDocument(pi, "doc", null, 1, true, file);
                            pe.BeginPage(ppi, pi, true, null); pe.BeginGenerateGraphics(null); pe.EndGenerateGraphics(null);
                            pe.EndPage(null); pe.EndDocument(null); pe.EndPlot(null);
                        }
                        log.AppendLine("pdf " + file);
                        tr.Commit();
                    }
                }
            }
            try { lm.CurrentLayout = "Model"; } catch { }
            File.WriteAllText(Path.Combine(tmp, "lay3_log.txt"), log.ToString(), Encoding.UTF8);
        }
    }
}
