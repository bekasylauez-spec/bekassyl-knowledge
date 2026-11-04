param([string]$Dwg, [string[]]$Commands, [string]$Done, [int]$Sec = 400)
# Runs commands in a separate AutoCAD (SPDS loaded), never the user's instance.
$s = $PSScriptRoot
$dll = Join-Path $s "BkSpds.dll"
Get-ChildItem (Split-Path $Dwg) -Filter "*.dwl*" -ErrorAction SilentlyContinue | Remove-Item -ErrorAction SilentlyContinue
$scr = "SECURELOAD`n0`nFILEDIA`n0`n_.NETLOAD`n$dll`n" + (($Commands | ForEach-Object { "$_`n" }) -join '') + "FILEDIA`n1`n_.QUIT`n_Y`n"
$scrPath = Join-Path $s "_run.scr"
[IO.File]::WriteAllText($scrPath, $scr, [Text.Encoding]::GetEncoding(1251))
if ($Done) { Remove-Item $Done -ErrorAction SilentlyContinue }
$p = Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" -ArgumentList "/nologo `"$Dwg`" /b `"$scrPath`"" -PassThru
$t0 = Get-Date
while (((Get-Date) - $t0).TotalSeconds -lt $Sec) {
  Start-Sleep 4
  if ($Done -and (Test-Path $Done)) { Start-Sleep 6; break }
  if ($p.HasExited) { break }
}
# only the process this script started; the user's AutoCAD is never touched
if (-not $p.HasExited) { if (-not $p.WaitForExit(30000)) { "killing own acad $($p.Id)"; $p.Kill() } }
if ($Done -and -not (Test-Path $Done)) { "no result file" }
