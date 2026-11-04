param([string]$In, [string]$Out, [string]$Tag, [double[]]$Win, [double]$Ox, [double]$Oy, [double]$K, [double]$W, [double]$H, [double]$KNew, [string]$No, [string]$Name)
# One Tekla sheet -> one Цех-style sheet: pass 1 (dims/texts at the new scale), pass 2 (SPDS frame/stamp/marks/axes)
$n = $PSScriptRoot; $s = Split-Path $n; $l = ($s -replace '\\', '/')
$acc = "C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"
function Acc([string]$dwg, [string]$lsp, [string]$cmd) {
  "SECURELOAD`n0`n(load `"$l/$lsp`")`n$cmd`n" | Set-Content "$s\_$cmd.scr" -Encoding ASCII -NoNewline
  $p = Start-Process $acc -ArgumentList "/i `"$dwg`" /s `"$s\_$cmd.scr`" /l ru-RU" -PassThru -NoNewWindow -RedirectStandardOutput "$s\_$cmd.log"
  if (-not $p.WaitForExit(400000)) { $p.Kill(); "$cmd killed" }
}
$env:GX0 = "$($Win[0])"; $env:GX1 = "$($Win[1])"; $env:GY0 = "$($Win[2])"; $env:GY1 = "$($Win[3])"
# pass 1
$env:DMPOUT = "$s\a_geo$Tag.txt"; Acc $In "geo.lsp" "GEO"
powershell -NoProfile -Command "Add-Type -Path '$s\Restyle.cs'; [Restyle]::Run('$s\a_geo$Tag.txt','$s\a_ops$Tag.txt',$KNew,'x')"
$p1 = "$s\a_p1_$Tag.dwg"; Remove-Item $p1 -ErrorAction SilentlyContinue
$env:APK = "$KNew"; $env:APOPS = "$s\a_ops$Tag.txt"; $env:APOUT = $p1
Acc $In "apply.lsp" "APL"
if (-not (Test-Path $p1)) { "pass 1 failed"; return }
# pass 2
$env:DMPOUT = "$s\a_geob$Tag.txt"; Acc $p1 "geo.lsp" "GEO"
powershell -NoProfile -Command "Add-Type -Path '$s\Spds.cs'; [Spds]::Run('$s\a_geob$Tag.txt','$s\a_spds$Tag.txt',$K,$Ox,$Oy,'$No','$Name',$W,$H,$KNew)"
Get-Content "$s\a_spds$Tag.txt" -Encoding UTF8 | Where-Object { $_ -match '^(FRAME|XFORM)' } | ForEach-Object { $_.Substring(0, [math]::Min(140, $_.Length)) }
$env:BK_DATA = "$n\stamp_b109.txt"; $env:BK_OPS = "$s\a_spds$Tag.txt"; $env:BK_SRC = "$s\al2.dwg"; $env:BK_LOG = "$s\a_log$Tag.txt"; $env:BK_AXLTS = "1"
Remove-Item $Out -ErrorAction SilentlyContinue
& "$n\acadrun.ps1" -Dwg $p1 -Commands @("BKSHEET", "_.SAVEAS", "2018", $Out) -Done $Out -Sec 500 | Out-Null
Get-Content $env:BK_LOG -Encoding UTF8
if (Test-Path $Out) { "ok $Tag -> $Out" } else { "pass 2 failed" }
