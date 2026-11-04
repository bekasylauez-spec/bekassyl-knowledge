param([string]$Geo, [double]$X, [double]$Y, [double]$R)
# prints entities of a geo dump within R of (X,Y), coordinates relative to (X,Y)
foreach ($ln in [IO.File]::ReadAllLines($Geo, [Text.Encoding]::GetEncoding(1251))) {
  $f = $ln -split "`t"
  $n = @($f[2] -split ' ' | Where-Object { $_ -ne '' } | ForEach-Object { [double]$_ })
  if ($n.Count -lt 2) { continue }
  $near = $false
  if ($f[0] -eq 'L') { $near = ([math]::Abs($n[0] - $X) -lt $R -and [math]::Abs($n[1] - $Y) -lt $R) -or ([math]::Abs($n[2] - $X) -lt $R -and [math]::Abs($n[3] - $Y) -lt $R) }
  else { $near = [math]::Abs($n[0] - $X) -lt $R -and [math]::Abs($n[1] - $Y) -lt $R }
  if (-not $near) { continue }
  if ($f[0] -eq 'L') { "{0} {1} ({2:N0},{3:N0})-({4:N0},{5:N0}) L={6:N0}" -f $f[0], $f[1], ($n[0] - $X), ($n[1] - $Y), ($n[2] - $X), ($n[3] - $Y), [math]::Sqrt(($n[2] - $n[0]) * ($n[2] - $n[0]) + ($n[3] - $n[1]) * ($n[3] - $n[1])) }
  elseif ($f[0] -eq 'T') { "T {0} ({1:N0},{2:N0}) h={3:N0} rot={4} ha={5} [{6}]" -f $f[1], ($n[0] - $X), ($n[1] - $Y), $n[4], $n[5], $n[8], $f[4] }
  elseif ($f[0] -eq 'C') { "C {0} ({1:N0},{2:N0}) r={3:N0}" -f $f[1], ($n[0] - $X), ($n[1] - $Y), $n[2] }
  else { "{0} {1} ({2:N0},{3:N0}) {4}" -f $f[0], $f[1], ($n[0] - $X), ($n[1] - $Y), ($f[3..($f.Count-1)] -join ' ') }
}
