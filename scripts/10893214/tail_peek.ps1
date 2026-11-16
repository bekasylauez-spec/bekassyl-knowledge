param([string[]]$Ids, [int]$TailKB = 600, [int]$Last = 6)
$dir = 'C:\Users\Admin\.claude\projects\D---------'
$Ids = @($Ids | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
foreach ($id in $Ids) {
  $f = Join-Path $dir ($id + '.jsonl')
  if (-not (Test-Path $f)) { "=== $id  (no file)"; continue }
  $fs = [IO.File]::Open($f, 'Open', 'Read', 'ReadWrite')
  try {
    $len = $fs.Length; $n = [int][Math]::Min($len, [long]$TailKB * 1024)
    $fs.Seek(-$n, 'End') | Out-Null
    $buf = New-Object byte[] $n; $r = 0
    while ($r -lt $n) { $k = $fs.Read($buf, $r, $n - $r); if ($k -le 0) { break }; $r += $k }
  } finally { $fs.Close() }
  $txt = [Text.Encoding]::UTF8.GetString($buf, 0, $r)
  $lines = @($txt -split "`n" | Where-Object { $_.Trim() })
  if ($n -lt $len -and $lines.Count -gt 0) { $lines = @($lines | Select-Object -Skip 1) }
  "=== $id  size=$([math]::Round($len/1MB,1))MB  mtime=$((Get-Item $f).LastWriteTime.ToString('HH:mm:ss'))  lines_in_tail=$($lines.Count)"
  $lines | Select-Object -Last $Last | ForEach-Object {
    $ln = $_
    try { $o = $ln | ConvertFrom-Json } catch { "  (unparsed, len=$($ln.Length)) head=" + $ln.Substring(0, [Math]::Min(160, $ln.Length)); return }
    $sr = ''; $ct = ''
    if ($o.message) {
      $sr = $o.message.stop_reason
      if ($o.message.content -is [array]) { $ct = ($o.message.content | ForEach-Object { $_.type }) -join ',' } elseif ($o.message.content) { $ct = 'str' }
    }
    "  type=$($o.type) sub=$($o.subtype) ts=$($o.timestamp) side=$($o.isSidechain) role=$($o.message.role) stop=$sr content=[$ct] len=$($ln.Length)"
    "      keys=" + (($o.PSObject.Properties.Name) -join ',')
  }
}
