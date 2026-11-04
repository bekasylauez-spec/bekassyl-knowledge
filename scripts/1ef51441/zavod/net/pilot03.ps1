# build plugin, analyse sheet 03, convert to SPDS in a separate AutoCAD, plot, render
$n = $PSScriptRoot; $s = Split-Path $n; $sp = Split-Path $s
$l = ($s -replace '\\', '/')
$a = "C:\Program Files\Autodesk\AutoCAD 2021"; $m = "C:\Program Files\CSoft\СПДС Металлоконструкции 2021 x64 для AutoCAD\mg142x64"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /out:"$n\BkSpds.dll" /r:"$a\acmgd.dll" /r:"$a\acdbmgd.dll" /r:"$a\accoremgd.dll" /r:"$m\mapimgd.dll" /r:"$m\mapibasetypes.dll" "$n\BkProbe.cs" "$n\BkSheet.cs"
if ($LASTEXITCODE -ne 0) { "compile failed"; return }
powershell -NoProfile -Command "Add-Type -Path '$s\Spds.cs'; [Spds]::Run('$s\geo03b.txt','$s\spds03.txt',220,233220,0,'3','Схема колонн')"
Copy-Item "$s\z03.dwg" "$s\z03in.dwg" -Force
$env:BK_DATA = "$n\stamp_b109.txt"; $env:BK_OPS = "$s\spds03.txt"; $env:BK_SRC = "$s\al2.dwg"; $env:BK_OUT = "$s\z03s.dwg"; $env:BK_LOG = "$s\bksheet.log"
$env:PLTLAY = "03 Схема колонн"; $env:PLTOUT = "$s\plot03s.pdf"
Remove-Item $env:BK_LOG, $env:PLTOUT, $env:BK_OUT -ErrorAction SilentlyContinue
& "$n\acadrun.ps1" -Dwg "$s\z03in.dwg" -Commands @("BKSHEET", "_.SAVEAS", "2018", "$s\z03s.dwg", "(load `"$l/plot.lsp`")", "PLT") -Done $env:PLTOUT -Sec 500
Get-Content $env:BK_LOG -Encoding UTF8
if (Test-Path $env:PLTOUT) {
  & "$sp\pdf2png.ps1" -Pdf $env:PLTOUT -OutDir "$s\png03s" -Width 9000 | Out-Null
  & "$sp\crop.ps1" "$s\png03s\p01.png" "$s\s03a.png" 0.0 0.40 0.30 0.62
  & "$sp\crop.ps1" "$s\png03s\p01.png" "$s\s03st.png" 0.70 0.80 1.0 1.0
  & "$sp\crop.ps1" "$s\png03s\p01.png" "$s\s03top.png" 0.0 0.0 0.30 0.18
}
