# Жаңа компьютерге орнату: білім базасын GitHub-тан алып, Obsidian мен Claude memory-ге қояды, автосинхронды қосады.
# Іске қосу (PowerShell):  iex (irm https://raw.githubusercontent.com/bekasylauez-spec/bekassyl-knowledge/main/tools/setup.ps1).TrimStart([char]0xFEFF)
# BEKA-1/BEKA-2 (жергілікті желі): Obsidian мен memory ортақ папкада, оларға тиіспейді - тек Git пен автосинхрон.
param([string]$Work = "D:\РАБОЧКА")
$ErrorActionPreference = "Stop"
$Repo  = "$env:USERPROFILE\Documents\bekassyl-knowledge"
$Url   = "https://bekasylauez-spec@github.com/bekasylauez-spec/bekassyl-knowledge.git"

function Need($cmd, $id) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "Орнатылуда: $id"
        winget install --id $id -e --accept-source-agreements --accept-package-agreements
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    }
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "$cmd табылмады - орнатып, қайта іске қос" }
}
Need git Git.Git
Need python Python.Python.3.13

if (Test-Path "$Repo\.git") { git -C $Repo pull --rebase --autostash } else { git clone $Url $Repo }

# Жұмыс папкасы, Obsidian базасы, Claude memory (кілт: D:\РАБОЧКА -> D---------)
$hasDrive = Test-Path (Split-Path $Work -Qualifier)
$Vault = if ($hasDrive) { "$Work\Bekassyl" } else { "$env:USERPROFILE\Documents\Bekassyl" }
$Key = $Work -replace '[^A-Za-z0-9]', '-'
$Mem = "$env:USERPROFILE\.claude\projects\$Key\memory"
$wi = if ($hasDrive) { Get-Item $Work -Force -ErrorAction SilentlyContinue }
$lan = ($wi -and $wi.LinkType) -or ((Get-Item $Mem -Force -ErrorAction SilentlyContinue).LinkType)
if ($lan) {
    Write-Host "Ортақ папка (жергілікті желі): Obsidian мен memory BEKA-1-де, көшірмейміз."
} else {
    if ($hasDrive) { New-Item -ItemType Directory -Force $Work | Out-Null }
    New-Item -ItemType Directory -Force $Vault, $Mem | Out-Null
    # тек жоқ файлдар келеді, осы компьютердегі нұсқа өшпейді
    robocopy "$Repo\obsidian" $Vault /E /XC /XN /XO /NFL /NDL /NJH /NJS | Out-Null
    robocopy "$Repo\memory"   $Mem   /E /XC /XN /XO /NFL /NDL /NJH /NJS | Out-Null
    Write-Host "Obsidian -> $Vault, Claude memory -> $Mem"
}

# Obsidian осы базаны ашсын
powershell -NoProfile -ExecutionPolicy Bypass -File "$Repo\tools\obsidian-vault.ps1" -Vault $Vault

# Claude жұмыс істеп болған сайын GitHub-қа автосинхрон
$env:PYTHONIOENCODING = "utf-8"
python "$Repo\tools\install_autosync.py"

# Бірінші синхрон: GitHub-қа кіру сұралса - bekasylauez-spec аккаунтымен кір
powershell -NoProfile -ExecutionPolicy Bypass -File "$Repo\tools\update.ps1" -Work $Work
Write-Host "ДАЙЫН. Claude-ты қайта іске қос." -ForegroundColor Green
