using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Reflection;
using System.Collections.Generic;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Multicad;
using Multicad.DatabaseServices;
using Multicad.Symbols;

namespace BkSpds
{
    public class Probe
    {
        static string Val(object v, int depth)
        {
            if (v == null) return "null";
            if (v is string || v.GetType().IsPrimitive || v is Enum) return v.ToString();
            var t = v.GetType();
            if (depth > 0 && t.Namespace != null && t.Namespace.StartsWith("Multicad") && !(v is System.Collections.IEnumerable))
            {
                var parts = new List<string>();
                foreach (var p in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
                {
                    if (p.GetIndexParameters().Length > 0) continue;
                    object pv; try { pv = p.GetValue(v, null); } catch { continue; }
                    parts.Add(p.Name + "=" + Val(pv, depth - 1));
                }
                return t.Name + "{" + string.Join("; ", parts) + "}";
            }
            if (v is System.Collections.IEnumerable)
            {
                var items = new List<string>(); int n = 0;
                foreach (var it in (System.Collections.IEnumerable)v) { if (n++ > 8) { items.Add("..."); break; } items.Add(Val(it, depth - 1)); }
                return "[" + string.Join(", ", items) + "]";
            }
            return v.ToString();
        }

        static void Dump(StringBuilder sb, McObject o)
        {
            foreach (var p in o.GetType().GetProperties(BindingFlags.Public | BindingFlags.Instance))
            {
                if (p.GetIndexParameters().Length > 0) continue;
                if (p.DeclaringType == typeof(McObject)) continue;
                object v; try { v = p.GetValue(o, null); } catch (System.Exception ex) { v = "ERR " + (ex.InnerException ?? ex).Message; }
                sb.AppendLine("    " + p.DeclaringType.Name + "." + p.Name + " = " + Val(v, 2));
            }
            try
            {
                var me = o as McEntity;
                if (me != null)
                {
                    var oid = new ObjectId(me.ID.ToOldIdPtr());
                    using (var tr = oid.Database.TransactionManager.StartTransaction())
                    {
                        var e = tr.GetObject(oid, OpenMode.ForRead) as Entity;
                        if (e != null) sb.AppendLine("    [acad] " + e.GetType().Name + " layer=" + e.Layer + " ext=" + e.GeometricExtents.MinPoint + " .. " + e.GeometricExtents.MaxPoint + " handle=" + e.Handle);
                        tr.Commit();
                    }
                }
            }
            catch (System.Exception ex) { sb.AppendLine("    [acad] err " + ex.Message); }
        }

        [CommandMethod("BKPROBE", CommandFlags.Session)]
        public void Run()
        {
            var sb = new StringBuilder();
            var want = (Environment.GetEnvironmentVariable("BKTYPES") ?? "McNotePosition,McNoteKnot,McFormat,McSectionVS,McAxisEntity").Split(',');
            var seen = new Dictionary<string, int>();
            try
            {
                var f = new ObjectFilter();
                f.AllObjects = true;
                f.SetCurrentDocument();
                var ids = McObjectManager.SelectObjects(f);
                foreach (var id in ids)
                {
                    var o = id.GetObject();
                    if (o == null) continue;
                    var tn = o.GetType().Name;
                    if (!want.Contains(tn)) continue;
                    int c; seen.TryGetValue(tn, out c); seen[tn] = c + 1;
                    if (c >= 2) continue;
                    sb.AppendLine("## " + tn);
                    var npx = o as McNotePosition;
                    if (npx != null)
                    {
                        sb.AppendLine("  origin " + npx.Origin + " angle " + npx.Angle + " leaderCount " + npx.Leader.Count);
                        foreach (var seg in npx.Leader.Childs) sb.AppendLine("  seg " + Val(seg, 2));
                    }
                    var me2 = o as McEntity;
                    if (me2 != null) sb.AppendLine("  db: layer=" + me2.DbEntity.Layer + " ltname=" + me2.DbEntity.LineTypeName + " lt=" + me2.DbEntity.LineType + " ltscale=" + me2.DbEntity.LineTypeScale + " scale=" + me2.DbEntity.Scale + " dscale=" + me2.DbEntity.DScale);
                    if (Environment.GetEnvironmentVariable("BKSHORT") == null) Dump(sb, o);
                }
            }
            catch (System.Exception ex) { sb.AppendLine("ERR " + ex); }
            File.WriteAllText(Environment.GetEnvironmentVariable("BKOUT") ?? @"C:\Temp\bkprobe.txt", sb.ToString(), Encoding.UTF8);
        }
    }
}
