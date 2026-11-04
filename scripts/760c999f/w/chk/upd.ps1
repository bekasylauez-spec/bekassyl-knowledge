$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$D = "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 1\КЖ Чертеж"
$C = "$SP\w\chk"
$env:PYTHONUTF8 = '1'
$files = @(
  @{k='fnd'; dst='fnd.dwg'; f='3.1 Фундамент БЦ Байтурсынова Блок1.dwg'; rx='3\.\d+'},
  @{k='vyp'; dst='vyp.dwg'; f='3.2 Выпуск БЦ Байтурсынова Блок1 (испр).dwg'; rx='3\.\d+'},
  @{k='wal'; dst='wal.dwg'; f='5. Стена БЦ Байтурсынова Блок1 (испр).dwg'; rx='5\.\d+'},
  @{k='p72'; dst='p72_fx.dwg'; f='7.2 Плита  на отм +13,400;+17,600;+21,500 БЦ Байтурсынова Блок1.dwg'; rx='7\.\d+'}
)
foreach ($x in $files) {
  $k = $x.k
  Copy-Item "$D\$($x.f)" "$C\$($x.dst)" -Force
  Copy-Item "$D\$($x.f)" "$C\$k.dwg" -Force
  & "$SP\net\run.ps1" -Cs "$SP\net\dxfo.cs" -Cmd "DXFO" -Dwg "$C\$k.dwg" -Env @{DXF_OUT = "$C\$k.dxf"} | Out-Null
  & "$SP\net\run.ps1" -Cs "$SP\net\tdump.cs" -Cmd "TDUMP" -Dwg "$C\$k.dwg" -Env @{TDUMP_OUT = "$C\$k.tables.txt"} | Out-Null
  & "$SP\net\run.ps1" -Cs "$SP\net\laydump.cs" -Cmd "LAYDUMP" -Dwg "$C\$k.dwg" -Env @{LAY_OUT = "$C\lay_$k.txt"} | Out-Null
  New-Item -ItemType Directory -Force "$C\pM_$k" | Out-Null
  $mk = python -X utf8 "$SP\w\mkjobs.py" "$C\$k.dxf" $x.rx "$C\pM_$k" 2>&1 | Where-Object { $_ -notmatch 'copy process' }
  "== $k : " + ($mk -join ' ; ')
  "layouts: " + ((Get-Content "$C\lay_$k.txt" -Encoding UTF8 | ForEach-Object { ($_ -split "`t")[2] }) -join ' ')
}
"UPD DONE"
