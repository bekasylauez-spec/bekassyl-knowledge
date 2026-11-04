using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(V4Lay.Cmds))]
namespace V4Lay
{
    // layout tabs from %LAY_JSON%: {"del":[names], "ren":[[old,new],..]} — deletes first, then renames in order
    public class Cmds
    {
        [CommandMethod("V4LAY")]
        public static void Run()
        {
            string jf = Environment.GetEnvironmentVariable("LAY_JSON");
            var log = new StringBuilder();
            try
            {
                var m = (Dictionary<string, object>)new JavaScriptSerializer().DeserializeObject(File.ReadAllText(jf, Encoding.UTF8));
                var lm = LayoutManager.Current;
                lm.CurrentLayout = "Model";
                if (m.ContainsKey("del"))
                    foreach (var n in (IList)m["del"])
                    {
                        try { lm.DeleteLayout(n.ToString()); log.AppendLine("deleted " + n); }
                        catch (System.Exception ex) { log.AppendLine("del ERR " + n + ": " + ex.Message); }
                    }
                if (m.ContainsKey("ren"))
                    foreach (var o in (IList)m["ren"])
                    {
                        var a = (IList)o;
                        try { lm.RenameLayout(a[0].ToString(), a[1].ToString()); log.AppendLine("renamed " + a[0] + " -> " + a[1]); }
                        catch (System.Exception ex) { log.AppendLine("ren ERR " + a[0] + ": " + ex.Message); }
                    }
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(jf + ".log", log.ToString(), Encoding.UTF8);
        }
    }
}
