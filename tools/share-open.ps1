# НЕГІЗГІ компьютер, құпиясөзсіз нұсқа: РАБОЧКА-ны желідегі барлығына оқу+өзгертуге ашады.
$ErrorActionPreference = "Stop"
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw "Әкімші ретінде іске қосыңыз" }

$Work = "D:\РАБОЧКА"; $Name = "РАБОЧКА"
$everyone = (New-Object Security.Principal.SecurityIdentifier "S-1-1-0").Translate([Security.Principal.NTAccount]).Value   # "Все"
if (-not (Get-SmbShare -Name $Name -ErrorAction SilentlyContinue)) { New-SmbShare -Name $Name -Path $Work | Out-Null }
Grant-SmbShareAccess -Name $Name -AccountName $everyone -AccessRight Change -Force | Out-Null
icacls $Work /grant "*S-1-1-0:(OI)(CI)M" /C /Q | Out-Null

Write-Host ""
Write-Host "РАБОЧКА желіге ашылды (Все: чтение + изменение)."
Write-Host "Енді ашылған терезеде: «Общий доступ с парольной защитой» -> ОТКЛЮЧИТЬ."
Start-Process "control.exe" "/name Microsoft.NetworkAndSharingCenter /page Advanced"
