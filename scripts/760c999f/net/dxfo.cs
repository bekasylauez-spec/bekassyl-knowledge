using System;
using System.IO;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(DxfO.Cmds))]
namespace DxfO
{
    public class Cmds
    {
        // write the current drawing as DXF to %DXF_OUT%
        [CommandMethod("DXFO")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            string p = Environment.GetEnvironmentVariable("DXF_OUT");
            try { db.DxfOut(p, 16, false); }
            catch (System.Exception ex) { File.WriteAllText(p + ".err", ex.ToString()); }
        }
    }
}
