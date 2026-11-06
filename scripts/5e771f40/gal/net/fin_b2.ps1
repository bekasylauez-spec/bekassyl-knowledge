# Block 2 final: fin2 (already kept to the sheet row, saved by the live instance) -> 4 parallel LAYFIX+PLOTL copies + full LAYFIX
$g = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e771f40-144d-493e-a1c3-679c0085cfb9\scratchpad\gal"
$w = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\9a1000cd-e0d9-42b2-b432-f6f3db0e7099\scratchpad\gal\w"
New-Item -ItemType Directory -Force "$w\pdf2n" | Out-Null
Get-ChildItem "$w\pdf2n" -Filter *.pdf | Remove-Item
$jobs = @()
foreach ($k in 0..3) { Copy-Item "$w\fin2.dwg" "$w\f2p$k.dwg" -Force }
foreach ($k in 0..3) {
  $jobs += Start-Job -ArgumentList $g, $w, $k -ScriptBlock { param($g, $w, $k)
    & "$g\net\run.ps1" -Cs "$g\net\layfix.cs" -Cmd "LAYFIX" -Dwg "$w\f2p$k.dwg" -Env @{ LAYFIX_JSON = "$w\lay2_p$k.json" } -Save
    & "$g\net\run.ps1" -Cs "$g\net\plotl.cs" -Cmd "PLOTL" -Dwg "$w\f2p$k.dwg" -Env @{ PLOTL_DIR = "$w\pdf2n" } }
}
$jobs += Start-Job -ArgumentList $g, $w -ScriptBlock { param($g, $w) & "$g\net\run.ps1" -Cs "$g\net\layfix.cs" -Cmd "LAYFIX" -Dwg "$w\fin2.dwg" -Env @{ LAYFIX_JSON = "$w\lay2_all.json" } -Save }
$jobs | Wait-Job | Receive-Job
(Get-ChildItem "$w\pdf2n" -Filter *.pdf).Count
