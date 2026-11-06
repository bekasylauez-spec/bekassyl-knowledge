using System;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(EraseH.Cmds))]
namespace EraseH
{
    // erase entities by handle: %ERASEH% = "H1,H2,..."
    public class Cmds
    {
        [CommandMethod("ERASEH")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var h in Environment.GetEnvironmentVariable("ERASEH").Split(','))
                {
                    ObjectId id;
                    if (db.TryGetObjectId(new Handle(Convert.ToInt64(h.Trim(), 16)), out id)) tr.GetObject(id, OpenMode.ForWrite).Erase();
                }
                tr.Commit();
            }
        }
    }
}
