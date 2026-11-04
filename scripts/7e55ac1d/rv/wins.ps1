param([string]$Click = "")
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$p = Get-Process Revit -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { "no revit"; exit }
"pid $($p.Id) title [$($p.MainWindowTitle)] responding $($p.Responding)"
$root = [Windows.Automation.AutomationElement]::RootElement
$c = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty, $p.Id)
foreach ($w in $root.FindAll([Windows.Automation.TreeScope]::Children, $c)) {
    "WIN " + $w.Current.Name + " | " + $w.Current.ClassName
    if ($w.Current.ClassName -match 'Afx|HwndWrapper' -and $w.Current.Name -match 'Autodesk Revit 2025') { continue }
    foreach ($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants, [Windows.Automation.Condition]::TrueCondition)) {
        $t = $e.Current.ControlType.ProgrammaticName
        if ($t -match 'Button|Text|Hyperlink') {
            "   $t : $($e.Current.Name)"
            if ($Click -and $e.Current.Name -like $Click) {
                $ip = $null
                if ($e.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern, [ref]$ip)) { $ip.Invoke(); "   CLICKED" }
            }
        }
    }
}
