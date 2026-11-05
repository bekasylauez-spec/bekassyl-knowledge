param([int]$Pid0, [int]$Secs = 240)
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class W { public delegate bool EP(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(EP f, IntPtr l);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
[DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }
"@
$t0 = Get-Date
while (((Get-Date) - $t0).TotalSeconds -lt $Secs) {
  [W]::EnumWindows({ param($h, $l) $p = 0; [void][W]::GetWindowThreadProcessId($h, [ref]$p)
    if ($p -eq $Pid0 -and [W]::IsWindowVisible($h)) { $sb = New-Object Text.StringBuilder 64; [void][W]::GetClassName($h, $sb, 64)
      if ($sb.ToString() -eq '#32770') { [void][W]::PostMessage($h, 0x0111, [IntPtr]1, [IntPtr]::Zero) } }
    return $true }, [IntPtr]::Zero) | Out-Null
  if (Test-Path "$env:TEMP\acadjob_ab\listening.txt") { Start-Sleep 3 }
  Start-Sleep 1
}
