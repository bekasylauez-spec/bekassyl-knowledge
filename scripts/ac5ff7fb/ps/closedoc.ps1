param([int]$ProcId, [string]$Name)
Add-Type @"
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public class W {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  public static string T(IntPtr h){var s=new StringBuilder(512);GetWindowText(h,s,512);return s.ToString();}
  public static string C(IntPtr h){var s=new StringBuilder(256);GetClassName(h,s,256);return s.ToString();}
  public static List<IntPtr> Kids(IntPtr p){var r=new List<IntPtr>();EnumChildWindows(p,(h,l)=>{r.Add(h);return true;},IntPtr.Zero);return r;}
  public static List<IntPtr> Tops(uint pid){var r=new List<IntPtr>();EnumWindows((h,l)=>{uint q;GetWindowThreadProcessId(h,out q);if(q==pid)r.Add(h);return true;},IntPtr.Zero);return r;}
}
"@
$da = [string][char]0x0414 + [char]0x0430
$p = Get-Process -Id $ProcId
$doc = $null
foreach ($h in [W]::Kids($p.MainWindowHandle)) { $t = [W]::T($h); if ($t -like "*$Name*" -and [W]::C($h) -like "Afx:*") { $doc = $h; break } }
if (-not $doc) { foreach ($h in [W]::Kids($p.MainWindowHandle)) { $t=[W]::T($h); if ($t -like "*$Name*") { "cand " + [W]::C($h) + " | " + $t } }; "no doc window"; exit 1 }
"doc window " + [W]::C($doc) + " | " + [W]::T($doc)
[W]::PostMessage($doc, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
for ($i=0; $i -lt 30; $i++) {
  Start-Sleep -Milliseconds 500
  foreach ($top in [W]::Tops([uint32]$ProcId)) {
    if (-not [W]::IsWindowVisible($top)) { continue }
    foreach ($b in [W]::Kids($top)) { $bt = [W]::T($b); if ([W]::C($b) -eq "Button" -and ($bt -eq ("&"+$da) -or $bt -eq $da -or $bt -eq "&Yes")) { "click " + $bt + " in " + [W]::T($top); [W]::PostMessage($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; $i = 99; break } }
    if ($i -ge 99) { break }
  }
}
Start-Sleep 3
$left = [W]::Kids($p.MainWindowHandle) | Where-Object { ([W]::T($_)) -like "*$Name*" }
"still open: " + ($left | Measure-Object).Count
