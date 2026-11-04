param([string]$In, [string]$Out, [string]$Tag, [string]$Layout, [double]$X0, [double]$X1, [double]$Y0, [double]$Y1, [int]$K)
# one sheet: geo dump -> analyse -> apply -> plot -> png
$s = $PSScriptRoot; $l = ($s -replace '\\', '/')
$acc = "C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"
function Acc([string]$dwg, [string]$lsp, [string]$cmd, [int]$sec = 300) {
  "SECURELOAD`n0`n(load `"$l/$lsp`")`n$cmd`n" | Set-Content "$s\_$cmd.scr" -Encoding ASCII -NoNewline
  $p = Start-Process $acc -ArgumentList "/i `"$dwg`" /s `"$s\_$cmd.scr`" /l ru-RU" -PassThru -NoNewWindow -RedirectStandardOutput "$s\_$cmd.log"
  if (-not $p.WaitForExit($sec * 1000)) { $p.Kill(); "$cmd killed" }
}
$env:DMPOUT = "$s\geo$Tag.txt"; $env:GX0 = "$X0"; $env:GX1 = "$X1"; $env:GY0 = "$Y0"; $env:GY1 = "$Y1"
Acc $In "geo.lsp" "GEO"
$ps = "Add-Type -Path '$s\Restyle.cs'; [Restyle]::Run('$s\geo$Tag.txt','$s\ops$Tag.txt',$K,'СПДС 1-$K')"
powershell -NoProfile -Command $ps
Remove-Item $Out -ErrorAction SilentlyContinue
$env:APK = "$K"; $env:APOPS = "$s\ops$Tag.txt"; $env:APOUT = $Out
Acc $In "apply.lsp" "APL"
if (-not (Test-Path $Out)) { "apply failed"; return }
$env:PLTLAY = $Layout; $env:PLTOUT = "$s\plot$Tag.pdf"
Acc $Out "plot.lsp" "PLT"
& "$s\..\pdf2png.ps1" -Pdf "$s\plot$Tag.pdf" -OutDir "$s\png$Tag" -Width 9000 | Out-Null
"ok $Tag"
