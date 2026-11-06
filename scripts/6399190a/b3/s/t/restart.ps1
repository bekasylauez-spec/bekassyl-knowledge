$S = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\s\t"
try { Stop-Process -Id ([int](Get-Content "$S\net\pid.txt")) -Force -ErrorAction Stop } catch {}
Start-Sleep 3
Remove-Item "D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 3\4.Колонна Блок 3.dwl*" -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\acadjob_mb3\*" -ErrorAction SilentlyContinue
& "$S\net\start.ps1" | Out-Null
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep 3
  & "$S\winlist.ps1" -ProcId ([int](Get-Content "$S\net\pid.txt")) -CloseDialogs | Out-Null
  if (Test-Path "$env:TEMP\acadjob_mb3\listening.txt") { break }
}
"listening " + (Test-Path "$env:TEMP\acadjob_mb3\listening.txt")
