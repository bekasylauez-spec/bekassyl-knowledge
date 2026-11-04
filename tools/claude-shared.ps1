# Claude-тың ортақ жады мен ережелері осы компьютердің кез келген папкасында бірдей жүктелсін.
# 1) Сессия басқа жолдан ашылса (BEKA-2: R:\ = \\192.168.0.107\рабочка -> projects\R--) оның memory папкасы
#    негізгі memory-ге junction болады: жазбалар бір жерде, қай папкада ашсаң да бірдей.
# 2) tools\CLAUDE.global.md -> %USERPROFILE%\.claude\CLAUDE.md ішіндегі белгіленген блок (қалған мәтінге тиіспейді).
# Админ құқығы керек емес. setup.ps1 шақырады; қолмен:  powershell -ExecutionPolicy Bypass -File claude-shared.ps1
param([string]$Work = "D:\РАБОЧКА", [string]$Mem = "")
$ErrorActionPreference = "Stop"
$Proj = "$env:USERPROFILE\.claude\projects"
$Key  = $Work -replace '[^A-Za-z0-9]', '-'
if (-not $Mem) { $Mem = "$Proj\$Key\memory" }
if (-not (Test-Path "$Mem\MEMORY.md")) { Write-Host "memory табылмады: $Mem - алдымен setup.ps1 / link-memory" -ForegroundColor Yellow }
else {
    # Жұмыс папкасына апаратын басқа дискілер: түбірінде .claude\memory\MEMORY.md бар (R:, subst, т.б.)
    $workRoot = if ($Work -match '^[A-Za-z]:') { $Work.Substring(0, 2).ToUpper() + '\' } else { '' }
    $roots = @(Get-PSDrive -PSProvider FileSystem -ErrorAction SilentlyContinue | ForEach-Object { $_.Root } |
        Where-Object { $_ -match '^[A-Za-z]:\\$' -and $_.ToUpper() -ne $workRoot -and (Test-Path (Join-Path $_ '.claude\memory\MEMORY.md')) })
    # Админ ретінде іске қосылса желілік дискілер көрінбейді - тұрақты қосылған дискілерді тізілімнен де аламыз
    foreach ($nk in Get-ChildItem HKCU:\Network -ErrorAction SilentlyContinue) {
        $r = $nk.PSChildName.ToUpper() + ':\'
        $rp = (Get-ItemProperty $nk.PSPath -ErrorAction SilentlyContinue).RemotePath
        if ($rp -and $roots -notcontains $r -and $r -ne $workRoot -and (Test-Path (Join-Path $rp '.claude\memory\MEMORY.md'))) { $roots += $r }
    }
    foreach ($r in $roots) {
        $k = $r -replace '[^A-Za-z0-9]', '-'           # R:\ -> R--
        if ($k -eq $Key) { continue }
        $am = "$Proj\$k\memory"
        New-Item -ItemType Directory -Force "$Proj\$k" | Out-Null
        $ai = Get-Item $am -Force -ErrorAction SilentlyContinue
        if ($ai -and $ai.LinkType) {
            cmd /c rmdir "$am" | Out-Null                # ескі сілтеме (ішіндегі файлдарға тимейді)
        } elseif ($ai -and -not (Get-ChildItem $am -Force)) {
            Remove-Item $am                                # бос папка (Claude өзі жасаған) - жай алмастырамыз
        } elseif ($ai) {
            # өз жазбалары болса: жоқтарын негізгі memory-ге, индекс жолдарын MEMORY.md-ге, папканы backup
            $known = Get-Content "$Mem\MEMORY.md" -Encoding UTF8 | ForEach-Object { if ($_ -match '\]\(([^)]+)\)') { $Matches[1] } }
            $moved = 0
            foreach ($f in Get-ChildItem $am -File -Filter *.md) {
                if ($f.Name -ne 'MEMORY.md' -and -not (Test-Path (Join-Path $Mem $f.Name))) { Copy-Item $f.FullName $Mem; $moved++ }
            }
            if (Test-Path "$am\MEMORY.md") {
                $add = @(Get-Content "$am\MEMORY.md" -Encoding UTF8 | Where-Object { $_ -match '\]\(([^)]+)\)' -and $known -notcontains $Matches[1] })
                if ($add.Count) { Add-Content "$Mem\MEMORY.md" (@('') + $add) -Encoding UTF8 }
            }
            $bak = "memory.bak-" + (Get-Date -Format 'yyyy-MM-dd_HHmm')
            Rename-Item $am $bak
            Write-Host "$am ішіндегі $moved жазба негізгі memory-ге көшті, ескі папка: $bak"
        }
        cmd /c mklink /J "$am" "$Mem" | Out-Null
        $n = @(Get-ChildItem $am -File -Filter *.md -ErrorAction SilentlyContinue).Count
        $ok = (Test-Path "$am\MEMORY.md")
        Write-Host ("memory: $am -> $Mem ($n жазба)" + $(if ($ok) { '' } else { ' - ҚАТЕ: MEMORY.md көрінбейді' })) -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })
    }
    if (-not $roots) { Write-Host "Жұмыс папкасына апаратын басқа диск жоқ (R: т.б.) - junction керек емес." }
}

# Барлық жобаға ортақ ережелер: ~/.claude/CLAUDE.md (memory емес, кез келген папкада жүктеледі)
$src = Join-Path $PSScriptRoot 'CLAUDE.global.md'
if (Test-Path $src) {
    $G = "$env:USERPROFILE\.claude\CLAUDE.md"
    $b = '<!-- bekassyl-global:start (tools\CLAUDE.global.md, setup.ps1 жаңартады - осы блокты қолмен түзетпе) -->'
    $e = '<!-- bekassyl-global:end -->'
    $block = $b + "`r`n" + [IO.File]::ReadAllText($src).Trim() + "`r`n" + $e
    $old = if (Test-Path $G) { [IO.File]::ReadAllText($G) } else { '' }
    $rx = [regex]'<!-- bekassyl-global:start[^>]*-->[\s\S]*?<!-- bekassyl-global:end -->'
    $new = if ($rx.IsMatch($old)) { $rx.Replace($old, [Text.RegularExpressions.MatchEvaluator] { param($m) $block }, 1) }
           elseif ($old.Trim()) { $old.TrimEnd() + "`r`n`r`n" + $block + "`r`n" } else { $block + "`r`n" }
    if ($new -ne $old) {
        if ($old) { Copy-Item $G "$G.bak" -Force }
        New-Item -ItemType Directory -Force (Split-Path $G) | Out-Null
        [IO.File]::WriteAllText($G, $new, (New-Object Text.UTF8Encoding $false))
        Write-Host "Ортақ ережелер -> $G" -ForegroundColor Green
    } else { Write-Host "Ортақ ережелер өзгеріссіз: $G" }
}
