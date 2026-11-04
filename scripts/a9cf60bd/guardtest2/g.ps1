# ЛИРА-САПР 2024: интерфейсті стандарт (ленталы) күйде ұстау.
# ЛИРА жабық кезде ғана жұмыс істейді: ашық ЛИРА жабылғанда Workspace кілтін өзі қайта жазады.
# ЛИРА-да «Окно → Стиль интерфейса» тобы: Лента Плюс/Металл/ЖБК/Пользователя | Меню | Панели инструментов.
# Классикалық режимнің белгісі: Workspace\ToolBars = 1 (жабылғанда жазылады). Лента: ToolBars = 0.
# Қалпына келтіру: golden .reg бар болса, соны импорттайды, жоқ болса, ToolBars=0 қояды.
# Кілтті жай өшіру жеткіліксіз: ЛИРА бір рет лентамен ашылады да, жабылғанда ToolBars=1 қайта жазуы мүмкін.

$ErrorActionPreference = 'SilentlyContinue'
$dir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$golden = Join-Path $dir 'Workspace_standard.reg'
$log    = Join-Path $dir 'lira_guard.log'
$key    = 'HKCU:\Software\LIRA SAPR\LIRA SAPR 2024\VISOR-SAPR\WorkspaceTEST'
$keyReg = 'HKCU\Software\LIRA SAPR\LIRA SAPR 2024\VISOR-SAPR\WorkspaceTEST'

function Log($m) { Add-Content -Path $log -Value ("{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $m) -Encoding UTF8 }



$ws = Get-ItemProperty -Path $key
if (-not $ws) { exit 0 }

# ToolBars мәні тек ЛИРА жабылғанда жазылады: жоқ болса, күй толық емес, тиіспейміз.
if ($null -eq $ws.ToolBars) { exit 0 }

if ($ws.ToolBars -eq 0) {
    # Ленталы күйдің эталонын бір рет сақтау (ЛИРА жабылған соң толық жазылған күй).
    if (-not (Test-Path $golden)) {
        reg export $keyReg $golden /y | Out-Null
        Log "golden сақталды (RibbonStyle=$($ws.RibbonStyle), ToolBars=0)"
    }
    exit 0
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
New-Item -ItemType Directory -Force (Join-Path $dir 'backup') | Out-Null
reg export $keyReg (Join-Path $dir "backup\Workspace_broken_$stamp.reg") /y | Out-Null
if (Test-Path $golden) {
    reg delete $keyReg /f | Out-Null
    reg import $golden 2>$null | Out-Null
    $src = 'golden'
} else {
    Set-ItemProperty -Path $key -Name ToolBars -Value 0 -Type DWord
    if (-not $ws.RibbonStyle) { Set-ItemProperty -Path $key -Name RibbonStyle -Value 2 -Type DWord }
    $src = 'ToolBars=0'
}
Log ("классикалық күй табылды (RibbonStyle={0}, ToolBars={1}) -> қалпына келтірілді ({2})" -f $ws.RibbonStyle, $ws.ToolBars, $src)
