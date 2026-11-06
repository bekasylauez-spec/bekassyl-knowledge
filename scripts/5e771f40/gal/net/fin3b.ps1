$g = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e771f40-144d-493e-a1c3-679c0085cfb9\scratchpad\gal"
$jobs = @()
foreach ($k in 1, 3) { Copy-Item "$g\w\fin3.dwg" "$g\w\finp$k.dwg" -Force }
foreach ($k in 1, 3) {
  $jobs += Start-Job -ArgumentList $g, $k -ScriptBlock { param($g, $k)
    & "$g\net\run.ps1" -Cs "$g\net\layfix.cs" -Cmd "LAYFIX" -Dwg "$g\w\finp$k.dwg" -Env @{ LAYFIX_JSON = "$g\w\layfix_p$k.json" } -Save
    & "$g\net\run.ps1" -Cs "$g\net\plotl.cs" -Cmd "PLOTL" -Dwg "$g\w\finp$k.dwg" -Env @{ PLOTL_DIR = "$g\w\pdf3" } }
}
$jobs += Start-Job -ArgumentList $g -ScriptBlock { param($g) & "$g\net\run.ps1" -Cs "$g\net\layfix.cs" -Cmd "LAYFIX" -Dwg "$g\w\fin3.dwg" -Env @{ LAYFIX_JSON = "$g\w\layfix3.json" } -Save }
$jobs | Wait-Job | Receive-Job
(Get-ChildItem "$g\w\pdf3" -Filter "6.*.pdf").Count
