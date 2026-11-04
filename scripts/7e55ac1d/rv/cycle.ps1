param([string]$JobFile)
# Close my Revit (answer "No" to saving the scratch boot doc), recompile RB.dll, queue the job, start Revit on boot.rte
$w = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\7e55ac1d-056c-477c-b1ef-1657f3036e17\scratchpad\rv"
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WC { [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l); }
"@
$p = Get-Process Revit -ErrorAction SilentlyContinue
if ($p) {
    $title = $p.MainWindowTitle
    if ($title -notmatch '\[boot') { "Revit has a non-scratch document open: $title"; exit 1 }
    $p.CloseMainWindow() | Out-Null
    Start-Sleep 2
    $root = [Windows.Automation.AutomationElement]::RootElement
    for ($i = 0; $i -lt 8 -and -not $p.HasExited; $i++) {
        $b = $root.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, "CommandButton_7")))
        $t = $root.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, "MainInstruction")))
        if ($b -and $t -and ($t.Current.Name -match '^Сохранить изменения в файле (boot|Проект)')) { "answer No: " + $t.Current.Name; [WC]::SendMessage([IntPtr]$b.Current.NativeWindowHandle, 0xF5, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
        Start-Sleep 3
    }
    if (-not $p.WaitForExit(90000)) { "Revit did not close"; exit 1 }
}
$rt = "C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.26"; $rv = "C:\Program Files\Autodesk\Revit 2025"
$refs = @("System.Private.CoreLib.dll", "System.Runtime.dll", "System.Collections.dll", "System.Linq.dll", "System.Text.Encoding.Extensions.dll", "netstandard.dll") | ForEach-Object { "/r:$rt\$_" }
$srcs = Get-ChildItem $w -Filter *.cs | Where-Object { $_.Name -ne 't.cs' } | ForEach-Object FullName
& C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /noconfig /nostdlib /t:library /utf8output /codepage:65001 /out:"$w\RB.dll" $refs "/r:$rv\RevitAPI.dll" "/r:$rv\RevitAPIUI.dll" $srcs
if ($LASTEXITCODE -ne 0) { "compile failed"; exit 1 }
Copy-Item "$w\RB.addin.off" "$env:APPDATA\Autodesk\Revit\Addins\2025\RB.addin" -Force
$jd = "$env:LOCALAPPDATA\rvjob"
Get-ChildItem $jd -File | Where-Object { $_.Name -notmatch '\.old' } | ForEach-Object { Rename-Item $_.FullName ($_.Name + ".old" + (Get-Random)) }
Copy-Item $JobFile "$jd\job.txt"
Start-Process "$rv\Revit.exe" -ArgumentList "`"$w\boot.rte`""
"started"
& "$w\dlgwatch.ps1"
