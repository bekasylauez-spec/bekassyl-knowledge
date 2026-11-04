param([string]$Job, [int]$Wait = 300, [switch]$Backup)
# compile the worker (all rv\*.cs) into a fresh dll and run one live job in the user's open Revit via the RBLive shim
$w = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\7e55ac1d-056c-477c-b1ef-1657f3036e17\scratchpad\rv"
$r = "D:\РАБОЧКА\От Рас груп\ЖК Қарасу село Абай\Revit"
$rt = "C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.26"; $rv = "C:\Program Files\Autodesk\Revit 2025"
$refs = @("System.Private.CoreLib.dll", "System.Runtime.dll", "System.Collections.dll", "System.Linq.dll", "System.Text.Encoding.Extensions.dll", "netstandard.dll") | ForEach-Object { "/r:$rt\$_" }
$srcs = Get-ChildItem $w -Filter *.cs | Where-Object { $_.Name -ne 't.cs' } | ForEach-Object FullName
$dll = "$w\live\w_" + (Get-Date -Format "HHmmss") + ".dll"
& C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /noconfig /nostdlib /t:library /utf8output /codepage:65001 /out:"$dll" $refs "/r:$rv\RevitAPI.dll" "/r:$rv\RevitAPIUI.dll" $srcs | Select-String "error"
if ($LASTEXITCODE -ne 0) { "compile failed"; exit 1 }
if ($Backup) { Copy-Item "$r\КМ Навес 1 Рампа.rvt" ("$r\Мусор\КМ Навес 1 Рампа (до правки " + (Get-Date -Format "HH-mm") + ").rvt") -Force }
$jd = "$env:LOCALAPPDATA\rvjob"; Remove-Item "$jd\livedone.txt" -ErrorAction SilentlyContinue
$Job = $Job.Replace("{r}", $r)
[IO.File]::WriteAllText("$jd\live.txt", "dll=$dll`n" + $Job.Replace(";", "`n") + "`n", (New-Object Text.UTF8Encoding $false))
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WMN { [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }
"@
$h = (Get-Process Revit).MainWindowHandle
$t = 0; while ($t -lt $Wait -and -not (Test-Path "$jd\livedone.txt")) { [WMN]::PostMessage($h, 0x0200, [IntPtr]::Zero, [IntPtr](300 + $t)) | Out-Null; Start-Sleep 2; $t += 2 }
if (Test-Path "$jd\livedone.txt") { Get-Content "$jd\livedone.txt" -Encoding UTF8 } else { "timeout" }
if (Test-Path "$r\КМ Навес 1 Рампа.0001.rvt") { Remove-Item "$r\КМ Навес 1 Рампа.0001.rvt" }
