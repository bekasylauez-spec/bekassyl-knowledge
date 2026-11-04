using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(V4.Cmds))]
namespace V4
{
    // JSON ops from %V4_JSON% (console AutoCAD):
    //  {t:"erase", h:[..]}
    //  {t:"eraseRegion", w:[x0,y0,x1,y1], types:["CIRCLE",..] (optional), keep:[h..]}
    //  {t:"text", h, v}            DBText.TextString / MText.Contents
    //  {t:"cells", h, cells:[[r,c,v],..]}
    //  {t:"delRows", h, r, n}
    //  {t:"delCol", h, c, widths:[..]}
    public class Cmds
    {
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static double D(object o) { return Convert.ToDouble(o, IC); }
        static IList L(object o) { return (IList)o; }
        static string S(Dictionary<string, object> m, string k) { object v; return m.TryGetValue(k, out v) && v != null ? v.ToString() : null; }

        // handles of entities imported in this run: "@<source handle>" -> new handle
        static Dictionary<string, string> imported = new Dictionary<string, string>();

        static ObjectId Id(Database db, string h)
        {
            ObjectId id;
            if (h.StartsWith("@")) { string nh; if (!imported.TryGetValue(h.Substring(1).ToUpper(), out nh)) return ObjectId.Null; h = nh; }
            return db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id) ? id : ObjectId.Null;
        }

