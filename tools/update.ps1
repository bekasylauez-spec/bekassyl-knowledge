# Синхрондау: GitHub-тағы жаңалықты алады, осы компьютердегі жаңа білімді (Obsidian, memory, чаттар) жібереді.
# Іске қосу:  powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\bekassyl-knowledge\tools\update.ps1"
param([string]$Work = "D:\РАБОЧКА")
$ErrorActionPreference = "Stop"
$Repo  = "$env:USERPROFILE\Documents\bekassyl-knowledge"
$Vault = "$env:USERPROFILE\Documents\Bekassyl"
$Mem   = "$env:USERPROFILE\.claude\projects\$($Work -replace '[^A-Za-z0-9]', '-')\memory"

git -C $Repo pull --rebase --autostash
New-Item -ItemType Directory -Force $Vault, $Mem | Out-Null
robocopy "$Repo\obsidian" $Vault /E /XO /NFL /NDL /NJH /NJS | Out-Null
robocopy "$Repo\memory"   $Mem   /E /XO /NFL /NDL /NJH /NJS | Out-Null

python "$Repo\tools\build.py"
git -C $Repo add -A
git -C $Repo diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git -C $Repo commit -q -m "Жаңарту: $env:COMPUTERNAME $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git -C $Repo push
    Write-Host "GitHub жаңартылды"
} else { Write-Host "Жаңалық жоқ" }
