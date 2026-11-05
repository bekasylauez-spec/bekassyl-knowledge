using System;
using System.IO;
using System.Reflection;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;

[assembly: CommandClass(typeof(PLListen.Cmds))]
namespace PLListen
{
    // Polls %TEMP%\acadjob_pl on Idle. job.txt = "dll|Namespace.Type|Method|target dwg name".
    // Activates the target document for the job, then returns to the document the user had active.
    public class Cmds
    {
        static string dir = Path.Combine(Environment.GetEnvironmentVariable("TEMP"), "acadjob_pl");
        static bool on, busy;
        [CommandMethod("PLLISTEN", CommandFlags.Session)]
        public static void Start()
        {
            Directory.CreateDirectory(dir);
            if (!on) { Application.Idle += OnIdle; on = true; }
            File.WriteAllText(Path.Combine(dir, "listening.txt"), "on");
        }
        [CommandMethod("PLSTOP", CommandFlags.Session)]
        public static void Stop()
        {
            if (on) { Application.Idle -= OnIdle; on = false; }
            File.WriteAllText(Path.Combine(dir, "listening.txt"), "off");
        }
        static void OnIdle(object s, EventArgs e)
        {
            if (busy) return;
            var job = Path.Combine(dir, "job.txt");
            if (!File.Exists(job)) return;
            busy = true;
            string res;
            Document prev = Application.DocumentManager.MdiActiveDocument;
            try
            {
                var parts = File.ReadAllText(job, System.Text.Encoding.UTF8).Trim().Split('|');
                File.Delete(job);
                Document doc = null;
                foreach (Document d in Application.DocumentManager)
                    if (string.Equals(Path.GetFileName(d.Name), parts[3], StringComparison.OrdinalIgnoreCase)) doc = d;
                if (doc == null) throw new System.Exception("target doc not open: " + parts[3]);
                if (Application.DocumentManager.MdiActiveDocument != doc) Application.DocumentManager.MdiActiveDocument = doc;
                var asm = Assembly.LoadFrom(parts[0]);
                var m = asm.GetType(parts[1]).GetMethod(parts[2], BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static);
                using (doc.LockDocument()) { m.Invoke(null, null); }
                res = "OK " + doc.Name;
            }
            catch (System.Exception ex) { res = "ERR " + (ex.InnerException ?? ex).ToString(); }
            try { if (prev != null && Application.DocumentManager.MdiActiveDocument != prev) Application.DocumentManager.MdiActiveDocument = prev; } catch { }
            File.WriteAllText(Path.Combine(dir, "done.txt"), res, System.Text.Encoding.UTF8);
            busy = false;
        }
    }
}
