# download_then_shutdown.ps1 — BEKA-2: Chrome жүктеуі (Downloads\*.crdownload) біткен соң компьютерді өшіреді.
# 17.11.2026 пайдаланушы: «гуглда ревит тартылып жатыр, біткесін компты өшір».
# Іске қосу: Task Scheduler «BEKA2 download shutdown» (Claude PowerShell-і job object ішінде — ұзақ процесс тапсырма арқылы).
# Тоқтату: осы папкада STOP_DOWNLOAD файлын жаса; өшу санағы басталып кетсе: shutdown /a
# Логика:
#  1) .crdownload қалмаса және GraceSec бойы жаңасы шықпаса — бітті.
#  2) StallMin минут бірде-бір .crdownload өспесе (Chrome да диске жазбаса) — тоқтап қалды:
#     ZIP толық болса (Chrome «Сохранить» растауын күтіп тұр) — дерек жоғалмасын деп hardlink .zip жасайды;
#     толық болмаса (желі үзілді) — Chrome жартылай файлды жалғастыру үшін өзі сақтайды.
#  3) Өшірер алдында: Revit/AutoCAD/ЛИРА/Office ашық болса — өшірмейді (сақталмаған жұмыс);
#     пайдаланушы компьютерде болса (соңғы ActiveSec ішінде тінтуір/пернетақта) — IdleNeedSec тыныштықты күтеді.
#  4) shutdown /s /t ShutdownDelay (/t > 0 болғанда /f өзі қосылады). Жұмыс кезінде компьютер ұйқыға кетпейді.
param(
  [string]$Dir = "$env:USERPROFILE\Downloads",
  [int]$PollSec = 15,
  [double]$StallMin = 20,
  [int]$GraceSec = 90,
  [int]$ShutdownDelay = 120,
  [int]$ActiveSec = 300,
  [int]$IdleNeedSec = 600,
  [string]$TaskName = 'BEKA2 download shutdown',
  [switch]$DryRun
)
$ErrorActionPreference = 'Continue'
$Here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Log    = Join-Path $Here 'download_watch.log'
$Status = Join-Path $Here 'download_status.txt'
$Stop   = Join-Path $Here 'STOP_DOWNLOAD'
$Enc    = New-Object System.Text.UTF8Encoding $true

function Log([string]$m) { [System.IO.File]::AppendAllText($Log, (Get-Date -Format 'dd.MM HH:mm:ss') + '  ' + $m + "`r`n", $Enc) }
function SetStatus([string]$m) { [System.IO.File]::WriteAllText($Status, $m + '  ' + (Get-Date -Format 'dd.MM HH:mm:ss') + "`r`n", $Enc) }
function Unreg { & schtasks.exe /delete /tn $TaskName /f 2>$null | Out-Null }

