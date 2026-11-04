$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$D = "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 2\КЖ Чертеж"
$C = "$SP\w\chk2"
$env:PYTHONUTF8 = '1'
$files = @(
  @{k='ved'; f='1.Ведомости БЦ Байтурсынова Блок 2.dwg'; rx='1\.\d+'},
  @{k='sch'; f='2. Схема каркаса БЦ Байтурсынова Блок 2.dwg'; rx='2\.\d+'},
  @{k='fnd'; f='3.1 Фундамент БЦ Байтурсынова Блок 2.dwg'; rx='3\.\d+'},
  @{k='col'; f='4. Колонна БЦ Байтурсынова Блок 2.dwg'; rx='4\.\d+'},
  @{k='wal'; f='5. Стена БЦ Байтурсынова Блок 2.dwg'; rx='5\.\d+'},
  @{k='rig'; f='6.1 Ригель на отм -0.750 БЦ Байтурсынова Блок 2.dwg'; rx='6\.\d+'},
  @{k='p71'; f='7.1 Плита на отм -0.750 БЦ Байтурсынова Блок 2.dwg'; rx='7\.\d+'}
)
foreach ($x in $files) {
  $k = $x.k
  Copy-Item "$D\$($x.f)" "$C\$k.dwg" -Force
  & "$SP\net\run.ps1" -Cs "$SP\net\dxfo.cs" -Cmd "DXFO" -Dwg "$C\$k.dwg" -Env @{DXF_OUT = "$C\$k.dxf"} | Out-Null
  & "$SP\net\run.ps1" -Cs "$SP\net\tdump.cs" -Cmd "TDUMP" -Dwg "$C\$k.dwg" -Env @{TDUMP_OUT = "$C\$k.tables.txt"} | Out-Null
  & "$SP\net\run.ps1" -Cs "$SP\net\laydump.cs" -Cmd "LAYDUMP" -Dwg "$C\$k.dwg" -Env @{LAY_OUT = "$C\lay_$k.txt"} | Out-Null
  New-Item -ItemType Directory -Force "$C\pM_$k" | Out-Null
  $mk = python -X utf8 "$SP\w\mkjobs.py" "$C\$k.dxf" $x.rx "$C\pM_$k" 2>&1 | Where-Object { $_ -notmatch 'copy process' }
  "== $k : " + ($mk -join ' ; ')
  "layouts: " + ((Get-Content "$C\lay_$k.txt" -Encoding UTF8 | ForEach-Object { ($_ -split "`t")[2] }) -join ' ')
}
"ALL2 DONE"
