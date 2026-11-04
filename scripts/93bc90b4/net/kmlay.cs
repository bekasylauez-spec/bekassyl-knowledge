using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(KmLay.Cmd))]

namespace KmLay
{
    // One layout per model frame: LAY|name|x0|S|W|H|media ; one viewport shows the frame at 1:S
    public class Cmd
    {
        static double D(string s) { return double.Parse(s, CultureInfo.InvariantCulture); }

        [CommandMethod("KMLAY")]
        public void Run()
        {
            var lines = File.ReadAllLines(Environment.GetEnvironmentVariable("KMLAY_CONF"), Encoding.UTF8);
            StreamWriter log = null; string outPath = null;
            foreach (var c in lines) { var p = c.Split('|'); if (p[0] == "LOG") log = new StreamWriter(p[1], false, Encoding.UTF8); if (p[0] == "OUT") outPath = p[1]; }
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                Application.SetSystemVariable("LAYOUTCREATEVIEWPORT", 0);
                var lm = LayoutManager.Current;
                int tab = 1;
                foreach (var c in lines)
                {
                    var p = c.Split('|'); if (p[0] != "LAY") continue;
                    string name = p[1]; double x0 = D(p[2]), S = D(p[3]), W = D(p[4]), H = D(p[5]); string media = p[6];
                    ObjectId layId = lm.CreateLayout(name);
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var lay = (Layout)tr.GetObject(layId, OpenMode.ForWrite);
                        var v = PlotSettingsValidator.Current;
                        v.SetPlotConfigurationName(lay, "DWG To PDF.pc3", media);
                        try { v.SetPlotPaperUnits(lay, PlotPaperUnit.Millimeters); } catch { }
                        try { v.SetPlotRotation(lay, PlotRotation.Degrees000); } catch { }
                        try { v.SetPlotType(lay, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout); } catch { }
                        try { v.SetUseStandardScale(lay, true); v.SetStdScaleType(lay, StdScaleType.StdScale1To1); } catch { }
                        try { v.SetCurrentStyleSheet(lay, "monochrome.ctb"); } catch { }
                        lay.TabOrder = tab++;
                        var ps = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForWrite);
                        // overall paper viewport first, then the sheet viewport
                        var ov = new Viewport(); ps.AppendEntity(ov); tr.AddNewlyCreatedDBObject(ov, true);
                        ov.CenterPoint = new Point3d(W / 2, H / 2, 0); ov.Width = W * 1.2; ov.Height = H * 1.2;
                        ov.ViewCenter = new Point2d(W / 2, H / 2); ov.ViewHeight = H * 1.2;
                        var vp = new Viewport(); ps.AppendEntity(vp); tr.AddNewlyCreatedDBObject(vp, true);
                        vp.Layer = "Defpoints";
                        vp.CenterPoint = new Point3d(W / 2, H / 2, 0); vp.Width = W + 2; vp.Height = H + 2;
                        vp.ViewDirection = Vector3d.ZAxis; vp.ViewTarget = new Point3d(x0 + W * S / 2, H * S / 2, 0);
                        vp.ViewCenter = Point2d.Origin; vp.ViewHeight = (H + 2) * S; vp.CustomScale = 1.0 / S;
                        vp.Locked = true;
                        tr.Commit();
                    }
                    lm.CurrentLayout = name;
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        var lay = (Layout)tr.GetObject(layId, OpenMode.ForRead);
                        var ps = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForRead);
                        int k = 0;
                        foreach (ObjectId id in ps) { var vp = tr.GetObject(id, OpenMode.ForWrite) as Viewport; if (vp == null) continue; if (k++ > 0) vp.On = true; }
                        tr.Commit();
                    }
                    log.WriteLine("LAY " + name + " S=" + S);
                }
                lm.CurrentLayout = "Model";
                try { lm.DeleteLayout("Лист1"); } catch (System.Exception ex) { log.WriteLine("del " + ex.Message); }
                db.SaveAs(outPath, DwgVersion.Current);
                log.WriteLine("SAVED " + outPath);
            }
            catch (System.Exception ex) { log.WriteLine("ERR " + ex); }
            log.Close();
        }
    }
}
