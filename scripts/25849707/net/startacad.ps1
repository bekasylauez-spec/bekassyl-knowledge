$boot = Join-Path $PSScriptRoot "boot.scr"
$cl = '"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" /nologo /b "' + $boot + '"'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = $cl}
$r.ProcessId