if (-not ('DlW' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class DlW {
  [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);
  [StructLayout(LayoutKind.Sequential)] public struct LII { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")] static extern bool GetLastInputInfo(ref LII p);
  public static uint IdleSec() {
    LII l = new LII(); l.cbSize = (uint)Marshal.SizeOf(typeof(LII));
    if (!GetLastInputInfo(ref l)) return 0;
    return unchecked((uint)Environment.TickCount - l.dwTime) / 1000;
  }
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  public static extern bool CreateHardLink(string newName, string existing, IntPtr sa);
}
'@
}

function RealSize([string]$p) {
  # Ашық файлда каталог жазбасы ескіреді — нақты өлшем handle арқылы
  try { $fs = [System.IO.File]::Open($p, 'Open', 'Read', 'ReadWrite, Delete') } catch { return $null }
  try { return $fs.Length } finally { $fs.Close() }
}

function ZipComplete([string]$p) {
  # Соңында EOCD бар ма және central directory дәл соған (немесе ZIP64 жазбасына) тіреле ме
  try { $fs = [System.IO.File]::Open($p, 'Open', 'Read', 'ReadWrite, Delete') } catch { return $false }
  try {
    $len = $fs.Length
    if ($len -lt 22) { return $false }
    $h = New-Object byte[] 4; [void]$fs.Read($h, 0, 4)
    if ($h[0] -ne 0x50 -or $h[1] -ne 0x4B -or $h[2] -ne 3 -or $h[3] -ne 4) { return $false }
    $n = [int][Math]::Min($len, 65557); $b = New-Object byte[] $n
    $fs.Position = $len - $n; $r = 0
    while ($r -lt $n) { $k = $fs.Read($b, $r, $n - $r); if ($k -le 0) { break }; $r += $k }
    for ($i = $n - 22; $i -ge 0; $i--) {
      if ($b[$i] -ne 0x50 -or $b[$i+1] -ne 0x4B -or $b[$i+2] -ne 5 -or $b[$i+3] -ne 6) { continue }
      $eocd = $len - $n + $i
      $cdSize = [BitConverter]::ToUInt32($b, $i + 12); $cdOff = [BitConverter]::ToUInt32($b, $i + 16)
      if (([int64]$cdOff + [int64]$cdSize) -eq $eocd) { return $true }
      $j = $i - 20
      if ($j -lt 0 -or $b[$j] -ne 0x50 -or $b[$j+1] -ne 0x4B -or $b[$j+2] -ne 6 -or $b[$j+3] -ne 7) { return $false }
      $z = [BitConverter]::ToInt64($b, $j + 8)
      if ($z -lt 0 -or ($z + 56) -gt $len) { return $false }
      $rec = New-Object byte[] 56; $fs.Position = $z; [void]$fs.Read($rec, 0, 56)
      if ($rec[0] -ne 0x50 -or $rec[1] -ne 0x4B -or $rec[2] -ne 6 -or $rec[3] -ne 6) { return $false }
      return (([BitConverter]::ToInt64($rec, 48) + [BitConverter]::ToInt64($rec, 40)) -eq $z)
    }
    return $false
  } finally { $fs.Close() }
}

$AppRx = '^(Revit|acad|accoreconsole|Lira.*|EXCEL|WINWORD|POWERPNT|TeklaStructures|IdeaStatiCa.*)$'
function WorkApps { @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match $AppRx } | ForEach-Object { $_.ProcessName } | Sort-Object -Unique) }
function CheckAbort {
  if (Test-Path -LiteralPath $Stop) {
    Log 'STOP_DOWNLOAD файлы — тоқтадым, компьютерді өшірмеймін'
    Remove-Item -LiteralPath $Stop -ErrorAction SilentlyContinue; SetStatus 'STOPPED'; Unreg; exit 0
  }
}

if ($MyInvocation.InvocationName -eq '.') { return }   # dot-source: тек функциялар (тест үшін)

trap { Log ('ҚАТЕ: ' + $_.Exception.Message); continue }

$start = Get-Date
[void][DlW]::SetThreadExecutionState([uint32]2147483649)   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED — ұйқыға кетпесін
Log ("=== басталды pid $PID; папка $Dir; тоқтау шегі $StallMin мин" + $(if ($DryRun) { '; DryRun' } else { '' }))
SetStatus 'STARTING'
$state = @{}; $noneSince = $null; $lastAct = Get-Date; $prevW = $null
$repT = $null; $repS = [int64]0; $reason = $null
while (-not $reason) {
  CheckAbort
  $now = Get-Date
  $cr = @(Get-ChildItem -LiteralPath $Dir -Filter '*.crdownload' -File -ErrorAction SilentlyContinue)
  $w = (Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue | Measure-Object -Property WriteTransferCount -Sum).Sum
  $busy = ($null -ne $prevW -and $null -ne $w -and ($w - $prevW) -gt 20MB); $prevW = $w
  if ($cr.Count -eq 0) {
    if ($null -eq $noneSince) { $noneSince = $now; Log ".crdownload қалмады — $GraceSec с күтемін"; SetStatus 'FINISHING' }
    elseif (($now - $noneSince).TotalSeconds -ge $GraceSec) { $reason = 'completed' }
  } else {
    if ($null -ne $noneSince) { Log 'жаңа .crdownload пайда болды — күтуді жалғастырамын'; $noneSince = $null }
    $total = [int64]0
    foreach ($f in $cr) {
      $sz = RealSize $f.FullName
      if ($null -eq $sz) { continue }
      $total += $sz
      if (-not $state.ContainsKey($f.FullName)) { $state[$f.FullName] = $sz; $lastAct = $now; Log ('бақылаймын: {0}  {1:N2} ГБ' -f $f.Name, ($sz / 1GB)) }
      elseif ($state[$f.FullName] -ne $sz) { $state[$f.FullName] = $sz; $lastAct = $now }
    }
    if ($busy) { $lastAct = $now }
    if (($now - $lastAct).TotalMinutes -ge $StallMin) { $reason = 'stalled' }
    if ($null -eq $repT) { $repT = $now; $repS = $total }
    elseif (($now - $repT).TotalSeconds -ge 300) {
      Log ('{0:N2} ГБ, {1:N2} МБ/с' -f ($total / 1GB), (($total - $repS) / ($now - $repT).TotalSeconds / 1MB)); $repT = $now; $repS = $total
    }
    SetStatus ('DOWNLOADING {0:N2} GB, files {1}, no-growth {2:N1} min' -f ($total / 1GB), $cr.Count, ($now - $lastAct).TotalMinutes)
  }
  if (-not $reason) { Start-Sleep -Seconds $PollSec }
}
Log "себеп: $reason"

