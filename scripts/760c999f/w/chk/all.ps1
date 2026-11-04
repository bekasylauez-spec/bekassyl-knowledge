$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$D = "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 1\КЖ Чертеж"
$C = "$SP\w\chk"
$env:PYTHONUTF8 = '1'
$files = @(
  @{k='g11'; f='1.1 Общие данные  БЦ Байтурсынова Блок1.dwg'; rx='1\.\d+'},
  @{k='g12'; f='1.2 Котлован БЦ Байтурсынова Блок1.dwg'; rx='1\.\d+'},
  @{k='sch'; f='2. Схема каркаса БЦ Байтурсынова Блок1.dwg'; rx='2\.\d+'},
  @{k='fnd'; f='3.1 Фундамент БЦ Байтурсынова Блок1.dwg'; rx='3\.\d+'},
  @{k='vyp'; f='3.2 Выпуск БЦ Байтурсынова Блок1.dwg'; rx='3\.\d+'},
  @{k='col'; f='4. Колонна БЦ Байтурсынова Блок1.dwg'; rx='4\.\d+'},
  @{k='wal'; f='5. Стена БЦ Байтурсынова Блок1.dwg'; rx='5\.\d+'},
  @{k='rig'; f='6.1 Ригель  БЦ Байтурсынова Блок1.dwg'; rx='6\.\d+'},
  @{k='p71'; f='7.1 Плита  на отм -0.100;+5.000;+9.200 БЦ Байтурсынова Блок1.dwg'; rx='7\.\d+'},
  @{k='p72'; f='7.2 Плита  на отм +13,400;+17,600;+21,500 БЦ Байтурсынова Блок1.dwg'; rx='7\.\d+'},
  @{k='st8'; f='8. Лестница БЦ Байтурсынова Блок1.dwg'; rx='8\.\d+'},
  @{k='rmp'; f='9. Рампа Бц Байтурсынова Блок1.dwg'; rx='9\.\d+'}
)
foreach ($x in $files) {
  $k = $x.k
  Copy-Item "$D\$($x.f)" "$C\$k.dwg" -Force
  & "$SP\net\run.ps1" -Cs "$SP\net\dxfo.cs" -Cmd "DXFO" -Dwg "$C\$k.dwg" -Env @{DXF_OUT = "$C\$k.dxf"} | Out-Null
  & "$SP\net\run.ps1" -Cs "$SP\net\tdump.cs" -Cmd "TDUMP" -Dwg "$C\$k.dwg" -Env @{TDUMP_OUT = "$C\$k.tables.txt"} | Out-Null
  New-Item -ItemType Directory -Force "$C\pl_$k" | Out-Null
  $mk = python -X utf8 "$SP\w\mkjobs.py" "$C\$k.dxf" $x.rx "$C\pl_$k" 2>&1 | Where-Object { $_ -notmatch 'copy process' }
  $pm = & "$SP\net\plotmerge.ps1" -Dwg "$C\$k.dwg" -Dir "$C\pl_$k"
  "$k : " + ($mk -join ' ; ') + " | " + ($pm -join ' ')
}
"ALL DONE"
