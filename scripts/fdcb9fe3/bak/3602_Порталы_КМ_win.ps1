# UI helpers for Revit dialogs: . .\win.ps1 ; Get-Wins <pid> ; Click-Text <pid> "Загрузить один раз" ; Shot out.png
Add-Type -ReferencedAssemblies System.Drawing,System.Windows.Forms @"
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public static class W {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static string Txt(IntPtr h){ var s=new StringBuilder(512); GetWindowText(h,s,512); return s.ToString(); }
  public static string Cls(IntPtr h){ var s=new StringBuilder(256); GetClassName(h,s,256); return s.ToString(); }
  public static List<IntPtr> Tops(uint pid){ var r=new List<IntPtr>(); EnumWindows((h,l)=>{uint p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)) r.Add(h); return true;}, IntPtr.Zero); return r; }
  public static List<IntPtr> Kids(IntPtr w){ var r=new List<IntPtr>(); EnumChildWindows(w,(h,l)=>{r.Add(h); return true;}, IntPtr.Zero); return r; }
  public static void Click(int x,int y){ SetCursorPos(x,y); System.Threading.Thread.Sleep(80); mouse_event(2,0,0,0,0); System.Threading.Thread.Sleep(60); mouse_event(4,0,0,0,0); }
}
"@
function Get-Wins($procId) { foreach ($h in [W]::Tops($procId)) { $r = New-Object W+RECT; [W]::GetWindowRect($h, [ref]$r) | Out-Null; [pscustomobject]@{ H = $h; Title = [W]::Txt($h); Class = [W]::Cls($h); Rect = "$($r.L),$($r.T),$($r.R),$($r.B)" } } }
function Get-Kids($h) { foreach ($k in [W]::Kids($h)) { $r = New-Object W+RECT; [W]::GetWindowRect($k, [ref]$r) | Out-Null; [pscustomobject]@{ H = $k; Text = [W]::Txt($k); Class = [W]::Cls($k); Vis = [W]::IsWindowVisible($k); Rect = "$($r.L),$($r.T),$($r.R),$($r.B)" } } }
function Click-Text($procId, $text) {
  foreach ($t in [W]::Tops($procId)) { foreach ($k in [W]::Kids($t)) { if ([W]::Txt($k) -like $text -and [W]::IsWindowVisible($k)) {
    $r = New-Object W+RECT; [W]::GetWindowRect($k, [ref]$r) | Out-Null; [W]::SetForegroundWindow($t) | Out-Null; Start-Sleep -Milliseconds 200
    [W]::Click([int](($r.L + $r.R) / 2), [int](($r.T + $r.B) / 2)); return "clicked '$([W]::Txt($k))' in '$([W]::Txt($t))'" } } }
  return "not found: $text" }
function Shot($out, $x0 = 0, $y0 = 0, $w = 0, $h = 0) {
  Add-Type -AssemblyName System.Windows.Forms, System.Drawing
  $b = [Windows.Forms.Screen]::PrimaryScreen.Bounds; if ($w -eq 0) { $x0 = $b.X; $y0 = $b.Y; $w = $b.Width; $h = $b.Height }
  $bmp = New-Object Drawing.Bitmap $w, $h; $g = [Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($x0, $y0, 0, 0, $bmp.Size)
  $bmp.Save($out, [Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); $out }
