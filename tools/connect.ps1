# ЕКІНШІ компьютер: негізгі компьютердегі РАБОЧКА-ны осында D:\РАБОЧКА болып ашады, білім базасын орнатады.
# Әкімші PowerShell-де:  iex (irm https://raw.githubusercontent.com/bekasylauez-spec/bekassyl-knowledge/main/tools/connect.ps1).TrimStart([char]0xFEFF)
param([string[]]$Hosts = @("DESKTOP-0BGBHI9", "192.168.0.107"), [string]$MainUser = "Admin")
$ErrorActionPreference = "Stop"
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw "PowerShell-ді әкімші ретінде ашыңыз: Пуск-ты оң басып -> Терминал (администратор)" }

Get-NetConnectionProfile | Where-Object NetworkCategory -eq "Public" | Set-NetConnectionProfile -NetworkCategory Private
Enable-NetFirewallRule -Group "@FirewallAPI.dll,-32752"   # Network Discovery

$Unc = $null
foreach ($h in $Hosts) {
    if (-not (Test-Connection $h -Count 1 -Quiet)) { continue }
    if (-not (Test-Path "\$h\РАБОЧКА")) {
        Write-Host "Негізгі компьютердің ($h) Windows құпиясөзін енгізіңіз:"
        cmdkey /add:$h /user:"$($Hosts[0])\$MainUser" /pass
    }
    if (Test-Path "\$h\РАБОЧКА") { $Unc = "\$h\РАБОЧКА"; break }
}
if (-not $Unc) { throw "Негізгі компьютер табылмады. Онда share-main.ps1 іске қосылғанын және кабель жалғанғанын тексеріңіз." }

# Claude memory жолға байланған, сондықтан әр компьютерде бірдей D:\РАБОЧКА
$Work = if (Test-Path "D:\") { "D:\РАБОЧКА" } else { "C:\РАБОЧКА" }
$item = Get-Item $Work -Force -ErrorAction SilentlyContinue
if ($item -and -not $item.LinkType) {
    if (Get-ChildItem $Work -Force | Select-Object -First 1) { Rename-Item $Work "$Work (осы компьютер)" }
    else { Remove-Item $Work }
}
if (-not (Get-Item $Work -Force -ErrorAction SilentlyContinue)) { New-Item -ItemType SymbolicLink -Path $Work -Target $Unc | Out-Null }
Write-Host "$Work -> $Unc"

# Білім базасы (Obsidian, Claude memory)
$f = "$env:TEMP\bekassyl-setup.ps1"
Invoke-WebRequest https://raw.githubusercontent.com/bekasylauez-spec/bekassyl-knowledge/main/tools/setup.ps1 -OutFile $f -UseBasicParsing
& $f -Work $Work
