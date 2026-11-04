Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
public static class Rot {
    [DllImport("ole32.dll")] static extern int GetRunningObjectTable(int r, out IRunningObjectTable rot);
    [DllImport("ole32.dll")] static extern int CreateBindCtx(int r, out IBindCtx ctx);
    public static List<string> Names() {
        var res = new List<string>();
        IRunningObjectTable rot; GetRunningObjectTable(0, out rot);
        IEnumMoniker em; rot.EnumRunning(out em);
        var ms = new IMoniker[1];
        while (em.Next(1, ms, IntPtr.Zero) == 0) {
            IBindCtx ctx; CreateBindCtx(0, out ctx);
            string n; ms[0].GetDisplayName(ctx, null, out n); res.Add(n);
        }
        return res;
    }
    public static List<object> All(string name) {
        var res = new List<object>();
        IRunningObjectTable rot; GetRunningObjectTable(0, out rot);
        IEnumMoniker em; rot.EnumRunning(out em);
        var ms = new IMoniker[1];
        while (em.Next(1, ms, IntPtr.Zero) == 0) {
            IBindCtx ctx; CreateBindCtx(0, out ctx);
            string n; ms[0].GetDisplayName(ctx, null, out n);
            if (n == name) { object o; rot.GetObject(ms[0], out o); res.Add(o); }
        }
        return res;
    }
    public static object Get(string name) {
        IRunningObjectTable rot; GetRunningObjectTable(0, out rot);
        IEnumMoniker em; rot.EnumRunning(out em);
        var ms = new IMoniker[1];
        while (em.Next(1, ms, IntPtr.Zero) == 0) {
            IBindCtx ctx; CreateBindCtx(0, out ctx);
            string n; ms[0].GetDisplayName(ctx, null, out n);
            if (n == name) { object o; rot.GetObject(ms[0], out o); return o; }
        }
        return null;
    }
}
"@
$k=0
foreach($a in [Rot]::All("!{8B4929F8-076F-4AEC-AFEE-8928747B7AE3}")){ $k++; try { $n=$a.Documents.Count; for($i=0;$i -lt $n;$i++){ "$k : " + $a.Documents.Item($i).FullName } } catch { "$k err $_" } }
