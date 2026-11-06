$S = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\d50da53a-3ac3-4689-a264-f515b6d8bdb3\scratchpad\s\t"
try { Stop-Process -Id ([int](Get-Content "$S\net\pid.txt")) -Force -ErrorAction Stop } catch {}
Start-Sleep 3
Remove-Item "D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 2\4.Колонна Блок 2.dwl*" -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\acadjob_mb2\*" -ErrorAction SilentlyContinue
& "$S\net\start.ps1" | Out-Null
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep 3
  & "$S\winlist.ps1" -ProcId ([int](Get-Content "$S\net\pid.txt")) -CloseDialogs | Out-Null
  if (Test-Path "$env:TEMP\acadjob_mb2\listening.txt") { break }
}
"listening " + (Test-Path "$env:TEMP\acadjob_mb2\listening.txt")
