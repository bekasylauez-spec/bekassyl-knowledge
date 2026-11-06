using System;
using System.Globalization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(EraseWin.Cmds))]
namespace EraseWin
{
    // erase every model-space entity whose extents are not fully inside %KEEPWIN% = "x0,y0,x1,y1"; purge blocks after
    public class Cmds
    {
        [CommandMethod("ERASEWIN")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var w = Array.ConvertAll(Environment.GetEnvironmentVariable("KEEPWIN").Split(','), s => double.Parse(s, CultureInfo.InvariantCulture));
            int n = 0, k = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    bool keep = false;
                    try { var ex = e.GeometricExtents; keep = ex.MinPoint.X >= w[0] && ex.MaxPoint.X <= w[2] && ex.MinPoint.Y >= w[1] && ex.MaxPoint.Y <= w[3]; } catch { keep = false; }
                    if (keep) { k++; continue; }
                    try { e.UpgradeOpen(); e.Erase(); n++; } catch { }
                }
                tr.Commit();
            }
            Application.DocumentManager.MdiActiveDocument.Editor.WriteMessage("\nERASEWIN erased " + n + " kept " + k + "\n");
        }
    }
}
