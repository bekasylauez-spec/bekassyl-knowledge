using System;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(FramesL.Cmds))]
namespace FramesL
{
    // list SPDS format frames (handle + extents) to %FRAMES_OUT%
    public class Cmds
    {
        [CommandMethod("FRAMESL")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var sb = new StringBuilder();
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                foreach (ObjectId id in ms)
                {
                    string dn = id.ObjectClass.DxfName; if (!dn.Contains("FORMAT") && !dn.Contains("FRAME")) continue;
                    var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                    try { var x = e.GeometricExtents; sb.AppendLine(dn + " " + e.Handle + " " + x.MinPoint.X.ToString("0") + " " + x.MinPoint.Y.ToString("0") + " " + x.MaxPoint.X.ToString("0") + " " + x.MaxPoint.Y.ToString("0")); } catch { sb.AppendLine(dn + " " + e.Handle + " noext"); }
                }
                tr.Commit();
            }
            File.WriteAllText(Environment.GetEnvironmentVariable("FRAMES_OUT"), sb.ToString());
        }
    }
}
