param([string[]]$Variants)
# which SPDS object type makes the DWG unreadable without SPDS (accoreconsole)?
$n = $PSScriptRoot; $s = Split-Path $n
$a = "C:\Program Files\Autodesk\AutoCAD 2021"; $m = "C:\Program Files\CSoft\СПДС Металлоконструкции 2021 x64 для AutoCAD\mg142x64"
# & csc /nologo /target:library /platform:x64 /out:"$n\BkSpds.dll" /r:"$a\acmgd.dll" /r:"$a\acdbmgd.dll" /r:"$a\accoremgd.dll" /r:"$m\mapimgd.dll" /r:"$m\mapibasetypes.dll" "$n\BkProbe.cs" "$n\BkSheet.cs"
$env:BK_DATA = "$n\stamp_b109.txt"; $env:BK_OPS = "$s\spds03.txt"; $env:BK_SRC = "$s\al2.dwg"; $env:BK_LOG = "$s\bksheet.log"
foreach ($v in $Variants) {
  $env:BK_ONLY = $v
  $out = "$s\bis_" + ($v -replace ',', '_') + ".dwg"
  Remove-Item $out -ErrorAction SilentlyContinue
  Copy-Item "$s\z03.dwg" "$s\z03in.dwg" -Force
  & "$n\acadrun.ps1" -Dwg "$s\z03in.dwg" -Commands @("BKSHEET", "_.SAVEAS", "2018", $out) -Done $out -Sec 400 | Out-Null
  $p = Start-Process "$a\accoreconsole.exe" -ArgumentList "/i `"$out`" /s `"$s\ins.scr`" /l ru-RU" -PassThru -NoNewWindow -RedirectStandardOutput "$s\t.log"
  $p.WaitForExit(200000) | Out-Null
  $t = [Text.Encoding]::Unicode.GetString([IO.File]::ReadAllBytes("$s\t.log"))
  "$v : " + $(if ($t -match 'ErrorStatus=(\d+)') { "ERR $($matches[1])" } else { "ok" })
}
Remove-Item Env:BK_ONLY
