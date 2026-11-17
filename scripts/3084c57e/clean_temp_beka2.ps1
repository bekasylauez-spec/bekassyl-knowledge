# BEKA-2: C:\ Temp қоқысын тазалау (AutoCAD/Revit уақытша файлдары, ескі сессиялардың ауыр файлдары)
# Әдепкі: dry-run. -Apply болса ғана өшіреді. Лог: scratchpad\clean_temp_log.tsv
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$sp   = 'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\3084c57e-bfd6-4f37-98c3-78b360193443\scratchpad'
$temp = 'C:\Users\beka\AppData\Local\Temp'
$curSession = '3084c57e-bfd6-4f37-98c3-78b360193443'
$now  = Get-Date
$log  = New-Object System.Collections.Generic.List[string]

$busy = Get-Process | Where-Object { $_.ProcessName -match '^(acad|accoreconsole|revit|LiraSapr|LirAnSvr.*|Installer|AdODIS.*|setup)$' }
if ($busy) { Write-Output ("STOP: running -> " + (($busy | ForEach-Object ProcessName | Sort-Object -Unique) -join ', ')); exit 1 }

$cats = [ordered]@{}
function Add-Item([string]$cat, [string]$path, [long]$size, [string]$kind) {
    if (-not $cats.Contains($cat)) { $cats[$cat] = [pscustomobject]@{N=0; Bytes=0L; Items=(New-Object System.Collections.Generic.List[object])} }
    $c = $cats[$cat]; $c.N++; $c.Bytes += $size; $c.Items.Add([pscustomobject]@{Path=$path; Size=$size; Kind=$kind})
}

# 1) Temp түбі
$di = New-Object IO.DirectoryInfo $temp
foreach ($f in $di.EnumerateFiles()) {
    $age = ($now - $f.LastWriteTime).TotalHours
    if ($f.Name -like 'UND*.ac$') { Add-Item 'AutoCAD undo UND*.ac$' $f.FullName $f.Length 'file'; continue }
    if ($f.Extension -eq '' -and $f.Name -match '^[0-9A-Fa-f]{4,}$' -and $age -gt 24) { Add-Item 'AutoCAD plot temp (hex, >1 күн)' $f.FullName $f.Length 'file'; continue }
    if ($f.Extension -ieq '.tmp' -and $age -gt 48) { Add-Item '.tmp (>2 күн)' $f.FullName $f.Length 'file'; continue }
    if ($f.Extension -ieq '.dmp' -and $age -gt 48) { Add-Item '.dmp (>2 күн)' $f.FullName $f.Length 'file'; continue }
}

# 2) GUID атаулы temp папкалар (AutoCAD/Revit/IDEA сессия қалдықтары), 12 сағаттан ескі, ішінде reparse жоқ
foreach ($d in $di.EnumerateDirectories()) {
    if ($d.Name -notmatch '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$') { continue }
    if (($now - $d.LastWriteTime).TotalHours -lt 12) { continue }
    $fs = @(Get-ChildItem -LiteralPath $d.FullName -Recurse -Force -ErrorAction SilentlyContinue)
    if ($fs | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { Write-Output "skip (reparse inside): $($d.FullName)"; continue }
    if ($fs | Where-Object { $_.Name -ieq 'DismHost.exe' }) { continue }
    $sz = ($fs | Where-Object { -not $_.PSIsContainer } | Measure-Object Length -Sum).Sum; if (-not $sz) { $sz = 0 }
    Add-Item 'AutoCAD/Revit GUID temp папкалар' $d.FullName $sz 'dir'
}

# 3) Ескі Claude сессияларының (48 сағаттан ескі) ауыр қайта жасалатын файлдары; скрипт/.lir/.dwg/.pdf/.rfa/.rvt қалады
$heavy = '.output','.dxf','.png','.jpg','.jpeg','.bmp','.gif','.webp','.mp4','.wav','.mp3','.bak','.~lir','.~~lir','.tmp','.emf'
foreach ($proj in (New-Object IO.DirectoryInfo "$temp\claude").EnumerateDirectories()) {
    foreach ($sess in $proj.EnumerateDirectories()) {
        if ($sess.Name -eq $curSession) { continue }
        $files = @($sess.EnumerateFiles('*', [IO.SearchOption]::AllDirectories))
        if (-not $files) { continue }
        $newest = ($files | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        if (($now - $newest).TotalHours -lt 48) { continue }
        foreach ($f in $files) { if ($heavy -contains $f.Extension.ToLower()) { Add-Item 'Ескі Claude сессия: ауыр файлдар' $f.FullName $f.Length 'file' } }
    }
}

$total = 0L
foreach ($k in $cats.Keys) { $c = $cats[$k]; $total += $c.Bytes; '{0,-40} {1,7} дана {2,9:N2} ГБ' -f $k, $c.N, ($c.Bytes/1GB) }
'{0,-40} {1,7}      {2,9:N2} ГБ' -f 'БАРЛЫҒЫ', '', ($total/1GB)
if (-not $Apply) { 'DRY-RUN (өшірілген жоқ)'; exit 0 }

$freed = 0L; $fail = 0
foreach ($k in $cats.Keys) {
    foreach ($it in $cats[$k].Items) {
        try {
            if ($it.Kind -eq 'dir') {
                cmd /c rd /s /q "`"$($it.Path)`"" 2>$null
                if (Test-Path -LiteralPath $it.Path) { throw 'still exists' }
            } else { [IO.File]::Delete($it.Path) }
            $freed += $it.Size; $log.Add("OK`t$k`t$($it.Size)`t$($it.Path)")
        } catch { $fail++; $log.Add("FAIL`t$k`t$($it.Size)`t$($it.Path)`t$($_.Exception.Message)") }
    }
}
[IO.File]::WriteAllLines("$sp\clean_temp_log.tsv", $log, (New-Object Text.UTF8Encoding($false)))
'ӨШІРІЛДІ: {0:N2} ГБ, қате: {1}' -f ($freed/1GB), $fail
