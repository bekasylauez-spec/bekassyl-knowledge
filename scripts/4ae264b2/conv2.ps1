$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\4ae264b2-3d49-4a11-8864-2d6523e82a02\scratchpad"
$OLD = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\net"
$acad = "C:\Program Files\Autodesk\AutoCAD 2021"
$src = "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 1\КЖ Чертеж"
New-Item -ItemType Directory -Force "$SP\dxf" | Out-Null
$dxfo = "$OLD\dxfo_100819832.dll"
$td = Get-ChildItem "$OLD\tdump_*.dll" | Sort-Object LastWriteTime | Select-Object -Last 1
$lines = @("(setvar `"SECURELOAD`" 0)", "(setvar `"FILEDIA`" 0)", "_.NETLOAD", "`"$dxfo`"", "_.NETLOAD", "`"$($td.FullName)`"", "DXFO", "TDUMP", "_.QUIT", "_Y")
$scr = "$SP\conv.scr"
[IO.File]::WriteAllText($scr, ($lines -join "`r`n") + "`r`n", [Text.Encoding]::GetEncoding(1251))
$jobs = @()
$i = 0
foreach ($f in Get-ChildItem $src -Filter *.dwg) {
  $i++
  $k = "f{0:D2}" -f $i
  Copy-Item $f.FullName "$SP\dxf\$k.dwg" -Force
  "$k`t$($f.Name)" | Out-File -Append -Encoding utf8 "$SP\dxf\map.txt"
  $psi = New-Object Diagnostics.ProcessStartInfo "$acad\accoreconsole.exe", "/i `"$SP\dxf\$k.dwg`" /s `"$scr`" /l ru-RU"
  $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true; $psi.RedirectStandardOutput = $true
  $psi.EnvironmentVariables["DXF_OUT"] = "$SP\dxf\$k.dxf"
  $psi.EnvironmentVariables["TDUMP_OUT"] = "$SP\dxf\$k.tables.txt"
  $p = [Diagnostics.Process]::Start($psi)
  $jobs += ,@($p, $k)
  if ($jobs.Count -ge 4) { foreach ($j in $jobs) { $null = $j[0].StandardOutput.ReadToEnd(); $j[0].WaitForExit() }; $jobs = @() }
}
foreach ($j in $jobs) { $null = $j[0].StandardOutput.ReadToEnd(); $j[0].WaitForExit() }
Get-ChildItem "$SP\dxf" | Select-Object Name, Length
