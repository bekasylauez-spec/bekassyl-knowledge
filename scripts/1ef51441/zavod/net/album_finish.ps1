param([string]$In)
# layouts from the FRAME rows of every sheet, then one PDF of all layouts
$n = $PSScriptRoot; $s = Split-Path $n
$rows = @()
foreach ($tag in 'T1', 'T2', '01', '02', '03', '05', '06', '08', '09', '04', '07', '10', '11') {
  $f = "$s\a_spds$tag.txt"
  if (-not (Test-Path $f)) { continue }
  $fr = Get-Content $f -Encoding UTF8 | Where-Object { $_ -like "FRAME`t*" } | Select-Object -First 1
  $p = $fr -split "`t"
  $name = if ($tag -eq 'T1') { 'Т1' } elseif ($tag -eq 'T2') { 'Т2' } else { $p[4] }
  $rows += "$name`t$($p[1])`t$($p[2])`t$($p[6])"
}
[IO.File]::WriteAllLines("$s\album_sheets.txt", $rows, (New-Object Text.UTF8Encoding $false))
$rows
$out = "$s\album_final.dwg"; $pdf = "$s\album_final.pdf"
Remove-Item $out, $pdf -ErrorAction SilentlyContinue
$env:BK_SHEETS = "$s\album_sheets.txt"; $env:BK_LOG = "$s\album_layouts.log"
& "$n\acadrun.ps1" -Dwg $In -Commands @("BKLAYOUTS", "_.SAVEAS", "2018", $out, "_.-EXPORT", "_PDF", "_A", $pdf) -Done $pdf -Sec 900 | Out-Null
Get-Content $env:BK_LOG -Encoding UTF8
"dwg: $(Test-Path $out)  pdf: $(Test-Path $pdf)"
