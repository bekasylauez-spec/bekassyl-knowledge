$before=(Get-PSDrive C).Free
$script:fail=0; $script:n=0
function del($p){ try{ [System.IO.File]::Delete($p); $script:n++ }catch{ $script:fail++ } }
function deldir($p){ try{ [System.IO.Directory]::Delete($p,$true); $script:n++ }catch{ Get-ChildItem -LiteralPath $p -Recurse -File -Force -ErrorAction SilentlyContinue | % { del $_.FullName }; $script:fail++ } }
function delitem($i){ if($i.PSIsContainer){ deldir $i.FullName } else { del $i.FullName } }

# 1. LIRA Work residues (LIRA closed). Keep .lir/.ald/.rez/.DOCS
$w="C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Work"
Get-ChildItem -LiteralPath $w -File -Force | ? { $_.Name -match '#' -or $_.Extension -match '^\.(f74|crsn)' -or $_.Name -match '_(pv|01|01c)\.' } | % { del $_.FullName }
Get-ChildItem -LiteralPath "$w\TempDir" -Force -ErrorAction SilentlyContinue | % { delitem $_ }
"LIRA: $script:n deleted, $script:fail locked"

# 2. Temp root except claude and Rar$*
$script:n=0;$script:fail=0
Get-ChildItem -LiteralPath $env:TEMP -Force | ? { $_.Name -ne 'claude' -and $_.Name -notlike 'Rar$*' } | % { delitem $_ }
"Temp: $script:n deleted, $script:fail in use"

# 3. Old claude sessions: heavy files only, scripts kept
$cur='5db772bd-c405-453b-be09-59a886ce694e'; $script:n=0;$script:fail=0
Get-ChildItem -LiteralPath "$env:TEMP\claude" -Recurse -File -Force -ErrorAction SilentlyContinue | ? { $_.FullName -notmatch $cur -and $_.Extension -match '^\.(output|dxf|dwg|bak|png|pdf|jpg|log|sv\$|zip|tmp)$' } | % { del $_.FullName }
"claude: $script:n deleted, $script:fail failed"

Get-ChildItem -LiteralPath C:\Windows\Temp -Force -ErrorAction SilentlyContinue | % { delitem $_ }
"Freed GB: " + [math]::Round(((Get-PSDrive C).Free-$before)/1GB,2) + "  Free now GB: " + [math]::Round((Get-PSDrive C).Free/1GB,1)
