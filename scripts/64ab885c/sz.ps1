param($root)
function Sz($p){ $t=0; try{ $t=(Get-ChildItem -LiteralPath $p -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum }catch{}; [math]::Round($t/1GB,2) }
Get-ChildItem -LiteralPath $root -Force -Directory -ErrorAction SilentlyContinue | Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) } | ForEach-Object { [pscustomobject]@{GB=(Sz $_.FullName); Path=$_.FullName} } | Sort-Object GB -Descending | Select-Object -First 25 | Format-Table -AutoSize | Out-String -Width 200
