param([string]$In, [string]$Out)
# Splits the Завод ОД sheet (A2) into Цех-style A3 sheets 1.1 / 1.2 / 1.3
$n = $PSScriptRoot; $s = Split-Path $n
$CI = [Globalization.CultureInfo]::InvariantCulture
function F($v) { ([double]$v).ToString("0.###", $CI) }
$k = 100; $ox1 = 1800000; $ox2 = 1850000; $ox3 = 1900000
$recs = foreach ($ln in [IO.File]::ReadAllLines("$s\zv_01.txt", [Text.Encoding]::GetEncoding(1251))) {
  $f = $ln -split "`t"; $c = @($f[2] -split ' ' | Where-Object { $_ -ne '' } | ForEach-Object { [double]$_ })
  [pscustomobject]@{ T = $f[0]; H = $f[1]; X = $c[0]; Y = $c[1]; X2 = $(if ($f[0] -eq 'L') { $c[2] } else { $c[0] }); Y2 = $(if ($f[0] -eq 'L') { $c[3] } else { $c[1] }); S = $f[$f.Count - 1] }
}
$o = New-Object Collections.Generic.List[string]
$o.Add("FRAME`t$ox1 0`t$k`tA3x1`t1.1`tОбщие данные (начало)`t420 297")
$o.Add("FRAME`t$ox2 0`t$k`tA3x1`t1.2`tОбщие данные (окончание)`t420 297")
$o.Add("FRAME`t$ox3 0`t$k`tA3x1`t1.3`tВедомость рабочих чертежей основного комплекта`t420 297")
# ---- ОД text rows: column A (x0 118574) then column B (x0 136714) ----
function Rows($x0, $x1, $ymin, $origX) {
  $tx = $recs | Where-Object { $_.T -eq 'T' -and $_.X -ge $x0 -and $_.X -lt $x1 -and $_.Y -gt $ymin }
  $groups = $tx | Group-Object { [math]::Round($_.Y / 50) } | Sort-Object { - [double]$_.Name }
  foreach ($g in $groups) {
    $y = ($g.Group | Measure-Object Y -Maximum).Maximum
    $hs = @($g.Group | ForEach-Object { $_.H })
    $hs += @($recs | Where-Object { $_.T -eq 'WI' -and $_.X -ge $x0 - 200 -and $_.X -lt $x1 -and ($y - $_.Y) -ge 0 -and ($y - $_.Y) -lt 400 } | ForEach-Object { $_.H })
    $txt = ($g.Group | Sort-Object X | ForEach-Object { $_.S }) -join ' '
    [pscustomobject]@{ Y = $y; H = $hs; S = $txt; OX = $origX }
  }
}
$rows = @(Rows 118000 136000 500 118574) + @(Rows 136000 155600 6000 136714)
$cols = @(@{ X = $ox1 + 25 * $k; Top = 285 * $k; Bot = 62 * $k }, @{ X = $ox1 + 215 * $k; Top = 285 * $k; Bot = 66 * $k },
          @{ X = $ox2 + 25 * $k; Top = 285 * $k; Bot = 10 * $k }, @{ X = $ox2 + 215 * $k; Top = 285 * $k; Bot = 160 * $k })
$cix = 0; $y = $cols[0].Top; $prev = $null
for ($i = 0; $i -lt $rows.Count; $i++) {
  $r = $rows[$i]
  $gap = if ($prev -and $prev.OX -eq $r.OX) { $prev.Y - $r.Y } else { 455 }
  $ny = $y - $gap
  # a heading never stays alone at the bottom of a column
  $isHead = $r.S -match '^\s*\d+(\.\d+)?\.?\s+[А-ЯA-Z]'
  $nextGap = if ($i + 1 -lt $rows.Count -and $rows[$i + 1].OX -eq $r.OX) { $r.Y - $rows[$i + 1].Y } else { 0 }
  if ($ny -lt $cols[$cix].Bot -or ($isHead -and ($ny - $nextGap) -lt $cols[$cix].Bot)) { $cix++; if ($cix -ge $cols.Count) { "OVERFLOW at row $i"; break }; $ny = $cols[$cix].Top }
  $o.Add("MOVE`t$(F ($cols[$cix].X - $r.OX)) $(F ($ny - $r.Y))`t$($r.H -join ' ')")
  $y = $ny; $prev = $r
}
"rows $($rows.Count), last column $cix, last y $y"
# ---- «Ведомость ссылочных…» -> 1.2 right, above the stamp; «Принятые технические решения» + ГИП -> 1.1 bottom left ----
$ref = $recs | Where-Object { $_.X -ge 98000 -and $_.X -le 117700 -and $_.Y -ge 8150 -and $_.Y -le 16450 -and $_.X2 -ge 98000 -and $_.X2 -le 117700 -and $_.Y2 -ge 8150 -and $_.Y2 -le 16450 } | ForEach-Object { $_.H }
$o.Add("MOVE`t$(F ($ox2 + 215 * $k - 98600)) $(F (66 * $k - 8300))`t$($ref -join ' ')")
$acc = $recs | Where-Object { $_.X -ge 98000 -and $_.X -le 117700 -and $_.Y -ge 400 -and $_.Y -le 5100 -and $_.X2 -ge 98000 -and $_.X2 -le 117700 -and $_.Y2 -ge 400 -and $_.Y2 -le 5100 } | ForEach-Object { $_.H }
$o.Add("MOVE`t$(F ($ox1 + 25 * $k - 98600)) 0`t$($acc -join ' ')")
"ref $($ref.Count), accepted $($acc.Count)"
# what is left of the old A2 sheet (frame, stamp, old ведомость) goes
$o.Add("ERASEWIN`t96500 156100 -100 42100")
# ---- 1.3: ведомость (ГОСТ Р 21.101 form: 15 | 140 | 30, header 15, rows 8) ----
$sheets = @(@('1.1', 'Общие данные (начало)'), @('1.2', 'Общие данные (окончание)'), @('1.3', 'Ведомость рабочих чертежей основного комплекта'),
            @('1.4', 'Техническая спецификация металла'), @('2.1', 'Схема расположения баз колонн'), @('2.2', 'Нагрузки. Таблица расчетных нагрузок на фундаменты'),
            @('3', 'Схема расположения колонн'), @('4', 'Схема расположения элементов по нижним поясам ферм'), @('5', 'Схема расположения элементов по верхним поясам ферм'),
            @('6', 'Схема расположения подкрановых конструкций'), @('7', 'Схема перекрытия'), @('8', 'Разрезы 1-1, 2-2, 3-3'), @('9', 'Ферма ФФ1'),
            @('10', 'Базы колонн. Узлы 1, 2'), @('11', 'Узлы 3-8'))
