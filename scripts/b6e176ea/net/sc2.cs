using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;

[assembly: CommandClass(typeof(SC2.Cmds))]
namespace SC2
{
    // JSON ops from %TEMP%\sc_ops.json, log to %TEMP%\sc_log.txt
    public class Cmds
    {
        static StringBuilder log = new StringBuilder();
        static string tmp = Environment.GetEnvironmentVariable("TEMP");
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static double D(object o) { return Convert.ToDouble(o, IC); }
        static int I(object o) { return Convert.ToInt32(o); }
        static string S(Dictionary<string, object> m, string k, string def) { object v; return m.TryGetValue(k, out v) && v != null ? v.ToString() : def; }
        static bool Has(Dictionary<string, object> m, string k) { object v; return m.TryGetValue(k, out v) && v != null; }
        static IList L(object o) { return (IList)o; }
        static Point3d P(object o) { var a = L(o); return new Point3d(D(a[0]), D(a[1]), 0); }
        static string F(double v) { return v.ToString("0.###", IC); }

        static ObjectId H(Database db, string h)
        {
            ObjectId id;
            if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id)) return id;
            throw new System.Exception("no handle " + h);
        }

        [CommandMethod("SCAPPLY2")]
        public static void Cmd() { Apply(); }

        public static void Apply()
        {
            log.Clear();
            var doc = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument;
            var db = doc.Database;
            var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
            var ops = (IList)js.DeserializeObject(File.ReadAllText(Path.Combine(tmp, "sc_ops.json"), Encoding.UTF8));
            foreach (var o in ops)
            {
                var m = (Dictionary<string, object>)o;
                if (S(m, "t", "") == "savedoc")
                {
                    try { db.SaveAs(doc.Name, true, DwgVersion.Current, db.SecurityParameters); log.AppendLine("saved " + doc.Name); }
                    catch (System.Exception ex) { log.AppendLine("ERR savedoc: " + ex.Message); }
                    continue;
                }
                if (S(m, "t", "") == "setvar")
                {
                    try { Autodesk.AutoCAD.ApplicationServices.Core.Application.SetSystemVariable(S(m, "name", ""), Convert.ToInt16(m["value"])); log.AppendLine("setvar " + S(m, "name", "")); }
                    catch (System.Exception ex) { log.AppendLine("ERR setvar: " + ex.Message); }
                    continue;
                }
                try
                {
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        Op(db, tr, m);
                        tr.Commit();
                    }
                }
                catch (System.Exception ex) { log.AppendLine("ERR " + S(m, "t", "?") + ": " + ex.Message); }
            }
            File.WriteAllText(Path.Combine(tmp, "sc_log.txt"), log.ToString(), Encoding.UTF8);
        }

        static bool In(Point3d p, double[] w) { return p.X >= w[0] && p.X <= w[2] && p.Y >= w[1] && p.Y <= w[3]; }
        static double[] Win(object o) { var a = L(o); return new double[] { D(a[0]), D(a[1]), D(a[2]), D(a[3]) }; }

        static void SetFormula(Table tb, int r, int c, string f, string fmt, double th)
        {
            var cell = tb.Cells[r, c];
            cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
            cell.TextString = "";
            if (cell.Contents.Count == 0) cell.Contents.Add();
            cell.Contents[0].Formula = f;
            if (th > 0) cell.Contents[0].TextHeight = th;
            cell.DataFormat = fmt;
        }

        static void Op(Database db, Transaction tr, Dictionary<string, object> m)
        {
            string t = S(m, "t", "");
            if (t == "xform")
            {
                // rotate about base (deg) then move by d
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var b = L(m["base"]); var dv = L(m["d"]);
                var bp = new Point3d(D(b[0]), D(b[1]), 0);
                if (Math.Abs(D(m["rot"])) > 1e-9) e.TransformBy(Matrix3d.Rotation(D(m["rot"]) * Math.PI / 180.0, Vector3d.ZAxis, bp));
                e.TransformBy(Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0)));
                var x = e.GeometricExtents;
                log.AppendLine("xform " + e.Handle + " " + e.GetType().Name + " ext " + F(x.MinPoint.X) + "," + F(x.MinPoint.Y) + " " + F(x.MaxPoint.X) + "," + F(x.MaxPoint.Y));
            }
            else if (t == "arc")
            {
                // radius and (optionally) start/end angles in degrees
                var a = (Arc)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                a.Radius = D(m["r"]);
                if (Has(m, "sa")) a.StartAngle = D(m["sa"]) * Math.PI / 180.0;
                if (Has(m, "ea")) a.EndAngle = D(m["ea"]) * Math.PI / 180.0;
            }
            else if (t == "plset")
            {
                var pl = (Polyline)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var p = L(m["p"]);
                pl.SetPointAt(I(m["i"]), new Point2d(D(p[0]), D(p[1])));
            }
            else if (t == "lineset")
            {
                var ln = (Line)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                if (Has(m, "p1")) ln.StartPoint = P(m["p1"]);
                if (Has(m, "p2")) ln.EndPoint = P(m["p2"]);
            }
            else if (t == "dimpts")
            {
                // move the extension-line origins of a linear dimension (p1 = XLine1Point, p2 = XLine2Point)
                var e = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var rd = e as RotatedDimension; var ad = e as AlignedDimension;
                if (rd != null) { if (Has(m, "p1")) rd.XLine1Point = P(m["p1"]); if (Has(m, "p2")) rd.XLine2Point = P(m["p2"]); log.AppendLine("dimpts " + rd.Handle + " = " + F(rd.Measurement)); }
                else if (ad != null) { if (Has(m, "p1")) ad.XLine1Point = P(m["p1"]); if (Has(m, "p2")) ad.XLine2Point = P(m["p2"]); log.AppendLine("dimpts " + ad.Handle + " = " + F(ad.Measurement)); }
                else log.AppendLine("dimpts: not a linear dimension " + e.GetType().Name);
            }
            else if (t == "props")
            {
                // general properties: lts = linetype scale, lw = lineweight in 0.01 mm (5 = 0.05 mm)
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                try
                {
                    if (Has(m, "lts")) e.LinetypeScale = D(m["lts"]);
                    if (Has(m, "lw")) e.LineWeight = (LineWeight)I(m["lw"]);
                    log.AppendLine("props " + e.Handle + " " + e.GetType().Name + " lts=" + F(e.LinetypeScale) + " lw=" + (int)e.LineWeight);
                }
                catch (System.Exception ex) { log.AppendLine("props FAIL " + e.Handle + " " + e.GetType().Name + " " + ex.Message); }
            }
            else if (t == "bscale")
            {
                var br = (BlockReference)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var sc = L(m["s"]);
                br.ScaleFactors = new Scale3d(D(sc[0]), D(sc[1]), sc.Count > 2 ? D(sc[2]) : 1.0);
                log.AppendLine("bscale " + br.Handle + " ext " + Ext(br));
            }
            else if (t == "plw")
            {
                var pl = (Polyline)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                pl.ConstantWidth = D(m["w"]);
            }
            else if (t == "mt")
            {
                var mt = (MText)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                if (Has(m, "s")) mt.Contents = S(m, "s", "");
                if (Has(m, "w")) mt.Width = D(m["w"]);
                if (Has(m, "at")) mt.Location = P(m["at"]);
                if (Has(m, "lsf")) mt.LineSpacingFactor = D(m["lsf"]);
                if (Has(m, "th")) mt.TextHeight = D(m["th"]);
                log.AppendLine("mt " + mt.Handle + " ext " + Ext(mt));
            }
            else if (t == "mtrepl")
            {
                var mt = (MText)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                string c = mt.Contents;
                foreach (var pr in L(m["pairs"])) { var a = L(pr); if (!c.Contains(a[0].ToString())) log.AppendLine("mtrepl miss: " + a[0].ToString().Substring(0, Math.Min(30, a[0].ToString().Length))); c = c.Replace(a[0].ToString(), a[1].ToString()); }
                mt.Contents = c;
            }
            else if (t == "txt")
            {
                var e = (DBText)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                e.TextString = S(m, "s", "");
            }
            else if (t == "erase")
            {
                foreach (var h in L(m["h"])) { var e = tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite); e.Erase(); }
            }
            else if (t == "eraseregion")
            {
                var w = Win(m["win"]);
                var keep = new HashSet<string>(); if (Has(m, "keep")) foreach (var k in L(m["keep"])) keep.Add(k.ToString().ToUpper());
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                int n = 0; var sb = new StringBuilder();
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    if (keep.Contains(e.Handle.ToString())) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (In(x.MinPoint, w) && In(x.MaxPoint, w))
                    {
                        sb.Append(e.Handle + ":" + e.GetType().Name + " ");
                        if (!Has(m, "dry")) { e.UpgradeOpen(); e.Erase(); }
                        n++;
                    }
                }
                log.AppendLine("eraseregion " + n + " " + sb.ToString());
            }
            else if (t == "list")
            {
                var w = Win(m["win"]);
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (In(x.MinPoint, w) && In(x.MaxPoint, w)) log.AppendLine(e.Handle + " " + e.GetType().Name + " " + e.Layer + " " + Ext(e));
                }
            }
            else if (t == "dumptable")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                log.AppendLine("TABLE " + tb.Handle + " rows " + tb.Rows.Count + " cols " + tb.Columns.Count + " pos " + tb.Position + " style " + tb.TableStyleName + " ext " + Ext(tb));
                var sbw = new StringBuilder("colw:"); for (int c = 0; c < tb.Columns.Count; c++) sbw.Append(" " + F(tb.Columns[c].Width)); log.AppendLine(sbw.ToString());
                for (int r = 0; r < tb.Rows.Count; r++)
                {
                    var sb = new StringBuilder("r" + r + " h=" + F(tb.Rows[r].Height) + " |");
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var cell = tb.Cells[r, c];
                        string f = ""; try { if (cell.Contents.Count > 0 && cell.Contents[0].HasFormula) f = " F{" + cell.Contents[0].Formula + "}"; } catch { }
                        string mr = ""; try { var rg = cell.GetMergeRange(); if (rg != null && (rg.TopRow != rg.BottomRow || rg.LeftColumn != rg.RightColumn)) mr = " M[" + rg.TopRow + "," + rg.LeftColumn + "-" + rg.BottomRow + "," + rg.RightColumn + "]"; } catch { }
                        string th = ""; try { if (cell.Contents.Count > 0) th = " th" + F(cell.Contents[0].TextHeight) + " rot" + F(cell.Contents[0].Rotation); } catch { }
                        string txt = ""; try { txt = cell.GetTextString(FormatOption.FormatOptionNone); } catch { try { txt = cell.TextString; } catch { } }
                        sb.Append(" [" + c + "]" + txt.Replace("\n", "/") + f + mr + (Has(m, "full") ? th : "") + " |");
                    }
                    log.AppendLine(sb.ToString());
                }
            }
            else if (t == "cell")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var o in L(m["c"]))
                {
                    var a = L(o); int r = I(a[0]), c = I(a[1]);
                    var cell = tb.Cells[r, c];
                    double th = 0; try { if (cell.Contents.Count > 0) th = cell.Contents[0].TextHeight; } catch { }
                    if (Has(m, "th")) th = D(m["th"]);
                    try { if (cell.Contents.Count > 0 && cell.Contents[0].HasFormula) { cell.Contents.Clear(); cell.Contents.Add(); } } catch { }
                    cell.DataType = new DataTypeParameter(DataType.String, UnitType.Unitless);
                    cell.TextString = a[2].ToString();
                    if (th > 0 && cell.Contents.Count > 0) cell.Contents[0].TextHeight = th;
                }
            }
            else if (t == "formula")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                string fmt = S(m, "fmt", "%lu2%pr3");
                foreach (var o in L(m["c"]))
                {
                    var a = L(o); int r = I(a[0]), c = I(a[1]);
                    double th = 0; try { if (tb.Cells[r, c].Contents.Count > 0) th = tb.Cells[r, c].Contents[0].TextHeight; } catch { }
                    if (Has(m, "th")) th = D(m["th"]);
                    SetFormula(tb, r, c, a[2].ToString(), fmt, th);
                }
            }
            else if (t == "delrows")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                tb.DeleteRows(I(m["r"]), I(m["n"]));
            }
            else if (t == "insrows")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                int r = I(m["r"]); double hgt = Has(m, "rh") ? D(m["rh"]) : tb.Rows[r - 1].Height;
                tb.InsertRows(r, hgt, I(m["n"]));
            }
            else if (t == "cellth")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var o in L(m["c"])) { var a = L(o); var cl = tb.Cells[I(a[0]), I(a[1])]; cl.TextHeight = D(m["th"]); try { if (cl.Contents.Count > 0) cl.Contents[0].TextHeight = D(m["th"]); } catch { } }
            }
            else if (t == "celldbg")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                foreach (var o in L(m["c"]))
                {
                    var a = L(o); var cl = tb.Cells[I(a[0]), I(a[1])];
                    string st = "?"; try { st = ((TextStyleTableRecord)tr.GetObject(cl.TextStyleId.Value, OpenMode.ForRead)).Name; } catch { }
                    string f = ""; try { if (cl.Contents.Count > 0 && cl.Contents[0].HasFormula) f = cl.Contents[0].Formula; } catch { }
                    string tx = ""; try { tx = cl.GetTextString(FormatOption.FormatOptionNone); } catch { }
                    log.AppendLine("cell " + a[0] + "," + a[1] + " style=" + st + " th=" + cl.TextHeight + " dt=" + cl.DataType + " f=" + f + " txt=" + tx + " ts=" + cl.TextString);
                }
            }
            else if (t == "cellclr")
            {
                // print / copy cell content colour: src [r,c] -> dst [[r,c],...]
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                for (int r = 0; r < tb.Rows.Count; r++) { var sb = new StringBuilder("r" + r + ":"); for (int c = 0; c < tb.Columns.Count; c++) { string ci = "?"; try { ci = tb.Cells[r, c].ContentColor.ColorIndex.ToString(); if (tb.Cells[r, c].Contents.Count > 0) ci += "/" + tb.Cells[r, c].Contents[0].ContentColor.ColorIndex; } catch { } sb.Append(" " + ci); } log.AppendLine(sb.ToString()); }
                if (Has(m, "src"))
                {
                    var sa = L(m["src"]); var sc = tb.Cells[I(sa[0]), I(sa[1])];
                    foreach (var o in L(m["dst"])) { var a = L(o); var d = tb.Cells[I(a[0]), I(a[1])]; d.ContentColor = sc.ContentColor; try { if (d.Contents.Count > 0 && sc.Contents.Count > 0) d.Contents[0].ContentColor = sc.Contents[0].ContentColor; } catch { } }
                }
            }
            else if (t == "copyrowfmt")
            {
                // copy text height / alignment from row src to rows dst..dst+n-1
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                int src = I(m["src"]), dst = I(m["dst"]), n = I(m["n"]);
                for (int r = dst; r < dst + n; r++)
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var s = tb.Cells[src, c]; var d = tb.Cells[r, c];
                        try { d.Alignment = s.Alignment; } catch { }
                        try { d.TextStyleId = s.TextStyleId; } catch { }
                        try { d.TextHeight = s.TextHeight; } catch { }
                    }
            }
            else if (t == "rowstyle")
            {
                // copy alignment, text style/height and grid line weights from row src to rows dst..dst+n-1
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                int src = I(m["src"]), dst = I(m["dst"]), n = I(m["n"]);
                for (int r = dst; r < dst + n; r++)
                {
                    tb.Rows[r].Height = tb.Rows[src].Height;
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var a = tb.Cells[src, c]; var b = tb.Cells[r, c];
                        try { b.Alignment = a.Alignment; } catch { }
                        try { b.TextStyleId = a.TextStyleId; } catch { }
                        try { b.TextHeight = a.TextHeight; } catch { }
                        try { if (b.Contents.Count > 0 && a.Contents.Count > 0) b.Contents[0].TextHeight = a.Contents[0].TextHeight; } catch { }
                        foreach (var gt in new[] { GridLineType.HorizontalTop, GridLineType.HorizontalBottom, GridLineType.VerticalLeft, GridLineType.VerticalRight })
                        {
                            try { tb.SetGridLineWeight(r, c, gt, tb.GetGridLineWeight(src, c, gt)); } catch { }
                            try { tb.SetGridVisibility(r, c, gt, tb.GetGridVisibility(src, c, gt)); } catch { }
                        }
                    }
                }
            }
            else if (t == "styles")
            {
                var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                foreach (ObjectId id in st) { var r = (TextStyleTableRecord)tr.GetObject(id, OpenMode.ForRead); log.AppendLine("STYLE " + r.Name + " | " + r.FileName + " | " + r.Font.TypeFace + " | h" + r.TextSize + " w" + r.XScale + " obl" + r.ObliquingAngle); }
                if (Has(m, "h"))
                {
                    var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                    var seen = new HashSet<string>();
                    for (int r = 0; r < tb.Rows.Count; r++) for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        string n = "?"; try { var sid = tb.Cells[r, c].TextStyleId; if (sid.HasValue) n = ((TextStyleTableRecord)tr.GetObject(sid.Value, OpenMode.ForRead)).Name; } catch { }
                        seen.Add(n);
                    }
                    log.AppendLine("table styles: " + string.Join(",", seen));
                }
            }
            else if (t == "tfont")
            {
                // set every cell text style; strip inline font switches except the square-tube glyph
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                var sid = st[S(m, "style", "Isocpeur")];
                var rx = new System.Text.RegularExpressions.Regex(@"\\f(?!BankGothic)[^;]*;");
                int n = 0;
                for (int r = 0; r < tb.Rows.Count; r++) for (int c = 0; c < tb.Columns.Count; c++)
                {
                    var cell = tb.Cells[r, c];
                    try { cell.TextStyleId = sid; } catch { }
                    try
                    {
                        for (int k = 0; k < cell.Contents.Count; k++)
                        {
                            cell.Contents[k].TextStyleId = sid;
                            if (cell.Contents[k].HasFormula) continue;
                            string txt = cell.Contents[k].TextString;
                            if (txt == null) continue;
                            string nt = rx.Replace(txt, "");
                            if (nt != txt) { cell.Contents[k].TextString = nt; n++; }
                        }
                    }
                    catch { }
                }
                log.AppendLine("tfont stripped " + n);
            }
            else if (t == "unmerge")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var a = L(m["rg"]);
                tb.UnmergeCells(CellRange.Create(tb, I(a[0]), I(a[1]), I(a[2]), I(a[3])));
            }
            else if (t == "merge")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var a = L(m["rg"]);
                tb.MergeCells(CellRange.Create(tb, I(a[0]), I(a[1]), I(a[2]), I(a[3])));
            }
            else if (t == "rowh")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var o in L(m["r"])) { var a = L(o); tb.Rows[I(a[0])].Height = D(a[1]); }
            }
            else if (t == "tpos")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                tb.Position = P(m["at"]);
            }
            else if (t == "recompute")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                tb.RecomputeTableBlock(true);
                log.AppendLine("table ext " + Ext(tb));
            }
            else if (t == "evalfields")
            {
                db.EvaluateFields();
            }
            else if (t == "wblock")
            {
                using (var nd = db.Wblock()) nd.SaveAs(S(m, "file", ""), DwgVersion.Current);
            }
            else if (t == "import")
            {
                // clone handles from side dwg, scale about base by s, move base -> to; repl: {oldHandle: newContents}
                var repl = Has(m, "repl") ? (Dictionary<string, object>)m["repl"] : new Dictionary<string, object>();
                double s = Has(m, "s") ? D(m["s"]) : 1.0;
                var bs = P(m["base"]); var to = P(m["to"]);
                var xf = Matrix3d.Displacement(to - bs) * Matrix3d.Scaling(s, bs);
                using (var side = new Database(false, true))
                {
                    side.ReadDwgFile(S(m, "file", ""), FileOpenMode.OpenForReadAndAllShare, true, "");
                    side.CloseInput(true);
                    var ids = new ObjectIdCollection(); var olds = new List<string>();
                    foreach (var h in L(m["h"])) { ObjectId id; if (side.TryGetObjectId(new Handle(Convert.ToInt64(h.ToString(), 16)), out id)) { ids.Add(id); olds.Add(h.ToString().ToUpper()); } else log.AppendLine("import: no " + h); }
                    var map = new IdMapping();
                    var msId = SymbolUtilityServices.GetBlockModelSpaceId(db);
                    side.WblockCloneObjects(ids, msId, map, DuplicateRecordCloning.Ignore, false);
                    var sb = new StringBuilder("import " + S(m, "tag", "") + ":");
                    for (int i = 0; i < ids.Count; i++)
                    {
                        if (!map.Contains(ids[i])) continue;
                        var nid = map[ids[i]].Value;
                        var e = tr.GetObject(nid, OpenMode.ForWrite) as Entity; if (e == null) continue;
                        e.TransformBy(xf);
                        object rv;
                        if (repl.TryGetValue(olds[i], out rv))
                        {
                            if (e is MText) ((MText)e).Contents = rv.ToString();
                            else if (e is DBText) ((DBText)e).TextString = rv.ToString();
                        }
                        if (Has(m, "layer")) e.Layer = S(m, "layer", "0");
                        sb.Append(" " + olds[i] + ">" + e.Handle);
                    }
                    log.AppendLine(sb.ToString());
                }
            }
            else if (t == "blockdef")
            {
                // replace block definition `name` from side dwg; then text replace inside the block
                using (var side = new Database(false, true))
                {
                    side.ReadDwgFile(S(m, "file", ""), FileOpenMode.OpenForReadAndAllShare, true, "");
                    side.CloseInput(true);
                    string name = S(m, "name", "");
                    ObjectId sid;
                    using (var str = side.TransactionManager.StartTransaction())
                    {
                        var sbt = (BlockTable)str.GetObject(side.BlockTableId, OpenMode.ForRead);
                        sid = sbt[name];
                        str.Commit();
                    }
                    var ids = new ObjectIdCollection(); ids.Add(sid);
                    var map = new IdMapping();
                    side.WblockCloneObjects(ids, db.BlockTableId, map, DuplicateRecordCloning.Replace, false);
                    var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                    var btr = (BlockTableRecord)tr.GetObject(bt[name], OpenMode.ForRead);
                    var repl = Has(m, "repl") ? (Dictionary<string, object>)m["repl"] : new Dictionary<string, object>();
                    int n = 0;
                    foreach (ObjectId id in btr)
                    {
                        var mt = tr.GetObject(id, OpenMode.ForRead) as MText; if (mt == null) continue;
                        string c = mt.Contents, c0 = c;
                        foreach (var kv in repl) c = c.Replace(kv.Key, kv.Value.ToString());
                        if (c != c0) { mt.UpgradeOpen(); mt.Contents = c; n++; }
                    }
                    log.AppendLine("blockdef " + name + " replaced, texts changed " + n);
                }
            }
            else if (t == "clone")
            {
                var src = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var ne = (Entity)src.Clone();
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
                ms.AppendEntity(ne); tr.AddNewlyCreatedDBObject(ne, true);
                var dv = L(m["d"]); ne.TransformBy(Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0)));
                if (Has(m, "s")) { if (ne is MText) ((MText)ne).Contents = S(m, "s", ""); else if (ne is DBText) ((DBText)ne).TextString = S(m, "s", ""); }
                log.AppendLine("clone " + src.Handle + ">" + ne.Handle);
            }
            else if (t == "newtable")
            {
                // new table in the style of table h1: pos = top-left, colw[], rowh[], cells [[r,c,"text"]], merge [[r0,c0,r1,c1]],
                // bord [[r,c,T,B,L,R]] line weights, fcells [[r,c,formula,format]]
                var src = (Table)tr.GetObject(H(db, S(m, "h1", "")), OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
                var cw = L(m["colw"]); var rh = L(m["rowh"]);
                var tb = new Table();
                tb.SetDatabaseDefaults(db);
                tb.TableStyle = src.TableStyle;
                tb.Layer = src.Layer;
                tb.SetSize(rh.Count, cw.Count);
                tb.Position = P(m["pos"]);
                try { if (tb.Cells[0, 0].IsMerged == true) tb.UnmergeCells(CellRange.Create(tb, 0, 0, 0, cw.Count - 1)); } catch { }
                for (int k = 0; k < cw.Count; k++) tb.Columns[k].Width = D(cw[k]);
                for (int r = 0; r < rh.Count; r++) tb.Rows[r].Height = D(rh[r]);
                double th = Has(m, "th") ? D(m["th"]) : 187.5;
                for (int r = 0; r < rh.Count; r++)
                    for (int k = 0; k < cw.Count; k++)
                    {
                        tb.Cells[r, k].TextStyleId = src.Cells[3, 2].TextStyleId;
                        tb.Cells[r, k].TextHeight = th;
                        tb.Cells[r, k].Alignment = CellAlignment.MiddleCenter;
                    }
                ms.AppendEntity(tb); tr.AddNewlyCreatedDBObject(tb, true);
                if (Has(m, "merge")) foreach (var o in L(m["merge"])) { var a = L(o); tb.MergeCells(CellRange.Create(tb, I(a[0]), I(a[1]), I(a[2]), I(a[3]))); }
                if (Has(m, "cells")) foreach (var o in L(m["cells"])) { var c = L(o); var cl = tb.Cells[I(c[0]), I(c[1])]; cl.TextString = c[2].ToString(); if (c.Count > 3) cl.Contents[0].TextHeight = D(c[3]); }
                if (Has(m, "left")) foreach (var o in L(m["left"])) { var c = L(o); tb.Cells[I(c[0]), I(c[1])].Alignment = CellAlignment.MiddleLeft; }
                if (Has(m, "bord")) foreach (var o in L(m["bord"]))
                {
                    var c = L(o); var bd = tb.Cells[I(c[0]), I(c[1])].Borders;
                    var cbs = new[] { bd.Top, bd.Bottom, bd.Left, bd.Right };
                    for (int q = 0; q < 4; q++) { cbs[q].IsVisible = true; cbs[q].LineWeight = (LineWeight)I(c[2 + q]); }
                }
                if (Has(m, "fcells")) foreach (var o in L(m["fcells"]))
                {
                    var c = L(o); var cl = tb.Cells[I(c[0]), I(c[1])];
                    cl.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
                    if (cl.Contents.Count == 0) cl.Contents.Add();
                    cl.Contents[0].Formula = c[2].ToString();
                    cl.Contents[0].TextHeight = th;
                    cl.DataFormat = c[3].ToString();
                }
                tb.GenerateLayout();
                log.AppendLine("newtable " + tb.Handle + " ext " + Ext(tb));
            }
            else if (t == "tstyle")
            {
                // set cell text style: by "style" name or copied from cell "src" [r,c]
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                ObjectId sid;
                if (Has(m, "src")) { var a = L(m["src"]); var sc = tb.Cells[I(a[0]), I(a[1])]; sid = (sc.Contents.Count > 0 && !sc.Contents[0].TextStyleId.IsNull) ? sc.Contents[0].TextStyleId : sc.TextStyleId.Value; }
                else { var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead); sid = st[S(m, "style", "")]; }
                foreach (var o in L(m["c"]))
                {
                    var a = L(o); var cl = tb.Cells[I(a[0]), I(a[1])];
                    cl.TextStyleId = sid;
                    try { if (cl.Contents.Count > 0) cl.Contents[0].TextStyleId = sid; } catch { }
                }
                log.AppendLine("tstyle " + ((TextStyleTableRecord)tr.GetObject(sid, OpenMode.ForRead)).Name);
            }
            else if (t == "rect")
            {
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
                var w = Win(m["win"]);
                var pl = new Polyline();
                pl.SetDatabaseDefaults(db);
                pl.AddVertexAt(0, new Point2d(w[0], w[1]), 0, 0, 0);
                pl.AddVertexAt(1, new Point2d(w[2], w[1]), 0, 0, 0);
                pl.AddVertexAt(2, new Point2d(w[2], w[3]), 0, 0, 0);
                pl.AddVertexAt(3, new Point2d(w[0], w[3]), 0, 0, 0);
                pl.Closed = true;
                pl.Layer = S(m, "layer", "0");
                pl.LineWeight = (LineWeight)I(m["lw"]);
                pl.ColorIndex = 256;
                ms.AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true);
                log.AppendLine("rect " + pl.Handle);
            }
            else if (t == "dellayout")
            {
                var lm = LayoutManager.Current;
                foreach (var n in L(m["names"])) { try { lm.DeleteLayout(n.ToString()); log.AppendLine("dellayout " + n); } catch (System.Exception ex) { log.AppendLine("dellayout " + n + ": " + ex.Message); } }
            }
            else if (t == "mklayouts")
            {
                // each: name, media, W, H, vc[x,y], sc ; create layout, page setup, activate, add model viewport
                var lm = LayoutManager.Current;
                var psv = PlotSettingsValidator.Current;
                foreach (var o in L(m["list"]))
                {
                    var q = (Dictionary<string, object>)o; string name = S(q, "name", "");
                    try
                    {
                        ObjectId lid = lm.GetLayoutId(name);
                        if (lid.IsNull) lid = lm.CreateLayout(name);
                        var lay = (Layout)tr.GetObject(lid, OpenMode.ForWrite);
                        var ps = new PlotSettings(lay.ModelType); ps.CopyFrom(lay);
                        psv.SetPlotConfigurationName(ps, "DWG To PDF.pc3", null);
                        psv.RefreshLists(ps);
                        psv.SetCanonicalMediaName(ps, S(q, "media", ""));
                        psv.SetPlotPaperUnits(ps, PlotPaperUnit.Millimeters);
                        psv.SetPlotRotation(ps, PlotRotation.Degrees000);
                        psv.SetPlotType(ps, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout);
                        psv.SetUseStandardScale(ps, true); psv.SetStdScaleType(ps, StdScaleType.StdScale1To1);
                        try { psv.SetCurrentStyleSheet(ps, "monochrome.ctb"); } catch { }
                        lay.CopyFrom(ps);
                        if (Has(q, "tab")) lay.TabOrder = I(q["tab"]);
                        lm.CurrentLayout = name;
                        var btr = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForWrite);
                        int k = 0; foreach (ObjectId id in btr) { var v = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (v != null && v.Number != 1) k++; }
                        double W = D(q["W"]), Hh = D(q["H"]);
                        var nv = new Viewport(); nv.SetDatabaseDefaults(db);
                        nv.CenterPoint = new Point3d(W / 2, Hh / 2, 0); nv.Width = W; nv.Height = Hh;
                        btr.AppendEntity(nv); tr.AddNewlyCreatedDBObject(nv, true);
                        try { nv.Layer = "Defpoints"; } catch { }
                        nv.ViewDirection = Vector3d.ZAxis; nv.ViewTarget = Point3d.Origin;
                        var vc = L(q["vc"]); nv.ViewCenter = new Point2d(D(vc[0]), D(vc[1]));
                        nv.CustomScale = 1.0 / D(q["sc"]);
                        try { nv.On = true; } catch (System.Exception ex) { log.AppendLine("vp.On " + name + ": " + ex.Message); }
                        nv.Locked = true;
                        log.AppendLine("layout " + name + " vp " + nv.Handle + " num " + nv.Number + " prev " + k + " media " + lay.CanonicalMediaName);
                    }
                    catch (System.Exception ex) { log.AppendLine("ERR layout " + name + ": " + ex.Message); }
                }
                lm.CurrentLayout = "Model";
            }
            else if (t == "dxfout")
            {
                db.DxfOut(S(m, "file", ""), 16, DwgVersion.Current);
            }
            else if (t == "regen")
            {
                Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument.SendStringToExecute("_.REGENALL\n", true, false, false);
            }
            else if (t == "save")
            {
                db.SaveAs(S(m, "file", ""), DwgVersion.Current);
            }
        }
        static string Ext(Entity e) { try { var x = e.GeometricExtents; return F(x.MinPoint.X) + "," + F(x.MinPoint.Y) + "," + F(x.MaxPoint.X) + "," + F(x.MaxPoint.Y); } catch { return "noext"; } }
    }
}
