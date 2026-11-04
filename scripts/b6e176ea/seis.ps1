param([string]$Acc, [string]$CX, [string]$CY, [string]$CZ, [int]$Soil = 2, [string]$Qh = "4", [string]$Qv = "1.5")
# fill the LIRA dialog «Сейсмика (СП РК EN 1998-1:2004/2012, НТП РК 08-01.1-2017)» through window messages and press OK
$h = Join-Path $PSScriptRoot "win.ps1"
. $h list | Out-Null
if (-not ([System.Management.Automation.PSTypeName]"SeisM").Type) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class SeisM { [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }
"@
}
$dlg = ((& $h list | Where-Object { $_ -like "*Сейсмика (СП РК EN 1998*" }) -replace ' \|.*','')
if (-not $dlg) { "no dialog"; exit 1 }
$kids = & $h kids $dlg
$edits = @($kids | Where-Object { $_ -match '\| Edit \|' } | ForEach-Object { ($_ -split ' \| ')[0] })
$combo = ($kids | Where-Object { $_ -match '\| ComboBox \|' } | Select-Object -First 1) -replace ' \|.*',''
$btns = @($kids | Where-Object { $_ -match '\| Button \| $' } | ForEach-Object { ($_ -split ' \| ')[0] })
$vals = @("1", $Acc, $Qh, $Qv, "0.2", "1", "1", "1", $CX, $CY, $CZ)
for ($i = 0; $i -lt 11; $i++) { & $h set $edits[$i] $vals[$i] | Out-Null }
[SeisM]::SendMessage([IntPtr][long]$combo, 0x014E, [IntPtr]$Soil, [IntPtr]::Zero) | Out-Null
for ($i = 0; $i -lt 11; $i++) { $edits[$i] + " = " + [WinH]::Txt([IntPtr][long]$edits[$i]) }
& $h click $btns[0]
Start-Sleep 2
& $h list
