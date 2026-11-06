Add-Type @"
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Runtime.InteropServices.ComTypes;
public class Rot {
  [DllImport("ole32.dll")] static extern int GetRunningObjectTable(int r, out IRunningObjectTable p);
  [DllImport("ole32.dll")] static extern int CreateBindCtx(int r, out IBindCtx p);
  public static List<object[]> All() { var res=new List<object[]>(); IRunningObjectTable rot; GetRunningObjectTable(0,out rot); IEnumMoniker em; rot.EnumRunning(out em);
    IMoniker[] m=new IMoniker[1]; IntPtr f=IntPtr.Zero; IBindCtx bc; CreateBindCtx(0,out bc);
    while(em.Next(1,m,f)==0){ string n; m[0].GetDisplayName(bc,null,out n); object o=null; try{ rot.GetObject(m[0],out o);}catch{} res.Add(new object[]{n,o}); }
    return res; } }
"@
