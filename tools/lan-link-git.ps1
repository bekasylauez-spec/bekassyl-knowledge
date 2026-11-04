# BEKA-2: Git + GitHub автосинхрон. Права администратора не нужны (winget может спросить сам).
$ErrorActionPreference = 'Stop'
$Log = "$env:TEMP\link-git.log"
try { Start-Transcript $Log -Force | Out-Null } catch {}
function Native { $ErrorActionPreference = 'Continue'; & $args[0] @($args | Select-Object -Skip 1) 2>&1 | ForEach-Object { Write-Host "  $_" }; return $LASTEXITCODE }
try {
    Write-Host "Комп: $env:COMPUTERNAME, пользователь: $env:USERNAME"
    $Repo = "$env:USERPROFILE\Documents\bekassyl-knowledge"
    $Url  = 'https://bekasylauez-spec@github.com/bekasylauez-spec/bekassyl-knowledge.git'
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host 'Устанавливаю Git...'
        Native winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements | Out-Null
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    }
    if (Test-Path "$Repo\.git") {
        # Репо - только собранная копия: при конфликте возвращаем к версии GitHub, всё пересоберётся из файлов на диске
        if ((Test-Path "$Repo\.git\rebase-merge") -or (Test-Path "$Repo\.git\rebase-apply")) { Native git -C $Repo rebase --abort | Out-Null }
        if ((Native git -C $Repo fetch origin) -ne 0) { throw 'git fetch не прошёл (интернет?)' }
        Native git -C $Repo reset --hard origin/main | Out-Null
    } else {
        if ((Native git clone $Url $Repo) -ne 0) { throw 'git clone не прошёл' }
    }
    Native git -C $Repo log -1 --format='репо: %h %s' | Out-Null
    & "$Repo\tools\setup.ps1"
    Write-Host 'ГОТОВО. Перезапусти Claude на этом компе.' -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red; Write-Host $_.ScriptStackTrace
} finally {
    try { Stop-Transcript | Out-Null } catch {}
    foreach ($h in 'BEKA-1', '192.168.0.107') {
        try { Copy-Item $Log "\\$h\РАБОЧКА\.claude\link-git-$env:COMPUTERNAME.log" -Force; Write-Host "Лог отправлен на $h"; break } catch {}
    }
}
