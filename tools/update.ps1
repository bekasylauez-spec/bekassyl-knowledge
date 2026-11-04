# Синхрондау: GitHub-тағы жаңалықты алады, осы компьютердегі жаңа білімді (Obsidian, memory, чаттар, скрипттер) жібереді.
# Іске қосу:  powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\bekassyl-knowledge\tools\update.ps1"
# -Quiet: фонда (Claude hook) - құпиясөз терезесін ашпайды, қате болса тек логқа жазады.
param([string]$Work = "D:\РАБОЧКА", [switch]$Quiet)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$Repo  = "$env:USERPROFILE\Documents\bekassyl-knowledge"
$Vault = if (Test-Path "$Work\Bekassyl") { "$Work\Bekassyl" } else { "$env:USERPROFILE\Documents\Bekassyl" }
$Mem   = "$env:USERPROFILE\.claude\projects\$($Work -replace '[^A-Za-z0-9]', '-')\memory"
$State = "$env:LOCALAPPDATA\bekassyl-sync"
$Log   = "$State\sync.log"
New-Item -ItemType Directory -Force $State | Out-Null
function Say($m) { $l = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $env:COMPUTERNAME $m"; Add-Content $Log $l -Encoding UTF8; if (-not $Quiet) { Write-Host $m } }
if ($Quiet) { $env:GIT_TERMINAL_PROMPT = "0"; $env:GCM_INTERACTIVE = "never" }

# Бір уақытта екі синхрон болмасын
$lock = "$State\sync.lock"
if (Test-Path $lock) {
    $lp = [int]("0" + (Get-Content $lock -Raw -ErrorAction SilentlyContinue).Trim())
    $alive = $lp -and (Get-Process -Id $lp -ErrorAction SilentlyContinue)
    if ($alive -and ((Get-Date) - (Get-Item $lock).LastWriteTime).TotalMinutes -lt 15) { Say "өткізілді: басқа синхрон жүріп жатыр (PID $lp)"; return }
}
Set-Content $lock $PID
try {
    $lastSync = if (Test-Path "$State\last-ok.txt") { [datetime](Get-Content "$State\last-ok.txt" -Raw).Trim() } else { $null }

    # 1. GitHub-тан алу
    # Репо - тек жиналған көшірме (бастапқы файлдар дискте), сондықтан конфликт болса GitHub нұсқасына қайтарып, қайта жинаймыз
    $ErrorActionPreference = "Continue"
    if ((Test-Path "$Repo\.git\rebase-merge") -or (Test-Path "$Repo\.git\rebase-apply")) { git -C $Repo rebase --abort 2>&1 | Out-Null }
    $before = (git -C $Repo rev-parse HEAD).Trim()
    git -C $Repo pull --rebase --autostash -q 2>&1 | ForEach-Object { "$_" } | Out-Null
    if ($LASTEXITCODE -ne 0) {
        git -C $Repo rebase --abort 2>&1 | Out-Null
        git -C $Repo fetch -q origin 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { $ErrorActionPreference = "Stop"; throw "git fetch сәтсіз (интернет?)" }
        git -C $Repo reset -q --hard origin/main 2>&1 | Out-Null
        Say "конфликт: репо GitHub нұсқасына қайтарылды, осы компьютердегі қайта жиналады"
    }
    $ErrorActionPreference = "Stop"
    $after = (git -C $Repo rev-parse HEAD).Trim()

    # 2. Басқа компьютерден келген өзгерісті осында қою - тек мұнда соңғы синхроннан кейін өзгермеген файлдарға
    $env:PYTHONIOENCODING = "utf-8"
    $Py = & "$Repo\tools\findpy.ps1"
    if (-not $Py) { throw "Python табылмады (tools\setup.ps1 қайта іске қос)" }
    function RunPy { $ErrorActionPreference = 'Continue'; $o = & $Py @args 2>&1 | ForEach-Object { "$_" }; [pscustomobject]@{ Code = $LASTEXITCODE; Out = $o } }
    if ($before -ne $after) {
        New-Item -ItemType Directory -Force $Vault, $Mem | Out-Null
        $ls = if ($lastSync) { $lastSync.ToString('s') } else { '-' }
        $r = RunPy "$Repo\tools\build.py" restore $before $after $ls $Vault $Mem
        if ($r.Code -ne 0) { throw "restore: $($r.Out -join ' | ')" }
        Say "GitHub-тан алынды: $($r.Out -join '; ')"
    }

    # 3. Осы компьютердегіні репоға жинау
    $b = RunPy "$Repo\tools\build.py"
    if ($b.Code -ne 0) { throw "build.py: $($b.Out -join ' | ')" }
    $out = $b.Out

    # 4. Жіберу
    git -C $Repo add -A
    git -C $Repo diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        $n = (git -C $Repo diff --cached --name-only | Measure-Object).Count
        git -C $Repo commit -q -m "Жаңарту: $env:COMPUTERNAME $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        $ErrorActionPreference = "Continue"
        $po = git -C $Repo push -q 2>&1 | ForEach-Object { "$_" }
        $pc = $LASTEXITCODE
        $ErrorActionPreference = "Stop"
        if ($pc -ne 0) { throw "git push сәтсіз (GitHub-қа кіру керек болуы мүмкін): $($po -join ' | ')" }
        Say "GitHub жаңартылды: $n файл ($($out -join '; '))"
    } else { Say "жаңалық жоқ" }
    Set-Content "$State\last-ok.txt" (Get-Date -Format 's')
} catch {
    Say "ҚАТЕ: $($_.Exception.Message)"
    if (-not $Quiet) { throw }
} finally {
    Remove-Item $lock -ErrorAction SilentlyContinue
    $all = Get-Content $Log -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($all.Count -gt 500) { $all | Select-Object -Last 300 | Set-Content $Log -Encoding UTF8 }
    # LAN: copy this PC's log next to the shared work folder so BEKA-1 can read it
    if (Test-Path "$Work\.claude") { try { Copy-Item $Log "$Work\.claude\sync-$env:COMPUTERNAME.log" -Force } catch {} }
}
