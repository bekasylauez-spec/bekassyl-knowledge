# BEKA-2: Git + GitHub автосинхрон. Права администратора не нужны (winget может спросить сам).
$ErrorActionPreference = 'Stop'
$Log = "$env:TEMP\link-git.log"
try { Start-Transcript $Log -Force | Out-Null } catch {}
try {
    Write-Host "Комп: $env:COMPUTERNAME, пользователь: $env:USERNAME"
    $Repo = "$env:USERPROFILE\Documents\bekassyl-knowledge"
    $Url  = 'https://bekasylauez-spec@github.com/bekasylauez-spec/bekassyl-knowledge.git'
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host 'Устанавливаю Git...'
        winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    }
    if (Test-Path "$Repo\.git") { git -C $Repo pull --rebase --autostash } else { git clone $Url $Repo }
    if ($LASTEXITCODE -ne 0) { throw 'git не смог получить репозиторий' }
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
