using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

namespace AL
{
    // Console ops: reads %TEMP%\al_ops.json (list of {t:...}), writes %TEMP%\al_log.txt
    public class Cmds
    {
        static StringBuilder log = new StringBuilder();
        static string tmp = Environment.GetEnvironmentVariable("TEMP");
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static double D(object o) { return Convert.ToDouble(o, IC); }
        static int I(object o) { return Convert.ToInt32(o, IC); }
        static string S(Dictionary<string, object> m, string k, string def) { object v; return m.TryGetValue(k, out v) && v != null ? v.ToString() : def; }
        static bool Has(Dictionary<string, object> m, string k) { object v; return m.TryGetValue(k, out v) && v != null; }
        static IList L(object o) { return (IList)o; }
        static Dictionary<string, string> map = new Dictionary<string, string>();

        static ObjectId H(Database db, string h)
        {
            if (map.ContainsKey(h)) h = map[h];
            ObjectId id;
            if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id)) return id;
            throw new System.Exception("no handle " + h);
        }
        static string F(double v) { return v.ToString("0.##", IC); }

        [CommandMethod("APPLYOPS", CommandFlags.Session)]
        public static void ApplyCmd()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            using (doc.LockDocument()) Apply(doc.Database);
        }

        public static void Apply(Database db)
        {
            log.Clear();
            var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
            var ops = (IList)js.DeserializeObject(File.ReadAllText(Path.Combine(tmp, "al_ops.json"), Encoding.UTF8));
            int nerr = 0;
            foreach (var o in ops)
            {
                var m = (Dictionary<string, object>)o;
                string t = S(m, "t", "");
                try
                {
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        One(db, tr, m, t);
                        tr.Commit();
                    }
                }
                catch (System.Exception ex) { nerr++; log.AppendLine("ERR " + t + " " + S(m, "h", "") + ": " + ex.Message); }
            }
            log.AppendLine("DONE errors " + nerr);
            File.WriteAllText(Path.Combine(tmp, "al_log.txt"), log.ToString(), Encoding.UTF8);
        }

        static BlockTableRecord MS(Database db, Transaction tr)
        {
            var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
            return (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
        }

        static void One(Database db, Transaction tr, Dictionary<string, object> m, string t)
        {
            if (t == "tdump")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var ext = tb.GeometricExtents;
                log.AppendLine("TABLE " + tb.Handle + " rows " + tb.Rows.Count + " cols " + tb.Columns.Count + " pos " + F(tb.Position.X) + "," + F(tb.Position.Y) + " W " + F(tb.Width) + " H " + F(tb.Height) + " ext " + F(ext.MinPoint.X) + "," + F(ext.MinPoint.Y) + "," + F(ext.MaxPoint.X) + "," + F(ext.MaxPoint.Y) + " layer " + tb.Layer + " style " + tb.TableStyle.ToString());
                var cw = new StringBuilder("COLS:");
                for (int c = 0; c < tb.Columns.Count; c++) cw.Append(" " + F(tb.Columns[c].Width));
                log.AppendLine(cw.ToString());
                for (int r = 0; r < tb.Rows.Count; r++)
                {
                    var sb = new StringBuilder("R" + r + " h" + F(tb.Rows[r].Height) + ":");
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var cell = tb.Cells[r, c]; string f = "";
                        try { string ed = cell.GetTextString(FormatOption.ForEditing); if (ed != cell.TextString) f = "{" + ed + "}"; } catch { }
                        string fo = ""; try { if (cell.Contents.Count > 0 && !string.IsNullOrEmpty(cell.Contents[0].Formula)) fo = "[=" + cell.Contents[0].Formula + "]"; } catch { }
                        string mg = ""; try { var rg = cell.GetMergeRange(); if (rg != null) mg = "<" + rg.TopRow + "," + rg.LeftColumn + "-" + rg.BottomRow + "," + rg.RightColumn + ">"; } catch { }
                        string th = ""; try { th = "(" + F(cell.TextHeight) + ")"; } catch { }
                        sb.Append(" | " + cell.TextString.Replace("\n", "\\n").Replace("\r", "") + f + fo + mg + th);
                    }
                    log.AppendLine(sb.ToString());
                }
            }
            else if (t == "tset")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["cells"]))
                {
                    var a = L(q); int r = I(a[0]), c = I(a[1]); string v = a[2].ToString();
                    var cell = tb.Cells[r, c];
                    double th = 0; try { th = cell.TextHeight; } catch { }
                    try { if (cell.Contents.Count > 0) cell.Contents[0].Formula = null; } catch { }
                    cell.TextString = v;
                    if (th > 0) try { cell.TextHeight = th; } catch { }
                }
                tb.GenerateLayout();
            }
            else if (t == "tfreeze")
            {
                // every cell with a field or formula -> plain text of its current display value
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                int n = 0;
                for (int r = 0; r < tb.Rows.Count; r++)
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var cell = tb.Cells[r, c];
                        bool isf = false; string shown = cell.TextString;
                        try { string ed = cell.GetTextString(FormatOption.ForEditing); if (ed.Contains("%<")) isf = true; } catch { }
                        try { if (cell.Contents.Count > 0 && !string.IsNullOrEmpty(cell.Contents[0].Formula)) isf = true; } catch { }
                        if (!isf) continue;
                        double th = 0; try { th = cell.TextHeight; } catch { }
                        try { if (cell.Contents.Count > 0) cell.Contents[0].Formula = null; } catch { }
                        cell.Contents.Clear(); cell.Contents.Add();
                        cell.DataType = new DataTypeParameter(DataType.String, UnitType.Unitless);
                        cell.TextString = shown;
                        if (th > 0) try { cell.TextHeight = th; } catch { }
                        n++;
                    }
                tb.GenerateLayout();
                log.AppendLine("FROZEN " + tb.Handle + " " + n);
            }
            else if (t == "trows")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                string mode = S(m, "mode", "del"); int at = I(m["at"]), n = I(m["n"]);
                if (mode == "del") tb.DeleteRows(at, n); else tb.InsertRowsAndInherit(at, I(m["from"]), n);
                tb.GenerateLayout();
            }
            else if (t == "theight")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["rows"])) { var a = L(q); tb.Rows[I(a[0])].Height = D(a[1]); }
                tb.GenerateLayout();
            }
            else if (t == "tmerge")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var a = L(m["r"]); var rg = CellRange.Create(tb, I(a[0]), I(a[1]), I(a[2]), I(a[3]));
                if (S(m, "mode", "merge") == "merge") tb.MergeCells(rg); else tb.UnmergeCells(rg);
                tb.GenerateLayout();
            }
            else if (t == "talign")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var al = (CellAlignment)Enum.Parse(typeof(CellAlignment), S(m, "al", "MiddleCenter"));
                foreach (var q in L(m["cells"])) { var a = L(q); tb.Cells[I(a[0]), I(a[1])].Alignment = al; }
                tb.GenerateLayout();
            }
            else if (t == "move")
            {
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                e.TransformBy(Matrix3d.Displacement(new Vector3d(D(m["dx"]), D(m["dy"]), 0)));
            }
            else if (t == "movewin")
            {
                // move every model-space entity whose extents lie inside win
                var w = L(m["win"]); double dx = D(m["dx"]), dy = D(m["dy"]); int n = 0;
                foreach (ObjectId id in MS(db, tr))
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X < D(w[0]) || x.MinPoint.Y < D(w[1]) || x.MaxPoint.X > D(w[2]) || x.MaxPoint.Y > D(w[3])) continue;
                    e.UpgradeOpen(); e.TransformBy(Matrix3d.Displacement(new Vector3d(dx, dy, 0))); n++;
                }
                log.AppendLine("MOVEWIN " + n);
            }
            else if (t == "settext")
            {
                var e = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                if (e is MText) ((MText)e).Contents = S(m, "text", "");
                else if (e is DBText) ((DBText)e).TextString = S(m, "text", "");
                else throw new System.Exception("not text " + e.GetType().Name);
            }
            else if (t == "ext")
            {
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var x = e.GeometricExtents;
                log.AppendLine("EXT " + e.Handle + " " + e.GetType().Name + " " + F(x.MinPoint.X) + "," + F(x.MinPoint.Y) + "," + F(x.MaxPoint.X) + "," + F(x.MaxPoint.Y));
            }
            else if (t == "list")
            {
                // every entity whose extents touch win
                var w = L(m["win"]);
                foreach (ObjectId id in MS(db, tr))
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    string txt = "";
                    if (e is MText) txt = ((MText)e).Text; else if (e is DBText) txt = ((DBText)e).TextString;
                    log.AppendLine("E " + e.GetType().Name + " " + e.Handle + " " + e.Layer + " " + F(x.MinPoint.X) + "," + F(x.MinPoint.Y) + "," + F(x.MaxPoint.X) + "," + F(x.MaxPoint.Y) + " " + txt.Replace("\n", "\\n"));
                }
            }
            else if (t == "clone")
            {
                var ids = new ObjectIdCollection();
                foreach (var h in L(m["hs"])) ids.Add(H(db, h.ToString()));
                var mp = new IdMapping();
                db.DeepCloneObjects(ids, MS(db, tr).ObjectId, mp, false);
                double dx = D(m["dx"]), dy = D(m["dy"]);
                var sb = new StringBuilder("CLONE");
                foreach (IdPair p in mp)
                {
                    if (!p.IsPrimary) continue;
                    var e = tr.GetObject(p.Value, OpenMode.ForWrite) as Entity; if (e == null) continue;
                    e.TransformBy(Matrix3d.Displacement(new Vector3d(dx, dy, 0)));
                    sb.Append(" " + tr.GetObject(p.Key, OpenMode.ForRead).Handle + "->" + e.Handle);
                }
                log.AppendLine(sb.ToString());
            }
            else if (t == "erase")
            {
                foreach (var h in L(m["hs"])) { var e = tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite); e.Erase(); }
            }
            else if (t == "save")
            {
                db.SaveAs(S(m, "file", ""), true, DwgVersion.Current, db.SecurityParameters);
                log.AppendLine("SAVED " + S(m, "file", ""));
            }
            else if (t == "dxfout")
            {
                db.DxfOut(S(m, "file", ""), 16, DwgVersion.Current);
            }
            else throw new System.Exception("unknown op " + t);
        }
    }
}