$x0 = $ox3 + 25 * $k; $xs = @($x0, ($x0 + 15 * $k), ($x0 + 155 * $k), ($x0 + 185 * $k)); $top = 275 * $k; $hb = $top - 15 * $k; $bot = $hb - 8 * $k * $sheets.Count
$o.Add("TXT`t$(F ($x0 + 92.5 * $k)) $(F ($top + 6 * $k))`tВедомость рабочих чертежей основного комплекта`t$(F (3.5 * $k)) $(F (185 * $k)) 5")
foreach ($yy in @($top, $hb, $bot)) { $o.Add("LINE`t$(F $xs[0]) $(F $yy) $(F $xs[3]) $(F $yy)`t50") }
for ($i = 1; $i -lt $sheets.Count; $i++) { $yy = $hb - 8 * $k * $i; $o.Add("LINE`t$(F $xs[0]) $(F $yy) $(F $xs[3]) $(F $yy)") }
foreach ($xx in $xs) { $o.Add("LINE`t$(F $xx) $(F $top) $(F $xx) $(F $bot)`t50") }
$hy = $top - 7.5 * $k
$o.Add("TXT`t$(F ($xs[0] + 7.5 * $k)) $(F $hy)`tЛист`t$(F (2.5 * $k)) $(F (14 * $k)) 5")
$o.Add("TXT`t$(F ($xs[1] + 70 * $k)) $(F $hy)`tНаименование`t$(F (2.5 * $k)) $(F (100 * $k)) 5")
$o.Add("TXT`t$(F ($xs[2] + 15 * $k)) $(F $hy)`tПримечание`t$(F (2.5 * $k)) $(F (28 * $k)) 5")
for ($i = 0; $i -lt $sheets.Count; $i++) {
  $yy = $hb - 8 * $k * $i - 4 * $k
  $o.Add("TXT`t$(F ($xs[0] + 7.5 * $k)) $(F $yy)`t$($sheets[$i][0])`t$(F (2.5 * $k)) $(F (14 * $k)) 5")
  $o.Add("TXT`t$(F ($xs[1] + 2 * $k)) $(F $yy)`t$($sheets[$i][1])`t$(F (2.5 * $k)) $(F (136 * $k)) 4")
}
# ---- notes on the other sheets point to the new numbers ----
$o.Add("REPL`tведомость чертежей основного комплекта на листе 1\.?`tведомость чертежей основного комплекта на листах 1.1-1.3.")
$o.Add("REPL`tСпецификация металлопроката на листе 2\.?`tТехническая спецификация металла на листе 1.4.")
$o.Add("REPL`tРазрезы на листе 4\.?`tРазрезы на листе 8.")
$o.Add("REPL`tОбщие данные см\. лист 1\.1\.`tОбщие данные см. листы 1.1-1.3.")
[IO.File]::WriteAllLines("$s\ops_od.txt", $o, (New-Object Text.UTF8Encoding $false))
"ops $($o.Count)"
$a = "C:\Program Files\Autodesk\AutoCAD 2021"; $m = "C:\Program Files\CSoft\СПДС Металлоконструкции 2021 x64 для AutoCAD\mg142x64"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /out:"$n\BkSpds.dll" /r:"$a\acmgd.dll" /r:"$a\acdbmgd.dll" /r:"$a\accoremgd.dll" /r:"$m\mapimgd.dll" /r:"$m\mapibasetypes.dll" "$n\BkProbe.cs" "$n\BkSheet.cs"
if ($LASTEXITCODE -ne 0) { "compile failed"; return }
$env:BK_DATA = "$n\stamp_b109.txt"; $env:BK_SRC = "$s\al2.dwg"; $env:BK_OPS = "$s\ops_od.txt"; $env:BK_LOG = "$s\ops_od.log"
Remove-Item $Out -ErrorAction SilentlyContinue
& "$n\acadrun.ps1" -Dwg $In -Commands @("TILEMODE", "1", "BKSHEET", "_.SAVEAS", "2018", $Out) -Done $Out -Sec 600 | Out-Null
Get-Content $env:BK_LOG -Encoding UTF8
"out: $(Test-Path $Out)"
