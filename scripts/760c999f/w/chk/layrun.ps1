param([string[]]$Keys)
$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$D = "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 1\КЖ Чертеж"
$C = "$SP\w\chk"
$env:PYTHONUTF8 = '1'
$names = @{g11='1.1 Общие данные  БЦ Байтурсынова Блок1.dwg'; g12='1.2 Котлован БЦ Байтурсынова Блок1.dwg'; sch='2. Схема каркаса БЦ Байтурсынова Блок1.dwg'; fnd='3.1 Фундамент БЦ Байтурсынова Блок1.dwg'; vyp='3.2 Выпуск БЦ Байтурсынова Блок1.dwg'; col='4. Колонна БЦ Байтурсынова Блок1.dwg'; wal='5. Стена БЦ Байтурсынова Блок1.dwg'; rig='6.1 Ригель  БЦ Байтурсынова Блок1.dwg'; p71='7.1 Плита  на отм -0.100;+5.000;+9.200 БЦ Байтурсынова Блок1.dwg'; p72='7.2 Плита  на отм +13,400;+17,600;+21,500 БЦ Байтурсынова Блок1.dwg'; st8='8. Лестница БЦ Байтурсынова Блок1.dwg'; rmp='9. Рампа Бц Байтурсынова Блок1.dwg'}
foreach ($k in $Keys) {
  $dwg = "$C\${k}_L.dwg"
  Copy-Item "$D\$($names[$k])" $dwg -Force
  if ($k -eq 'g11') { & "$SP\net\run.ps1" -Cs "$SP\net\v4.cs" -Cmd "V4OPS" -Dwg $dwg -Env @{V4_JSON = "$C\fx_g11rc.json"} -Save | Out-Null }
  & "$SP\net\run.ps1" -Cs "$SP\net\layfix.cs" -Cmd "LAYFIX" -Dwg $dwg -Env @{LAYFIX_JSON = "$C\lay_$k.json"} -Save | Out-Null
  "== $k"; Get-Content "$C\lay_$k.json.log" -Encoding UTF8 | Where-Object { $_ -match 'ERR|created|renamed|deleted' }
  (Get-Content "$C\lay_$k.json.log" -Encoding UTF8 | Where-Object { $_ -match 'new vp' }).Count.ToString() + " layouts set"
  & "$SP\net\run.ps1" -Cs "$SP\net\plotl.cs" -Cmd "PLOTL" -Dwg $dwg -Env @{JOB_DIR = "$C\pL_$k"} | Out-Null
  $bad = Get-Content "$C\pL_$k\plotl_log.txt" -Encoding UTF8 | Where-Object { $_ -notmatch ' ok True' }
  "plotted " + ((Get-Content "$C\pL_$k\plotl_log.txt" -Encoding UTF8 | Where-Object { $_ -match ' ok True' }).Count) + " bad: " + ($bad -join ' | ')
  python -X utf8 "$SP\w\merge.py" "$C\pL_$k"
}
"LAYRUN DONE"
