using System;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(TDump.Cmds))]
namespace TDump
{
    public class Cmds
    {
        [CommandMethod("TDUMP")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var sb = new StringBuilder();
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                    foreach (ObjectId id in ms)
                    {
                        var t = tr.GetObject(id, OpenMode.ForRead) as Table;
                        if (t == null) continue;
                        sb.AppendLine("TABLE " + t.Handle + " pos " + t.Position + " rows " + t.Rows.Count + " cols " + t.Columns.Count + " style " + t.TableStyleName + " w " + t.Width + " h " + t.Height);
                        for (int c = 0; c < t.Columns.Count; c++) sb.Append(" cw" + c + "=" + t.Columns[c].Width);
                        sb.AppendLine();
                        for (int r = 0; r < t.Rows.Count; r++)
                        {
                            sb.Append("  R" + r + " h=" + t.Rows[r].Height + " |");
                            for (int c = 0; c < t.Columns.Count; c++)
                            {
                                var cell = t.Cells[r, c];
                                string s = "";
                                try { s = cell.GetTextString(FormatOption.FormatOptionNone); } catch { }
                                string f = "";
                                try { if (cell.Contents.Count > 0 && cell.Contents[0].HasFormula) f = " {F:" + cell.Contents[0].Formula + "}"; } catch { }
                                try { if (cell.Contents.Count > 0 && cell.Contents[0].BlockTableRecordId.IsValid) f += " {BLK}"; } catch { }
                                sb.Append(" " + s.Replace("\r", "").Replace("\n", "\\n") + f + " |");
                            }
                            sb.AppendLine();
                        }
                    }
                    tr.Commit();
                }
            }
            catch (System.Exception ex) { sb.AppendLine("ERR " + ex); }
            File.WriteAllText(Environment.GetEnvironmentVariable("TDUMP_OUT"), sb.ToString(), Encoding.UTF8);
        }
    }
}
