using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(Ed.Cmds))]
namespace Ed
{
    // ops from %ED_JSON%: [{h, op:"text", find, repl} | {h, op:"cell", r, c, value}]
    public class Cmds
    {
        [CommandMethod("EDOPS")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var log = new StringBuilder();
            try
            {
                var ops = (object[])new JavaScriptSerializer().DeserializeObject(File.ReadAllText(Environment.GetEnvironmentVariable("ED_JSON"), Encoding.UTF8));
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    foreach (Dictionary<string, object> o in ops)
                    {
                        ObjectId id;
                        if (!db.TryGetObjectId(new Handle(Convert.ToInt64((string)o["h"], 16)), out id)) { log.AppendLine("no handle " + o["h"]); continue; }
                        var e = tr.GetObject(id, OpenMode.ForWrite);
                        string op = (string)o["op"];
                        if (op == "text")
                        {
                            string f = (string)o["find"], r = (string)o["repl"];
                            if (e is DBText) { var t = (DBText)e; string b = t.TextString; t.TextString = b.Replace(f, r); log.AppendLine(o["h"] + " TEXT '" + b + "' -> '" + t.TextString + "'"); }
                            else if (e is MText) { var t = (MText)e; string b = t.Contents; t.Contents = b.Replace(f, r); log.AppendLine(o["h"] + " MTEXT '" + b + "' -> '" + t.Contents + "'"); }
                        }
                        else if (op == "shift")
                        {
                            // move the last row of table h to the top (row 2) of table "to"
                            var t = (Table)e;
                            ObjectId id2; db.TryGetObjectId(new Handle(Convert.ToInt64((string)o["to"], 16)), out id2);
                            var t2 = (Table)tr.GetObject(id2, OpenMode.ForWrite);
                            int last = t.Rows.Count - 1;
                            var vals = new string[t.Columns.Count];
                            for (int c = 0; c < vals.Length; c++) vals[c] = t.Cells[last, c].TextString;
                            double hh = t.Rows[last].Height;
                            t2.InsertRowsAndInherit(2, 2, 1);
                            t2.Rows[2].Height = hh;
                            for (int c = 0; c < vals.Length; c++) t2.Cells[2, c].TextString = vals[c];
                            t.DeleteRows(last, 1);
                            t.GenerateLayout(); t2.GenerateLayout();
                            log.AppendLine(o["h"] + " -> " + o["to"] + " row '" + string.Join("|", vals) + "' rows " + t.Rows.Count + "/" + t2.Rows.Count);
                        }
                        else if (op == "gridcopy")
                        {
                            // copy cell borders of row "from" onto row "r"
                            var t = (Table)e; int r = Convert.ToInt32(o["r"]), fr = Convert.ToInt32(o["from"]);
                            for (int c = 0; c < t.Columns.Count; c++)
                            {
                                var sb = t.Cells[fr, c].Borders; var db2 = t.Cells[r, c].Borders;
                                var ss = new[] { sb.Top, sb.Bottom, sb.Left, sb.Right };
                                var dd = new[] { db2.Top, db2.Bottom, db2.Left, db2.Right };
                                for (int k = 0; k < 4; k++)
                                {
                                    log.AppendLine("  c" + c + " b" + k + " vis " + dd[k].IsVisible + " <- " + ss[k].IsVisible + " lw " + dd[k].LineWeight + " <- " + ss[k].LineWeight);
                                    dd[k].IsVisible = ss[k].IsVisible;
                                    dd[k].LineWeight = ss[k].LineWeight;
                                    dd[k].Color = ss[k].Color;
                                }
                            }
                            t.GenerateLayout();
                            log.AppendLine(o["h"] + " grid row " + r + " <- " + fr);
                        }
                        else if (op == "erase")
                        {
                            ((Entity)e).Erase();
                            log.AppendLine(o["h"] + " erased " + e.GetType().Name);
                        }
                        else if (op == "mwidth")
                        {
                            var t = (MText)e; double b = t.Width;
                            t.Width = Convert.ToDouble(o["w"]);
                            log.AppendLine(o["h"] + " mtext width " + b + " -> " + t.Width + " actual " + t.ActualWidth);
                        }
                        else if (op == "move")
                        {
                            var dv = new Autodesk.AutoCAD.Geometry.Vector3d(Convert.ToDouble(o["dx"]), Convert.ToDouble(o["dy"]), 0);
                            ((Entity)e).TransformBy(Autodesk.AutoCAD.Geometry.Matrix3d.Displacement(dv));
                            log.AppendLine(o["h"] + " moved " + dv);
                        }
                        else if (op == "recompute")
                        {
                            var t = (Table)e; t.GenerateLayout(); t.RecomputeTableBlock(true);
                            log.AppendLine(o["h"] + " recomputed rows " + t.Rows.Count + " h " + t.Height);
                        }
                        else if (op == "cell")
                        {
                            var t = (Table)e; int r = Convert.ToInt32(o["r"]), c = Convert.ToInt32(o["c"]);
                            string b = t.Cells[r, c].TextString;
                            t.Cells[r, c].TextString = (string)o["value"];
                            t.GenerateLayout();
                            log.AppendLine(o["h"] + " cell " + r + "," + c + " '" + b + "' -> '" + t.Cells[r, c].TextString + "'");
                        }
                    }
                    tr.Commit();
                }
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(Environment.GetEnvironmentVariable("ED_JSON") + ".log", log.ToString(), Encoding.UTF8);
        }
    }
}
