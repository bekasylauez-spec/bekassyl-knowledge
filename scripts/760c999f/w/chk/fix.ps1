$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$D = "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 1\КЖ Чертеж"
$C = "$SP\w\chk"
$env:PYTHONUTF8 = '1'
$files = @(
  @{k='rig'; f='6.1 Ригель  БЦ Байтурсынова Блок1.dwg'; rx='6\.\d+'},
  @{k='rmp'; f='9. Рампа Бц Байтурсынова Блок1.dwg'; rx='9\.\d+'},
  @{k='st8'; f='8. Лестница БЦ Байтурсынова Блок1.dwg'; rx='8\.\d+'},
  @{k='sch'; f='2. Схема каркаса БЦ Байтурсынова Блок1.dwg'; rx='2\.\d+'},
  @{k='col'; f='4. Колонна БЦ Байтурсынова Блок1.dwg'; rx='4\.\d+'},
  @{k='g11'; f='1.1 Общие данные  БЦ Байтурсынова Блок1.dwg'; rx='1\.\d+'},
  @{k='p72'; f='7.2 Плита  на отм +13,400;+17,600;+21,500 БЦ Байтурсынова Блок1.dwg'; rx='7\.\d+'}
)
foreach ($x in $files) {
  $k = $x.k
  "== $k " + (Get-Item "$D\$($x.f)").LastWriteTime
  Copy-Item "$D\$($x.f)" "$C\${k}_fx.dwg" -Force
  & "$SP\net\run.ps1" -Cs "$SP\net\v4.cs" -Cmd "V4OPS" -Dwg "$C\${k}_fx.dwg" -Env @{V4_JSON = "$C\fx_$k.json"} -Save | Out-Null
  Get-Content "$C\fx_$k.json.log" -Encoding UTF8
  & "$SP\net\run.ps1" -Cs "$SP\net\tdump.cs" -Cmd "TDUMP" -Dwg "$C\${k}_fx.dwg" -Env @{TDUMP_OUT = "$C\${k}_fx.tables.txt"} | Out-Null
  & "$SP\net\run.ps1" -Cs "$SP\net\dxfo.cs" -Cmd "DXFO" -Dwg "$C\${k}_fx.dwg" -Env @{DXF_OUT = "$C\${k}_fx.dxf"} | Out-Null
  New-Item -ItemType Directory -Force "$C\pf_$k" | Out-Null
  python -X utf8 "$SP\w\mkjobs.py" "$C\${k}_fx.dxf" $x.rx "$C\pf_$k" 2>&1 | Where-Object { $_ -notmatch 'copy process' } | Select-Object -Last 1
  & "$SP\net\plotmerge.ps1" -Dwg "$C\${k}_fx.dwg" -Dir "$C\pf_$k"
}
"FIX DONE"
