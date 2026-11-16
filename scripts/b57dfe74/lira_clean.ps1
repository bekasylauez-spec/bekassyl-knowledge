# LIRA-SAPR work folder: delete calculation result files of CLOSED, OLD models only.
# Deleted classes : <model>#NN.<model> , <model>.f74* , <model>.crsn1 , <model>_pv/_01/_01c.<model>
# Always kept     : .ald .rez .txt .rpt .rpl , #sn/#rsm/#sl/#pr/#of files, *.DOCS folders, everything of protected models
# Protected model : open in LIRA (window captions), any file newer than $RecentDays, or any file locked by a process.
param(
    [string]$W = 'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\work',
    [int]$RecentDays = 7,
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'

Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class WinCap {
    delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    static string Text(IntPtr h) { var sb = new StringBuilder(512); GetWindowText(h, sb, 512); return sb.ToString(); }
    // captions of all top-level windows of the process and all of their child windows (read-only)
    public static List<string> Captions(uint pid) {
        var res = new List<string>();
        var tops = new List<IntPtr>();
        EnumWindows((h, l) => { uint p; GetWindowThreadProcessId(h, out p); if (p == pid) tops.Add(h); return true; }, IntPtr.Zero);
        foreach (var t in tops) {
            var s = Text(t); if (s.Length > 0) res.Add(s);
            EnumChildWindows(t, (h, l) => { var c = Text(h); if (c.Length > 0) res.Add(c); return true; }, IntPtr.Zero);
        }
        return res;
    }
}
'@

# --- what LIRA has open
$caps = New-Object System.Collections.Generic.List[string]
$liraStart = $null
foreach ($p in Get-Process LiraSapr -ErrorAction SilentlyContinue) {
    if (-not $liraStart -or $p.StartTime -lt $liraStart) { $liraStart = $p.StartTime }
    foreach ($c in [WinCap]::Captions([uint32]$p.Id)) { $caps.Add($c) }
}
$capsLower = @($caps | ForEach-Object { $_.ToLower() } | Select-Object -Unique)
'LIRA running: {0}; started: {1}; window captions read: {2}' -f [bool]$liraStart, $liraStart, $capsLower.Count

# --- classify files
$di = New-Object IO.DirectoryInfo($W)
$models = @{}
function Get-Model([string]$b) {
    $k = $b.ToLower()
    if (-not $models.ContainsKey($k)) { $models[$k] = New-Object PSObject -Property @{ Name = $b; Del = (New-Object System.Collections.Generic.List[object]); Keep = (New-Object System.Collections.Generic.List[object]) } }
    return $models[$k]
}
foreach ($f in $di.EnumerateFiles()) {
    $n = $f.Name
    $m = [regex]::Match($n, '^(?<b>.+)#(?<n>[0-9]{2}[0-9A-Za-z]*)\.(?<b2>.+)$')
    if ($m.Success -and $m.Groups['b'].Value.ToLower() -eq $m.Groups['b2'].Value.ToLower()) { (Get-Model $m.Groups['b'].Value).Del.Add($f); continue }
    $m = [regex]::Match($n, '^(?<b>.+)\.(f74[a-z]*|crsn1)$', 'IgnoreCase')
    if ($m.Success) { (Get-Model $m.Groups['b'].Value).Del.Add($f); continue }
    $m = [regex]::Match($n, '^(?<b>.+)_(pv|01|01c)\.(?<b2>.+)$', 'IgnoreCase')
    if ($m.Success -and $m.Groups['b'].Value.ToLower() -eq $m.Groups['b2'].Value.ToLower()) { (Get-Model $m.Groups['b'].Value).Del.Add($f); continue }
    # everything else is kept; attach to its model for the "newest file" test
    $m = [regex]::Match($n, '^(?<b>.+)#[A-Za-z]+\.(?<b2>.+)$')
    if ($m.Success) { (Get-Model $m.Groups['b'].Value).Keep.Add($f); continue }
    $ext = $f.Extension
    $b = if ($ext) { $n.Substring(0, $n.Length - $ext.Length) } else { $n }
    (Get-Model $b).Keep.Add($f)
}

$cut = (Get-Date).AddDays(-$RecentDays)
$grand = [long]0; $plan = New-Object System.Collections.Generic.List[object]
'--- models ---'
foreach ($k in ($models.Keys | Sort-Object)) {
    $mo = $models[$k]
    if ($mo.Del.Count -eq 0) { continue }
    $delSize = [long]0; $newest = [datetime]::MinValue
    foreach ($f in $mo.Del) { $delSize += $f.Length; if ($f.LastWriteTime -gt $newest) { $newest = $f.LastWriteTime } }
    foreach ($f in $mo.Keep) { if ($f.LastWriteTime -gt $newest) { $newest = $f.LastWriteTime } }
    $docs = Join-Path $W ($mo.Name + '.DOCS')
    if (Test-Path -LiteralPath $docs) { $dn = (Get-Item -LiteralPath $docs).LastWriteTime; if ($dn -gt $newest) { $newest = $dn } }
    $reasons = @()
    if ($capsLower | Where-Object { $_.Contains($k) }) { $reasons += 'OPEN in LIRA' }
    if ($newest -ge $cut) { $reasons += ('recent ({0:MM-dd HH:mm})' -f $newest) }
    if ($liraStart -and $newest -ge $liraStart) { $reasons += 'touched since LIRA started' }
    $locked = 0
    foreach ($f in $mo.Del) { try { $fs = [IO.File]::Open($f.FullName, 'Open', 'Read', 'None'); $fs.Close() } catch { $locked++ } }
    if ($locked -gt 0) { $reasons += ('{0} file(s) in use' -f $locked) }
    if ($reasons.Count -eq 0) {
        $grand += $delSize; $plan.Add($mo)
        'DELETE  {0,9:N1} MB  {1,3} files  newest {2:yyyy-MM-dd}  kept: {3} files  [{4}]' -f ($delSize / 1MB), $mo.Del.Count, $newest, $mo.Keep.Count, $mo.Name
    } else {
        'PROTECT {0,9:N1} MB  {1,3} files  [{2}]  <- {3}' -f ($delSize / 1MB), $mo.Del.Count, $mo.Name, ($reasons -join '; ')
    }
}
'planned: {0} model(s), {1:N1} GB' -f $plan.Count, ($grand / 1GB)

if ($Apply) {
    $ok = 0; $fail = 0; $freed = [long]0
    foreach ($mo in $plan) {
        foreach ($f in $mo.Del) {
            try { $len = $f.Length; if ($f.IsReadOnly) { $f.IsReadOnly = $false }; [IO.File]::Delete($f.FullName); $ok++; $freed += $len }
            catch { $fail++; '  could not delete: ' + $f.Name }
        }
    }
    'DELETED: {0} files, {1:N1} GB   failed: {2}' -f $ok, ($freed / 1GB), $fail
} else { 'DRY RUN - nothing deleted' }
