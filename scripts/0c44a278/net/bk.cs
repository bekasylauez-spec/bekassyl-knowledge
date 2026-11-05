using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.ApplicationServices.Core;

[assembly: CommandClass(typeof(BK.Cmds))]
namespace BK
{
    public class Cmds
    {
        static StringBuilder log = new StringBuilder();
        static string tmp = Environment.GetEnvironmentVariable("TEMP");
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static double D(object o) { return Convert.ToDouble(o, IC); }
        static string S(Dictionary<string, object> m, string k, string def) { object v; return m.TryGetValue(k, out v) && v != null ? v.ToString() : def; }
        static bool Has(Dictionary<string, object> m, string k) { object v; return m.TryGetValue(k, out v) && v != null; }
        static IList L(object o) { return (IList)o; }
        static Point2d P2(object o) { var a = L(o); return new Point2d(D(a[0]), D(a[1])); }
        static Point3d P(object o) { var a = L(o); return new Point3d(D(a[0]), D(a[1]), 0); }
        static Dictionary<string, string> map = new Dictionary<string, string>();
        static string mapFile;
        static ObjectId H(Database db, string h)
        {
            if (map.ContainsKey(h)) h = map[h];
            ObjectId id;
            if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id)) return id;
            throw new System.Exception("no handle " + h);
        }
        static void Tag(Dictionary<string, object> m, Entity e) { string t = S(m, "tag", null); if (t != null) map[t] = e.Handle.ToString(); }
        static void Props(Entity e, Dictionary<string, object> m, Database db, Transaction tr)
        {
            if (Has(m, "tpl"))
            {
                var t = (Entity)tr.GetObject(H(db, S(m, "tpl", "")), OpenMode.ForRead);
                e.Layer = t.Layer; e.Color = t.Color; e.Linetype = t.Linetype; e.LinetypeScale = t.LinetypeScale; e.LineWeight = t.LineWeight;
            }
            string lay = S(m, "layer", null);
            if (lay != null)
            {
                var lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);
                if (!lt.Has(lay))
                {
                    lt.UpgradeOpen(); var r = new LayerTableRecord(); r.Name = lay;
                    if (Has(m, "laylike")) { var src = (LayerTableRecord)tr.GetObject(lt[S(m, "laylike", "")], OpenMode.ForRead); r.Color = src.Color; r.LineWeight = src.LineWeight; r.LinetypeObjectId = src.LinetypeObjectId; }
                    lt.Add(r); tr.AddNewlyCreatedDBObject(r, true);
                }
                e.Layer = lay;
            }
            if (Has(m, "color")) e.ColorIndex = Convert.ToInt32(m["color"]);
            if (Has(m, "lw")) e.LineWeight = (LineWeight)Convert.ToInt32(m["lw"]);
        }
        static BlockTableRecord MS(Database db, Transaction tr) { return (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite); }
        static Entity DClone(Database db, Transaction tr, ObjectId src)
        {
            var ids = new ObjectIdCollection(); ids.Add(src); var im = new IdMapping();
            db.DeepCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), im, false);
            foreach (IdPair p in im) if (p.IsCloned && p.IsPrimary && p.Key == src) return (Entity)tr.GetObject(p.Value, OpenMode.ForWrite);
            throw new System.Exception("clone failed");
        }

        [CommandMethod("BKOPS")]
        public static void Apply()
        {
            log.Clear(); map.Clear();
            string jf = Path.Combine(tmp, "bk_ops.json");
            var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
            var root = (Dictionary<string, object>)js.DeserializeObject(File.ReadAllText(jf, Encoding.UTF8));
            mapFile = S(root, "map", Path.Combine(tmp, "bk_map.json"));
            try { var mm = (Dictionary<string, object>)js.DeserializeObject(File.ReadAllText(mapFile, Encoding.UTF8)); foreach (var kv in mm) map[kv.Key] = kv.Value.ToString(); } catch { }
            var db = HostApplicationServices.WorkingDatabase;
            int nerr = 0, n = 0;
            foreach (var o in L(root["ops"]))
            {
                var m = (Dictionary<string, object>)o;
                try
                {
                    using (var tr = db.TransactionManager.StartTransaction()) { Op(db, tr, m); tr.Commit(); }
                    n++;
                }
                catch (System.Exception ex) { nerr++; log.AppendLine("ERR " + S(m, "t", "?") + " " + S(m, "tag", "") + " " + S(m, "h", "") + ": " + ex.Message); }
            }
            log.AppendLine("done ops " + n + " errors " + nerr);
            File.WriteAllText(mapFile, new JavaScriptSerializer().Serialize(map), Encoding.UTF8);
            File.WriteAllText(S(root, "log", Path.Combine(tmp, "bk_log.txt")), log.ToString(), Encoding.UTF8);
        }

        static void Op(Database db, Transaction tr, Dictionary<string, object> m)
        {
            string t = S(m, "t", "");
            if (t == "pl")
            {
                var pl = new Polyline(); var pts = L(m["p"]);
                for (int i = 0; i < pts.Count; i++) pl.AddVertexAt(i, P2(pts[i]), 0, 0, 0);
                pl.Closed = Has(m, "closed") && (bool)m["closed"];
                pl.SetDatabaseDefaults(db); Props(pl, m, db, tr);
                if (Has(m, "w")) pl.ConstantWidth = D(m["w"]);
                MS(db, tr).AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true); Tag(m, pl);
            }
            else if (t == "circle")
            {
                var c = new Circle(P(m["c"]), Vector3d.ZAxis, D(m["r"])); c.SetDatabaseDefaults(db); Props(c, m, db, tr);
                MS(db, tr).AppendEntity(c); tr.AddNewlyCreatedDBObject(c, true); Tag(m, c);
            }
            else if (t == "clone")
            {
                var e = DClone(db, tr, H(db, S(m, "h", "")));
                var bs = Has(m, "base") ? P(m["base"]) : Point3d.Origin; var to = Has(m, "to") ? P(m["to"]) : bs;
                if (Has(m, "rot")) e.TransformBy(Matrix3d.Rotation(D(m["rot"]), Vector3d.ZAxis, bs));
                e.TransformBy(Matrix3d.Displacement(to - bs));
                if (Has(m, "text")) { if (e is MText) ((MText)e).Contents = S(m, "text", ""); else if (e is DBText) ((DBText)e).TextString = S(m, "text", ""); }
                if (Has(m, "attr") && e is BlockReference)
                    foreach (ObjectId aid in ((BlockReference)e).AttributeCollection) { var ar = (AttributeReference)tr.GetObject(aid, OpenMode.ForWrite); ar.TextString = S(m, "attr", ""); }
                if (Has(m, "pts") && e is Polyline)
                {
                    var pl = (Polyline)e; var pts = L(m["pts"]);
                    while (pl.NumberOfVertices > pts.Count) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                    for (int i = 0; i < pts.Count; i++) { if (i < pl.NumberOfVertices) pl.SetPointAt(i, P2(pts[i])); else pl.AddVertexAt(i, P2(pts[i]), 0, 0, 0); pl.SetBulgeAt(i, 0); }
                }
                Props(e, m, db, tr); Tag(m, e);
            }
            else if (t == "lineset")
            {
                var l = (Line)DClone(db, tr, H(db, S(m, "h", "")));
                l.StartPoint = P(m["s"]); l.EndPoint = P(m["e"]); Props(l, m, db, tr); Tag(m, l);
            }
            else if (t == "dim")
            {
                var e = DClone(db, tr, H(db, S(m, "h", "")));
                if (e is RotatedDimension)
                {
                    var d = (RotatedDimension)e;
                    d.XLine1Point = P(m["p1"]); d.XLine2Point = P(m["p2"]); d.DimLinePoint = P(m["dl"]);
                    d.Rotation = Has(m, "rot") ? D(m["rot"]) : 0;
                }
                else if (e is AlignedDimension)
                {
                    var d = (AlignedDimension)e; d.XLine1Point = P(m["p1"]); d.XLine2Point = P(m["p2"]); d.DimLinePoint = P(m["dl"]);
                }
                var dm = (Dimension)e;
                dm.DimensionText = S(m, "txt", "");
                dm.UsingDefaultTextPosition = true;
                if (Has(m, "tx")) { dm.UsingDefaultTextPosition = false; dm.TextPosition = P(m["tx"]); }
                Props(e, m, db, tr); Tag(m, e);
            }
            else if (t == "ml")
            {
                var e = (MLeader)DClone(db, tr, H(db, S(m, "h", "")));
                var bs = P(m["base"]); var to = P(m["to"]);
                e.TransformBy(Matrix3d.Displacement(to - bs));
                if (Has(m, "text")) { var mt = e.MText; mt.Contents = S(m, "text", ""); e.MText = mt; }
                var lines = new List<int>();
                foreach (int li in e.GetLeaderIndexes()) foreach (int ln in e.GetLeaderLineIndexes(li)) lines.Add(ln);
                var arr = L(m["arrows"]);
                for (int i = 0; i < lines.Count; i++)
                {
                    if (i < arr.Count) e.SetFirstVertex(lines[i], P(arr[i]));
                    else e.RemoveLeaderLine(lines[i]);
                }
                Props(e, m, db, tr); Tag(m, e);
            }
            else if (t == "mlinfo")
            {
                var e = (MLeader)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var sb = new StringBuilder("ML " + e.Handle + " txtloc " + e.TextLocation + " txt=" + (e.MText != null ? e.MText.Contents : ""));
                foreach (int li in e.GetLeaderIndexes()) foreach (int ln in e.GetLeaderLineIndexes(li))
                    { sb.Append(" | L" + li + "/" + ln + " n=" + e.VerticesCount(ln)); for (int k = 0; k < e.VerticesCount(ln); k++) sb.Append(" " + e.GetVertex(ln, k)); }
                log.AppendLine(sb.ToString());
            }
            else if (t == "move")
            {
                var dv = L(m["d"]);
                foreach (var h in L(m["h"])) ((Entity)tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite)).TransformBy(Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0)));
            }
            else if (t == "settext")
            {
                var e = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                try { if (e.HasFields) e.RemoveField(); } catch { }
                if (e is MText) ((MText)e).Contents = S(m, "s", ""); else if (e is DBText) ((DBText)e).TextString = S(m, "s", "");
                else if (e is BlockReference) foreach (ObjectId aid in ((BlockReference)e).AttributeCollection) { var ar = (AttributeReference)tr.GetObject(aid, OpenMode.ForWrite); if (!Has(m, "tagname") || ar.Tag == S(m, "tagname", "")) ar.TextString = S(m, "s", ""); }
            }
            else if (t == "replace")
            {
                var w = L(m["win"]); string a = S(m, "a", ""), b = S(m, "b", ""); int n = 0;
                foreach (ObjectId id in MS(db, tr))
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    if (e is MText && ((MText)e).Contents.Contains(a)) { e.UpgradeOpen(); ((MText)e).Contents = ((MText)e).Contents.Replace(a, b); n++; }
                    else if (e is DBText && ((DBText)e).TextString.Contains(a)) { e.UpgradeOpen(); ((DBText)e).TextString = ((DBText)e).TextString.Replace(a, b); n++; }
                    else if (e is Dimension && ((Dimension)e).DimensionText.Contains(a)) { e.UpgradeOpen(); ((Dimension)e).DimensionText = ((Dimension)e).DimensionText.Replace(a, b); n++; }
                    else if (e is MLeader && ((MLeader)e).MText != null && ((MLeader)e).MText.Contents.Contains(a)) { e.UpgradeOpen(); var ml = (MLeader)e; var mt = ml.MText; mt.Contents = mt.Contents.Replace(a, b); ml.MText = mt; n++; }
                    else if (e is BlockReference) foreach (ObjectId aid in ((BlockReference)e).AttributeCollection) { var ar = (AttributeReference)tr.GetObject(aid, OpenMode.ForRead); if (ar.TextString.Contains(a)) { ar.UpgradeOpen(); ar.TextString = ar.TextString.Replace(a, b); n++; } }
                }
                log.AppendLine("replace " + a + " " + n);
            }
            else if (t == "eraselayer")
            {
                var w = L(m["win"]); string lay = S(m, "layer", ""); int n = 0; var ids = new List<ObjectId>();
                foreach (ObjectId id in MS(db, tr))
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null || e.Layer != lay) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    ids.Add(id);
                }
                foreach (var id in ids) { tr.GetObject(id, OpenMode.ForWrite).Erase(); n++; }
                log.AppendLine("eraselayer " + lay + " " + n);
            }
            else if (t == "eraseregion")
            {
                var w = L(m["win"]);
                var keep = new HashSet<string>(); if (Has(m, "keep")) foreach (var k in L(m["keep"])) keep.Add(k.ToString().ToUpper());
                var ms = MS(db, tr); int n = 0; var ids = new List<ObjectId>();
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    if (keep.Contains(e.Handle.ToString())) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    bool inside = x.MinPoint.X >= D(w[0]) && x.MaxPoint.X <= D(w[2]) && x.MinPoint.Y >= D(w[1]) && x.MaxPoint.Y <= D(w[3]);
                    if (inside) ids.Add(id);
                }
                foreach (var id in ids) { tr.GetObject(id, OpenMode.ForWrite).Erase(); n++; }
                log.AppendLine("eraseregion " + n);
            }
            else if (t == "erase")
            {
                foreach (var h in L(m["h"])) { try { tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite).Erase(); } catch (System.Exception ex) { log.AppendLine("erase " + h + ": " + ex.Message); } }
            }
            else if (t == "movewin")
            {
                var w = L(m["win"]); var dv = L(m["d"]); var mx = Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0));
                var ids = new List<ObjectId>(); foreach (ObjectId id in MS(db, tr)) ids.Add(id); int n = 0;
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X >= D(w[0]) && x.MaxPoint.X <= D(w[2]) && x.MinPoint.Y >= D(w[1]) && x.MaxPoint.Y <= D(w[3])) { e.UpgradeOpen(); e.TransformBy(mx); n++; }
                }
                log.AppendLine("movewin " + n);
            }
            else if (t == "stretch")
            {
                var w = L(m["win"]); double wx0 = D(w[0]), wy0 = D(w[1]), wx1 = D(w[2]), wy1 = D(w[3]);
                var dv = L(m["d"]); var vec = new Vector3d(D(dv[0]), D(dv[1]), 0);
                Func<Point3d, bool> inW = q => q.X >= wx0 && q.X <= wx1 && q.Y >= wy0 && q.Y <= wy1;
                IList sel = Has(m, "sel") ? L(m["sel"]) : null;
                int nm = 0, ns = 0, nf = 0;
                var ids = new List<ObjectId>();
                if (Has(m, "hs")) { foreach (var hh in L(m["hs"])) { try { ids.Add(H(db, hh.ToString())); } catch { } } }
                else foreach (ObjectId id in MS(db, tr)) ids.Add(id);
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (sel != null && (x.MinPoint.X < D(sel[0]) || x.MaxPoint.X > D(sel[2]) || x.MinPoint.Y < D(sel[1]) || x.MaxPoint.Y > D(sel[3]))) continue;
                    if (x.MaxPoint.X < wx0 || x.MinPoint.X > wx1 || x.MaxPoint.Y < wy0 || x.MinPoint.Y > wy1) continue;
                    try
                    {
                        if (x.MinPoint.X >= wx0 && x.MaxPoint.X <= wx1 && x.MinPoint.Y >= wy0 && x.MaxPoint.Y <= wy1) { e.UpgradeOpen(); e.TransformBy(Matrix3d.Displacement(vec)); nm++; continue; }
                        if (e is Hatch) { RebuildHatch(db, tr, (Hatch)e, inW, vec); ns++; continue; }
                        var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                        var idx = new IntegerCollection(); bool all = pc.Count > 0;
                        for (int i = 0; i < pc.Count; i++) { if (inW(pc[i])) idx.Add(i); else all = false; }
                        if (idx.Count == 0) continue;
                        e.UpgradeOpen();
                        if (all || e is DBText || e is MText || e is BlockReference || e is MLeader) { if (all || inW(pc[0])) { e.TransformBy(Matrix3d.Displacement(vec)); nm++; } }
                        else { e.MoveStretchPointsAt(idx, vec); ns++; }
                    }
                    catch (System.Exception ex) { nf++; log.AppendLine("stretch fail " + e.Handle + " " + e.GetType().Name + " " + ex.Message); }
                }
                log.AppendLine("stretch moved " + nm + " stretched " + ns + " failed " + nf);
            }
            else if (t == "tdump")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                log.AppendLine("TABLE rows " + tb.Rows.Count + " cols " + tb.Columns.Count + " pos " + tb.Position + " h " + tb.Height);
                for (int r = 0; r < tb.Rows.Count; r++)
                {
                    var sb = new StringBuilder("R" + r + " h" + tb.Rows[r].Height.ToString("0", IC) + ":");
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var cell = tb.Cells[r, c]; string f = "";
                        try { string ed = cell.GetTextString(FormatOption.ForEditing); if (ed != cell.TextString) f = "{" + ed + "}"; } catch { }
                        sb.Append(" | " + cell.TextString.Replace("\n", "\\n") + f);
                    }
                    log.AppendLine(sb.ToString());
                }
            }
            else if (t == "tset")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["cells"]))
                {
                    var a = L(q); int r = Convert.ToInt32(a[0]), c = Convert.ToInt32(a[1]); string v = a[2].ToString();
                    var cell = tb.Cells[r, c];
                    if (v.StartsWith("=")) { cell.TextString = ""; cell.Contents[0].Formula = "%<\\AcExpr (" + v.Substring(1) + ")>%"; }
                    else cell.TextString = v;
                }
            }
            else if (t == "trows")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                string mode = S(m, "mode", "del"); int at = Convert.ToInt32(m["at"]), n = Convert.ToInt32(m["n"]);
                if (mode == "del") tb.DeleteRows(at, n); else tb.InsertRowsAndInherit(at, Convert.ToInt32(m["from"]), n);
            }
            else if (t == "list")
            {
                var w = L(m["win"]);
                foreach (ObjectId id in MS(db, tr))
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    log.AppendLine("L\t" + id.ObjectClass.DxfName + "\t" + e.Handle + "\t" + e.Layer + "\t" + x.MinPoint.X.ToString("0", IC) + "," + x.MinPoint.Y.ToString("0", IC) + "," + x.MaxPoint.X.ToString("0", IC) + "," + x.MaxPoint.Y.ToString("0", IC));
                }
            }
            else if (t == "freezefields")
            {
                int n = 0; var ids = new List<ObjectId>(); foreach (ObjectId id in MS(db, tr)) ids.Add(id);
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead);
                    try { if (e.HasFields && !(e is Table)) { e.UpgradeOpen(); e.RemoveField(); n++; } } catch { }
                    var br = e as BlockReference;
                    if (br != null) foreach (ObjectId aid in br.AttributeCollection) { var ar = tr.GetObject(aid, OpenMode.ForRead); try { if (ar.HasFields) { ar.UpgradeOpen(); ar.RemoveField(); n++; } } catch { } }
                }
                log.AppendLine("freezefields " + n);
            }
            else if (t == "saveas")
            {
                db.SaveAs(S(m, "file", ""), DwgVersion.Current); log.AppendLine("saved " + S(m, "file", ""));
            }
            else throw new System.Exception("unknown op " + t);
        }
        static void RebuildHatch(Database db, Transaction tr, Hatch h, Func<Point3d, bool> inW, Vector3d vec)
        {
            h.UpgradeOpen();
            var loops = new List<Point2dCollection>(); var types = new List<HatchLoopTypes>();
            for (int i = 0; i < h.NumberOfLoops; i++)
            {
                var lp = h.GetLoopAt(i); var pc = new Point2dCollection();
                if (lp.IsPolyline) foreach (BulgeVertex bv in lp.Polyline) pc.Add(bv.Vertex);
                else foreach (Curve2d c in lp.Curves) pc.Add(c.StartPoint);
                for (int k = 0; k < pc.Count; k++) { var p3 = new Point3d(pc[k].X, pc[k].Y, 0); if (inW(p3)) pc[k] = new Point2d(pc[k].X + vec.X, pc[k].Y + vec.Y); }
                loops.Add(pc); types.Add(lp.LoopType);
            }
            while (h.NumberOfLoops > 0) h.RemoveLoopAt(0);
            for (int i = 0; i < loops.Count; i++)
            {
                var bc = new DoubleCollection(); foreach (Point2d q in loops[i]) bc.Add(0);
                if (loops[i].Count > 0 && loops[i][0] != loops[i][loops[i].Count - 1]) { loops[i].Add(loops[i][0]); bc.Add(0); }
                h.AppendLoop(HatchLoopTypes.External | HatchLoopTypes.Polyline, loops[i], bc);
            }
            h.EvaluateHatch(true);
        }
    }
}
