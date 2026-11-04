$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$C = "$SP\w\chk"
foreach ($k in @('g11','g12','sch','fnd','vyp','col','wal','rig','p71','p72','st8','rmp')) {
  $src = if (Test-Path "$C\${k}_fx2.dwg") { "$C\${k}_fx2.dwg" } elseif (Test-Path "$C\${k}_fx.dwg") { "$C\${k}_fx.dwg" } else { "$C\$k.dwg" }
  & "$SP\net\run.ps1" -Cs "$SP\net\laydump.cs" -Cmd "LAYDUMP" -Dwg $src -Env @{LAY_OUT = "$C\lay_$k.txt"} | Out-Null
  "$k " + $src.Split('\')[-1] + " : " + ((Get-Content "$C\lay_$k.txt" -Encoding UTF8 | ForEach-Object { ($_ -split "`t")[2] }) -join ' ')
}
"LAYDUMP DONE"
