param([string]$In)
# 2.1 «Схема расположения баз колонн» and 2.2 «Нагрузки…» added to the album DWG
$n = $PSScriptRoot; $s = Split-Path $n
$CI = [Globalization.CultureInfo]::InvariantCulture
function F($v) { ([double]$v).ToString("0.###", $CI) }
$k = 220; $ox = 1400000; $dx = $ox - 233220
$o = New-Object Collections.Generic.List[string]
$o.Add("FRAME`t$ox 0`t$k`tA1x1`t2.1`tСхема расположения баз колонн`t841 594")
# axes of sheet 3, shifted
foreach ($l in (Get-Content "$s\a_spds03.txt" -Encoding UTF8 | Where-Object { $_ -like "AXIS`t*" })) {
  $f = $l -split "`t"; $p = $f[2] -split ' ' | ForEach-Object { [double]$_ }; $c = $f[4] -split ' ' | ForEach-Object { [double]$_ }
  $o.Add("AXIS`t$($f[1])`t$(F ($p[0]+$dx)) $(F $p[1]) $(F ($p[2]+$dx)) $(F $p[3])`t$($f[3])`t$(F ($c[0]+$dx)) $(F $c[1])")
}
$o.Add("CLONEDIMS`t233220 418240 0 130680 $dx 0")
# base blocks from the node plans (sheet 10): centre from the bolt holes
$o.Add("MKBLOCK`tБаза_Б1`t1366928.2 2955.6 370 770")
$o.Add("MKBLOCK`tБаза_Б2`t1368480.3 2811.9 370 915")
$x1 = 251857.233 + $dx
$rows = @(@('A', 58998.904, 150, 'Б1', 750), @('M', 118998.904, -150, 'Б1', 750), @('E', 82998.904, 0, 'Б2', 895), @('H', 94998.904, 0, 'Б2', 895))
foreach ($r in $rows) {
  for ($i = 1; $i -le 28; $i++) {
    if ($r[0] -eq 'M' -and $i -ge 13 -and $i -le 16) { continue }     # К2: base not given in the source
    $x = $x1 + 6000 * ($i - 1); $y = $r[1] + $r[2]
    $o.Add("INS`tБаза_$($r[3])`t$(F $x) $(F $y)")
    # row A sits on the dimension chains: its marks go up from the upper corner
    $up = $r[0] -eq 'A'
    $tx = $x + 350; $ty = if ($up) { $y + $r[4] } else { $y - $r[4] }
    $oy = if ($up) { $ty + 2.5*$k } else { $ty - 2.5*$k }
    $o.Add("MARK`t$($r[3])`t$(F ($tx + 2.5*$k)) $(F $oy) 0 $(F $tx) $(F $ty)")
  }
}
$o.Add("TXT`t$(F ($ox + 420.5*$k)) $(F (564*$k))`t\LСхема расположения баз колонн`t$(F (5*$k)) $(F (300*$k)) 2")
$o.Add("TXT`t$(F ($ox + 600*$k)) $(F (95*$k))`t1. Общие данные см. лист 1.1.\n2. Базы колонн Б1, Б2 - узлы 1, 2 на листе 10.\n3. Нагрузки на фундаменты см. лист 2.2.\n4. Базы колонн К2, СФ, СФ1, К3 будут показаны после получения данных.`t$(F (3*$k)) $(F (230*$k)) 1")
[IO.File]::WriteAllLines("$s\ops21.txt", $o, (New-Object Text.UTF8Encoding $false))
# 2.2: the Цех table form, values and Цех items dropped
$drop = '^[\d\s,.±+\-]+$|Кровельн|Собственный вес|Снеговая|Мостовой кран|Стеновые панели|Сейсмичн|^Б\d$|\.\.\.|^Б,Б/1$|^А,В$|загр\.'
$o2 = @("FRAME`t1700000 0`t100`tA3x1v`t2.2`tНагрузки. Таблица расчетных нагрузок на фундаменты`t297 420",
        "IMPORT`t$s\ceh1spds.dwg`t918365 948065 -316650 -274650 781635 316650 929565 -311150`t$drop")
[IO.File]::WriteAllLines("$s\ops22.txt", $o2, (New-Object Text.UTF8Encoding $false))
"ops: 2.1 $($o.Count) lines, 2.2 $($o2.Count) lines"
$a = "C:\Program Files\Autodesk\AutoCAD 2021"; $m = "C:\Program Files\CSoft\СПДС Металлоконструкции 2021 x64 для AutoCAD\mg142x64"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /out:"$n\BkSpds.dll" /r:"$a\acmgd.dll" /r:"$a\acdbmgd.dll" /r:"$a\accoremgd.dll" /r:"$m\mapimgd.dll" /r:"$m\mapibasetypes.dll" "$n\BkProbe.cs" "$n\BkSheet.cs"
$env:BK_DATA = "$n\stamp_b109.txt"; $env:BK_SRC = "$s\al2.dwg"; $env:BK_AXLTS = "1"
foreach ($step in @(@("$s\ops21.txt", $In, "$s\alb_21.dwg"), @("$s\ops22.txt", "$s\alb_21.dwg", "$s\alb_22.dwg"))) {
  $env:BK_OPS = $step[0]; $env:BK_LOG = $step[0] + ".log"; Remove-Item $step[2] -ErrorAction SilentlyContinue
  & "$n\acadrun.ps1" -Dwg $step[1] -Commands @("TILEMODE", "1", "BKSHEET", "_.SAVEAS", "2018", $step[2]) -Done $step[2] -Sec 600 | Out-Null
  Get-Content $env:BK_LOG -Encoding UTF8
  if (-not (Test-Path $step[2])) { "failed $($step[0])"; return }
}
"ok"
