using System;
using System.IO;
using System.Text;
using System.Reflection;
using System.Collections.Generic;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Events;

namespace RB_Live
{
    // stays loaded in the user's Revit; on idle picks up %LOCALAPPDATA%\rvjob\live.txt, loads the worker dll named in it
    // from bytes (so it can be rebuilt between jobs) and runs RB.App.LiveRun on the active document
    public class LiveApp : IExternalApplication
    {
        static string JobDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "rvjob");
        bool busy = false;

        public Result OnStartup(UIControlledApplication a) { a.Idling += OnIdling; return Result.Succeeded; }
        public Result OnShutdown(UIControlledApplication a) { return Result.Succeeded; }

        void OnIdling(object sender, IdlingEventArgs e)
        {
            if (busy) return;
            string job = Path.Combine(JobDir, "live.txt");
            if (!File.Exists(job)) return;
            busy = true;
            string res;
            try
            {
                Dictionary<string, string> J = new Dictionary<string, string>();
                foreach (string ln in File.ReadAllLines(job, Encoding.UTF8))
                {
                    int i = ln.IndexOf('=');
                    if (i > 0) J[ln.Substring(0, i).Trim()] = ln.Substring(i + 1).Trim();
                }
                File.Delete(job);
                Assembly asm = Assembly.Load(File.ReadAllBytes(J["dll"]));
                MethodInfo m = asm.GetType("RB.App").GetMethod("LiveRun", BindingFlags.Public | BindingFlags.Static);
                res = (string)m.Invoke(null, new object[] { (UIApplication)sender, J });
            }
            catch (Exception ex) { res = "LIVE ERROR " + ex; }
            File.WriteAllText(Path.Combine(JobDir, "livedone.txt"), res ?? "", Encoding.UTF8);
            busy = false;
        }
    }
}