        // clone model-space entities of DWG src (by handles, or all fully inside window w) into db, shifted by d
        static string Import(Database db, string src, IList handles, IList w, Vector3d d)
        {
            var sb = new StringBuilder();
            using (var sdb = new Database(false, true))
            {
                sdb.ReadDwgFile(src, FileOpenMode.OpenForReadAndAllShare, true, "");
                var ids = new ObjectIdCollection();
                using (var str = sdb.TransactionManager.StartTransaction())
                {
                    if (handles != null)
                        foreach (var h in handles) { ObjectId sid; if (sdb.TryGetObjectId(new Handle(Convert.ToInt64(h.ToString(), 16)), out sid)) ids.Add(sid); }
                    else
                    {
                        double x0 = D(w[0]), y0 = D(w[1]), x1 = D(w[2]), y1 = D(w[3]);
                        var sms = (BlockTableRecord)str.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(sdb), OpenMode.ForRead);
                        foreach (ObjectId sid in sms)
                        {
                            var e = str.GetObject(sid, OpenMode.ForRead) as Entity;
                            if (e == null) continue;
                            Extents3d x;
                            try { x = e.GeometricExtents; } catch { continue; }
                            if (x.MinPoint.X >= x0 && x.MaxPoint.X <= x1 && x.MinPoint.Y >= y0 && x.MaxPoint.Y <= y1) ids.Add(sid);
                        }
                    }
                    str.Commit();
                }
                var im = new IdMapping();
                sdb.WblockCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), im, DuplicateRecordCloning.Ignore, false);
                int n = 0;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    foreach (ObjectId sid in ids)
                    {
                        if (!im.Contains(sid)) continue;
                        var nid = im[sid].Value;
                        if (nid.IsNull) continue;
                        imported[sid.Handle.ToString().ToUpper()] = nid.Handle.ToString();
                        if (d.Length > 0) { var e = (Entity)tr.GetObject(nid, OpenMode.ForWrite); e.TransformBy(Matrix3d.Displacement(d)); }
                        n++;
                    }
                    tr.Commit();
                }
                sb.Append("source " + ids.Count + " cloned " + n);
            }
            return sb.ToString();
        }

        [CommandMethod("V4OPS")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var log = new StringBuilder();
            string jf = Environment.GetEnvironmentVariable("V4_JSON");
            try
            {
                var ops = (object[])new JavaScriptSerializer().DeserializeObject(File.ReadAllText(jf, Encoding.UTF8));
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                    foreach (Dictionary<string, object> m in ops)
                    {
                        string t = S(m, "t");
                        try
                        {
                            if (t == "erase")
                            {
                                foreach (var h in L(m["h"]))
                                {
                                    var id = Id(db, h.ToString());
                                    if (id.IsNull || id.IsErased) { log.AppendLine("erase: no " + h); continue; }
                                    var e = (Entity)tr.GetObject(id, OpenMode.ForWrite);
                                    log.AppendLine("erase " + h + " " + e.GetType().Name);
                                    e.Erase();
                                }
                            }
                            else if (t == "eraseRegion")
                            {
                                var w = L(m["w"]);
                                double x0 = D(w[0]), y0 = D(w[1]), x1 = D(w[2]), y1 = D(w[3]);
                                var types = new HashSet<string>();
                                if (m.ContainsKey("types")) foreach (var o in L(m["types"])) types.Add(o.ToString());
                                var keep = new HashSet<string>();
                                if (m.ContainsKey("keep")) foreach (var o in L(m["keep"])) keep.Add(o.ToString().ToUpper());
                                var hit = new Dictionary<string, int>();
                                foreach (ObjectId id in ms)
                                {
                                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                                    if (e == null || keep.Contains(e.Handle.ToString())) continue;
                                    string dxf = id.ObjectClass.DxfName;
                                    if (types.Count > 0 && !types.Contains(dxf)) continue;
                                    Extents3d x;
                                    try { x = e.GeometricExtents; } catch { continue; }
                                    if (x.MinPoint.X >= x0 && x.MaxPoint.X <= x1 && x.MinPoint.Y >= y0 && x.MaxPoint.Y <= y1)
                                    {
                                        e.UpgradeOpen(); e.Erase();
                                        int c; hit.TryGetValue(dxf, out c); hit[dxf] = c + 1;
                                    }
                                }
                                var sb = new StringBuilder();
                                foreach (var kv in hit) sb.Append(" " + kv.Key + "=" + kv.Value);
                                log.AppendLine("eraseRegion " + S(m, "tag") + ":" + sb);
                            }
                            else if (t == "text")
                            {
                                var e = tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                string v = S(m, "v");
                                if (e is DBText) { log.AppendLine("text " + S(m, "h") + " '" + ((DBText)e).TextString + "' -> '" + v + "'"); ((DBText)e).TextString = v; }
                                else if (e is MText) { log.AppendLine("mtext " + S(m, "h") + " '" + ((MText)e).Contents + "' -> '" + v + "'"); ((MText)e).Contents = v; }
                            }
                            else if (t == "cells")
                            {
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                foreach (var o in L(m["cells"]))
                                {
                                    var a = L(o); int r = Convert.ToInt32(a[0]), c = Convert.ToInt32(a[1]);
                                    string b = tb.Cells[r, c].TextString;
                                    tb.Cells[r, c].TextString = a[2].ToString();
                                    if (a.Count > 3)
                                    {
                                        // copy text height / alignment from a reference cell [rr,cc]
                                        var rf = L(a[3]); var rc = tb.Cells[Convert.ToInt32(rf[0]), Convert.ToInt32(rf[1])];
                                        if (tb.Cells[r, c].Contents.Count == 0) tb.Cells[r, c].Contents.Add();
                                        tb.Cells[r, c].Contents[0].TextHeight = rc.Contents[0].TextHeight;
                                        tb.Cells[r, c].Alignment = rc.Alignment;
                                    }
                                    log.AppendLine("cell " + S(m, "h") + " " + r + "," + c + " '" + b + "' -> '" + a[2] + "'");
                                }
                                if (!m.ContainsKey("nolayout")) tb.GenerateLayout();
                            }
                            else if (t == "formula")
                            {
                                // cells [[r,c,"=expr"],..]: formula cells shown with 2 decimals
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                foreach (var o in L(m["cells"]))
                                {
                                    var a = L(o); int r = Convert.ToInt32(a[0]), c = Convert.ToInt32(a[1]);
                                    var cell = tb.Cells[r, c];
                                    cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
                                    cell.DataFormat = a.Count > 3 ? a[3].ToString() : "%lu2%pr2";
                                    double th = cell.Contents.Count > 0 ? cell.Contents[0].TextHeight : 0;
                                    cell.Contents.Clear(); cell.Contents.Add();
                                    cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
                                    cell.DataFormat = a.Count > 3 ? a[3].ToString() : "%lu2%pr2";
                                    cell.Contents[0].Formula = a[2].ToString();
                                    if (th > 0) cell.Contents[0].TextHeight = th;
                                    log.AppendLine("formula " + r + "," + c + " " + a[2] + " -> '" + cell.TextString + "'");
                                }
                                tb.GenerateLayout();
                            }
                            else if (t == "stretchWin")
                            {
                                // entities fully inside window w: above ycut -> move dy; crossing ycut -> stretch points above ycut by dy
                                var w = L(m["w"]); double x0 = D(w[0]), y0 = D(w[1]), x1 = D(w[2]), y1 = D(w[3]);
                                double ycut = D(m["ycut"]), dy = D(m["dy"]);
                                var keep = new HashSet<string>(); if (m.ContainsKey("keep")) foreach (var o in L(m["keep"])) keep.Add(o.ToString().ToUpper());
                                int nm = 0, ns = 0; var sb = new StringBuilder();
                                var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                                foreach (var id in ids)
                                {
                                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                                    if (keep.Contains(id.Handle.ToString())) continue;
                                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                                    if (x.MinPoint.X < x0 || x.MaxPoint.X > x1 || x.MinPoint.Y < y0 || x.MaxPoint.Y > y1) continue;
                                    if (x.MaxPoint.Y <= ycut) continue;
                                    e.UpgradeOpen();
                                    if (x.MinPoint.Y >= ycut) { e.TransformBy(Matrix3d.Displacement(new Vector3d(0, dy, 0))); nm++; continue; }
                                    var pts = new Point3dCollection(); e.GetStretchPoints(pts);
                                    var idx = new IntegerCollection();
                                    for (int i = 0; i < pts.Count; i++) if (pts[i].Y > ycut) idx.Add(i);
                                    if (idx.Count > 0) e.MoveStretchPointsAt(idx, new Vector3d(0, dy, 0));
                                    ns++; sb.Append(" " + id.Handle + ":" + id.ObjectClass.DxfName + "/" + idx.Count + "of" + pts.Count);
                                }
                                log.AppendLine("stretchWin moved " + nm + " stretched " + ns + sb);
                            }
                            else if (t == "stretchWinX")
                            {
                                // entities fully inside window w: right of xcut -> move dx; crossing xcut -> stretch points right of xcut by dx
                                var w = L(m["w"]); double x0 = D(w[0]), y0 = D(w[1]), x1 = D(w[2]), y1 = D(w[3]);
                                double xcut = D(m["xcut"]), dx = D(m["dx"]);
                                var keep = new HashSet<string>(); if (m.ContainsKey("keep")) foreach (var o in L(m["keep"])) keep.Add(o.ToString().ToUpper());
                                int nm = 0, ns = 0; var sb = new StringBuilder();
                                var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                                foreach (var id in ids)
                                {
                                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                                    if (keep.Contains(id.Handle.ToString())) continue;
                                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                                    if (x.MinPoint.X < x0 || x.MaxPoint.X > x1 || x.MinPoint.Y < y0 || x.MaxPoint.Y > y1) continue;
                                    if (x.MaxPoint.X <= xcut) continue;
                                    e.UpgradeOpen();
                                    if (x.MinPoint.X >= xcut) { e.TransformBy(Matrix3d.Displacement(new Vector3d(dx, 0, 0))); nm++; continue; }
                                    var pts = new Point3dCollection(); try { e.GetStretchPoints(pts); } catch { sb.Append(" " + id.Handle + ":nostretch"); continue; }
                                    var idx = new IntegerCollection();
                                    for (int i = 0; i < pts.Count; i++) if (pts[i].X > xcut) idx.Add(i);
                                    if (idx.Count > 0) e.MoveStretchPointsAt(idx, new Vector3d(dx, 0, 0));
                                    ns++; sb.Append(" " + id.Handle + ":" + id.ObjectClass.DxfName + "/" + idx.Count + "of" + pts.Count);
                                }
                                log.AppendLine("stretchWinX moved " + nm + " stretched " + ns + sb);
                            }
                            else if (t == "insRows")
                            {
                                // insert n rows at index r, formatted like row "from"
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                tb.InsertRowsAndInherit(Convert.ToInt32(m["r"]), Convert.ToInt32(m["from"]), Convert.ToInt32(m["n"]));
                                tb.GenerateLayout();
                                log.AppendLine("insRows " + S(m, "h") + " rows now " + tb.Rows.Count);
                            }
                            else if (t == "dval")
                            {
                                // cells [[r,c,number,format],..]: plain double values (no formula/field)
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                foreach (var o in L(m["cells"]))
                                {
                                    var a = L(o); int r = Convert.ToInt32(a[0]), c = Convert.ToInt32(a[1]);
                                    var cell = tb.Cells[r, c];
                                    double th = cell.Contents.Count > 0 ? cell.Contents[0].TextHeight : 0;
                                    cell.Contents.Clear(); cell.Contents.Add();
                                    cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
                                    cell.DataFormat = a.Count > 3 ? a[3].ToString() : "%lu2%pr2";
                                    cell.Contents[0].Value = D(a[2]);
                                    if (th > 0) cell.Contents[0].TextHeight = th;
                                    log.AppendLine("dval " + S(m, "h") + " " + r + "," + c + " = " + a[2] + " -> '" + cell.TextString + "'");
                                }
                                tb.GenerateLayout();
                            }
                            else if (t == "merge")
                            {
                                // r0,c0,r1,c1
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                var a = L(m["rc"]);
                                tb.MergeCells(CellRange.Create(tb, Convert.ToInt32(a[0]), Convert.ToInt32(a[1]), Convert.ToInt32(a[2]), Convert.ToInt32(a[3])));
                                tb.GenerateLayout();
                                log.AppendLine("merge " + S(m, "h") + " " + a[0] + "," + a[1] + "," + a[2] + "," + a[3]);
                            }
                            else if (t == "delRows")
                            {
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                tb.DeleteRows(Convert.ToInt32(m["r"]), Convert.ToInt32(m["n"]));
                                tb.GenerateLayout();
                                log.AppendLine("delRows " + S(m, "h") + " rows now " + tb.Rows.Count + " h=" + tb.Height);
                            }
                            else if (t == "delCol")
                            {
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                tb.DeleteColumns(Convert.ToInt32(m["c"]), 1);
                                if (m.ContainsKey("widths")) { var ws = L(m["widths"]); for (int i = 0; i < ws.Count; i++) tb.Columns[i].Width = D(ws[i]); }
                                tb.GenerateLayout();
                                log.AppendLine("delCol " + S(m, "h") + " cols now " + tb.Columns.Count + " w=" + tb.Width);
                            }
                            else if (t == "clone")
                            {
                                // copy entity h with displacement dx,dy (one copy per item of "d": [[dx,dy],..])
                                var src = Id(db, S(m, "h"));
                                foreach (var o in L(m["d"]))
                                {
                                    var a = L(o);
                                    var ids = new ObjectIdCollection { src };
                                    var im = new IdMapping();
                                    db.DeepCloneObjects(ids, ms.ObjectId, im, false);
                                    var ne = (Entity)tr.GetObject(im[src].Value, OpenMode.ForWrite);
                                    ne.TransformBy(Matrix3d.Displacement(new Vector3d(D(a[0]), D(a[1]), 0)));
                                    log.AppendLine("clone " + S(m, "h") + " -> " + ne.Handle + " d=" + a[0] + "," + a[1]);
                                }
                            }
                            else if (t == "props")
                            {
                                var e = (Entity)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                if (m.ContainsKey("layer")) e.Layer = S(m, "layer");
                                var mt = e as MText;
                                if (mt != null)
                                {
                                    if (m.ContainsKey("x")) mt.Location = new Point3d(D(m["x"]), D(m["y"]), 0);
                                    if (m.ContainsKey("w")) mt.Width = D(m["w"]);
                                    if (m.ContainsKey("th")) mt.TextHeight = D(m["th"]);
                                }
                                var tx = e as DBText;
                                if (tx != null && m.ContainsKey("th")) tx.Height = D(m["th"]);
                                log.AppendLine("props " + S(m, "h") + " " + e.GetType().Name);
                            }
                            else if (t == "moveRegion")
                            {
                                // move every entity whose extents lie inside w by dx,dy (needs full AutoCAD for SPDS objects)
                                var w = L(m["w"]);
                                double x0 = D(w[0]), y0 = D(w[1]), x1 = D(w[2]), y1 = D(w[3]);
                                var mv = Matrix3d.Displacement(new Vector3d(D(m["dx"]), D(m["dy"]), 0));
                                var hit = new List<ObjectId>();
                                foreach (ObjectId id in ms)
                                {
                                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                                    if (e == null) continue;
                                    Extents3d x;
                                    try { x = e.GeometricExtents; } catch { continue; }
                                    if (x.MinPoint.X >= x0 && x.MaxPoint.X <= x1 && x.MinPoint.Y >= y0 && x.MaxPoint.Y <= y1) hit.Add(id);
                                }
                                int ok = 0;
                                foreach (var id in hit)
                                {
                                    try { var e = (Entity)tr.GetObject(id, OpenMode.ForWrite); e.TransformBy(mv); ok++; }
                                    catch (System.Exception ex) { log.AppendLine("  move fail " + id.Handle + " " + id.ObjectClass.DxfName + " " + ex.Message); }
                                }
                                log.AppendLine("moveRegion " + S(m, "tag") + ": " + ok + "/" + hit.Count);
                            }
                            else if (t == "replaceAll")
                            {
                                // ordered substring replacements in every TEXT/MTEXT of model space (and table cells)
                                var pairs = L(m["pairs"]);
                                int nt = 0, nc = 0;
                                foreach (ObjectId id in ms)
                                {
                                    var e = tr.GetObject(id, OpenMode.ForRead);
                                    if (e is DBText || e is MText)
                                    {
                                        string s0 = e is DBText ? ((DBText)e).TextString : ((MText)e).Contents, s = s0;
                                        foreach (var p in pairs) { var a = L(p); s = s.Replace(a[0].ToString(), a[1].ToString()); }
                                        if (s == s0) continue;
                                        e.UpgradeOpen();
                                        if (e is DBText) ((DBText)e).TextString = s; else ((MText)e).Contents = s;
                                        nt++;
                                    }
                                    else if (e is Table && m.ContainsKey("tables"))
                                    {
                                        var tb = (Table)e; bool ch = false;
                                        for (int r = 0; r < tb.Rows.Count; r++)
                                            for (int c = 0; c < tb.Columns.Count; c++)
                                            {
                                                string s0 = tb.Cells[r, c].TextString, s = s0;
                                                if (string.IsNullOrEmpty(s0)) continue;
                                                foreach (var p in pairs) { var a = L(p); s = s.Replace(a[0].ToString(), a[1].ToString()); }
                                                if (s == s0) continue;
                                                if (!ch) { tb.UpgradeOpen(); ch = true; }
                                                tb.Cells[r, c].TextString = s; nc++;
                                            }
                                        if (ch && !m.ContainsKey("nolayout")) tb.GenerateLayout();
                                    }
                                }
                                log.AppendLine("replaceAll " + S(m, "tag") + ": texts " + nt + " cells " + nc);
                            }
                            else if (t == "import")
                            {
                                var d = m.ContainsKey("d") ? new Vector3d(D(L(m["d"])[0]), D(L(m["d"])[1]), 0) : new Vector3d();
                                log.AppendLine("import " + S(m, "tag") + ": " + Import(db, S(m, "src"), m.ContainsKey("h") ? L(m["h"]) : null, m.ContainsKey("w") ? L(m["w"]) : null, d));
                            }
                            else if (t == "importBlock")
                            {
                                // replace block definition "name" with the one from DWG "src"
                                using (var sdb = new Database(false, true))
                                {
                                    sdb.ReadDwgFile(S(m, "src"), FileOpenMode.OpenForReadAndAllShare, true, "");
                                    using (var str = sdb.TransactionManager.StartTransaction())
                                    {
                                        var sbt = (BlockTable)str.GetObject(sdb.BlockTableId, OpenMode.ForRead);
                                        var ids = new ObjectIdCollection { sbt[S(m, "name")] };
                                        var im = new IdMapping();
                                        sdb.WblockCloneObjects(ids, db.BlockTableId, im, DuplicateRecordCloning.Replace, false);
                                        str.Commit();
                                    }
                                }
                                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                                var btr = (BlockTableRecord)tr.GetObject(bt[S(m, "name")], OpenMode.ForRead);
                                int n = 0; foreach (ObjectId x in btr) n++;
                                log.AppendLine("importBlock " + S(m, "name") + " entities now " + n + " refs " + btr.GetBlockReferenceIds(true, false).Count);
                            }
                            else if (t == "dyn")
                            {
                                // list (and optionally set: props {name: value}) dynamic block properties
                                var br = (BlockReference)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                Dictionary<string, object> pv = m.ContainsKey("props") ? (Dictionary<string, object>)m["props"] : null;
                                foreach (DynamicBlockReferenceProperty p in br.DynamicBlockReferencePropertyCollection)
                                {
                                    string line = "  dyn " + S(m, "h") + " '" + p.PropertyName + "'=" + Convert.ToString(p.Value, IC) + " ro=" + p.ReadOnly + " type=" + p.UnitsType;
                                    object v;
                                    if (pv != null && pv.TryGetValue(p.PropertyName, out v) && !p.ReadOnly)
                                    {
                                        if (p.Value is double) p.Value = D(v); else if (p.Value is short) p.Value = Convert.ToInt16(v); else if (p.Value is int) p.Value = Convert.ToInt32(v); else p.Value = v.ToString();
                                        line += " -> " + Convert.ToString(p.Value, IC);
                                    }
                                    log.AppendLine(line);
                                }
                            }
                            else if (t == "dimdx")
                            {
                                // shift a linear dimension's extension-line points by dx1/dx2 (x only); optional "v": new DimensionText
                                var e = tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                var dm = e as Dimension; var rd = e as RotatedDimension; var ad = e as AlignedDimension;
                                double dx1 = m.ContainsKey("dx1") ? D(m["dx1"]) : 0, dx2 = m.ContainsKey("dx2") ? D(m["dx2"]) : 0;
                                if (rd != null) { rd.XLine1Point = rd.XLine1Point + new Vector3d(dx1, 0, 0); rd.XLine2Point = rd.XLine2Point + new Vector3d(dx2, 0, 0); }
                                else if (ad != null) { ad.XLine1Point = ad.XLine1Point + new Vector3d(dx1, 0, 0); ad.XLine2Point = ad.XLine2Point + new Vector3d(dx2, 0, 0); }
                                if (dm != null && (dx1 != 0 || dx2 != 0)) dm.TextPosition = dm.TextPosition + new Vector3d((dx1 + dx2) / 2, 0, 0);
                                if (dm != null && m.ContainsKey("v")) dm.DimensionText = S(m, "v");
                                log.AppendLine("dimdx " + S(m, "h") + (rd != null ? " m=" + rd.Measurement : ad != null ? " m=" + ad.Measurement : " not linear") + (m.ContainsKey("v") ? " txt=" + S(m, "v") : ""));
                            }
                            else if (t == "dimpts")
                            {
                                var e = tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                var rd = e as RotatedDimension; var ad = e as AlignedDimension;
                                Func<object, Point3d> P = o => { var a = L(o); return new Point3d(D(a[0]), D(a[1]), 0); };
                                if (rd != null) { if (m.ContainsKey("p1")) rd.XLine1Point = P(m["p1"]); if (m.ContainsKey("p2")) rd.XLine2Point = P(m["p2"]); log.AppendLine("dimpts " + S(m, "h") + " m=" + rd.Measurement); }
                                else if (ad != null) { if (m.ContainsKey("p1")) ad.XLine1Point = P(m["p1"]); if (m.ContainsKey("p2")) ad.XLine2Point = P(m["p2"]); log.AppendLine("dimpts " + S(m, "h") + " m=" + ad.Measurement); }
                                else log.AppendLine("dimpts " + S(m, "h") + " not a linear dim: " + e.GetType().Name);
                            }
                            else if (t == "rehatch")
                            {
                                // recreate hatch h with loops from closed polylines b (pattern/props copied), erase the old one
                                var old = (Hatch)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                var nh = new Hatch(); nh.SetDatabaseDefaults();
                                ms.AppendEntity(nh); tr.AddNewlyCreatedDBObject(nh, true);
                                nh.Layer = old.Layer; nh.Color = old.Color; nh.Linetype = old.Linetype; nh.LineWeight = old.LineWeight;
                                nh.SetHatchPattern(old.PatternType, old.PatternName);
                                nh.PatternScale = old.PatternScale; nh.PatternAngle = old.PatternAngle; nh.PatternDouble = old.PatternDouble;
                                nh.Associative = false; nh.Normal = old.Normal; nh.Elevation = old.Elevation;
                                int loops = 0;
                                foreach (var bh in L(m["b"])) { var ids = new ObjectIdCollection { Id(db, bh.ToString()) }; nh.AppendLoop(HatchLoopTypes.Default, ids); loops++; }
                                nh.EvaluateHatch(true);
                                try { nh.BackgroundColor = old.BackgroundColor; } catch { }
                                old.Erase();
                                log.AppendLine("rehatch " + S(m, "h") + " -> " + nh.Handle + " loops " + loops + " pattern " + old.PatternName);
                            }
                            else if (t == "clipY")
                            {
                                // clamp polyline/line vertices: y above ymax -> ymax, y below ymin -> ymin
                                double? ymax = m.ContainsKey("ymax") ? (double?)D(m["ymax"]) : null, ymin = m.ContainsKey("ymin") ? (double?)D(m["ymin"]) : null;
                                Func<double, double> C = y => { if (ymax.HasValue && y > ymax.Value) y = ymax.Value; if (ymin.HasValue && y < ymin.Value) y = ymin.Value; return y; };
                                foreach (var h in L(m["h"]))
                                {
                                    var e = tr.GetObject(Id(db, h.ToString()), OpenMode.ForWrite);
                                    if (e is Polyline) { var pl = (Polyline)e; for (int i = 0; i < pl.NumberOfVertices; i++) { var p = pl.GetPoint2dAt(i); pl.SetPointAt(i, new Point2d(p.X, C(p.Y))); } }
                                    else if (e is Line) { var ln = (Line)e; ln.StartPoint = new Point3d(ln.StartPoint.X, C(ln.StartPoint.Y), 0); ln.EndPoint = new Point3d(ln.EndPoint.X, C(ln.EndPoint.Y), 0); }
                                    log.AppendLine("clipY " + h + " " + e.GetType().Name);
                                }
                            }
                            else if (t == "move")
                            {
                                var e = (Entity)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                e.TransformBy(Matrix3d.Displacement(new Vector3d(D(m["dx"]), D(m["dy"]), 0)));
                                log.AppendLine("move " + S(m, "h") + " " + m["dx"] + "," + m["dy"]);
                            }
                            else if (t == "plpts")
                            {
                                // replace all vertices of a polyline: pts [[x,y],..] (bulges reset to 0)
                                var pl = (Polyline)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                var pts = L(m["pts"]);
                                while (pl.NumberOfVertices > pts.Count) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                                for (int i = 0; i < pts.Count; i++)
                                {
                                    var a = L(pts[i]); var p = new Point2d(D(a[0]), D(a[1]));
                                    if (i < pl.NumberOfVertices) { pl.SetPointAt(i, p); pl.SetBulgeAt(i, 0); } else pl.AddVertexAt(i, p, 0, 0, 0);
                                }
                                log.AppendLine("plpts " + S(m, "h") + " n=" + pl.NumberOfVertices);
                            }
                            else if (t == "recompute")
                            {
                                var tb = (Table)tr.GetObject(Id(db, S(m, "h")), OpenMode.ForWrite);
                                tb.GenerateLayout(); tb.RecomputeTableBlock(true);
                                log.AppendLine("recompute " + S(m, "h") + " rows " + tb.Rows.Count + " cols " + tb.Columns.Count + " w=" + tb.Width + " h=" + tb.Height);
                            }
                            else log.AppendLine("unknown op " + t);
                        }
                        catch (System.Exception ex) { log.AppendLine("ERR op " + t + " " + S(m, "h") + ": " + ex.Message); }
                    }
                    tr.Commit();
                }
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(jf + ".log", log.ToString(), Encoding.UTF8);
        }
    }
}
