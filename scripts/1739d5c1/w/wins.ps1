param([int]$ProcId, [string]$Out)
# list and capture the top-level windows of one process (our own acad only)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class W {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  public struct RECT { public int L, T, R, B; }
  public static List<IntPtr> Top(uint pid) { var l = new List<IntPtr>(); EnumWindows((h, x) => { uint p; GetWindowThreadProcessId(h, out p); if (p == pid && IsWindowVisible(h)) l.Add(h); return true; }, IntPtr.Zero); return l; }
  public static List<string> Kids(IntPtr w) { var l = new List<string>(); EnumChildWindows(w, (h, x) => { var s = new StringBuilder(512); GetWindowText(h, s, 512); var c = new StringBuilder(128); GetClassName(h, c, 128); if (s.Length > 0 && IsWindowVisible(h)) l.Add(c + ": " + s); return true; }, IntPtr.Zero); return l; }
}
"@
$i = 0
foreach ($h in [W]::Top($ProcId)) {
  $t = New-Object Text.StringBuilder 512; [void][W]::GetWindowText($h, $t, 512)
  $c = New-Object Text.StringBuilder 128; [void][W]::GetClassName($h, $c, 128)
  $r = New-Object W+RECT; [void][W]::GetWindowRect($h, [ref]$r)
  "[$i] $c '$t' $($r.L),$($r.T) $($r.R - $r.L)x$($r.B - $r.T)"
  [W]::Kids($h) | Select-Object -First 25 | ForEach-Object { "     $_" }
  $w = $r.R - $r.L; $hh = $r.B - $r.T
  if ($Out -and $w -gt 50 -and $hh -gt 50) {
    $bmp = New-Object Drawing.Bitmap $w, $hh; $g = [Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
    [void][W]::PrintWindow($h, $dc, 2); $g.ReleaseHdc($dc); $bmp.Save("$Out$i.png"); $g.Dispose(); $bmp.Dispose()
  }
  $i++
}
