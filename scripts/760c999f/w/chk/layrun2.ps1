param([string[]]$Keys)
$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$C = "$SP\w\chk"
$env:PYTHONUTF8 = '1'
# pre-layout sources = user's original layouts + today's content fixes
$src = @{g11='g11_fx.dwg'; g12='g12.dwg'; sch='sch_fx2.dwg'; fnd='fnd.dwg'; vyp='vyp.dwg'; col='col_fx.dwg'; wal='wal.dwg'; rig='rig_fx.dwg'; p71='p71.dwg'; p72='p72_fx.dwg'; st8='st8_fx.dwg'; rmp='rmp_fx2.dwg'}
foreach ($k in $Keys) {
  $dwg = "$C\${k}_L2.dwg"
  Copy-Item "$C\$($src[$k])" $dwg -Force
  if ($k -eq 'g11') { & "$SP\net\run.ps1" -Cs "$SP\net\v4.cs" -Cmd "V4OPS" -Dwg $dwg -Env @{V4_JSON = "$C\fx_g11rc.json"} -Save | Out-Null }
  & "$SP\net\run.ps1" -Cs "$SP\net\layfix.cs" -Cmd "LAYFIX" -Dwg $dwg -Env @{LAYFIX_JSON = "$C\lay2_$k.json"} -Save | Out-Null
  "== $k"; Get-Content "$C\lay2_$k.json.log" -Encoding UTF8 | Where-Object { $_ -match 'ERR|created|renamed|new vp' }
  & "$SP\net\run.ps1" -Cs "$SP\net\plotl.cs" -Cmd "PLOTL" -Dwg $dwg -Env @{JOB_DIR = "$C\pL2_$k"} | Out-Null
  $bad = Get-Content "$C\pL2_$k\plotl_log.txt" -Encoding UTF8 | Where-Object { $_ -notmatch ' ok True' }
  "plotted " + ((Get-Content "$C\pL2_$k\plotl_log.txt" -Encoding UTF8 | Where-Object { $_ -match ' ok True' }).Count) + " bad: " + ($bad -join ' | ')
  python -X utf8 "$SP\w\merge.py" "$C\pL2_$k"
}
"LAYRUN2 DONE"
