# kill my AutoCAD instance (pid.txt), reopen nos3.dwg with the listener; answer the "recover" dialogs
$g = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e771f40-144d-493e-a1c3-679c0085cfb9\scratchpad\gal"
$jd = "$env:TEMP\acadjob_m3"
$old = [int](Get-Content "$g\net\pid.txt" -Raw).Trim()
try { Stop-Process -Id $old -Force -ErrorAction Stop; "killed $old" } catch { "not running $old" }
Start-Sleep 3
foreach ($f in @("$jd\listening.txt", "$jd\job.txt", "$jd\done.txt", "$g\w\nos3.dwl", "$g\w\nos3.dwl2")) { if (Test-Path $f) { [IO.File]::Delete($f) } }
$cl = "`"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe`" `"$g\w\nos3.dwg`" /nologo /b `"$g\net\boot.scr`""
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cl }
$p = Get-Process -Id $r.ProcessId
$p.Id | Set-Content "$g\net\pid.txt"
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type @"
using System;using System.Runtime.InteropServices;
public class UR{[DllImport("user32.dll")]public static extern IntPtr PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);}
"@
$root = [Windows.Automation.AutomationElement]::RootElement
$pc = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty, $p.Id)
for ($i = 0; $i -lt 150; $i++) {
  Start-Sleep 2
  if (Test-Path "$jd\listening.txt") { "listening pid $($p.Id)"; exit 0 }
  $wc = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ControlTypeProperty, [Windows.Automation.ControlType]::Window)
  $dlgs = @(); foreach ($top in $root.FindAll([Windows.Automation.TreeScope]::Children, $pc)) { foreach ($d in $top.FindAll([Windows.Automation.TreeScope]::Descendants, $wc)) { if ($d.Current.Name -match 'поврежд|Восстан') { $dlgs += $d } } }
  foreach ($w in $dlgs) {
    foreach ($nm in @("Восстановить", "Закрыть")) {
      $c = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::NameProperty, $nm)
      $b = $w.FindFirst([Windows.Automation.TreeScope]::Descendants, $c)
      if ($b -and $b.Current.NativeWindowHandle) {
        $h = [IntPtr]$b.Current.NativeWindowHandle
        [UR]::PostMessage($h, 0x0201, [IntPtr]1, [IntPtr]0x000A000A) | Out-Null
        [UR]::PostMessage($h, 0x0202, [IntPtr]0, [IntPtr]0x000A000A) | Out-Null
        "clicked $nm"
      }
    }
  }
}
"relaunch timeout"
exit 1
