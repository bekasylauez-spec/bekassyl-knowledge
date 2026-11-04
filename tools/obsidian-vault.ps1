# Obsidian на BEKA-2: открыть общую базу D:\РАБОЧКА\Bekassyl (она лежит на BEKA-1).
# Права администратора не нужны. Параметры только для проверки.
param([string]$AppData = $env:APPDATA, [string]$Docs = [Environment]::GetFolderPath('MyDocuments'),
      [string]$Vault = 'D:\РАБОЧКА\Bekassyl', [switch]$NoLaunch)
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
$Log = "$env:TEMP\link-obsidian.log"
try { Start-Transcript $Log -Force | Out-Null } catch {}
try {
Write-Host "Комп: $env:COMPUTERNAME, пользователь: $env:USERNAME, время: $stamp"

# 1. Общая база доступна?
if (-not (Test-Path "$Vault\.obsidian")) {
    Write-Host "Не вижу $Vault\.obsidian. Сначала должна работать D:\РАБОЧКА (link-memory.cmd)." -ForegroundColor Red; return
}
$n = (Get-ChildItem $Vault -Recurse -File -Filter *.md | Measure-Object).Count
Write-Host "Общая база: $Vault ($n заметок)" -ForegroundColor Green

# 2. Obsidian установлен?
$exe = @("$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe", "$env:LOCALAPPDATA\Obsidian\Obsidian.exe",
         "$env:ProgramFiles\Obsidian\Obsidian.exe", "${env:ProgramFiles(x86)}\Obsidian\Obsidian.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
    $cmd = (Get-ItemProperty 'Registry::HKEY_CLASSES_ROOT\obsidian\shell\open\command' -ErrorAction SilentlyContinue).'(default)'
    if ($cmd -match '"([^"]+Obsidian\.exe)"') { $exe = $Matches[1] }
}
if ($exe) { Write-Host "Obsidian: $exe" } else { Write-Host 'Obsidian не установлен. Скачай с https://obsidian.md и установи, потом запусти этот файл снова.' -ForegroundColor Yellow }

# 3. Закрыть Obsidian (при выходе он перезаписывает свои настройки)
if (-not $NoLaunch) {
    $p = Get-Process Obsidian -ErrorAction SilentlyContinue
    if ($p) { Write-Host 'Закрываю Obsidian...'; $p | ForEach-Object { $_.CloseMainWindow() | Out-Null }; Start-Sleep 3
              Get-Process Obsidian -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep 1 }
}

# 4. Старые локальные копии базы: перенести в общую только те заметки, которых там нет
$cfgDir = "$AppData\obsidian"; $cfg = "$cfgDir\obsidian.json"
$old = @()
if (Test-Path $cfg) {
    $j = Get-Content $cfg -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($pr in @($j.vaults.PSObject.Properties)) { $old += $pr.Value.path }
}
$old += Join-Path $Docs 'Bekassyl'
$vaultFull = (Get-Item $Vault).FullName.TrimEnd('\')
foreach ($o in ($old | Select-Object -Unique)) {
    if (-not $o -or -not (Test-Path $o)) { continue }
    $oi = Get-Item $o -Force
    if ($oi.LinkType -or $oi.FullName.TrimEnd('\') -ieq $vaultFull) { continue }   # ссылка или сама общая база
    $files = Get-ChildItem $o -Recurse -File -Force | Where-Object { $_.FullName -notmatch '\\\.(obsidian|trash|git)\\' }
    $added = 0; $newer = @()
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($oi.FullName.TrimEnd('\').Length + 1)
        $dst = Join-Path $Vault $rel
        if (-not (Test-Path $dst)) {
            New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
            Copy-Item $f.FullName $dst; $added++
        } elseif ($f.LastWriteTime -gt (Get-Item $dst).LastWriteTime.AddSeconds(2) -and
                  (Get-FileHash $f.FullName).Hash -ne (Get-FileHash $dst).Hash) {
            $h = (Get-FileHash $f.FullName).Hash
            $saved = Get-ChildItem (Join-Path $Vault '99_Changelog') -Directory -Filter "_с_$($env:COMPUTERNAME)_*" -ErrorAction SilentlyContinue |
                     Where-Object { $s = Join-Path $_.FullName $rel; (Test-Path $s) -and (Get-FileHash $s).Hash -eq $h }
            if (-not $saved) { $newer += $rel }
        }
    }
    Write-Host "Локальная копия $o : перенесено новых файлов $added"
    if ($newer) {
        $keep = Join-Path $Vault "99_Changelog\_с_$($env:COMPUTERNAME)_$stamp"
        foreach ($r in $newer) { $d = Join-Path $keep $r; New-Item -ItemType Directory -Force (Split-Path $d) | Out-Null; Copy-Item (Join-Path $o $r) $d }
        Write-Host "На этом компе новее, чем в общей базе ($($newer.Count)): сохранены в $keep - разберу вручную:" -ForegroundColor Yellow
        $newer | ForEach-Object { Write-Host "   $_" }
    }
}

# 5. obsidian.json: общая база - единственная открытая
New-Item -ItemType Directory -Force $cfgDir | Out-Null
if (Test-Path $cfg) { Copy-Item $cfg "$cfg.bak-$stamp"; Write-Host "Копия настроек: $cfg.bak-$stamp" }
$vaults = [ordered]@{}; $id = $null
if ($j -and $j.vaults) {
    foreach ($pr in @($j.vaults.PSObject.Properties)) {
        $v = [ordered]@{}; foreach ($q in $pr.Value.PSObject.Properties) { $v[$q.Name] = $q.Value }
        $v['open'] = $false
        if ("$($v['path'])".TrimEnd('\') -ieq $Vault.TrimEnd('\')) { $id = $pr.Name }
        $vaults[$pr.Name] = $v
    }
}
if (-not $id) { $id = -join ((1..16) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) }); $vaults[$id] = [ordered]@{ path = $Vault } }
$vaults[$id]['path'] = $Vault
$vaults[$id]['ts'] = [long]([DateTimeOffset]::Now.ToUnixTimeMilliseconds())
$vaults[$id]['open'] = $true
$out = [ordered]@{}
if ($j) { foreach ($q in $j.PSObject.Properties) { if ($q.Name -ne 'vaults') { $out[$q.Name] = $q.Value } } }
$out['vaults'] = $vaults
[IO.File]::WriteAllText($cfg, ($out | ConvertTo-Json -Depth 10 -Compress), (New-Object Text.UTF8Encoding $false))   # без BOM, иначе Obsidian не прочитает
Write-Host "obsidian.json: открывается $Vault" -ForegroundColor Green

# 6. Запуск
if ($exe -and -not $NoLaunch) { Start-Process $exe; Write-Host 'Obsidian запущен.' }
Write-Host 'ГОТОВО.' -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red; Write-Host $_.ScriptStackTrace
} finally {
    try { Stop-Transcript | Out-Null } catch {}
    if (-not $NoLaunch) {
        foreach ($h in 'BEKA-1', '192.168.0.107') {
            try { Copy-Item $Log "\\$h\РАБОЧКА\.claude\link-obsidian-$env:COMPUTERNAME.log" -Force; Write-Host "Лог отправлен на $h"; break } catch {}
        }
    }
}
