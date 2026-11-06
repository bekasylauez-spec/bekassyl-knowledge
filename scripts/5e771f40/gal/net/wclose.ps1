param([int]$AcadPid, [string]$DocName)
# close one drawing in a given AutoCAD (window level): WM_CLOSE to its MDI child, answer «Да» to the save prompt
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class W {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EP f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  public static string T(IntPtr h){var s=new StringBuilder(512);GetWindowText(h,s,512);return s.ToString();}
  public static string C(IntPtr h){var s=new StringBuilder(256);GetClassName(h,s,256);return s.ToString();}
  public static List<IntPtr> Kids(IntPtr p){var r=new List<IntPtr>();EnumChildWindows(p,(h,l)=>{r.Add(h);return true;},IntPtr.Zero);return r;}
  public static List<IntPtr> Tops(uint pid){var r=new List<IntPtr>();EnumWindows((h,l)=>{uint q;GetWindowThreadProcessId(h,out q);if(q==pid)r.Add(h);return true;},IntPtr.Zero);return r;}
}
"@
$main = (Get-Process -Id $AcadPid).MainWindowHandle
$mdi = [W]::Kids($main) | Where-Object { [W]::T($_) -like "*$DocName*" -and [W]::C($_) -like "Afx:*" } | Select-Object -First 1
if (-not $mdi) { "mdi child not found"; exit 1 }
[W]::PostMessage($mdi, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "WM_CLOSE sent"
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Milliseconds 700
  foreach ($t in [W]::Tops([uint32]$AcadPid)) {
    if ([W]::C($t) -eq "#32770") {
      foreach ($b in [W]::Kids($t)) { if ([W]::C($b) -eq "Button" -and [W]::T($b) -match "^&?Да") { [W]::PostMessage($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "clicked Да" } }
    }
  }
  if (-not ([W]::Kids($main) | Where-Object { [W]::T($_) -like "*$DocName*" })) { "closed"; exit 0 }
}
"still open"; exit 2