$msg = 'Жүктеу бітті — компьютер 2 минуттан кейін өшеді. Тоқтату: Win+R → shutdown /a'
if ($reason -eq 'stalled') {
  $msg = 'Жүктеу тоқтап қалды — компьютер 2 минуттан кейін өшеді. Тоқтату: Win+R → shutdown /a'
  foreach ($f in @(Get-ChildItem -LiteralPath $Dir -Filter '*.crdownload' -File -ErrorAction SilentlyContinue)) {
    $sz = RealSize $f.FullName
    if (ZipComplete $f.FullName) {
      $link = Join-Path $Dir ('Revit_жүктеу_' + (Get-Date -Format 'yyyyMMdd_HHmm') + '.zip')
      if ([DlW]::CreateHardLink($link, $f.FullName, [IntPtr]::Zero)) { Log ('{0}: ZIP толық ({1:N2} ГБ), Chrome растауын күтіп тұр — дерек жоғалмасын деп hardlink: {2}' -f $f.Name, ($sz / 1GB), $link) }
      else { Log ('hardlink жасалмады, қате {0}' -f [Runtime.InteropServices.Marshal]::GetLastWin32Error()) }
    } else {
      Log ('{0}: {1:N2} ГБ, толық емес (желі үзілген болуы мүмкін) — Chrome жартылай файлды жалғастыру үшін сақтайды' -f $f.Name, ($sz / 1GB))
    }
  }
} else {
  Get-ChildItem -LiteralPath $Dir -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -ne '.crdownload' } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 3 |
    ForEach-Object { Log ('файл: {0}  {1:N2} ГБ  {2:dd.MM HH:mm}' -f $_.Name, ($_.Length / 1GB), $_.LastWriteTime) }
}

function CheckApps {
  $a = WorkApps
  if ($a.Count -gt 0) {
    Log ('ашық бағдарлама: ' + ($a -join ', ') + ' — сақталмаған жұмыс жоғалмасын деп компьютерді өшірмеймін')
    SetStatus 'SKIPPED_APPS'; Unreg; exit 0
  }
}
CheckAbort; CheckApps
$idle = [DlW]::IdleSec()
if ($idle -lt $ActiveSec) {
  Log "пайдаланушы компьютерде (соңғы әрекет $idle с бұрын) — $IdleNeedSec с тыныштықты күтемін"
  SetStatus 'WAIT_IDLE'
  while ([DlW]::IdleSec() -lt $IdleNeedSec) { Start-Sleep -Seconds 30; CheckAbort; CheckApps }
}
if ($DryRun) { Log "DryRun: shutdown /s /t $ShutdownDelay — орындалмады"; SetStatus 'DRYRUN'; exit 0 }
& "$env:SystemRoot\System32\shutdown.exe" /s /t $ShutdownDelay /c $msg
$ec = $LASTEXITCODE
Log "shutdown /s /t $ShutdownDelay берілді (код $ec)"
SetStatus "SHUTDOWN code $ec"
Unreg
