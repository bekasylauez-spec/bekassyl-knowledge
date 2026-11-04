# ЛИРА-САПР 2024: интерфейсті стандарт (ленталы) күйде ұстау.
# ЛИРА жабық кезде ғана жұмыс істейді (ашық ЛИРА жабылғанда реестрді өзі қайта жазады).
# Бұзылу белгісі: Workspace\RibbonStyle != 2 немесе ToolBars = 1 (классикалық панельдер).
# Қалпына келтіру: Workspace кілтін өшіріп, golden .reg импорттау (жоқ болса — ЛИРА әдепкісі = лента).

$ErrorActionPreference = 'SilentlyContinue'
$dir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$golden = Join-Path $dir 'Workspace_standard.reg'
$log    = Join-Path $dir 'lira_guard.log'
$key    = 'HKCU:\Software\LIRA SAPR\LIRA SAPR 2024\VISOR-SAPR\WorkspaceTEST'
$keyReg = 'HKCU\Software\LIRA SAPR\LIRA SAPR 2024\VISOR-SAPR\WorkspaceTEST'

function Log($m) { Add-Content -Path $log -Value ("{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $m) -Encoding UTF8 }



$ws = Get-ItemProperty -Path $key
$broken = (-not $ws) -or ($ws.RibbonStyle -ne 2) -or ($ws.ToolBars -eq 1)

if (-not $broken) {
    # Дұрыс күйдің эталонын бір рет сақтап қою (ЛИРА жабылған соң толық жазылған күй).
    if (-not (Test-Path $golden) -and $ws) {
        reg export $keyReg $golden /y | Out-Null
        Log "golden сақталды"
    }
    exit 0
}

if (-not $ws) { exit 0 }   # кілт жоқ = ЛИРА әдепкісі (лента), түзетудің керегі жоқ

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
New-Item -ItemType Directory -Force (Join-Path $dir 'backup') | Out-Null
reg export $keyReg (Join-Path $dir "backup\Workspace_broken_$stamp.reg") /y | Out-Null
reg delete $keyReg /f | Out-Null
if (Test-Path $golden) { reg import $golden 2>$null | Out-Null; $src = 'golden' } else { $src = 'әдепкі' }
Log ("бұзылған күй табылды (RibbonStyle={0}, ToolBars={1}) -> қалпына келтірілді ({2})" -f $ws.RibbonStyle, $ws.ToolBars, $src)
