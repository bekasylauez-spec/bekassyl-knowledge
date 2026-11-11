# Run a C# file (absolute path) in Revit through runner_stub; with -Log waits for an Idling job's log file (Revit kept in front).
param([Parameter(Mandatory)][string]$File, [string]$Log, [int]$Timeout = 300, [string]$Lib)
$auto = "D:\Бекасыл КЖ КМ\Revit_оформление\_авто"
. "$auto\revit.ps1"
if ($Log -and (Test-Path $Log)) { Remove-Item $Log }
# -Lib: a helper file appended after the script (the script closes its last method, the lib leaves its last one open)
if ($Lib) { $job = Join-Path $env:TEMP ("cs_job_" + [IO.Path]::GetFileName($File)); [IO.File]::WriteAllText($job, [IO.File]::ReadAllText($File, [Text.Encoding]::UTF8) + "`n" + [IO.File]::ReadAllText($Lib, [Text.Encoding]::UTF8), (New-Object Text.UTF8Encoding($false))); $File = $job }
$stub = [IO.File]::ReadAllText("$auto\runner_stub.cs", [Text.Encoding]::UTF8).Replace("__FILE__", $File)
$r = Invoke-RevitCode -Code $stub -TimeoutSec 120
if (-not $r.result.success) { return ($r | ConvertTo-Json -Depth 4) }
"run: " + $r.result.result
if (-not $Log) { return }
if (-not ("WIdle" -as [type])) { Add-Type 'using System; using System.Runtime.InteropServices; public class WIdle { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); }' }
$p = Get-Process Revit | ? { $_.MainWindowHandle -ne 0 } | Select -First 1; [WIdle]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
for ($i = 0; $i -lt $Timeout * 2; $i++) { [WIdle]::SetCursorPos(900 + ($i % 5) * 20, 600) | Out-Null; Start-Sleep -Milliseconds 500; if (Test-Path $Log) { break } }
Start-Sleep -Milliseconds 300
if (Test-Path $Log) { Get-Content $Log -Encoding UTF8 } else { "no log in $Timeout s" }
