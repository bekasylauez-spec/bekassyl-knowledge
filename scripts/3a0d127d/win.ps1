param([string]$Action = 'list', [string]$Text, [string]$Shot)
if (-not ("WinX" -as [type])) {
Add-Type -ReferencedAssemblies System.Drawing,System.Windows.Forms @'
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Drawing;
public class WinX {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
  public struct RECT { public int L, T, R, B; }
  public static string T(IntPtr h){ var s=new StringBuilder(512); GetWindowText(h,s,512); return s.ToString(); }
  public static string C(IntPtr h){ var s=new StringBuilder(256); GetClassName(h,s,256); return s.ToString(); }
  public static List<IntPtr> Tops(uint pid){ var r=new List<IntPtr>(); EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)) r.Add(h); return true; }, IntPtr.Zero); return r; }
  public static List<IntPtr> Kids(IntPtr w){ var r=new List<IntPtr>(); EnumChildWindows(w,(h,l)=>{ r.Add(h); return true; }, IntPtr.Zero); return r; }
  public static void Click(int x,int y){ SetCursorPos(x,y); System.Threading.Thread.Sleep(80); mouse_event(2,0,0,0,0); mouse_event(4,0,0,0,0); }
  public static void Shot(string f){ var b=System.Windows.Forms.SystemInformation.VirtualScreen; using(var bm=new Bitmap(b.Width,b.Height)){ using(var g=Graphics.FromImage(bm)) g.CopyFromScreen(b.Left,b.Top,0,0,bm.Size); bm.Save(f); } }
}
'@
}
$p = Get-Process Revit -ErrorAction SilentlyContinue | Select -First 1
if (-not $p) { "no revit"; return }
$out = @()
foreach ($w in [WinX]::Tops([uint32]$p.Id)) {
  $r = New-Object WinX+RECT; [WinX]::GetWindowRect($w, [ref]$r) | Out-Null
  $out += "TOP [$([WinX]::C($w))] '$([WinX]::T($w))' ($($r.L),$($r.T),$($r.R),$($r.B))"
  foreach ($k in [WinX]::Kids($w)) { $t = [WinX]::T($k); if ($t -and [WinX]::IsWindowVisible($k)) { $kr = New-Object WinX+RECT; [WinX]::GetWindowRect($k, [ref]$kr) | Out-Null
    $out += "   [$([WinX]::C($k))] '$t' ($($kr.L),$($kr.T),$($kr.R),$($kr.B))"
    if ($Action -eq 'click' -and $t -eq $Text) { [WinX]::SetForegroundWindow($w) | Out-Null; Start-Sleep -Milliseconds 200; [WinX]::Click([int](($kr.L+$kr.R)/2), [int](($kr.T+$kr.B)/2)); $out += "   CLICKED" } } }
}
if ($Shot) { [WinX]::Shot($Shot); $out += "shot $Shot" }
$out
