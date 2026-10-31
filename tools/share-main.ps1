# НЕГІЗГІ компьютер (файлдар осында): D:\РАБОЧКА папкасын жергілікті желіге ашады — оқу және өзгерту.
# Әкімші PowerShell-де:  iex (irm https://raw.githubusercontent.com/bekasylauez-spec/bekassyl-knowledge/main/tools/share-main.ps1).TrimStart([char]0xFEFF)
$ErrorActionPreference = "Stop"
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw "PowerShell-ді әкімші ретінде ашыңыз: Пуск-ты оң басып -> Терминал (администратор)" }

$Work = "D:\РАБОЧКА"; $Name = "РАБОЧКА"
# Ethernet "Public" болса, Windows ортақ папкаларды бұғаттайды -> "Private"
Get-NetConnectionProfile | Where-Object NetworkCategory -eq "Public" | Set-NetConnectionProfile -NetworkCategory Private
Enable-NetFirewallRule -Group "@FirewallAPI.dll,-28502"   # File and Printer Sharing
Enable-NetFirewallRule -Group "@FirewallAPI.dll,-32752"   # Network Discovery

$user = "$env:COMPUTERNAME\$env:USERNAME"
if (Get-SmbShare -Name $Name -ErrorAction SilentlyContinue) { Remove-SmbShare -Name $Name -Force }
New-SmbShare -Name $Name -Path $Work -FullAccess $user | Out-Null

$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet* | Select-Object -First 1).IPAddress
Write-Host ""
Write-Host "Дайын. Екінші компьютер үшін: \$env:COMPUTERNAME\$Name  (IP: $ip)"
Write-Host "Кіру аты: $user  — құпиясөзі осы компьютердің Windows құпиясөзі."
