$g = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e771f40-144d-493e-a1c3-679c0085cfb9\scratchpad\gal"
Copy-Item "$g\w\m3w.dwg" "$g\w\fin3.dwg" -Force
& "$g\net\run.ps1" -Cs "$g\net\erasewin.cs" -Cmd "ERASEWIN" -Dwg "$g\w\fin3.dwg" -Env @{ KEEPWIN = "46100,419900,3227800,434950" } -Save
Select-String -Path "$g\net\console_erasewin.txt" -Pattern "ERASEWIN erased" | Select-Object -First 1
& "$g\net\run.ps1" -Cs "$g\net\layfix.cs" -Cmd "LAYFIX" -Dwg "$g\w\fin3.dwg" -Env @{ LAYFIX_JSON = "$g\w\layfix3.json" } -Save
Get-ChildItem "$g\w\pdf3" -Filter *.pdf | Remove-Item
& "$g\net\run.ps1" -Cs "$g\net\plotl.cs" -Cmd "PLOTL" -Dwg "$g\w\fin3.dwg" -Env @{ PLOTL_DIR = "$g\w\pdf3" }
(Get-ChildItem "$g\w\pdf3" -Filter *.pdf).Count
