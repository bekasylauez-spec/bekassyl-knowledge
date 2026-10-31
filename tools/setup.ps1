# Жаңа компьютерге орнату: білім базасын GitHub-тан алып, Obsidian мен Claude memory-ге қояды.
# Іске қосу (PowerShell):  irm https://raw.githubusercontent.com/bekasylauez-spec/bekassyl-knowledge/main/tools/setup.ps1 | iex
param([string]$Work = "D:\РАБОЧКА")
$ErrorActionPreference = "Stop"
$Repo  = "$env:USERPROFILE\Documents\bekassyl-knowledge"
$Vault = "$env:USERPROFILE\Documents\Bekassyl"
$Url   = "https://bekasylauez-spec@github.com/bekasylauez-spec/bekassyl-knowledge.git"

function Need($cmd, $id) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        winget install --id $id -e --accept-source-agreements --accept-package-agreements
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    }
}
Need git Git.Git
Need python Python.Python.3.13

if (Test-Path "$Repo\.git") { git -C $Repo pull --ff-only } else { git clone $Url $Repo }

# Claude memory папкасы жұмыс папкасының жолынан шығады: D:\РАБОЧКА -> D---------
$Key = $Work -replace '[^A-Za-z0-9]', '-'
$Mem = "$env:USERPROFILE\.claude\projects\$Key\memory"
New-Item -ItemType Directory -Force $Work, $Vault, $Mem | Out-Null

# /XO: тек жаңа файлдар келеді, осы компьютердегі жаңалау нұсқа өшпейді
robocopy "$Repo\obsidian" $Vault /E /XO /NFL /NDL /NJH /NJS | Out-Null
robocopy "$Repo\memory"   $Mem   /E /XO /NFL /NDL /NJH /NJS | Out-Null

Write-Host "Дайын: Obsidian -> $Vault, Claude memory -> $Mem, жұмыс папкасы -> $Work"
