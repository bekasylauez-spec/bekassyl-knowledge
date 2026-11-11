param([Parameter(Mandatory)]$Script, [Parameter(Mandatory)]$Out, $Timeout = 180)
# run a script that queues work on Revit's Idling, bring Revit forward until the result file appears
$root = "D:\Бекасыл КЖ КМ\Revit_оформление\_авто"
if (Test-Path $Out) { Remove-Item $Out }
& "$root\run.ps1" -Files $Script -TimeoutSec 60 | Out-Null
if (-not ("WIdle" -as [type])) { Add-Type 'using System; using System.Runtime.InteropServices; public class WIdle { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); }' }
$p = Get-Process Revit | Select -First 1; [WIdle]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
for ($i = 0; $i -lt $Timeout * 2; $i++) { [WIdle]::SetCursorPos(700 + ($i % 5) * 20, 500) | Out-Null; Start-Sleep -Milliseconds 500; if (Test-Path $Out) { break } }
Start-Sleep -Milliseconds 300
if (Test-Path $Out) { Get-Content $Out -Encoding UTF8 } else { "no result in $Timeout s" }