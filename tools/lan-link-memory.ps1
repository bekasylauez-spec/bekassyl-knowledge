# Общая память Claude для BEKA-2: память лежит на BEKA-1 в РАБОЧКА\.claude\memory,
# здесь вместо своей папки memory ставится ссылка на неё. Запускать на BEKA-2 от администратора.
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
$Log = "$env:TEMP\link-memory.log"
try { Start-Transcript $Log -Force | Out-Null } catch {}
try {
Write-Host "Комп: $env:COMPUTERNAME, пользователь: $env:USERNAME, профиль: $env:USERPROFILE, время: $stamp"

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'Нужно запустить от администратора (правой кнопкой -> Запуск от имени администратора).' -ForegroundColor Red
    return
}
if ($env:COMPUTERNAME -eq 'BEKA-1') { Write-Host 'Это BEKA-1 - здесь запускать не нужно, память уже тут.' -ForegroundColor Yellow; return }

# 1. Найти общую папку на BEKA-1
$Unc = $null
foreach ($h in 'BEKA-1', '192.168.0.107') {
    if (Test-Path "\\$h\РАБОЧКА\.claude\memory\MEMORY.md") { $Unc = "\\$h\РАБОЧКА"; break }
}
if (-not $Unc) { Write-Host 'Не вижу \\BEKA-1\РАБОЧКА\.claude\memory. Проверь, что BEKA-1 включён и папка открывается.' -ForegroundColor Red; return }
$Shared = "$Unc\.claude\memory"
Write-Host "Общая память: $Shared" -ForegroundColor Green

# 2. D:\РАБОЧКА - если это ссылка на старое имя DESKTOP-0BGBHI9, перенаправить на BEKA-1
$Work = 'D:\РАБОЧКА'
$wi = Get-Item $Work -Force -ErrorAction SilentlyContinue
if ($wi -and $wi.LinkType -eq 'SymbolicLink') {
    $t = @($wi.Target)[0]
    if ($t -match 'DESKTOP-0BGBHI9' -or -not (Test-Path "$Work\.claude")) {
        Write-Host "D:\РАБОЧКА указывала на $t - перенаправляю на $Unc"
        cmd /c rmdir "$Work" | Out-Null
        New-Item -ItemType SymbolicLink -Path $Work -Target $Unc | Out-Null
    } else { Write-Host "D:\РАБОЧКА -> $t (работает)" }
} elseif (-not $wi) {
    New-Item -ItemType SymbolicLink -Path $Work -Target $Unc | Out-Null
    Write-Host "Создана ссылка D:\РАБОЧКА -> $Unc"
} else { Write-Host 'D:\РАБОЧКА - обычная папка на этом компе, не трогаю.' -ForegroundColor Yellow }

# 3. Папка памяти Claude этого компа
$Proj = "$env:USERPROFILE\.claude\projects\D---------"
$Mem  = "$Proj\memory"
New-Item -ItemType Directory -Force $Proj | Out-Null
$mi = Get-Item $Mem -Force -ErrorAction SilentlyContinue

if ($mi -and $mi.LinkType) {
    Write-Host "memory уже ссылка -> $(@($mi.Target)[0])"
    cmd /c rmdir "$Mem" | Out-Null
} elseif ($mi) {
    # Перенести то, чего нет на BEKA-1; одинаковые имена с разным текстом - оставить версию BEKA-1, копию BEKA-2 сохранить
    $conf = "$Shared\_с_BEKA-2_$stamp"
    $new = 0; $diff = @()
    foreach ($f in Get-ChildItem $Mem -File) {
        if ($f.Name -eq 'MEMORY.md') { continue }
        $s = Join-Path $Shared $f.Name
        if (-not (Test-Path $s)) { Copy-Item $f.FullName $s; $new++ }
        elseif ((Get-FileHash $f.FullName).Hash -ne (Get-FileHash $s).Hash) {
            New-Item -ItemType Directory -Force $conf | Out-Null; Copy-Item $f.FullName $conf; $diff += $f.Name
        }
    }
    # MEMORY.md: добавить строки, которых нет в общем индексе (по имени файла в ссылке)
    $li = "$Mem\MEMORY.md"
    if (Test-Path $li) {
        $sharedIdx = Get-Content "$Shared\MEMORY.md" -Encoding UTF8
        $known = $sharedIdx | ForEach-Object { if ($_ -match '\]\(([^)]+)\)') { $Matches[1] } }
        $add = Get-Content $li -Encoding UTF8 | Where-Object { $_ -match '\]\(([^)]+)\)' -and $known -notcontains $Matches[1] }
        $addN = @($add).Count
        if ($add) {
            $raw = [IO.File]::ReadAllText("$Shared\MEMORY.md")
            if ($raw -and -not $raw.EndsWith("`n")) { $add = @('') + $add }
            Add-Content "$Shared\MEMORY.md" $add -Encoding UTF8
        }
        Write-Host "В общий MEMORY.md добавлено строк: $addN"
    }
    Write-Host "Новых заметок с BEKA-2 перенесено: $new"
    if ($diff) { Write-Host "Разные версии (оставлена версия BEKA-1, копии BEKA-2 в $conf): $($diff -join ', ')" -ForegroundColor Yellow }
    Rename-Item $Mem "memory.bak-$stamp"
    Write-Host "Старая память BEKA-2 сохранена: $Proj\memory.bak-$stamp"
}

New-Item -ItemType SymbolicLink -Path $Mem -Target $Shared | Out-Null
$n = (Get-ChildItem $Mem -File | Measure-Object).Count
Write-Host "ГОТОВО: $Mem -> $Shared ($n файлов). Перезапусти Claude на этом компе." -ForegroundColor Green
Get-Item $Mem -Force | Format-List FullName, LinkType, Target
Get-ChildItem "$env:USERPROFILE\.claude\projects" -Force | Format-Table Name, LinkType -AutoSize
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace
} finally {
    try { Stop-Transcript | Out-Null } catch {}
    foreach ($h in 'BEKA-1', '192.168.0.107') {
        try { Copy-Item $Log "\\$h\РАБОЧКА\.claude\link-memory-$env:COMPUTERNAME.log" -Force; Write-Host "Лог отправлен на $h"; break } catch {}
    }
}
