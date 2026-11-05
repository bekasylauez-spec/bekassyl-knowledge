param([int]$procId)
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
$ws = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
foreach ($w in $ws) {
  $r = $w.Current.BoundingRectangle
  "WIN '$($w.Current.Name)' class=$($w.Current.ClassName) rect=$($r.X),$($r.Y),$($r.Width),$($r.Height)"
  $all = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  $i = 0
  foreach ($e in $all) { if ($i -gt 80) { break }; $i++; $c=$e.Current; if ($c.Name) { "  [$($c.ControlType.ProgrammaticName)] '$($c.Name)' $($c.BoundingRectangle)" } }
}
