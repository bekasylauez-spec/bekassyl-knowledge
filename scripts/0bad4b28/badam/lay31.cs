using System;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(Lay31.Cmd))]
namespace Lay31
{
    public class Cmd
    {
        [CommandMethod("LAY31FIX")]
        public void Fix()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var lm = LayoutManager.Current;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                Func<string, Viewport> first = name => {
                    var lay = (Layout)tr.GetObject(lm.GetLayoutId(name), OpenMode.ForRead);
                    var btr = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForRead);
                    foreach (ObjectId id in btr) { var v = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (v != null) return v; }
                    return null; };
                var a = first("4"); var b = first("3.1");
                b.UpgradeOpen(); b.ViewCenter = a.ViewCenter; b.ViewHeight = a.ViewHeight;
                Application.DocumentManager.MdiActiveDocument.Editor.WriteMessage("\nLAY31FIX ok " + b.ViewCenter + "\n");
                tr.Commit();
            }
        }

        [CommandMethod("LAY31")]
        public void Run()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            var ed = doc.Editor;
            var db = doc.Database;
            try
            {
                var lm = LayoutManager.Current;
                if (lm.LayoutExists("3.1")) { ed.WriteMessage("\nLAY31: exists\n"); return; }
                int tab;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var src = (Layout)tr.GetObject(lm.GetLayoutId("4"), OpenMode.ForRead);
                    tab = src.TabOrder;
                    tr.Commit();
                }
                lm.CloneLayout("4", "3.1", tab + 1);
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var lay = (Layout)tr.GetObject(lm.GetLayoutId("3.1"), OpenMode.ForRead);
                    var btr = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForRead);
                    int n = 0;
                    foreach (ObjectId id in btr)
                    {
                        var vp = tr.GetObject(id, OpenMode.ForRead) as Viewport;
                        if (vp == null || vp.Number == 1) continue;
                        vp.UpgradeOpen();
                        ed.WriteMessage("\nVP {0} center {1} target {2} twist {3} h {4}", vp.Number, vp.ViewCenter, vp.ViewTarget, vp.TwistAngle, vp.ViewHeight);
                        vp.ViewCenter = new Point2d(vp.ViewCenter.X - 252000, vp.ViewCenter.Y);
                        n++;
                    }
                    // also list the source viewports for comparison
                    tr.Commit();
                    ed.WriteMessage("\nLAY31: moved {0} viewports\n", n);
                }
            }
            catch (System.Exception ex)
            {
                ed.WriteMessage("\nLAY31 ERROR: " + ex + "\n");
            }
        }
    }
}
