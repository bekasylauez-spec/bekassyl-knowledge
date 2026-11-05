param([string]$Ops, [int]$Wait = 900, [string]$Doc = "2.Схема каркас для клауда (ригели).dwg")
$net = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\2ce8f87a-4a49-4808-8cfa-d9a5f578e5ce\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$mc = (Get-ChildItem "C:\Program Files\CSoft" -Directory | ForEach-Object { Join-Path $_.FullName "mg142x64" } | Where-Object { Test-Path (Join-Path $_ "mapimgd.dll") } | Select-Object -First 1)
$src = Get-Item "$net\rz.cs"; $stamp = "$net\rz_last.txt"
$dll = if ((Test-Path $stamp) -and ((Get-Content $stamp -Raw).Split('|')[0] -eq $src.LastWriteTime.Ticks)) { (Get-Content $stamp -Raw).Split('|')[1].Trim() } else { $null }
if (-not $dll) {
  $dll = Join-Path $net ("rgj_" + (Get-Date -Format HHmmssfff) + ".dll")
  & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /r:"$mc\mapimgd.dll" /r:"$mc\mapibasetypes.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\rz.cs" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "compile failed" }
  Set-Content $stamp ("" + $src.LastWriteTime.Ticks + "|" + $dll)
}
Copy-Item $Ops "$env:TEMP\rg_ops.json" -Force
$jd = "$env:TEMP\acadjob_rg"; Remove-Item "$jd\done.txt" -ErrorAction SilentlyContinue
[IO.File]::WriteAllText("$jd\job.txt", "$dll|RG.Cmds|Apply|$Doc", [Text.Encoding]::UTF8)
for ($i = 0; $i -lt $Wait -and -not (Test-Path "$jd\done.txt"); $i++) { Start-Sleep 1 }
if (Test-Path "$jd\done.txt") { Get-Content "$jd\done.txt" -Encoding UTF8 | Select-Object -First 3 } else { "timeout" }
Get-Content "$env:TEMP\rg_log.txt" -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -Last 25
