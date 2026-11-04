param([string]$Ops, [string]$Target, [int]$Wait = 400)
# compile rn.cs (Multicad/SPDS) and run RN.Cmds.Apply in MY AutoCAD instance via the SVLISTEN listener
$net = Split-Path $MyInvocation.MyCommand.Path
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$mc = (Get-ChildItem "C:\Program Files\CSoft" -Directory | ForEach-Object { Join-Path $_.FullName "mg142x64" } | Where-Object { Test-Path (Join-Path $_ "mapimgd.dll") } | Select-Object -First 1)
$dll = Join-Path $net ("rns_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /r:"$mc\mapimgd.dll" /r:"$mc\mapibasetypes.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\rn.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
Copy-Item $Ops "$env:TEMP\lk_ops.json" -Force
$jd = "$env:TEMP\acadjob_sv"; Remove-Item "$jd\done.txt" -ErrorAction SilentlyContinue
[IO.File]::WriteAllText("$jd\job.txt", "$dll|RN.Cmds|Apply|$Target", [Text.Encoding]::UTF8)
for ($i = 0; $i -lt $Wait -and -not (Test-Path "$jd\done.txt"); $i++) { Start-Sleep 1 }
if (Test-Path "$jd\done.txt") { Get-Content "$jd\done.txt" -Encoding UTF8 | Select-Object -First 3 } else { "timeout" }
Get-Content "$env:TEMP\lk_log.txt" -Encoding UTF8 | Select-Object -Last 80
