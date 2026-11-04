# Claude hook: after Claude's turn (Stop) or at session end (SessionEnd), start update.ps1 hidden in the background.
# Stop: at most once every 10 minutes. SessionEnd (-Force): always.
# Started through WMI so it is not a child of Claude: a closing Claude session would otherwise kill it mid-sync.
param([switch]$Force, [int]$Minutes = 10)
$State = "$env:LOCALAPPDATA\bekassyl-sync"
New-Item -ItemType Directory -Force $State | Out-Null
$stamp = "$State\last-start.txt"
if (-not $Force -and (Test-Path $stamp) -and ((Get-Date) - (Get-Item $stamp).LastWriteTime).TotalMinutes -lt $Minutes) { exit 0 }
Set-Content $stamp (Get-Date -Format 's')
$upd = Join-Path $PSScriptRoot 'update.ps1'
$cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$upd`" -Quiet"
try {
    $si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ ShowWindow = [uint16]0 }
    $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; ProcessStartupInformation = $si }
    if ($r.ReturnValue -ne 0) { throw "Win32_Process.Create: $($r.ReturnValue)" }
} catch {
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$upd`"", '-Quiet')
}
exit 0
