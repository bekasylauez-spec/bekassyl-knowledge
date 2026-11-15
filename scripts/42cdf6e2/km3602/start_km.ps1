# Өз Revit данамды берілген файлмен (қайта) іске қосу, MCP көпірін қосу. Тінтуірсіз.
param([string]$Rvt)
. "D:\_claude_work\otst\win.ps1"; . "D:\Бекасыл КЖ КМ\_Стандарт_КЖ\скрипттер\revit_nomouse.ps1" 2>$null
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes,WindowsBase
$pidf="D:\_claude_work\otst\_pid.txt"; $id=[int](Get-Content $pidf); $p=Get-Process -Id $id -ErrorAction SilentlyContinue
if($p -and $p.ProcessName -eq 'Revit'){ $p.CloseMainWindow() | Out-Null; for($k=0;$k -lt 15 -and -not $p.HasExited;$k++){ Start-Sleep 2; foreach($l in @(Get-RvWins)){ if($l -match '#32770'){ $dh=[long]($l.Split('|')[0]); $els=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$dh).FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition); $b=$els | ? { $_.Current.Name -match '^Нет$' } | Select-Object -First 1; if($b){ [RvNoMouse]::BmClick([IntPtr]$b.Current.NativeWindowHandle) } } } }; if(-not $p.HasExited){ Stop-Process -Id $id -Force; "killed own instance" } }
$man="$env:APPDATA\Autodesk\Revit\Addins\2025\OtstBoot.addin"; $flag=Join-Path $env:LOCALAPPDATA "rvjob\otstboot.on"; $log=Join-Path $env:LOCALAPPDATA "rvjob\otstboot.txt"
'<?xml version="1.0" encoding="utf-8"?><RevitAddIns><AddIn Type="Application"><Name>OtstBoot</Name><Assembly>D:\_claude_work\otst\boot\OtstBoot3.dll</Assembly><AddInId>7C1D5E0A-2B6F-4D3C-9A1E-5F4B3C2D1E0F</AddInId><FullClassName>OtstBoot.App</FullClassName><VendorId>KZH</VendorId><VendorDescription>MCP switch autostart (temporary)</VendorDescription></AddIn></RevitAddIns>' | Set-Content $man -Encoding utf8
"on" | Set-Content $flag; [IO.File]::Delete($log)
$pr=Start-Process "C:\Program Files\Autodesk\Revit 2025\Revit.exe" -ArgumentList ('"'+$Rvt+'"') -PassThru; $pr.Id | Set-Content $pidf; "pid $($pr.Id)"
$ok=$false
for($i=0;$i -lt 120;$i++){ Start-Sleep 3; $w=@(Get-RvWins)
 foreach($l in $w){ if($l -match '#32770'){ $dh=[long]($l.Split('|')[0]); $els=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$dh).FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition); $names=($els | % { $_.Current.Name }) -join ' ; '
   if($names -match 'OtstBoot'){ $b=$els | ? { $_.Current.AutomationId -eq 'CommandButton_1002' } | Select-Object -First 1; [RvNoMouse]::BmClick([IntPtr]$b.Current.NativeWindowHandle); "[$i] load once" }
   elseif($names -match "подпис|Надстройк" -and ($els | ? { $_.Current.AutomationId -eq "CommandButton_1002" })){ $b=$els | ? { $_.Current.AutomationId -eq "CommandButton_1002" } | Select-Object -First 1; [RvNoMouse]::BmClick([IntPtr]$b.Current.NativeWindowHandle); "[$i] other add-in: load once" }
   elseif($l -match 'revitMCP'){ $b=$els | ? { $_.Current.Name -eq 'Закрыть' } | Select-Object -First 1; [RvNoMouse]::BmClick([IntPtr]$b.Current.NativeWindowHandle); "[$i] closed MCP box"; $ok=$true }
   else { "[$i] dialog: " + $names.Substring(0,[Math]::Min(250,$names.Length)) } } }
 $m=$w | ? { $_ -match 'Autodesk Revit 2025 - \[' }; if($m){ [RvNoMouse]::Nudge([IntPtr][long](@($m)[0].Split('|')[0]),$i) }
 if($ok){ break } }
[IO.File]::Delete($man); [IO.File]::Delete($flag)
Start-Sleep 2; "port: " + (Test-NetConnection 127.0.0.1 -Port 8080 -WarningAction SilentlyContinue).TcpTestSucceeded; Get-RvWins

